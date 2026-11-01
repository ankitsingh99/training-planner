"""
Tests for DynamicRollingPlanner.
Verifies periodization, adaptive modifications, and COROS display constraints.
"""

import datetime
from intervals_plan.analytics import ACWRMetric, IntensityDistribution, PhysiologicalReadiness, RollingAnalysisReport
from intervals_plan.athlete_profile import AthleteProfileConfig
from intervals_plan.rolling_planner import DynamicRollingPlanner


def _make_dummy_report(is_strained: bool = False, hours: float = 8.0) -> RollingAnalysisReport:
    readiness = PhysiologicalReadiness(
        ctl=20.0,
        atl=35.0 if is_strained else 22.0,
        tsb=-15.0 if is_strained else -2.0,
        resting_hr_baseline=50.0,
        recent_resting_hr=58.0 if is_strained else 50.0,
        rhr_delta=8.0 if is_strained else 0.0,
        rhr_elevated=is_strained,
        readiness_state="ELEVATED_FATIGUE" if is_strained else "OPTIMAL_OVERLOAD",
        readiness_score=35 if is_strained else 85,
        recommendation="Test guidance",
        target_next_week_tss=120.0,
        target_next_week_hours=hours if not is_strained else hours * 0.9,
    )
    acwr = ACWRMetric(
        acute_load_7d=180.0,
        chronic_load_28d=400.0,
        chronic_weekly_avg=100.0,
        ratio=1.8 if is_strained else 1.1,
        status="DANGER_ZONE" if is_strained else "SWEET_SPOT",
        guidance="Test ACWR guidance",
    )
    dist = IntensityDistribution(
        low_intensity_pct=80.0,
        moderate_intensity_pct=5.0,
        high_intensity_pct=15.0,
        total_moving_time_hours=8.0,
        is_polarized=True,
        summary="Test",
    )
    return RollingAnalysisReport(
        period_start="2026-10-04",
        period_end="2026-11-02",
        total_activities=10,
        total_moving_hours=8.0,
        total_load_tss=250.0,
        disciplines={},
        acwr=acwr,
        readiness=readiness,
        intensity_distribution=dist,
        raw_wellness_count=30,
    )


def test_rolling_planner_normal_week():
    profile = AthleteProfileConfig(weekly_hours=8.0)
    planner = DynamicRollingPlanner(profile)
    report = _make_dummy_report(is_strained=False)

    start_date = datetime.date(2026, 11, 2)
    events = planner.generate_plan(report, start_date=start_date, weeks_to_plan=1)

    assert len(events) == 7
    # Tuesday is 5K Pace Intervals
    tue = next(e for e in events if "tue" in (e.external_id or ""))
    assert "5K Pace Intervals" in tue.name
    assert tue.workout_doc is not None
    assert len(tue.workout_doc.steps) > 5

    # Thursday is Seiler 4x8m Intervals
    thu = next(e for e in events if "thu" in (e.external_id or ""))
    assert "Seiler 4x8m Intervals" in thu.name

    # Saturday is Long Endurance Ride
    sat = next(e for e in events if "sat" in (e.external_id or ""))
    assert "Long Endurance Ride" in sat.name
    assert sat.moving_time == 180 * 60  # 3 hours


def test_rolling_planner_strained_week():
    profile = AthleteProfileConfig(weekly_hours=8.0)
    planner = DynamicRollingPlanner(profile)
    report = _make_dummy_report(is_strained=True)

    start_date = datetime.date(2026, 11, 2)
    events = planner.generate_plan(report, start_date=start_date, weeks_to_plan=1)

    # Tuesday run should be adapted/substituted to Aerobic Flush
    tue = next(e for e in events if "tue" in (e.external_id or ""))
    assert "Substituted" in tue.name or "Flush" in tue.name
    assert "AUTONOMIC ADAPTATION" in tue.description

    # Thursday bike should be adapted to Recovery Spin
    thu = next(e for e in events if "thu" in (e.external_id or ""))
    assert "Recovery Spin" in thu.name
    assert "AUTONOMIC ADAPTATION" in thu.description


