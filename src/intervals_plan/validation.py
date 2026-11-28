"""
Validation, Normalization, and Mathematical Purity Utilities for Training Analyst.
Enforces deterministic calculations, unit consistency, timezone preservation, and Epley 1RM.
"""

from __future__ import annotations

import datetime
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# 1. Deterministic Formulas & Purity
# ---------------------------------------------------------------------------

def calculate_epley_1rm(weight_kg: Optional[float], repetitions: Optional[int]) -> Optional[float]:
    """
    Calculate estimated One-Repetition Maximum (1RM) using the canonical Epley formula:
        Estimated 1RM = Weight * (1 + Repetitions / 30)

    Validation rules (AT-036, AT-037):
    - Weight must be strictly positive (> 0) and not None.
    - Repetitions must be an integer between 1 and 30 inclusive (not 0, not > 30).
    - Returns None if input parameters are outside estimation range or missing.
    """
    if weight_kg is None or repetitions is None:
        return None
    try:
        w = float(weight_kg)
        r = int(repetitions)
    except (ValueError, TypeError):
        return None

    if w <= 0 or r <= 0 or r > 30:
        return None

    if r == 1:
        return round(w, 2)

    est = w * (1.0 + r / 30.0)
    return round(est, 2)


# ---------------------------------------------------------------------------
# 2. Unit and Timezone Normalization
# ---------------------------------------------------------------------------

def normalize_distance_meters(distance_value: Optional[float | int | str], unit: str = "m") -> Optional[float]:
    """
    Normalize any distance metric to meters (AT-014).
    Example: 5 km -> 5000.0, 5000 m -> 5000.0.
    """
    if distance_value is None:
        return None
    try:
        val = float(distance_value)
    except (ValueError, TypeError):
        return None

    unit_clean = unit.lower().strip()
    if unit_clean in ("km", "kilometer", "kilometers"):
        return round(val * 1000.0, 2)
    elif unit_clean in ("m", "meter", "meters"):
        return round(val, 2)
    elif unit_clean in ("mi", "mile", "miles"):
        return round(val * 1609.344, 2)
    elif unit_clean in ("ft", "feet"):
        return round(val * 0.3048, 2)
    return round(val, 2)


def normalize_duration_seconds(duration_value: Optional[float | int | str], unit: str = "s") -> Optional[float]:
    """
    Normalize any duration metric to seconds (AT-014).
    Example: 60 minutes -> 3600.0, 3600 seconds -> 3600.0.
    """
    if duration_value is None:
        return None
    try:
        val = float(duration_value)
    except (ValueError, TypeError):
        return None

    unit_clean = unit.lower().strip()
    if unit_clean in ("s", "sec", "second", "seconds"):
        return round(val, 2)
    elif unit_clean in ("m", "min", "minute", "minutes"):
        return round(val * 60.0, 2)
    elif unit_clean in ("h", "hr", "hour", "hours"):
        return round(val * 3600.0, 2)
    return round(val, 2)


def parse_iso_timestamp(ts_input: Any) -> datetime.datetime:
    """
    Parse timestamp preserving original UTC offset / timezone (AT-015).
    Guarantees a timezone-aware datetime instance in UTC or specified timezone.
    """
    if isinstance(ts_input, datetime.datetime):
        if ts_input.tzinfo is None:
            return ts_input.replace(tzinfo=datetime.timezone.utc)
        return ts_input

    if isinstance(ts_input, (int, float)):
        # Epoch timestamp
        return datetime.datetime.fromtimestamp(ts_input, tz=datetime.timezone.utc)

    ts_str = str(ts_input).strip()
    # Normalize trailing Z to +00:00 for fromisoformat compatibility
    if ts_str.endswith("Z"):
        ts_str = ts_str[:-1] + "+00:00"

    try:
        dt = datetime.datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception as exc:
        raise ValueError(f"Invalid timestamp format: '{ts_input}'") from exc


# ---------------------------------------------------------------------------
# 3. Exercise Normalization & Muscle Mapping (AT-021, AT-022, AT-038, AT-039)
# ---------------------------------------------------------------------------

