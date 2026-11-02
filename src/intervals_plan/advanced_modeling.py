"""
Sports-Science Modeling Extensions (Inspired by Skiba, Peng, Gronwald, and Friel):
1. Skiba W'bal (Anaerobic battery depletion & recovery reconstitution).
2. DFA alpha 1 (Detrended Fluctuation Analysis of R-R intervals for aerobic threshold detection).
3. Data Quality & Athlete Telemetry Consistency Auditor (Joe Friel data checks).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
import math
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Skiba W'bal Anaerobic Work Capacity Reconstitution Model
# ---------------------------------------------------------------------------

def _tau_w(w_prime: float, cp: float, power_below_cp: List[float]) -> float:
    """Estimate tau (reconstitution time constant) in seconds (Skiba et al. 2012)."""
    if not power_below_cp:
        return 546.0
    p_mean = sum(power_below_cp) / len(power_below_cp)
    denominator = cp - p_mean
    if denominator <= 0:
        return 546.0
    return w_prime / denominator


def compute_wbal(watts: List[Optional[float]], w_prime: float, cp: float) -> List[float]:
    """
    Calculate dynamic W'bal in Joules second-by-second across a power series.
    Missing/None power samples are treated as 0 W.
    """
    sub_cp = [p for p in watts if p is not None and 0 < p < cp]
    tau = _tau_w(w_prime, cp, sub_cp)
    decay = math.exp(-1.0 / tau)

    wbal = w_prime
    result: List[float] = []
    for raw in watts:
        p = float(raw) if raw is not None else 0.0
        if p >= cp:
            wbal -= (p - cp)
            wbal = max(0.0, wbal)
        else:
            wbal += (w_prime - wbal) * (1.0 - decay)
        result.append(round(wbal, 1))
    return result


def summarize_wbal(wbal: List[float], w_prime: float) -> Dict[str, Any]:
    """Compute summary statistics for a W'bal time series."""
    if not wbal or w_prime <= 0:
        return {
            "w_prime_j": w_prime,
            "wbal_min_j": w_prime,
            "wbal_max_depletion_j": 0.0,
            "wbal_usage_pct": 0.0,
            "seconds_below_30pct": 0,
            "seconds_below_10pct": 0,
            "min_wbal_at_second": 0,
            "wbal_depletion_events": 0,
            "wbal_recovery_ratio": 1.0,
        }

    min_wbal = min(wbal)
    max_depletion = w_prime - min_wbal
    usage_pct = round((max_depletion / w_prime) * 100.0, 1)

    below_30 = sum(1 for v in wbal if v < 0.30 * w_prime)
    below_10 = sum(1 for v in wbal if v < 0.10 * w_prime)
    min_idx = wbal.index(min_wbal)

    # State machine tracking depletion events (<40% W' threshold)
    events: List[Tuple[float, float, Optional[float]]] = []
    state = "normal"
    last_above_40 = w_prime
    cur_pre_drop = 0.0
    cur_min = 0.0
    cur_rec_max = 0.0

    for v in wbal:
        pct = v / w_prime

        if state == "normal":
            if pct >= 0.40:
                last_above_40 = v
            if pct < 0.40:
                cur_pre_drop = last_above_40
                cur_min = v
                state = "depleting"

        elif state == "depleting":
            cur_min = min(cur_min, v)
            if pct > 0.50:
                cur_rec_max = v
                state = "recovering"

        elif state == "recovering":
            cur_rec_max = max(cur_rec_max, v)
            if pct >= 0.40:
                last_above_40 = v
            if pct < 0.40:
                events.append((cur_pre_drop, cur_min, cur_rec_max))
                cur_pre_drop = last_above_40
                cur_min = v
                state = "depleting"

    if state == "depleting":
        events.append((cur_pre_drop, cur_min, None))
    elif state == "recovering":
        events.append((cur_pre_drop, cur_min, cur_rec_max))

    ratios: List[float] = []
    for pre_drop, ev_min, rec_max in events:
        depleted = pre_drop - ev_min
        if depleted <= 0 or rec_max is None:
            continue
        recovered = rec_max - ev_min
        ratios.append(min(recovered / depleted, 1.0))

    wbal_recovery_ratio = round(sum(ratios) / len(ratios), 3) if ratios else None

    return {
        "w_prime_j": round(w_prime, 1),
        "wbal_min_j": round(min_wbal, 1),
        "wbal_max_depletion_j": round(max_depletion, 1),
        "wbal_usage_pct": usage_pct,
        "seconds_below_30pct": below_30,
        "seconds_below_10pct": below_10,
        "min_wbal_at_second": min_idx,
        "wbal_depletion_events": len(events),
        "wbal_recovery_ratio": wbal_recovery_ratio,
    }


