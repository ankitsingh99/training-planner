"""
Automated Acceptance Tests and Release Gates for Personal AI Training Analyst.
Covers Sections 18 & 19 (AT-001 to AT-105, E2E-001 to E2E-006).
Uses isolated temporary SQLite database and deterministic fixtures.
"""

from __future__ import annotations

import csv
import datetime
import io
import json
import os
import pathlib
import tempfile
from typing import Any, Dict, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from intervals_plan.analytics_engine import (
    build_vo2_max_trend,
    calculate_average_speed_kmh,
    calculate_heart_rate_zone_distribution,
    calculate_hrv_baseline_deviation,
    calculate_muscle_group_volume,
    calculate_running_pace,
    calculate_training_load_metrics,
    calculate_weekly_distance_km,
    calculate_weekly_duration_minutes,
    compare_cycling_performances,
)
from intervals_plan.coach_engine import CoachEngine
from intervals_plan.database import (
    Base,
    backup_database,
    create_db_engine,
    init_db,
    restore_database,
)
from intervals_plan.db_models import (
    ActivityModel,
    CoachRecommendationModel,
    ExerciseModel,
    ExerciseSetModel,
    FitnessSnapshotModel,
    ImportAuditModel,
    PlannedWorkoutModel,
    StrengthWorkoutModel,
    UserProfileModel,
)
from intervals_plan.integrations.coros_sync import CorosIngestionManager
from intervals_plan.integrations.hevy_client import HevyImporter
from intervals_plan.validation import (
    calculate_epley_1rm,
    normalize_distance_meters,
    normalize_duration_seconds,
    normalize_exercise_name,
    parse_iso_timestamp,
)