CANONICAL_EXERCISE_SYNONYMS: Dict[str, str] = {
    "bench press": "bench press",
    "barbell bench press": "bench press",
    "bench press (barbell)": "bench press",
    "flat barbell bench press": "bench press",
    "flat bench press": "bench press",

    "incline bench press": "incline bench press",
    "barbell incline bench press": "incline bench press",
    "incline barbell bench press": "incline bench press",
    "incline bench press (barbell)": "incline bench press",

    "dumbbell bench press": "dumbbell bench press",
    "dumbbell press": "dumbbell bench press",
    "flat dumbbell press": "dumbbell bench press",

    "incline dumbbell press": "incline dumbbell press",
    "incline dumbbell bench press": "incline dumbbell press",

    "overhead press": "overhead press",
    "barbell overhead press": "overhead press",
    "military press": "overhead press",
    "standing overhead press": "overhead press",
    "shoulder press (barbell)": "overhead press",

    "lat pulldown": "lat pulldown",
    "lat pulldown (cable)": "lat pulldown",
    "cable lat pulldown": "lat pulldown",

    "pull up": "pull up",
    "pullup": "pull up",
    "pull-up": "pull up",

    "barbell row": "barbell row",
    "bent over row (barbell)": "barbell row",
    "barbell bent over row": "barbell row",

    "chest supported row": "chest supported row",
    "t-bar row": "chest supported row",
    "chest-supported t-bar row": "chest supported row",

    "squat": "squat",
    "barbell squat": "squat",
    "barbell back squat": "squat",
    "back squat": "squat",
    "squat (barbell)": "squat",

    "leg press": "leg press",
    "45 degree leg press": "leg press",

    "romanian deadlift": "romanian deadlift",
    "rdl": "romanian deadlift",
    "romanian deadlift (barbell)": "romanian deadlift",
    "barbell romanian deadlift": "romanian deadlift",

    "deadlift": "deadlift",
    "conventional deadlift": "deadlift",
    "barbell deadlift": "deadlift",

    "leg curl": "leg curl",
    "lying leg curl": "leg curl",
    "seated leg curl": "leg curl",

    "leg extension": "leg extension",

    "tricep pushdown": "tricep pushdown",
    "cable triceps pushdown": "tricep pushdown",
    "triceps pushdown": "tricep pushdown",
    "tricep extension": "tricep pushdown",
    "triceps extension": "tricep pushdown",

    "bicep curl": "bicep curl",
    "barbell curl": "bicep curl",
    "dumbbell curl": "bicep curl",
    "incline dumbbell curl": "bicep curl",

    "lateral raise": "lateral raise",
    "dumbbell lateral raise": "lateral raise",
    "cable lateral raise": "lateral raise",
    "side lateral raise": "lateral raise",

    "calf raise": "calf raise",
    "standing calf raise": "calf raise",
    "seated calf raise": "calf raise",
}

CANONICAL_MUSCLE_MAPPING: Dict[str, List[Tuple[str, float]]] = {
    "bench press": [("chest", 1.0), ("triceps", 0.5), ("shoulders_front", 0.5)],
    "incline bench press": [("chest", 1.0), ("shoulders_front", 0.75), ("triceps", 0.5)],
    "dumbbell bench press": [("chest", 1.0), ("triceps", 0.5), ("shoulders_front", 0.5)],
    "incline dumbbell press": [("chest", 1.0), ("shoulders_front", 0.75), ("triceps", 0.5)],
    "overhead press": [("shoulders_front", 1.0), ("triceps", 0.5), ("shoulders_side", 0.5)],
    "lat pulldown": [("lats", 1.0), ("biceps", 0.5)],
    "pull up": [("lats", 1.0), ("upper_back", 0.5), ("biceps", 0.5)],
    "barbell row": [("upper_back", 1.0), ("lats", 0.75), ("biceps", 0.5)],
    "chest supported row": [("upper_back", 1.0), ("lats", 0.75), ("biceps", 0.5)],
    "squat": [("quads", 1.0), ("glutes", 0.75)],
    "leg press": [("quads", 1.0), ("glutes", 0.5)],
    "romanian deadlift": [("hamstrings", 1.0), ("glutes", 0.75), ("upper_back", 0.5)],
    "deadlift": [("hamstrings", 0.75), ("glutes", 0.75), ("upper_back", 0.75), ("quads", 0.5)],
    "leg curl": [("hamstrings", 1.0)],
    "leg extension": [("quads", 1.0)],
    "tricep pushdown": [("triceps", 1.0)],
    "bicep curl": [("biceps", 1.0)],
    "lateral raise": [("shoulders_side", 1.0)],
    "calf raise": [("calves", 1.0)],
}