def test_rolling_planner_coros_compatibility():
    """Verify COROS display constraints: ASCII only, step names <= 20 chars."""
    profile = AthleteProfileConfig(weekly_hours=8.0)
    planner = DynamicRollingPlanner(profile)
    report = _make_dummy_report(is_strained=False)

    events = planner.generate_plan(report, start_date=datetime.date(2026, 11, 2), weeks_to_plan=1)
    for ev in events:
        # Check no emojis in name or description
        assert ev.name.isascii(), f"Non-ASCII name: {ev.name}"
        assert ev.description.isascii(), f"Non-ASCII description: {ev.description}"
        if ev.workout_doc and ev.workout_doc.steps:
            for step in ev.workout_doc.steps:
                assert step.text.isascii(), f"Non-ASCII step cue: {step.text}"
                assert len(step.text) <= 20, f"Step cue exceeds 20 chars: '{step.text}' ({len(step.text)})"


def test_rolling_planner_two_weeks():
    profile = AthleteProfileConfig(weekly_hours=8.0)
    planner = DynamicRollingPlanner(profile)
    report = _make_dummy_report(is_strained=False)

    start_date = datetime.date(2026, 11, 2)
    events = planner.generate_plan(report, start_date=start_date, weeks_to_plan=2)

    assert len(events) == 14
    w1_events = [e for e in events if "w1" in (e.external_id or "")]
    w2_events = [e for e in events if "w2" in (e.external_id or "")]
    assert len(w1_events) == 7
    assert len(w2_events) == 7


def test_rolling_planner_upcoming_monday_and_phases():
    # 1. From Wednesday (2026-11-04)
    wed = datetime.date(2026, 11, 4)
    mon = DynamicRollingPlanner.get_upcoming_monday(wed)
    assert mon == datetime.date(2026, 11, 9)

    # 2. Taper phase
    prof_taper = AthleteProfileConfig(
        target_race_date=(datetime.date(2026, 11, 2) + datetime.timedelta(days=7)).isoformat(),
        weekly_hours=8.0,
    )
    p_taper = DynamicRollingPlanner(prof_taper)
    report = _make_dummy_report(is_strained=False)
    events_taper = p_taper.generate_plan(report, start_date=datetime.date(2026, 11, 2), weeks_to_plan=1)
    assert len(events_taper) == 7

    # 3. Peak phase
    prof_peak = AthleteProfileConfig(
        target_race_date=(datetime.date(2026, 11, 2) + datetime.timedelta(days=21)).isoformat(),
        weekly_hours=8.0,
    )
    p_peak = DynamicRollingPlanner(prof_peak)
    events_peak = p_peak.generate_plan(report, start_date=datetime.date(2026, 11, 2), weeks_to_plan=1)
    assert len(events_peak) == 7


def test_rolling_planner_triathlon_goal():
    """Verify Swim and Brick generation for triathlon profiles."""
    prof_tri = AthleteProfileConfig(goal="olympic_triathlon", weekly_hours=10.0, swim_css_sec_100m=100)
    planner = DynamicRollingPlanner(prof_tri)
    report = _make_dummy_report(is_strained=False)

    events = planner.generate_plan(report, start_date=datetime.date(2026, 11, 2), weeks_to_plan=1)
    assert len(events) == 7

    # Wednesday is Swim CSS Threshold
    wed = next(e for e in events if "wed" in (e.external_id or ""))
    assert wed.type == "Swim"
    assert "CSS Threshold Swim" in wed.name
    assert "Fueling:" in wed.description

    # Friday is Aerobic Swim
    fri = next(e for e in events if "fri" in (e.external_id or ""))
    assert fri.type == "Swim"
    assert "Aerobic Base Swim" in fri.name

    # Saturday is Brick session
    sat = next(e for e in events if "sat" in (e.external_id or ""))
    assert sat.type == "Brick"
    assert "Brick" in sat.name


def test_rolling_planner_running_and_cycling_goals():
    report = _make_dummy_report(is_strained=False)

    # Running focus
    prof_run = AthleteProfileConfig(goal="running", weekly_hours=8.0)
    p_run = DynamicRollingPlanner(prof_run)
    events_run = p_run.generate_plan(report, start_date=datetime.date(2026, 11, 2), weeks_to_plan=1)
    assert len(events_run) == 7
    thu_run = next(e for e in events_run if "thu" in (e.external_id or ""))
    assert "Threshold Tempo Run" in thu_run.name

    # Cycling focus
    prof_bike = AthleteProfileConfig(goal="cycling", weekly_hours=9.0)
    p_bike = DynamicRollingPlanner(prof_bike)
    events_bike = p_bike.generate_plan(report, start_date=datetime.date(2026, 11, 2), weeks_to_plan=1)
    assert len(events_bike) == 7
    thu_bike = next(e for e in events_bike if "thu" in (e.external_id or ""))
    assert "SweetSpot" in thu_bike.name


