"""
COROS Activities and EvoLab Fitness Snapshot Ingestion and Synchronization.
Adheres strictly to PROJECT_SPEC.md Sections 4.1, 11, 18 (AT-010 to AT-018, AT-035).
"""

from __future__ import annotations

import datetime
import json
import logging
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from intervals_plan.db_models import (
    ActivityModel,
    FitnessSnapshotModel,
    ImportAuditModel,
)
from intervals_plan.validation import (
    normalize_distance_meters,
    normalize_duration_seconds,
    parse_iso_timestamp,
)

logger = logging.getLogger(__name__)


class CorosIngestionManager:
    """Manages ingestion of COROS activities and EvoLab fitness snapshots into SQLite."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def import_activities(
        self,
        activities_list: List[Dict[str, Any]],
        source_label: str = "COROS",
    ) -> ImportAuditModel:
        """
        Import a batch of COROS activity records into the normalized database.
        Enforces deduplication (AT-011), unit normalization (AT-014), timezone preservation (AT-015),
        null preservation for missing metrics (AT-013), and corrupt record isolation (AT-017).
        """
        discovered = len(activities_list)
        inserted = 0
        skipped = 0
        rejected = 0
        errors: List[str] = []
        earliest_dt: Optional[datetime.datetime] = None
        latest_dt: Optional[datetime.datetime] = None

        for idx, act in enumerate(activities_list):
            source_id = str(act.get("activity_id") or act.get("id") or act.get("source_id") or "")
            if not source_id:
                rejected += 1
                errors.append(f"Record #{idx}: Missing unique activity_id.")
                continue

            # Activity type normalization
            raw_type = (act.get("activity_type") or act.get("type") or "workout").lower().strip()
            # Normalize common naming
            if "bike" in raw_type or "ride" in raw_type or "cycling" in raw_type:
                act_type = "cycling"
            elif "run" in raw_type:
                act_type = "running"
            elif "swim" in raw_type:
                act_type = "swimming"
            else:
                act_type = raw_type

            # Parse start time
            start_raw = act.get("start_time") or act.get("startTime") or act.get("timestamp")
            if not start_raw:
                rejected += 1
                errors.append(f"Activity {source_id}: Missing start timestamp.")
                continue

            try:
                dt = parse_iso_timestamp(start_raw)
            except Exception as exc:
                rejected += 1
                errors.append(f"Activity {source_id}: Malformed timestamp '{start_raw}': {exc}")
                continue

            if earliest_dt is None or dt < earliest_dt:
                earliest_dt = dt
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt

            # Deduplication check (AT-011)
            existing = self.session.query(ActivityModel).filter_by(
                source=source_label,
                source_activity_id=source_id,
            ).first()

            if existing:
                skipped += 1
                continue

            # Duration normalization (AT-014)
            dur_raw = act.get("duration") or act.get("moving_time") or act.get("duration_seconds")
            dur_unit = act.get("duration_unit", "s")
            dur_sec = normalize_duration_seconds(dur_raw, unit=dur_unit)
            if dur_sec is None or dur_sec < 0:
                rejected += 1
                errors.append(f"Activity {source_id}: Missing or invalid duration '{dur_raw}'.")
                continue

            # Distance normalization (AT-014)
            dist_raw = act.get("distance") or act.get("distance_meters")
            dist_unit = act.get("distance_unit", "m")
            dist_m = normalize_distance_meters(dist_raw, unit=dist_unit) if dist_raw is not None else None

            # Speed and Pace (AT-032, AT-033): Preserve null if duration or distance is 0 / missing
            avg_speed: Optional[float] = None
            avg_pace: Optional[float] = None
            if dist_m is not None and dur_sec > 0:
                avg_speed = round(dist_m / dur_sec, 2)  # m/s
                if dist_m > 0:
                    avg_pace = round(dur_sec / (dist_m / 1000.0), 2)  # sec/km

            # Heart rate, cadence, power, training load: MUST remain None if missing (AT-013)
            avg_hr = float(act["average_heart_rate"]) if act.get("average_heart_rate") is not None else None
            max_hr = float(act["maximum_heart_rate"]) if act.get("maximum_heart_rate") is not None else None
            cadence_avg = float(act["cadence_avg"]) if act.get("cadence_avg") is not None else None
            cadence_max = float(act["cadence_max"]) if act.get("cadence_max") is not None else None
            power_avg = float(act["power_avg"]) if act.get("power_avg") is not None else None
            t_load = float(act["training_load"]) if act.get("training_load") is not None else None
            calories = float(act["calories"]) if act.get("calories") is not None else None
            elevation = float(act["elevation"]) if act.get("elevation") is not None else None

            hr_zones = act.get("hr_zones_seconds")

            new_activity = ActivityModel(
                activity_id=str(uuid.uuid4()),
                source=source_label,
                source_activity_id=source_id,
                activity_type=act_type,
                start_time=dt,
                duration=dur_sec,
                distance=dist_m,
                elevation=elevation,
                average_heart_rate=avg_hr,
                maximum_heart_rate=max_hr,
                average_speed=avg_speed,
                average_pace=avg_pace,
                calories=calories,
                training_load=t_load,
                cadence_avg=cadence_avg,
                cadence_max=cadence_max,
                power_avg=power_avg,
                hr_zones_seconds=hr_zones,
                raw_data_reference=json.dumps(act, default=str),
            )
            self.session.add(new_activity)
            inserted += 1

        audit = ImportAuditModel(
            audit_id=str(uuid.uuid4()),
            source=source_label,
            records_discovered=discovered,
            records_inserted=inserted,
            records_updated=0,
            duplicates_skipped=skipped,
            records_rejected=rejected,
            errors=errors,
            earliest_record_date=earliest_dt.isoformat() if earliest_dt else None,
            latest_record_date=latest_dt.isoformat() if latest_dt else None,
            report_summary=f"Processed {discovered} records from {source_label}. Inserted {inserted}, skipped {skipped} duplicates, rejected {rejected}.",
        )
        self.session.add(audit)
        self.session.commit()
        return audit

    def import_paginated_activities(
        self,
        fetch_page_fn: Callable[[int, int], List[Dict[str, Any]]],
        page_size: int = 50,
        max_pages: int = 100,
        source_label: str = "COROS",
    ) -> ImportAuditModel:
        """
        Paginate through all available pages without skipping (AT-010).
        Recovers gracefully if a page fails, preserving successful records (AT-012).
        """
        all_activities: List[Dict[str, Any]] = []
        page_errors: List[str] = []
        successful_pages = 0

        for page in range(1, max_pages + 1):
            try:
                page_data = fetch_page_fn(page, page_size)
                if not page_data:
                    break
                all_activities.extend(page_data)
                successful_pages += 1
                if len(page_data) < page_size:
                    # Last page reached
                    break
            except Exception as exc:
                err_msg = f"Pagination failed at page {page}: {exc}"
                logger.error(err_msg)
                page_errors.append(err_msg)
                break

        audit = self.import_activities(all_activities, source_label=source_label)
        if page_errors:
            audit.errors = (audit.errors or []) + page_errors
            audit.report_summary += f" [Encountered {len(page_errors)} pagination failure(s) after {successful_pages} successful pages]."
            self.session.commit()

        return audit

    def import_fitness_snapshot(
        self,
        snapshot_data: Dict[str, Any],
        source_label: str = "COROS",
    ) -> FitnessSnapshotModel:
        """
        Import a time-series physiological snapshot (VO2 max, RHR, HRV, threshold pace/HR).
        Preserves all historical measurements without overwriting previous snapshots (AT-035).
        """
        ts_raw = snapshot_data.get("timestamp") or datetime.datetime.now(datetime.timezone.utc)
        dt = parse_iso_timestamp(ts_raw)

        # Check existing snapshot at exact timestamp
        existing = self.session.query(FitnessSnapshotModel).filter_by(
            source=source_label,
            timestamp=dt,
        ).first()

        if existing:
            # Update fields if provided
            if snapshot_data.get("vo2_max") is not None:
                existing.vo2_max = float(snapshot_data["vo2_max"])
            if snapshot_data.get("resting_heart_rate") is not None:
                existing.resting_heart_rate = int(snapshot_data["resting_heart_rate"])
            if snapshot_data.get("hrv") is not None:
                existing.hrv = float(snapshot_data["hrv"])
            if snapshot_data.get("threshold_pace") is not None:
                existing.threshold_pace = float(snapshot_data["threshold_pace"])
            if snapshot_data.get("threshold_heart_rate") is not None:
                existing.threshold_heart_rate = int(snapshot_data["threshold_heart_rate"])
            if snapshot_data.get("training_load") is not None:
                existing.training_load = float(snapshot_data["training_load"])
            if snapshot_data.get("recovery_status") is not None:
                existing.recovery_status = str(snapshot_data["recovery_status"])
            self.session.commit()
            return existing

        new_snap = FitnessSnapshotModel(
            snapshot_id=str(uuid.uuid4()),
            timestamp=dt,
            source=source_label,
            vo2_max=float(snapshot_data["vo2_max"]) if snapshot_data.get("vo2_max") is not None else None,
            resting_heart_rate=int(snapshot_data["resting_heart_rate"]) if snapshot_data.get("resting_heart_rate") is not None else None,
            hrv=float(snapshot_data["hrv"]) if snapshot_data.get("hrv") is not None else None,
            threshold_pace=float(snapshot_data["threshold_pace"]) if snapshot_data.get("threshold_pace") is not None else None,
            threshold_heart_rate=int(snapshot_data["threshold_heart_rate"]) if snapshot_data.get("threshold_heart_rate") is not None else None,
            training_load=float(snapshot_data["training_load"]) if snapshot_data.get("training_load") is not None else None,
            recovery_status=str(snapshot_data["recovery_status"]) if snapshot_data.get("recovery_status") is not None else None,
            raw_data_reference=json.dumps(snapshot_data, default=str),
        )
        self.session.add(new_snap)
        self.session.commit()
        return new_snap