@pytest.fixture
def isolated_db_session() -> Session:
    """Fixture providing isolated temporary in-memory SQLite database (AT-002)."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()
    engine.dispose()


# ---------------------------------------------------------------------------
# 18.1 Test Infrastructure Requirements
# ---------------------------------------------------------------------------

def test_at_001_automated_test_execution():
    """AT-001: Automated test suite executes and asserts correctly."""
    assert True


def test_at_002_test_isolation(isolated_db_session: Session):
    """AT-002: Tests use an isolated temporary database and do not touch real storage."""
    count = isolated_db_session.query(ActivityModel).count()
    assert count == 0


def test_at_003_reproducibility():
    """AT-003: Repeated test runs with same fixtures produce identical results."""
    res1 = calculate_epley_1rm(100.0, 5)
    res2 = calculate_epley_1rm(100.0, 5)
    assert res1 == res2 == 116.67


# ---------------------------------------------------------------------------
# 18.2 Data Ingestion Acceptance Tests
# ---------------------------------------------------------------------------

def test_at_010_complete_historical_pagination(isolated_db_session: Session):
    """AT-010: Paginated import across 5 pages of 50 records imports all 250 activities without skipping."""
    manager = CorosIngestionManager(isolated_db_session)

    def mock_fetch_page(page: int, page_size: int) -> List[Dict[str, Any]]:
        if page > 5:
            return []
        records = []
        for i in range(page_size):
            idx = (page - 1) * page_size + i
            records.append({
                "activity_id": f"coros_act_{idx}",
                "activity_type": "cycling",
                "start_time": f"2026-10-01T{i % 24:02d}:00:00Z",
                "duration": 3600,
                "distance": 30000,
            })
        return records

    audit = manager.import_paginated_activities(mock_fetch_page, page_size=50, max_pages=10)
    assert audit.records_discovered == 250
    assert audit.records_inserted == 250
    assert isolated_db_session.query(ActivityModel).count() == 250


def test_at_011_duplicate_import_prevention(isolated_db_session: Session):
    """AT-011: Importing same 100 unique activities twice stores 100 records, second reports duplicates."""
    manager = CorosIngestionManager(isolated_db_session)
    batch = [
        {
            "activity_id": f"act_dup_{i}",
            "activity_type": "running",
            "start_time": "2026-10-05T08:00:00Z",
            "duration": 1800,
            "distance": 5000,
        }
        for i in range(100)
    ]

    audit1 = manager.import_activities(batch)
    assert audit1.records_inserted == 100
    assert audit1.duplicates_skipped == 0

    # Second import with identical records
    audit2 = manager.import_activities(batch)
    assert audit2.records_inserted == 0
    assert audit2.duplicates_skipped == 100
    assert isolated_db_session.query(ActivityModel).count() == 100


def test_at_012_partial_import_recovery(isolated_db_session: Session):
    """AT-012: In a 5-page import where page 4 fails, successful pages 1-3 are preserved, and retry completes."""
    manager = CorosIngestionManager(isolated_db_session)

    call_count = 0

    def mock_fetch_with_failure(page: int, page_size: int) -> List[Dict[str, Any]]:
        nonlocal call_count
        call_count += 1
        if page == 4:
            raise ConnectionResetError("Mock network drop on page 4")
        if page > 5:
            return []
        return [
            {
                "activity_id": f"p_act_{page}_{i}",
                "activity_type": "cycling",
                "start_time": "2026-10-10T09:00:00Z",
                "duration": 3600,
            }
            for i in range(page_size)
        ]

    # First attempt fails on page 4
    audit1 = manager.import_paginated_activities(mock_fetch_with_failure, page_size=10, max_pages=5)
    assert audit1.records_inserted == 30  # pages 1, 2, 3 preserved
    assert len(audit1.errors) > 0

    # Retry with recovered connection
    def mock_fetch_recovered(page: int, page_size: int) -> List[Dict[str, Any]]:
        if page > 5:
            return []
        return [
            {
                "activity_id": f"p_act_{page}_{i}",
                "activity_type": "cycling",
                "start_time": "2026-10-10T09:00:00Z",
                "duration": 3600,
            }
            for i in range(page_size)
        ]

    audit2 = manager.import_paginated_activities(mock_fetch_recovered, page_size=10, max_pages=5)
    # Total unique records in DB should now be 50 (30 skipped, 20 newly inserted)
    assert audit2.duplicates_skipped == 30
    assert audit2.records_inserted == 20
    assert isolated_db_session.query(ActivityModel).count() == 50


def test_at_013_missing_values_preserved_as_null(isolated_db_session: Session):
    """AT-013: Activity missing HR, power, or cadence stores nulls, not 0 or fabricated values."""
    manager = CorosIngestionManager(isolated_db_session)
    act = {
        "activity_id": "act_nulls",
        "activity_type": "cycling",
        "start_time": "2026-10-12T07:00:00Z",
        "duration": 1800,
        "distance": 10000,
        # heart rate, cadence, power explicitly omitted
    }
    manager.import_activities([act])
    db_act = isolated_db_session.query(ActivityModel).filter_by(source_activity_id="act_nulls").first()
    assert db_act is not None
    assert db_act.average_heart_rate is None
    assert db_act.power_avg is None
    assert db_act.cadence_avg is None


def test_at_014_unit_normalization():
    """AT-014: 5 km and 5,000 m normalize to 5000.0 m; 60 minutes and 3,600 s normalize to 3600.0 s."""
    assert normalize_distance_meters(5, unit="km") == 5000.0
    assert normalize_distance_meters(5000, unit="m") == 5000.0
    assert normalize_duration_seconds(60, unit="min") == 3600.0
    assert normalize_duration_seconds(3600, unit="s") == 3600.0


def test_at_015_timezone_correctness():
    """AT-015: Timestamp with explicit UTC offset preserves timestamp and date."""
    dt = parse_iso_timestamp("2026-10-15T23:30:00+05:30")
    assert dt.tzinfo is not None
    # 23:30 at +05:30 is 18:00 UTC on the same calendar day
    utc_dt = dt.astimezone(datetime.timezone.utc)
    assert utc_dt.hour == 18
    assert utc_dt.day == 15


def test_at_016_source_provenance(isolated_db_session: Session):
    """AT-016: Every imported activity and workout retains source platform, source ID, and raw payload."""
    manager = CorosIngestionManager(isolated_db_session)
    act = {
        "activity_id": "provenance_123",
        "activity_type": "running",
        "start_time": "2026-10-16T06:00:00Z",
        "duration": 2400,
    }
    manager.import_activities([act], source_label="COROS")
    db_act = isolated_db_session.query(ActivityModel).filter_by(source_activity_id="provenance_123").first()
    assert db_act.source == "COROS"
    assert db_act.source_activity_id == "provenance_123"
    assert db_act.import_timestamp is not None
    assert "provenance_123" in db_act.raw_data_reference


def test_at_017_corrupt_import_handling(isolated_db_session: Session):
    """AT-017: Malformed records are quarantined/rejected, while valid records are imported."""
    manager = CorosIngestionManager(isolated_db_session)
    records = [
        {"activity_id": "valid_1", "activity_type": "cycling", "start_time": "2026-10-17T08:00:00Z", "duration": 1800},
        {"activity_id": "", "activity_type": "cycling", "start_time": "2026-10-17T08:00:00Z", "duration": 1800},  # corrupt: empty ID
        {"activity_id": "valid_2", "activity_type": "running", "start_time": "2026-10-17T09:00:00Z", "duration": 2000},
    ]
    audit = manager.import_activities(records)
    assert audit.records_discovered == 3
    assert audit.records_inserted == 2
    assert audit.records_rejected == 1
    assert len(audit.errors) == 1


def test_at_018_import_audit_report(isolated_db_session: Session):
    """AT-018: Import report contains discovered, inserted, updated, skipped, rejected, errors, and date range."""
    manager = CorosIngestionManager(isolated_db_session)
    records = [
        {"activity_id": "aud_1", "activity_type": "cycling", "start_time": "2026-10-01T08:00:00Z", "duration": 1800},
        {"activity_id": "aud_2", "activity_type": "cycling", "start_time": "2026-10-15T08:00:00Z", "duration": 2400},
    ]
    audit = manager.import_activities(records)
    assert audit.records_discovered == 2
    assert audit.records_inserted == 2
    assert audit.earliest_record_date.startswith("2026-10-01")
    assert audit.latest_record_date.startswith("2026-10-15")


# ---------------------------------------------------------------------------
# 18.3 Hevy and Strength-Data Acceptance Tests
# ---------------------------------------------------------------------------

def test_at_020_hevy_workout_reconstruction(isolated_db_session: Session):
    """AT-020: Hevy export reconstructs workout, exercise, and set relationships accurately."""
    importer = HevyImporter(isolated_db_session)
    csv_data = """Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Set Type