def normalize_exercise_name(raw_name: str) -> str:
    """
    Clean and normalize an exercise name to canonical form if configured (AT-021).
    Preserves original name if no canonical alias exists.
    """
    clean = raw_name.lower().strip()
    # Strip common punctuation like commas, parentheses if matched
    clean_no_punct = re.sub(r"[^\w\s\(\)]", " ", clean)
    clean_no_punct = re.sub(r"\s+", " ", clean_no_punct).strip()

    if clean_no_punct in CANONICAL_EXERCISE_SYNONYMS:
        return CANONICAL_EXERCISE_SYNONYMS[clean_no_punct]

    # Try removing parentheses
    no_parens = re.sub(r"\(.*?\)", "", clean_no_punct).strip()
    if no_parens in CANONICAL_EXERCISE_SYNONYMS:
        return CANONICAL_EXERCISE_SYNONYMS[no_parens]

    return clean_no_punct


def get_exercise_muscle_mapping(exercise_name: str) -> Optional[List[Tuple[str, float]]]:
    """
    Retrieve configured primary and secondary muscle group contributions.
    Returns None if the exercise is unmapped (AT-039).
    """
    norm = normalize_exercise_name(exercise_name)
    if norm in CANONICAL_MUSCLE_MAPPING:
        return CANONICAL_MUSCLE_MAPPING[norm]
    return None


# ---------------------------------------------------------------------------
# 4. Pydantic Ingestion Schemas (Validation Gates)
# ---------------------------------------------------------------------------

class ActivityInboundSchema(BaseModel):
    source: str
    source_activity_id: str
    activity_type: str
    start_time: Any
    duration: float
    distance: Optional[float] = None
    elevation: Optional[float] = None
    average_heart_rate: Optional[float] = None
    maximum_heart_rate: Optional[float] = None
    average_speed: Optional[float] = None
    average_pace: Optional[float] = None
    calories: Optional[float] = None
    training_load: Optional[float] = None
    cadence_avg: Optional[float] = None
    cadence_max: Optional[float] = None
    power_avg: Optional[float] = None
    hr_zones_seconds: Optional[Dict[str, float]] = None
    raw_data_reference: Optional[str] = None

    @field_validator("source")
    @classmethod
    def validate_source_not_strava(cls, v: str) -> str:
        clean = v.upper().strip()
        if "STRAVA" in clean:
            raise ValueError("Strava is explicitly excluded from ingestion scope (Section 3).")
        return clean

    @field_validator("duration")
    @classmethod
    def validate_positive_duration(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Duration cannot be negative.")
        return v


class ExerciseSetInboundSchema(BaseModel):
    set_number: int
    repetitions: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[float] = None
    distance: Optional[float] = None
    set_type: str = "normal"
    estimated_rir: Optional[float] = None


class StrengthWorkoutInboundSchema(BaseModel):
    source: str
    source_workout_id: str
    workout_name: str
    date: Any
    duration: float
    raw_data_reference: Optional[str] = None
    sets: List[Dict[str, Any]] = Field(default_factory=list)

    @field_validator("source")
    @classmethod
    def validate_strength_source(cls, v: str) -> str:
        clean = v.upper().strip()
        if "STRAVA" in clean:
            raise ValueError("Strava is explicitly excluded from strength ingestion.")
        return clean


class FitnessSnapshotInboundSchema(BaseModel):
    source: str
    timestamp: Any
    vo2_max: Optional[float] = None
    resting_heart_rate: Optional[int] = None
    hrv: Optional[float] = None
    threshold_pace: Optional[float] = None
    threshold_heart_rate: Optional[int] = None
    training_load: Optional[float] = None
    recovery_status: Optional[str] = None
    raw_data_reference: Optional[str] = None