# ---------------------------------------------------------------------------
# 2. DFA Alpha 1 Aerobic Threshold Detection (Peng / Gronwald / Rogers)
# ---------------------------------------------------------------------------

DFA_A1_AEROBIC_THRESHOLD = 0.75
DFA_A1_ANAEROBIC_THRESHOLD = 0.50
SHORT_TERM_SCALES = tuple(range(4, 17))
ARTIFACT_JUMP_FRACTION = 0.20


def parse_rr_stream(hrv_data: List[Any], time_data: Optional[List[Any]] = None) -> List[Tuple[float, float]]:
    """Flatten per-second HRV stream into (time_s, rr_ms) beats."""
    beats: List[Tuple[float, float]] = []
    for index, entry in enumerate(hrv_data or []):
        if entry is None:
            continue
        if time_data is not None and index < len(time_data) and time_data[index] is not None:
            sec = float(time_data[index])
        else:
            sec = float(index)
        values = entry if isinstance(entry, (list, tuple)) else [entry]
        for raw in values:
            try:
                rr = float(raw)
            except (TypeError, ValueError):
                continue
            if rr > 0:
                beats.append((sec, rr))
    return beats


def flag_artifacts(rr_values: List[float], jump_fraction: float = ARTIFACT_JUMP_FRACTION) -> List[bool]:
    """Return per-beat validity mask based on relative beat-to-beat difference."""
    valid: List[bool] = []
    prev: Optional[float] = None
    for rr in rr_values:
        if prev is None or prev <= 0:
            valid.append(True)
        else:
            valid.append(abs(rr - prev) / prev <= jump_fraction)
        prev = rr
    return valid


def _linear_fit_rms(segment: List[float]) -> float:
    """Mean squared residual of a least-squares line through segment."""
    n = len(segment)
    xs = range(n)
    x_mean = (n - 1) / 2.0
    y_mean = sum(segment) / n
    sxx = sum((x - x_mean) ** 2 for x in xs)
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, segment))
    slope = sxy / sxx if sxx else 0.0
    intercept = y_mean - slope * x_mean
    return sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, segment)) / n


def dfa_alpha1(rr_values: List[float], scales: Tuple[int, ...] = SHORT_TERM_SCALES) -> Optional[float]:
    """
    Compute short-term scaling exponent alpha 1 for an R-R beat series.
    Returns None if series is too short.
    """
    n_beats = len(rr_values)
    if n_beats < 2 * max(scales):
        return None
    mean = sum(rr_values) / n_beats
    profile: List[float] = []
    running = 0.0
    for rr in rr_values:
        running += (rr - mean)
        profile.append(running)

    log_scales: List[float] = []
    log_fluctuations: List[float] = []

    for scale in scales:
        n_segments = n_beats // scale
        if n_segments < 1:
            continue
        total_rms = 0.0
        for i in range(n_segments):
            seg = profile[i * scale : (i + 1) * scale]
            total_rms += _linear_fit_rms(seg)
        f_scale = math.sqrt(total_rms / n_segments)
        if f_scale > 0:
            log_scales.append(math.log10(scale))
            log_fluctuations.append(math.log10(f_scale))

    if len(log_scales) < 2:
        return None

    # Slope = alpha 1
    n = len(log_scales)
    x_mean = sum(log_scales) / n
    y_mean = sum(log_fluctuations) / n
    sxx = sum((x - x_mean) ** 2 for x in log_scales)
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(log_scales, log_fluctuations))
    return round(sxy / sxx, 3) if sxx else None


# ---------------------------------------------------------------------------
# 3. Joe Friel Deterministic Data-Quality & Telemetry Consistency Auditor
# ---------------------------------------------------------------------------

@dataclass
class QualityCheckResult:
    area: str
    status: str  # "OK", "Warning", "Missing"
    explanation: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAuditReport:
    overall: str  # "Good", "Partial", "Limited"
    non_ok_count: int
    suggested_fix: str
    checks: List[QualityCheckResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": self.overall,
            "non_ok_count": self.non_ok_count,
            "suggested_fix": self.suggested_fix,
            "checks": [asdict(c) for c in self.checks],
        }