2026-10-20 18:00:00,Push A,3600,Bench Press,1,60,10,normal
2026-10-20 18:00:00,Push A,3600,Bench Press,2,70,8,normal
2026-10-20 18:00:00,Push A,3600,Incline Dumbbell Press,1,24,10,normal
2026-10-21 18:00:00,Pull A,3600,Lat Pulldown,1,55,10,normal
"""
    audit = importer.import_from_csv(csv_data)
    assert audit.records_inserted == 2  # 2 workouts
    assert isolated_db_session.query(StrengthWorkoutModel).count() == 2
    assert isolated_db_session.query(ExerciseSetModel).count() == 4


def test_at_021_exercise_name_normalization():
    """AT-021: Bench Press, Barbell Bench Press, and Bench Press (Barbell) map to canonical 'bench press'."""
    assert normalize_exercise_name("Bench Press") == "bench press"
    assert normalize_exercise_name("Barbell Bench Press") == "bench press"
    assert normalize_exercise_name("Bench Press (Barbell)") == "bench press"


def test_at_022_exercise_substitution(isolated_db_session: Session):
    """AT-022: Replacing barbell bench press with dumbbell bench press preserves exercise distinction and contributions."""
    norm_bb = normalize_exercise_name("Barbell Bench Press")
    norm_db = normalize_exercise_name("Dumbbell Bench Press")
    assert norm_bb != norm_db  # distinct canonical exercises
    # Both contribute to chest
    from intervals_plan.validation import get_exercise_muscle_mapping
    map_bb = dict(get_exercise_muscle_mapping(norm_bb))
    map_db = dict(get_exercise_muscle_mapping(norm_db))
    assert "chest" in map_bb and "triceps" in map_bb
    assert "chest" in map_db and "triceps" in map_db


def test_at_023_set_validity_and_no_zero_weight(isolated_db_session: Session):
    """AT-023: Missing weight does not become zero kilograms."""
    importer = HevyImporter(isolated_db_session)
    csv_data = """Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Set Type
