"""
Deterministic Fitness Analytics Engine for Personal AI Training Analyst.
Implements Sections 6 & 18.4 (AT-030 to AT-043) with pure mathematical rigor.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from intervals_plan.validation import (
    calculate_epley_1rm,
    get_exercise_muscle_mapping,
    normalize_distance_meters,
    normalize_duration_seconds,
    normalize_exercise_name,
)


# ---------------------------------------------------------------------------
# AT-030: Weekly Distance (Activity Type Isolation)
# ---------------------------------------------------------------------------

def calculate_weekly_distance_km(
    activities: Sequence[Dict[str, Any]],
    target_activity_type: str,
    target_week_start: Optional[datetime.date] = None,
) -> float:
    """
    Calculate weekly distance in kilometers for a specific activity type (AT-030, AT-040).
    - Only activities matching target_activity_type contribute (e.g. running never contributes to cycling).
    - Only activities within the calendar week of target_week_start contribute (if provided).
    - Deduplicates by (source, source_activity_id) so duplicate activities are counted exactly once.
    """
    clean_target = target_activity_type.lower().strip()
    total_meters = 0.0
    seen_keys: Set[str] = set()

    for act in activities:
        # Deduplication check (AT-040)
        source = act.get("source", "UNKNOWN")
        source_id = str(act.get("source_activity_id") or act.get("activity_id") or "")
        unique_key = f"{source}:{source_id}" if source_id else id(act)
        if unique_key in seen_keys:
            continue
        seen_keys.add(unique_key)

        act_type = str(act.get("activity_type") or act.get("type") or "").lower().strip()
        if act_type != clean_target:
            continue

        # Date filtering if week_start is specified
        if target_week_start is not None:
            dt_raw = act.get("start_time") or act.get("date")
            if isinstance(dt_raw, str):
                act_date = datetime.datetime.fromisoformat(dt_raw.replace("Z", "+00:00")).date()
            elif isinstance(dt_raw, datetime.datetime):
                act_date = dt_raw.date()
            elif isinstance(dt_raw, datetime.date):
                act_date = dt_raw
            else:
                continue

            # Target week range: [target_week_start, target_week_start + 7 days)
            if not (target_week_start <= act_date < target_week_start + datetime.timedelta(days=7)):
                continue

        dist = act.get("distance")
        if dist is not None:
            dist_unit = act.get("distance_unit", "m")
            dist_m = normalize_distance_meters(dist, unit=dist_unit)
            if dist_m is not None:
                total_meters += dist_m

    return round(total_meters / 1000.0, 2)


# ---------------------------------------------------------------------------
# AT-031: Weekly Training Duration
# ---------------------------------------------------------------------------

def calculate_weekly_duration_minutes(
    activities: Sequence[Dict[str, Any]],
    target_week_start: Optional[datetime.date] = None,
) -> float:
    """
    Calculate total training duration in minutes (AT-031, AT-040).
    - Duration must not be inferred from distance when actual duration is unavailable.
    - Counts unique activities once.
    """
    total_seconds = 0.0
    seen_keys: Set[str] = set()

    for act in activities:
        source = act.get("source", "UNKNOWN")
        source_id = str(act.get("source_activity_id") or act.get("activity_id") or "")
        unique_key = f"{source}:{source_id}" if source_id else id(act)
        if unique_key in seen_keys:
            continue
        seen_keys.add(unique_key)

        if target_week_start is not None:
            dt_raw = act.get("start_time") or act.get("date")
            if isinstance(dt_raw, str):
                act_date = datetime.datetime.fromisoformat(dt_raw.replace("Z", "+00:00")).date()
            elif isinstance(dt_raw, datetime.datetime):
                act_date = dt_raw.date()
            elif isinstance(dt_raw, datetime.date):
                act_date = dt_raw
            else:
                continue
            if not (target_week_start <= act_date < target_week_start + datetime.timedelta(days=7)):
                continue

        dur = act.get("duration") or act.get("duration_seconds")
        if dur is not None:
            dur_unit = act.get("duration_unit", "s")
            dur_sec = normalize_duration_seconds(dur, unit=dur_unit)
            if dur_sec is not None:
                total_seconds += dur_sec

    return round(total_seconds / 60.0, 2)


# ---------------------------------------------------------------------------
# AT-032: Average Speed
# ---------------------------------------------------------------------------

def calculate_average_speed_kmh(distance_km: Optional[float], duration_hours: Optional[float]) -> Optional[float]:
    """
    Calculate average speed in km/h (AT-032).
    - If duration is missing, zero, or negative, returns None (unavailable), not infinity or an arbitrary value.
    - If distance is missing, returns None.
    """
    if distance_km is None or duration_hours is None:
        return None
    try:
        dist = float(distance_km)
        dur = float(duration_hours)
    except (ValueError, TypeError):
        return None

    if dur <= 0 or dist < 0:
        return None

    return round(dist / dur, 2)


# ---------------------------------------------------------------------------
# AT-033: Running Pace
# ---------------------------------------------------------------------------

def calculate_running_pace(distance_km: Optional[float], duration_minutes: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculate running pace in sec/km and formatted 'M:SS /km' string (AT-033).
    - If distance is missing, zero, or duration is missing, returns (None, None).
    """
    if distance_km is None or duration_minutes is None:
        return None, None
    try:
        dist = float(distance_km)
        dur_min = float(duration_minutes)
    except (ValueError, TypeError):
        return None, None

    if dist <= 0 or dur_min <= 0:
        return None, None

    pace_sec_km = (dur_min * 60.0) / dist
    minutes = int(pace_sec_km // 60)
    seconds = int(round(pace_sec_km % 60))
    if seconds == 60:
        minutes += 1
        seconds = 0
    formatted = f"{minutes}:{seconds:02d} /km"
    return round(pace_sec_km, 2), formatted


# ---------------------------------------------------------------------------
# AT-034: Heart-Rate Zone Distribution
# ---------------------------------------------------------------------------

def calculate_heart_rate_zone_distribution(
    hr_samples: Sequence[int],
    zone_thresholds: Dict[str, Tuple[int, int]],
) -> Dict[str, Any]:
    """
    Calculate time spent in heart-rate zones based on second-by-second HR samples (AT-034).
    Boundary behavior rule: Zone range is [lower_bound, upper_bound].
    When a sample sits exactly on a boundary, it belongs to the lower zone if upper_bound is inclusive,
    specifically: low <= hr <= high.
    Returns exact duration per zone and total duration.
    """
    distribution: Dict[str, int] = {zone: 0 for zone in zone_thresholds}
    total_seconds = len(hr_samples)

    for hr in hr_samples:
        matched = False
        for zone, (low, high) in zone_thresholds.items():
            if low <= hr <= high:
                distribution[zone] += 1
                matched = True
                break
        if not matched and hr_samples:
            # Handle boundary above highest or below lowest
            first_zone = next(iter(zone_thresholds))
            last_zone = list(zone_thresholds.keys())[-1]
            if hr < zone_thresholds[first_zone][0]:
                distribution[first_zone] += 1
            else:
                distribution[last_zone] += 1

    return {
        "zones": distribution,
        "total_seconds": total_seconds,
        "total_minutes": round(total_seconds / 60.0, 2),
    }


# ---------------------------------------------------------------------------
# AT-035: VO2 Max History (Preserve All Snapshots)
# ---------------------------------------------------------------------------

def build_vo2_max_trend(snapshots: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Preserve all VO2 max measurements chronologically without overwriting (AT-035).
    """
    trend: List[Dict[str, Any]] = []
    for s in snapshots:
        vo2 = s.get("vo2_max")
        ts = s.get("timestamp") or s.get("date")
        if vo2 is not None and ts:
            trend.append({
                "timestamp": str(ts),
                "vo2_max": float(vo2),
                "source": s.get("source", "COROS"),
            })
    # Sort chronologically
    trend.sort(key=lambda x: str(x["timestamp"]))
    return trend


# ---------------------------------------------------------------------------
# AT-038 & AT-039: Muscle-Group Volume & Unmapped Exercise Detection
# ---------------------------------------------------------------------------

def calculate_muscle_group_volume(
    workout_sets: Sequence[Dict[str, Any]],
    custom_mapping: Optional[Dict[str, List[Tuple[str, float]]]] = None,
) -> Dict[str, Any]:
    """
    Calculate effective weekly volume per muscle group with fractional secondary contributions (AT-038).
    Flags any unmapped exercise rather than assigning arbitrary muscle groups (AT-039).
    """
    muscle_volume: Dict[str, float] = {}
    unmapped_exercises: List[str] = []

    for s in workout_sets:
        # Only working sets count towards effective volume
        set_type = str(s.get("set_type", "normal")).lower()
        if set_type in ("warmup", "warm_up"):
            continue

        ex_name = str(s.get("exercise_name") or s.get("exercise") or "").strip()
        if not ex_name:
            continue

        # Look up mapping
        mapping: Optional[List[Tuple[str, float]]] = None
        if custom_mapping and ex_name.lower() in custom_mapping:
            mapping = custom_mapping[ex_name.lower()]
        else:
            mapping = get_exercise_muscle_mapping(ex_name)

        if not mapping:
            if ex_name not in unmapped_exercises:
                unmapped_exercises.append(ex_name)
            continue

        for muscle, contribution in mapping:
            muscle_volume[muscle] = round(muscle_volume.get(muscle, 0.0) + contribution, 2)

    return {
        "muscle_volume": muscle_volume,
        "unmapped_exercises": unmapped_exercises,
    }


# ---------------------------------------------------------------------------
# AT-041: Deterministic Training Load (ATL, CTL, ACWR)
# ---------------------------------------------------------------------------

def calculate_training_load_metrics(
    daily_loads: Sequence[float],
    acute_days: int = 7,
    chronic_days: int = 42,
) -> Dict[str, float]:
    """
    Calculate Acute Training Load (ATL), Chronic Training Load (CTL), and ACWR (AT-041).
    Method: Rolling daily load averages over standard windows.
    - Acute window: trailing acute_days (default 7 days).
    - Chronic window: trailing chronic_days (default 42 days).
    - Missing days must be explicitly padded with 0.0 load.
    - ACWR = ATL / CTL (returns 1.0 if CTL is 0.0).
    """
    if not daily_loads:
        return {"atl": 0.0, "ctl": 0.0, "acwr": 1.0, "tsb": 0.0}

    loads = list(daily_loads)
    # Pad with zeros if fewer days provided than chronic_days
    if len(loads) < chronic_days:
        loads = [0.0] * (chronic_days - len(loads)) + loads

    # Acute load: trailing acute_days average
    acute_slice = loads[-acute_days:]
    atl = sum(acute_slice) / float(acute_days)

    # Chronic load: trailing chronic_days average
    chronic_slice = loads[-chronic_days:]
    ctl = sum(chronic_slice) / float(chronic_days)

    acwr = round(atl / ctl, 2) if ctl > 0 else 1.0
    tsb = round(ctl - atl, 2)

    return {
        "atl": round(atl, 2),
        "ctl": round(ctl, 2),
        "acwr": acwr,
        "tsb": tsb,
    }


# ---------------------------------------------------------------------------
# AT-042: Recovery Baseline Deviation (HRV)
# ---------------------------------------------------------------------------

def calculate_hrv_baseline_deviation(
    daily_hrv_measurements: Sequence[Optional[float]],
    baseline_hrv: float,
) -> Dict[str, Any]:
    """
    Calculate HRV deviations from configured baseline (AT-042).
    - Missing days (None) are filtered out and NOT treated as 0 ms.
    """
    valid_hrvs = [float(val) for val in daily_hrv_measurements if val is not None]
    if not valid_hrvs:
        return {
            "status": "UNAVAILABLE",
            "deviation_pct": 0.0,
            "mean_hrv": None,
            "message": "No recent HRV measurements available.",
        }

    mean_hrv = sum(valid_hrvs) / len(valid_hrvs)
    diff = mean_hrv - baseline_hrv
    dev_pct = round((diff / baseline_hrv) * 100.0, 1)

    return {
        "status": "NORMAL" if abs(dev_pct) <= 10.0 else ("ELEVATED" if dev_pct > 10.0 else "SUPPRESSED"),
        "mean_hrv": round(mean_hrv, 1),
        "baseline_hrv": baseline_hrv,
        "deviation_pct": dev_pct,
        "valid_days_count": len(valid_hrvs),
    }


# ---------------------------------------------------------------------------
# AT-043: Comparable Performance Assessment
# ---------------------------------------------------------------------------

def compare_cycling_performances(
    ride_a: Dict[str, Any],
    ride_b: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare two cycling activities without claiming false fitness improvement solely
    from higher speed when environmental conditions or heart rates differ (AT-043).
    """
    dist_a = ride_a.get("distance_km", 0.0)
    dist_b = ride_b.get("distance_km", 0.0)
    speed_a = ride_a.get("avg_speed_kmh", 0.0)
    speed_b = ride_b.get("avg_speed_kmh", 0.0)
    hr_a = ride_a.get("avg_hr")
    hr_b = ride_b.get("avg_hr")

    # If distances differ by > 15%, or heart rates differ significantly, state limitations
    dist_diff_pct = abs(dist_b - dist_a) / max(dist_a, 1.0) * 100.0

    if dist_diff_pct > 15.0 or (hr_a and hr_b and abs(hr_b - hr_a) > 10):
        return {
            "is_definitive_improvement": False,
            "limitation": "Workouts differ in distance or cardiovascular strain; higher speed cannot be attributed solely to improved fitness.",
            "speed_diff_kmh": round(speed_b - speed_a, 2),
        }

    improved = speed_b > speed_a
    return {
        "is_definitive_improvement": improved,
        "speed_diff_kmh": round(speed_b - speed_a, 2),
        "limitation": None,
    }