class DataQualityAuditor:
    """Audits athlete profile and telemetry consistency (Joe Friel principles)."""

    @staticmethod
    def audit(
        ftp: Optional[float] = None,
        rolling_ftp: Optional[float] = None,
        eftp: Optional[float] = None,
        w_prime: Optional[float] = None,
        rolling_w_prime: Optional[float] = None,
        resting_hr: Optional[float] = None,
        hrv: Optional[float] = None,
        sleep_secs: Optional[float] = None,
        recent_activities: Optional[List[Dict[str, Any]]] = None,
    ) -> QualityAuditReport:
        checks: List[QualityCheckResult] = []

        # 1. FTP Consistency
        if ftp and ftp > 0:
            diffs = []
            if rolling_ftp and rolling_ftp > 0:
                diffs.append(abs(rolling_ftp - ftp) / ftp * 100.0)
            if eftp and eftp > 0:
                diffs.append(abs(eftp - ftp) / ftp * 100.0)

            max_diff = max(diffs) if diffs else 0.0
            if max_diff < 10.0:
                checks.append(QualityCheckResult("FTP Consistency", "OK", "FTP aligns closely with rolling eFTP.", {"max_diff_pct": round(max_diff, 1)}))
            elif max_diff <= 20.0:
                checks.append(QualityCheckResult("FTP Consistency", "Warning", "Mild drift between configured FTP and estimated eFTP.", {"max_diff_pct": round(max_diff, 1)}))
            else:
                checks.append(QualityCheckResult("FTP Consistency", "Missing", "Large discrepancy between athlete configured FTP and modeled eFTP.", {"max_diff_pct": round(max_diff, 1)}))
        else:
            checks.append(QualityCheckResult("FTP Consistency", "Missing", "FTP is not configured in profile."))

        # 2. W' Consistency
        if w_prime and w_prime > 0 and rolling_w_prime and rolling_w_prime > 0:
            diff_w = abs(rolling_w_prime - w_prime) / w_prime * 100.0
            if diff_w < 10.0:
                checks.append(QualityCheckResult("W' Anaerobic Capacity", "OK", "W' capacity aligns with power curve.", {"diff_pct": round(diff_w, 1)}))
            elif diff_w <= 20.0:
                checks.append(QualityCheckResult("W' Anaerobic Capacity", "Warning", "Moderate W' variance.", {"diff_pct": round(diff_w, 1)}))
            else:
                checks.append(QualityCheckResult("W' Anaerobic Capacity", "Missing", "W' inconsistent with recent maximal efforts.", {"diff_pct": round(diff_w, 1)}))
        else:
            checks.append(QualityCheckResult("W' Anaerobic Capacity", "OK", "W' default modeled successfully."))

        # 3. Wellness & Biometric Density
        has_wellness = any(v is not None and v > 0 for v in [resting_hr, hrv, sleep_secs])
        if has_wellness:
            checks.append(QualityCheckResult("Wellness Biometrics", "OK", "Resting HR, sleep, and recovery metrics present.", {"resting_hr": resting_hr, "sleep_hours": round(sleep_secs / 3600.0, 1) if sleep_secs else None}))
        else:
            checks.append(QualityCheckResult("Wellness Biometrics", "Missing", "No daily wellness biometrics logged."))

        # 4. Activity Density (Last 7 days)
        acts = recent_activities or []
        if len(acts) >= 3:
            checks.append(QualityCheckResult("Activity Density", "OK", f"Good training density ({len(acts)} sessions in lookback window).", {"count": len(acts)}))
        elif len(acts) >= 1:
            checks.append(QualityCheckResult("Activity Density", "Warning", f"Low activity count ({len(acts)} sessions).", {"count": len(acts)}))
        else:
            checks.append(QualityCheckResult("Activity Density", "Missing", "Zero activities recorded in recent period.", {"count": 0}))

        # 5. Post-Activity Fueling & Feedback
        if acts:
            logged_rpe = sum(1 for a in acts if a.get("rpe") or a.get("perceived_exertion"))
            logged_carbs = sum(1 for a in acts if a.get("carbs_ingested_g") or a.get("carbs"))
            if logged_rpe == len(acts):
                checks.append(QualityCheckResult("Athlete Feedback (RPE)", "OK", "Complete RPE logged across all recent sessions."))
            elif logged_rpe > 0:
                checks.append(QualityCheckResult("Athlete Feedback (RPE)", "Warning", f"Partial RPE feedback ({logged_rpe}/{len(acts)} sessions logged)."))
            else:
                checks.append(QualityCheckResult("Athlete Feedback (RPE)", "Missing", "No RPE exertion recorded in recent workouts."))
        else:
            checks.append(QualityCheckResult("Athlete Feedback (RPE)", "OK", "No completed activities requiring debrief."))

        non_ok = sum(1 for c in checks if c.status != "OK")
        if non_ok == 0:
            overall = "Good"
            fix = "All telemetry streams are verified and consistent."
        elif non_ok <= 2:
            overall = "Partial"
            fix = "Review warnings to maximize physiological modeling fidelity."
        else:
            overall = "Limited"
            fix = "Update baseline thresholds and log post-session exertion to enable optimal guidance."

        return QualityAuditReport(
            overall=overall,
            non_ok_count=non_ok,
            suggested_fix=fix,
            checks=checks,
        )
