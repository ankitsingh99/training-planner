"""
Comprehensive Ingestion Script: Pull All Activity, Fitness, and Wellness Data.
Imports from Intervals.icu / COROS relay into the Unified SQLite Database.
Adheres strictly to PROJECT_SPEC.md (Sections 4, 5, 12, 18).
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import pathlib
import uuid
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from intervals_plan.config import Config
from intervals_plan.database import get_db_session, init_db
from intervals_plan.db_models import (
    ActivityModel,
    FitnessSnapshotModel,
    ImportAuditModel,
    UserProfileModel,
)
from intervals_plan.intervals_client import IntervalsClient
from intervals_plan.validation import parse_iso_timestamp

logger = logging.getLogger(__name__)


def pull_and_sync_all_data(start_date: str = "2025-01-01", end_date: Optional[str] = None) -> Dict[str, Any]:
    """Pull all available activity, fitness, and wellness data into the unified SQLite database."""
    init_db()
    cfg = Config.load()
    if not cfg.api_key:
        raise ValueError("INTERVALS_API_KEY is not configured in .env.")

    client = IntervalsClient(
        api_key=cfg.api_key,
        athlete_id=cfg.athlete_id,
        base_url=cfg.base_url,
    )

    end_d = end_date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    report: Dict[str, Any] = {
        "athlete_id": None,
        "athlete_name": None,
        "activities_discovered": 0,
        "activities_imported": 0,
        "activities_skipped_duplicates": 0,
        "activities_skipped_strava": 0,
        "wellness_records_discovered": 0,
        "wellness_records_imported": 0,
        "latest_weight_kg": None,
        "latest_rhr_bpm": None,
        "latest_hrv_ms": None,
        "date_range": f"{start_date} to {end_d}",
    }

    # 1. Athlete Information
    athlete = client.get_athlete()
    report["athlete_id"] = athlete.id
    report["athlete_name"] = athlete.name

    with get_db_session() as session:
        user = session.query(UserProfileModel).filter_by(user_id="default_athlete").first()
        if not user:
            user = UserProfileModel(
                user_id="default_athlete",
                age=27,
                height_cm=172.0,
                weight_kg=78.8,
                body_fat_pct=27.0,
                fat_mass_kg=21.3,
                muscle_mass_kg=31.3,
                resting_heart_rate=53,
                hrv_baseline=86.0,
                vo2_max=42.0,
            )
            session.add(user)

    # 2. Fetch & Ingest Wellness Records
    logger.info("Fetching wellness range from %s to %s", start_date, end_d)
    raw_wellness = client.get_wellness_range(start_date, end_d)
    report["wellness_records_discovered"] = len(raw_wellness)

    with get_db_session() as session:
        for w in raw_wellness:
            date_id = w.get("id")
            if not date_id:
                continue

            try:
                dt = parse_iso_timestamp(date_id + "T00:00:00Z")
            except Exception:
                continue

            weight = float(w["weight"]) if w.get("weight") is not None else None
            rhr = int(w["restingHR"]) if w.get("restingHR") is not None else None
            hrv = float(w["hrv"]) if w.get("hrv") is not None else None
            spo2 = float(w["spO2"]) if w.get("spO2") is not None else None
            sleep_sec = float(w["sleepSec"]) if w.get("sleepSec") is not None else None

            if weight:
                report["latest_weight_kg"] = weight
            if rhr:
                report["latest_rhr_bpm"] = rhr
            if hrv:
                report["latest_hrv_ms"] = hrv

            # Deduplication
            existing = session.query(FitnessSnapshotModel).filter_by(
                source="WELLNESS_SYNC",
                timestamp=dt,
            ).first()

            if existing:
                if weight:
                    existing.raw_data_reference = json.dumps(w)
                if rhr:
                    existing.resting_heart_rate = rhr
                if hrv:
                    existing.hrv = hrv
            else:
                snap = FitnessSnapshotModel(
                    snapshot_id=str(uuid.uuid4()),
                    timestamp=dt,
                    source="WELLNESS_SYNC",
                    resting_heart_rate=rhr,
                    hrv=hrv,
                    training_load=float(w.get("ctl", 0)) if w.get("ctl") else None,
                    raw_data_reference=json.dumps(w),
                )
                session.add(snap)
                report["wellness_records_imported"] += 1

        # Update UserProfile with latest weight if available
        if report["latest_weight_kg"]:
            user = session.query(UserProfileModel).filter_by(user_id="default_athlete").first()
            if user:
                user.weight_kg = report["latest_weight_kg"]
                if report["latest_rhr_bpm"]:
                    user.resting_heart_rate = report["latest_rhr_bpm"]
                if report["latest_hrv_ms"]:
                    user.hrv_baseline = report["latest_hrv_ms"]

    # 3. Fetch & Ingest Completed Activities
    logger.info("Fetching activities from %s to %s", start_date, end_d)
    raw_activities = client.get_activities(start_date, end_d)
    report["activities_discovered"] = len(raw_activities)

    with get_db_session() as session:
        for a in raw_activities:
            source = str(a.get("source") or "INTERVALS").upper()
            act_id = str(a.get("id") or "")

            # Exclude Strava (Section 3)
            if "STRAVA" in source:
                report["activities_skipped_strava"] += 1
                continue

            # Deduplication
            existing = session.query(ActivityModel).filter_by(
                source=source,
                source_activity_id=act_id,
            ).first()

            if existing:
                report["activities_skipped_duplicates"] += 1
                continue

            raw_type = str(a.get("type") or "workout").lower()
            if "ride" in raw_type or "bike" in raw_type or "cycling" in raw_type:
                act_type = "cycling"
            elif "run" in raw_type:
                act_type = "running"
            elif "swim" in raw_type:
                act_type = "swimming"
            else:
                act_type = raw_type

            start_raw = a.get("start_date_local") or a.get("start_date")
            try:
                dt = parse_iso_timestamp(start_raw)
            except Exception:
                continue

            dur_sec = float(a.get("moving_time") or a.get("elapsed_time") or 0.0)
            dist_m = float(a.get("distance") or 0.0) if a.get("distance") is not None else None
            avg_hr = float(a.get("average_heartrate")) if a.get("average_heartrate") is not None else None
            max_hr = float(a.get("max_heartrate")) if a.get("max_heartrate") is not None else None
            t_load = float(a.get("icu_training_load")) if a.get("icu_training_load") is not None else None
            cadence = float(a.get("average_cadence")) if a.get("average_cadence") is not None else None
            power = float(a.get("icu_average_watts")) if a.get("icu_average_watts") is not None else None
            elevation = float(a.get("total_elevation_gain")) if a.get("total_elevation_gain") is not None else None

            avg_speed = round(dist_m / dur_sec, 2) if dist_m and dur_sec > 0 else None
            avg_pace = round(dur_sec / (dist_m / 1000.0), 2) if dist_m and dur_sec > 0 else None

            new_activity = ActivityModel(
                activity_id=str(uuid.uuid4()),
                source=source,
                source_activity_id=act_id,
                activity_type=act_type,
                start_time=dt,
                duration=dur_sec,
                distance=dist_m,
                elevation=elevation,
                average_heart_rate=avg_hr,
                maximum_heart_rate=max_hr,
                average_speed=avg_speed,
                average_pace=avg_pace,
                training_load=t_load,
                cadence_avg=cadence,
                power_avg=power,
                raw_data_reference=json.dumps(a, default=str),
            )
            session.add(new_activity)
            report["activities_imported"] += 1

        # Record audit log
        audit = ImportAuditModel(
            audit_id=str(uuid.uuid4()),
            source="INTERVALS_COROS_SYNC",
            records_discovered=report["activities_discovered"] + report["wellness_records_discovered"],
            records_inserted=report["activities_imported"] + report["wellness_records_imported"],
            records_updated=0,
            duplicates_skipped=report["activities_skipped_duplicates"],
            records_rejected=report["activities_skipped_strava"],
            errors=[],
            earliest_record_date=start_date,
            latest_record_date=end_d,
            report_summary=f"Imported {report['activities_imported']} activities and {report['wellness_records_imported']} wellness records. Skipped {report['activities_skipped_strava']} Strava records per Section 3.",
        )
        session.add(audit)

    return report


if __name__ == "__main__":
    res = pull_and_sync_all_data()
    print(json.dumps(res, indent=2))
