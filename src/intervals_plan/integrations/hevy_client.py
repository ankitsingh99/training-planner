"""
Hevy Strength Training Ingestion Connector.
Supports Hevy Official REST API and Hevy CSV/JSON Export File Importers.
Adheres strictly to PROJECT_SPEC.md Sections 4.2, 11, 18 (AT-020 to AT-025).
"""

from __future__ import annotations

import csv
import datetime
import io
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import urllib.error
import urllib.parse
import urllib.request
import uuid

from sqlalchemy.orm import Session

from intervals_plan.database import get_db_session
from intervals_plan.db_models import (
    ExerciseModel,
    ExerciseSetModel,
    ImportAuditModel,
    StrengthWorkoutModel,
)
from intervals_plan.validation import (
    calculate_epley_1rm,
    get_exercise_muscle_mapping,
    normalize_duration_seconds,
    normalize_exercise_name,
    parse_iso_timestamp,
)

logger = logging.getLogger(__name__)


class HevyClient:
    """Official Hevy REST API Client (api.hevyapp.com/v1)."""

    DEFAULT_BASE_URL = "https://api.hevyapp.com/v1"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("HEVY_API_KEY", "")
        self.base_url = (base_url or os.environ.get("HEVY_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_configured:
            raise ValueError("HEVY_API_KEY is not configured in environment or credentials.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            url = f"{url}?{query}"

        req = urllib.request.Request(
            url,
            headers={
                "api-key": self.api_key,
                "Accept": "application/json",
                "User-Agent": "AdaptPulse-TrainingAnalyst/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            logger.error("Hevy API HTTP %d on %s: %s", exc.code, url, body)
            raise RuntimeError(f"Hevy API error HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            logger.error("Hevy API connection failure to %s: %s", url, exc.reason)
            raise RuntimeError(f"Hevy API unreachable: {exc.reason}") from exc

    def get_workouts(self, page: int = 1, page_size: int = 10, since: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """Retrieve paginated workouts from Hevy API."""
        params: Dict[str, Any] = {"page": page, "pageSize": page_size}
        if since:
            params["since"] = since.isoformat()
        return self._request("workouts", params)

    def get_routines(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Retrieve planned routines from Hevy API (AT-024)."""
        params = {"page": page, "pageSize": page_size}
        return self._request("routines", params)


class HevyImporter:
    """Imports Hevy workout data from API payloads or CSV/JSON export files into the unified SQLite database."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def import_from_csv(self, csv_content: str | io.StringIO) -> ImportAuditModel:
        """
        Import strength workouts from a standard Hevy CSV export string or file buffer.
        Reconstructs workouts, exercises, and sets safely (AT-020, AT-021, AT-023).
        Deduplicates previously imported workouts (AT-011).
        Quarantines corrupt rows and reports valid and rejected counts (AT-017, AT-018).
        """
        if isinstance(csv_content, str):
            f = io.StringIO(csv_content)
        else:
            f = csv_content

        reader = csv.DictReader(f)
        if not reader.fieldnames:
            audit = ImportAuditModel(
                audit_id=str(uuid.uuid4()),
                source="HEVY_CSV",
                records_discovered=0,
                records_inserted=0,
                records_updated=0,
                duplicates_skipped=0,
                records_rejected=1,
                errors=["Empty or invalid CSV file with missing headers."],
            )
            self.session.add(audit)
            self.session.commit()
            return audit

        # Group rows by workout key: (start_time, workout_title)
        discovered_rows = 0
        rejected_rows = 0
        errors: List[str] = []
        workouts_map: Dict[str, Dict[str, Any]] = {}

        for row_idx, row in enumerate(reader, start=2):
            discovered_rows += 1
            # Standard Hevy CSV headers or variations
            date_raw = row.get("Date") or row.get("start_time") or row.get("Start Time")
            title = (row.get("Workout Name") or row.get("title") or row.get("Workout Title") or "Strength Workout").strip()
            exercise_raw = (row.get("Exercise Name") or row.get("exercise_title") or row.get("Exercise") or "").strip()

            if not date_raw or not exercise_raw:
                rejected_rows += 1
                errors.append(f"Row {row_idx}: Missing required date or exercise name.")
                continue

            try:
                parsed_dt = parse_iso_timestamp(date_raw)
            except Exception as e:
                rejected_rows += 1
                errors.append(f"Row {row_idx}: Invalid date format '{date_raw}': {e}")
                continue

            # Workout key based on date and title
            w_key = f"{parsed_dt.isoformat()}_{title}"
            if w_key not in workouts_map:
                dur_raw = row.get("Duration") or row.get("duration_seconds") or 3600
                duration_sec = normalize_duration_seconds(dur_raw, unit="s") or 3600.0
                workouts_map[w_key] = {
                    "source_id": row.get("Workout ID") or w_key,
                    "title": title,
                    "date": parsed_dt,
                    "duration": duration_sec,
                    "sets": [],
                }

            # Parse set parameters
            set_num_raw = row.get("Set Order") or row.get("Set Number") or row.get("set_index") or len(workouts_map[w_key]["sets"]) + 1
            try:
                set_num = int(set_num_raw)
            except (ValueError, TypeError):
                set_num = len(workouts_map[w_key]["sets"]) + 1

            weight_raw = row.get("Weight") or row.get("weight_kg")
            weight_val: Optional[float] = None
            if weight_raw is not None and str(weight_raw).strip() != "":
                try:
                    weight_val = float(weight_raw)
                except (ValueError, TypeError):
                    errors.append(f"Row {row_idx}: Malformed weight '{weight_raw}'. Preserved as null.")

            reps_raw = row.get("Reps") or row.get("repetitions")
            reps_val: Optional[int] = None
            if reps_raw is not None and str(reps_raw).strip() != "":
                try:
                    reps_val = int(reps_raw)
                except (ValueError, TypeError):
                    errors.append(f"Row {row_idx}: Malformed reps '{reps_raw}'. Preserved as null.")

            set_type = (row.get("Set Type") or row.get("set_type") or "normal").lower().strip()
            rir_raw = row.get("RIR") or row.get("rir")
            rir_val: Optional[float] = None
            if rir_raw is not None and str(rir_raw).strip() != "":
                try:
                    rir_val = float(rir_raw)
                except (ValueError, TypeError):
                    pass

            workouts_map[w_key]["sets"].append({
                "exercise_name": exercise_raw,
                "set_number": set_num,
                "weight": weight_val,
                "repetitions": reps_val,
                "set_type": set_type,
                "rir": rir_val,
            })

        # Insert or reconcile workouts in database
        inserted_count = 0
        skipped_count = 0
        earliest_dt: Optional[datetime.datetime] = None
        latest_dt: Optional[datetime.datetime] = None

        for w_data in workouts_map.values():
            dt = w_data["date"]
            if earliest_dt is None or dt < earliest_dt:
                earliest_dt = dt
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt

            # Deduplication check (AT-011)
            existing = self.session.query(StrengthWorkoutModel).filter_by(
                source="HEVY",
                source_workout_id=w_data["source_id"],
            ).first()

            if existing:
                skipped_count += 1
                continue

            # Create workout
            workout_id = str(uuid.uuid4())
            new_workout = StrengthWorkoutModel(
                workout_id=workout_id,
                source="HEVY",
                source_workout_id=w_data["source_id"],
                workout_name=w_data["title"],
                date=dt,
                duration=w_data["duration"],
                raw_data_reference=json.dumps(w_data, default=str),
            )
            self.session.add(new_workout)

            # Process exercises and sets
            for s_data in w_data["sets"]:
                raw_name = s_data["exercise_name"]
                norm_name = normalize_exercise_name(raw_name)

                # Find or create exercise
                ex = self.session.query(ExerciseModel).filter_by(normalized_name=norm_name).first()
                if not ex:
                    mapping = get_exercise_muscle_mapping(raw_name) or []
                    ex = ExerciseModel(
                        exercise_id=str(uuid.uuid4()),
                        original_name=raw_name,
                        normalized_name=norm_name,
                        muscle_groups=[{"muscle": m, "contribution": c} for m, c in mapping],
                    )
                    self.session.add(ex)
                    self.session.flush()

                # Calculate Epley 1RM
                epley_1rm = calculate_epley_1rm(s_data["weight"], s_data["repetitions"])

                new_set = ExerciseSetModel(
                    set_id=str(uuid.uuid4()),
                    workout_id=workout_id,
                    exercise_id=ex.exercise_id,
                    set_number=s_data["set_number"],
                    repetitions=s_data["repetitions"],
                    weight=s_data["weight"],
                    set_type=s_data["set_type"],
                    estimated_rir=s_data["rir"],
                    estimated_1rm=epley_1rm,
                )
                self.session.add(new_set)

            inserted_count += 1

        audit = ImportAuditModel(
            audit_id=str(uuid.uuid4()),
            source="HEVY_CSV",
            records_discovered=discovered_rows,
            records_inserted=inserted_count,
            records_updated=0,
            duplicates_skipped=skipped_count,
            records_rejected=rejected_rows,
            errors=errors,
            earliest_record_date=earliest_dt.isoformat() if earliest_dt else None,
            latest_record_date=latest_dt.isoformat() if latest_dt else None,
            report_summary=f"Processed {discovered_rows} rows from Hevy CSV. Inserted {inserted_count} workouts, skipped {skipped_count} duplicates, rejected {rejected_rows} malformed rows.",
        )
        self.session.add(audit)
        self.session.commit()
        return audit

    def import_from_api_payload(self, workouts_json: List[Dict[str, Any]]) -> ImportAuditModel:
        """Import workouts from official Hevy REST API JSON payload."""
        discovered = len(workouts_json)
        inserted = 0
        skipped = 0
        rejected = 0
        errors: List[str] = []
        earliest_dt: Optional[datetime.datetime] = None
        latest_dt: Optional[datetime.datetime] = None

        for idx, w in enumerate(workouts_json):
            source_id = str(w.get("id") or w.get("workout_id") or "")
            if not source_id:
                rejected += 1
                errors.append(f"Payload index {idx}: Missing workout id.")
                continue

            dt_raw = w.get("start_time") or w.get("date")
            try:
                dt = parse_iso_timestamp(dt_raw)
            except Exception as e:
                rejected += 1
                errors.append(f"Workout {source_id}: Invalid timestamp '{dt_raw}': {e}")
                continue

            if earliest_dt is None or dt < earliest_dt:
                earliest_dt = dt
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt

            # Deduplication
            existing = self.session.query(StrengthWorkoutModel).filter_by(
                source="HEVY",
                source_workout_id=source_id,
            ).first()

            if existing:
                skipped += 1
                continue

            workout_id = str(uuid.uuid4())
            new_workout = StrengthWorkoutModel(
                workout_id=workout_id,
                source="HEVY",
                source_workout_id=source_id,
                workout_name=w.get("title") or w.get("name") or "Hevy Strength Workout",
                date=dt,
                duration=float(w.get("duration") or 3600.0),
                raw_data_reference=json.dumps(w, default=str),
            )
            self.session.add(new_workout)

            exercises_data = w.get("exercises") or []
            set_counter = 1
            for ex_item in exercises_data:
                raw_name = ex_item.get("title") or ex_item.get("name") or "Unknown Exercise"
                norm_name = normalize_exercise_name(raw_name)

                ex = self.session.query(ExerciseModel).filter_by(normalized_name=norm_name).first()
                if not ex:
                    mapping = get_exercise_muscle_mapping(raw_name) or []
                    ex = ExerciseModel(
                        exercise_id=str(uuid.uuid4()),
                        original_name=raw_name,
                        normalized_name=norm_name,
                        muscle_groups=[{"muscle": m, "contribution": c} for m, c in mapping],
                    )
                    self.session.add(ex)
                    self.session.flush()

                for s in ex_item.get("sets", []):
                    weight = s.get("weight_kg") if s.get("weight_kg") is not None else s.get("weight")
                    reps = s.get("reps") if s.get("reps") is not None else s.get("repetitions")
                    epley = calculate_epley_1rm(weight, reps)

                    new_set = ExerciseSetModel(
                        set_id=str(uuid.uuid4()),
                        workout_id=workout_id,
                        exercise_id=ex.exercise_id,
                        set_number=set_counter,
                        repetitions=reps,
                        weight=weight,
                        set_type=s.get("set_type", "normal"),
                        estimated_rir=s.get("rir"),
                        estimated_1rm=epley,
                    )
                    self.session.add(new_set)
                    set_counter += 1

            inserted += 1

        audit = ImportAuditModel(
            audit_id=str(uuid.uuid4()),
            source="HEVY_API",
            records_discovered=discovered,
            records_inserted=inserted,
            records_updated=0,
            duplicates_skipped=skipped,
            records_rejected=rejected,
            errors=errors,
            earliest_record_date=earliest_dt.isoformat() if earliest_dt else None,
            latest_record_date=latest_dt.isoformat() if latest_dt else None,
            report_summary=f"Processed {discovered} API workouts. Inserted {inserted}, skipped {skipped} duplicates, rejected {rejected}.",
        )
        self.session.add(audit)
        self.session.commit()
        return audit