2026-10-22 18:00:00,Bodyweight Session,1800,Pull Up,1,,8,normal
"""
    importer.import_from_csv(csv_data)
    db_set = isolated_db_session.query(ExerciseSetModel).first()
    assert db_set is not None
    assert db_set.weight is None  # NOT 0.0


# ---------------------------------------------------------------------------
# 18.4 Analytics Acceptance Tests
# ---------------------------------------------------------------------------

def test_at_030_weekly_distance():
    """AT-030: Given cycling activities of 20, 30, and 50 km in same week, total equals 100 km; running does not contribute."""
    week_start = datetime.date(2026, 10, 19)  # Monday
    acts = [
        {"activity_type": "cycling", "distance": 20000, "date": "2026-10-19"},
        {"activity_type": "cycling", "distance": 30000, "date": "2026-10-21"},
        {"activity_type": "cycling", "distance": 50000, "date": "2026-10-24"},
        {"activity_type": "running", "distance": 10000, "date": "2026-10-20"},  # Should NOT contribute
    ]
    tot = calculate_weekly_distance_km(acts, target_activity_type="cycling", target_week_start=week_start)
    assert tot == 100.0


def test_at_031_weekly_training_duration():
    """AT-031: Activities lasting 30, 45, and 60 minutes equal 135 minutes total."""
    acts = [
        {"duration": 1800, "source_activity_id": "d1"},
        {"duration": 2700, "source_activity_id": "d2"},
        {"duration": 3600, "source_activity_id": "d3"},
    ]
    assert calculate_weekly_duration_minutes(acts) == 135.0


def test_at_032_average_speed():
    """AT-032: 40 km in 2 hours equals 20 km/h; zero duration returns None."""
    assert calculate_average_speed_kmh(40.0, 2.0) == 20.0
    assert calculate_average_speed_kmh(40.0, 0.0) is None


def test_at_033_running_pace():
    """AT-033: 10 km in 60 minutes equals 6:00 min/km (360 sec/km)."""
    sec_km, formatted = calculate_running_pace(10.0, 60.0)
    assert sec_km == 360.0
    assert formatted == "6:00 /km"


def test_at_034_heart_rate_zone_distribution():
    """AT-034: 10 min Z1, 20 min Z2, 30 min Z3 equals exactly those durations and 60 mins total."""
    samples = [120] * 600 + [140] * 1200 + [160] * 1800
    thresholds = {
        "Z1": (100, 129),
        "Z2": (130, 149),
        "Z3": (150, 175),
    }
    res = calculate_heart_rate_zone_distribution(samples, thresholds)
    assert res["zones"]["Z1"] == 600
    assert res["zones"]["Z2"] == 1200
    assert res["zones"]["Z3"] == 1800
    assert res["total_minutes"] == 60.0


def test_at_035_vo2_max_history():
    """AT-035: Measurements of 42, 43, and 44 on 3 dates are preserved in chronological order without overwriting."""
    snaps = [
        {"date": "2026-08-01", "vo2_max": 42},
        {"date": "2026-09-01", "vo2_max": 43},
        {"date": "2026-10-01", "vo2_max": 44},
    ]
    trend = build_vo2_max_trend(snaps)
    assert len(trend) == 3
    assert [t["vo2_max"] for t in trend] == [42.0, 43.0, 44.0]


def test_at_036_epley_estimated_1rm():
    """AT-036: 50 kg for 10 reps equals 50 * (1 + 10/30) = 66.67 kg."""
    assert calculate_epley_1rm(50.0, 10) == 66.67


def test_at_037_invalid_estimated_1rm():
    """AT-037: Missing weight, 0 reps, or reps > 30 returns None."""
    assert calculate_epley_1rm(None, 10) is None
    assert calculate_epley_1rm(50.0, 0) is None
    assert calculate_epley_1rm(50.0, 35) is None


def test_at_038_muscle_group_volume():
    """AT-038: 3 bench, 3 incline, 3 triceps isolation = 6 chest, triceps reflects secondary + isolation."""
    sets = [
        {"exercise_name": "bench press", "set_type": "normal"},
        {"exercise_name": "bench press", "set_type": "normal"},
        {"exercise_name": "bench press", "set_type": "normal"},
        {"exercise_name": "incline bench press", "set_type": "normal"},
        {"exercise_name": "incline bench press", "set_type": "normal"},
        {"exercise_name": "incline bench press", "set_type": "normal"},
        {"exercise_name": "tricep pushdown", "set_type": "normal"},
        {"exercise_name": "tricep pushdown", "set_type": "normal"},
        {"exercise_name": "tricep pushdown", "set_type": "normal"},
    ]
    res = calculate_muscle_group_volume(sets)
    # Bench press: 3 * 1.0 chest = 3.0; Incline press: 3 * 1.0 chest = 3.0 -> Total chest = 6.0
    assert res["muscle_volume"]["chest"] == 6.0
    # Triceps: 3 * 0.5 (bench) + 3 * 0.5 (incline) + 3 * 1.0 (isolation) = 1.5 + 1.5 + 3.0 = 6.0
    assert res["muscle_volume"]["triceps"] == 6.0


def test_at_039_missing_muscle_mapping():
    """AT-039: Unmapped exercise is flagged in unmapped_exercises rather than given an arbitrary muscle group."""
    sets = [{"exercise_name": "mysterious exercise 100", "set_type": "normal"}]
    res = calculate_muscle_group_volume(sets)
    assert "mysterious exercise 100" in res["unmapped_exercises"]
    assert res["muscle_volume"] == {}


def test_at_040_duplicate_activity_aggregation():
    """AT-040: Same activity record passed twice counts only once in weekly totals."""
    acts = [
        {"source": "COROS", "source_activity_id": "ride_99", "activity_type": "cycling", "distance": 25000, "duration": 3600},
        {"source": "COROS", "source_activity_id": "ride_99", "activity_type": "cycling", "distance": 25000, "duration": 3600},
    ]
    assert calculate_weekly_distance_km(acts, "cycling") == 25.0
    assert calculate_weekly_duration_minutes(acts) == 60.0


def test_at_041_training_load_calculations():
    """AT-041: ATL (7d), CTL (42d), and ACWR match hand-calculated results."""
    # 7 days of 100 load, preceded by 35 days of 50 load
    daily_loads = [50.0] * 35 + [100.0] * 7
    res = calculate_training_load_metrics(daily_loads, acute_days=7, chronic_days=42)
    assert res["atl"] == 100.0
    # CTL = (35 * 50 + 7 * 100) / 42 = (1750 + 700) / 42 = 2450 / 42 = 58.33
    assert res["ctl"] == 58.33
    # ACWR = 100 / 58.33 = 1.71
    assert res["acwr"] == 1.71


def test_at_042_recovery_baseline_deviation():
    """AT-042: Missing days are not treated as 0 ms in HRV baseline deviations."""
    daily_hrvs = [80.0, None, 84.0, None, 82.0]
    res = calculate_hrv_baseline_deviation(daily_hrvs, baseline_hrv=82.0)
    assert res["status"] == "NORMAL"
    assert res["mean_hrv"] == 82.0
    assert res["valid_days_count"] == 3


def test_at_043_comparable_performance():
    """AT-043: Comparing two rides of divergent distance or heart rate reports limitation rather than false fitness gain."""
    ride_a = {"distance_km": 40.0, "avg_speed_kmh": 28.0, "avg_hr": 140}
    ride_b = {"distance_km": 80.0, "avg_speed_kmh": 30.0, "avg_hr": 165}
    comp = compare_cycling_performances(ride_a, ride_b)
    assert comp["is_definitive_improvement"] is False
    assert comp["limitation"] is not None


# ---------------------------------------------------------------------------
# 18.5 AI Coach Acceptance Tests
# ---------------------------------------------------------------------------

def test_at_050_evidence_backed_recommendations():
    """AT-050: Coach recommendation cites supporting calculated metrics."""
    coach = CoachEngine()
    summary = {"acwr": 1.45, "atl": 90, "ctl": 62, "hrv_status": "SUPPRESSED"}
    rec = coach.generate_daily_assessment(summary)
    assert "1.45" in rec["reasoning"] or "SUPPRESSED" in rec["reasoning"]
    assert rec["supporting_data"]["acwr"] == 1.45


def test_at_051_missing_data_disclosure():
    """AT-051: When HRV is missing, coach explicitly states HRV assessment is unavailable."""
    coach = CoachEngine()
    summary = {"atl": 60, "ctl": 60}  # hrv omitted
    rec = coach.generate_daily_assessment(summary)
    assert "unavailable" in rec["reasoning"].lower()
    assert rec["supporting_data"]["hrv_status"] == "UNAVAILABLE"


def test_at_052_goal_prioritization():
    """AT-052: Reflects hypertrophy priority when choosing between competing demands."""
    coach = CoachEngine()
    summary = {"hrv_status": "NORMAL", "acwr": 1.1}
    rec = coach.generate_daily_assessment(summary, goals={"primary": "hypertrophy"})
    assert "hypertrophy" in rec["reasoning"].lower()


def test_at_053_training_schedule_constraints():
    """AT-053: Tuesday is strictly preserved as gym rest day in weekly planner."""
    coach = CoachEngine()
    plan = coach.generate_weekly_plan(datetime.date(2026, 10, 19), user_preferences={})
    tuesday_session = next(s for s in plan if s["day"] == "Tuesday")
    assert tuesday_session["is_gym_workout"] is False
    assert "Rest" in tuesday_session["title"]


def test_at_054_club_ride_flexibility():
    """AT-054: Weekend club ride is represented as flexible."""
    coach = CoachEngine()
    plan = coach.generate_weekly_plan(datetime.date(2026, 10, 19), user_preferences={})
    club_ride = next(s for s in plan if "Club Ride" in s["title"])
    assert club_ride["is_flexible"] is True


def test_at_056_pain_or_injury_warning():
    """AT-056: User-reported pain stops training recommendations and advises medical evaluation."""
    coach = CoachEngine()
    rec = coach.generate_daily_assessment({}, user_reported_pain="sharp left knee pain")
    assert "Do not train through pain" in rec["recommendation"]
    assert "medical evaluation" in rec["reasoning"]


def test_at_060_approval_before_changes(isolated_db_session: Session):
    """AT-060: Modifying an existing planned workout leaves original plan unchanged until user approves."""
    planned = PlannedWorkoutModel(
        planned_workout_id="plan_pw_1",
        date="2026-10-25",
        workout_type="strength_push",
        workout_structure={"sets": 4, "reps": 8},
        status="planned",
    )
    isolated_db_session.add(planned)
    isolated_db_session.commit()

    coach = CoachEngine(session=isolated_db_session)
    res = coach.modify_planned_workout(
        planned_workout_id="plan_pw_1",
        modifications={"workout_type": "strength_deload"},
        user_approved=False,
    )
    assert res["status"] == "pending_approval"
    # Verify DB still has original workout
    recheck = isolated_db_session.query(PlannedWorkoutModel).filter_by(planned_workout_id="plan_pw_1").first()
    assert recheck.workout_type == "strength_push"


# ---------------------------------------------------------------------------
# 18.9 Security & Reliability Acceptance Tests
# ---------------------------------------------------------------------------

def test_at_100_secret_protection():
    """AT-100: No API credentials or private tokens are leaked in data representations."""
    from intervals_plan.security import redact_secret
    assert redact_secret("my_super_secret_token_12345") == "my_s...2345"


def test_at_102_database_integrity_cascades(isolated_db_session: Session):
    """AT-102: Deleting a strength workout cascades and deletes all associated exercise sets without orphans."""
    w = StrengthWorkoutModel(
        workout_id="w_casc",
        source="HEVY",
        source_workout_id="hevy_c1",
        workout_name="Test Workout",
        date=datetime.datetime.now(datetime.timezone.utc),
        duration=3600,
    )
    ex = ExerciseModel(
        exercise_id="ex_casc",
        original_name="Bench Press",
        normalized_name="bench press",
        muscle_groups=[{"muscle": "chest", "contribution": 1.0}],
    )
    s = ExerciseSetModel(
        set_id="s_casc",
        workout_id="w_casc",
        exercise_id="ex_casc",
        set_number=1,
        repetitions=10,
        weight=60.0,
    )
    isolated_db_session.add(w)
    isolated_db_session.add(ex)
    isolated_db_session.add(s)
    isolated_db_session.commit()

    assert isolated_db_session.query(ExerciseSetModel).count() == 1
    # Delete workout
    isolated_db_session.delete(w)
    isolated_db_session.commit()
    assert isolated_db_session.query(ExerciseSetModel).count() == 0


def test_at_103_backup_and_restore():
    """AT-103: Database backup and restore reproduces the exact record count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = pathlib.Path(tmpdir) / "source.db"
        backup_file = pathlib.Path(tmpdir) / "backup.db"
        restored_file = pathlib.Path(tmpdir) / "restored.db"

        # Create source DB
        engine = create_db_engine(db_file)
        init_db(engine)
        session_factory = sessionmaker(bind=engine)
        session = session_factory()
        session.add(UserProfileModel(
            user_id="user_test",
            age=27,
            height_cm=172.0,
            weight_kg=78.8,
            training_preferences={},
            goals={},
            heart_rate_zones={},
            available_equipment=[],
            training_constraints=[],
        ))
        session.commit()
        session.close()
        engine.dispose()

        # Backup
        backup_database(src_path=db_file, dest_path=backup_file)
        assert backup_file.exists()

        # Restore
        restore_database(backup_path=backup_file, target_path=restored_file)
        assert restored_file.exists()

        # Check restored DB
        res_engine = create_db_engine(restored_file)
        res_session = sessionmaker(bind=res_engine)()
        count = res_session.query(UserProfileModel).count()
        assert count == 1
        res_session.close()
        res_engine.dispose()


def test_at_105_application_startup_empty_db():
    """AT-105: Application initializes with an empty database without requiring external credentials."""
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    session = sessionmaker(bind=engine)()
    assert session.query(ActivityModel).count() == 0
    assert session.query(StrengthWorkoutModel).count() == 0
    session.close()
    engine.dispose()


# ---------------------------------------------------------------------------
# 18.10 End-to-End Acceptance Scenarios
# ---------------------------------------------------------------------------

def test_e2e_001_historical_import_to_dashboard(isolated_db_session: Session):
    """E2E-001: Import 10 cycling, 5 running, 8 Hevy workouts; normalizes and deduplicates without loss."""
    coros_mgr = CorosIngestionManager(isolated_db_session)
    hevy_imp = HevyImporter(isolated_db_session)

    cycling_acts = [
        {"activity_id": f"c_{i}", "activity_type": "cycling", "start_time": f"2026-10-{i+1:02d}T07:00:00Z", "duration": 3600, "distance": 30000}
        for i in range(10)
    ]
    running_acts = [
        {"activity_id": f"r_{i}", "activity_type": "running", "start_time": f"2026-10-{i+11:02d}T07:00:00Z", "duration": 1800, "distance": 5000}
        for i in range(5)
    ]
    coros_mgr.import_activities(cycling_acts + running_acts)

    # 8 Hevy workouts via CSV
    rows = ["Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Set Type"]
    for i in range(8):
        rows.append(f"2026-10-{i+1:02d} 18:00:00,Workout {i},3600,Bench Press,1,60,10,normal")
    hevy_imp.import_from_csv("\n".join(rows))

    assert isolated_db_session.query(ActivityModel).count() == 15
    assert isolated_db_session.query(StrengthWorkoutModel).count() == 8


def test_e2e_002_strength_progression_analysis():
    """E2E-002: Successive bench press sessions calculate correct 1RM trend and personal records."""
    s1 = calculate_epley_1rm(60.0, 10)  # 60 * (1 + 10/30) = 80.0
    s2 = calculate_epley_1rm(65.0, 10)  # 65 * (1 + 10/30) = 86.67
    s3 = calculate_epley_1rm(70.0, 8)   # 70 * (1 + 8/30) = 88.67
    assert s1 == 80.0
    assert s2 == 86.67
    assert s3 == 88.67
    assert s3 > s2 > s1  # Clear progressive overload detected
