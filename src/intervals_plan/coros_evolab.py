"""
COROS Training Hub & EvoLab Sports-Science Engine.

Implements the core physiological modeling algorithms of the COROS Training Hub:
1. EvoLab Load Dynamics: Base Fitness (42d), Load Impact (7d), and Fatigue Index (0-100).
2. 7-Day Training Load Range & Intensity Trend.
3. Running Fitness 4-Pillar Evaluation: Base, Endurance, Speed, and Sprint scores (40-100).
4. Deterministic Race Predictor: 5K, 10K, Half Marathon, and Marathon times & paces.
5. Real-Time Aerobic & Anaerobic Training Effect (0.0 - 5.0) and Recovery Countdown Timer (0-96h).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
import math
from typing import Any, Dict, List, Optional


def format_time_hms(seconds: int) -> str:
    """Format total seconds into human-readable HH:MM:SS or MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_pace(sec_per_km: int) -> str:
    """Format seconds per kilometer into M:SS /km."""
    m = sec_per_km // 60
    s = sec_per_km % 60
    return f"{m}:{s:02d} /km"


# ---------------------------------------------------------------------------
# 1. EvoLab Fatigue & Intensity Dynamics
# ---------------------------------------------------------------------------

class CorosFatigueZone:
    MINIMAL = "MINIMAL"          # 0 - 19
    PERFORMANCE = "PERFORMANCE"  # 20 - 39
    OPTIMIZED = "OPTIMIZED"      # 40 - 59
    HIGH = "HIGH"                # 60 - 79
    EXCESSIVE = "EXCESSIVE"      # 80 - 100


@dataclass
class EvoLabMetrics:
    base_fitness: float          # 42-day rolling load average (equivalent to CTL)
    load_impact: float           # 7-day rolling load average (equivalent to ATL)
    fatigue_score: float         # 0 - 100 index
    fatigue_zone: str            # MINIMAL, PERFORMANCE, OPTIMIZED, HIGH, EXCESSIVE
    fatigue_description: str
    intensity_trend: str
    seven_day_load: float
    recommended_min_load: float
    recommended_max_load: float
    load_recommendation_status: str  # BELOW, RECOMMENDED, EXCESSIVE

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# 2. Running Fitness & 4-Pillar Breakdown
# ---------------------------------------------------------------------------

@dataclass
class RunningFitnessBreakdown:
    overall_score: float
    base_score: float        # Aerobic Endurance (>30km)
    endurance_score: float   # Lactate Threshold (~10km)
    speed_score: float       # VO2 Max (~3km)
    sprint_score: float      # Anaerobic Power (~400m)
    threshold_pace_sec_km: int
    threshold_pace_formatted: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# 3. Race Predictor (Riegel / Cameron Model)
# ---------------------------------------------------------------------------

@dataclass
class RacePrediction:
    distance_name: str
    distance_km: float
    predicted_seconds: int
    predicted_time_formatted: str
    predicted_pace_formatted: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# 4. Training Effect & Recovery Timer
# ---------------------------------------------------------------------------

@dataclass
class TrainingEffectResult:
    aerobic_te: float
    aerobic_label: str
    anaerobic_te: float
    anaerobic_label: str
    recovery_hours: float
    recovery_pct: int
    recovery_state: str  # FRESH, TIRED, EXHAUSTED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# 5. Core COROS EvoLab Calculation Engine
# ---------------------------------------------------------------------------

class CorosEvoLabEngine:
    """Computes all COROS Training Hub and EvoLab physiological metrics deterministically."""

    @staticmethod
    def calculate_fatigue(base_fitness: float, load_impact: float) -> Tuple[float, str, str, str]:
        """
        Calculate COROS Fatigue score (0-100) and identify current training zone.
        When load_impact == base_fitness, fatigue is centered at 50 (Optimized).
        """
        raw = 50.0 + (load_impact - base_fitness) * 1.5
        score = max(0.0, min(100.0, round(raw, 1)))

        if score < 20.0:
            zone = CorosFatigueZone.MINIMAL
            desc = "Recent training load is light. Fully rested, but prolonged stay risks fitness loss."
            trend = "Recovery / Minimal stimulus"
        elif score < 40.0:
            zone = CorosFatigueZone.PERFORMANCE
            desc = "Fatigue is shed while retaining high fitness. Optimal for race taper or personal best efforts."
            trend = "Peak performance / Tapered"
        elif score < 60.0:
            zone = CorosFatigueZone.OPTIMIZED
            desc = "Training load is in the sweet spot. Ideal for progressive aerobic and structural adaptation."
            trend = "Optimal progressive overload"
        elif score < 80.0:
            zone = CorosFatigueZone.HIGH
            desc = "Significant fatigue accumulated. Monitor recovery closely and schedule rest soon."
            trend = "High fatigue accumulation"
        else:
            zone = CorosFatigueZone.EXCESSIVE
            desc = "Severe physiological stress relative to baseline. Rest and active recovery mandatory."
            trend = "Excessive load / Overtraining risk"

        return score, zone, desc, trend

    @staticmethod
    def calculate_load_recommendation(base_fitness: float, recent_daily_loads: List[float]) -> Tuple[float, float, float, str]:
        """
        Calculate 7-day cumulative load and recommended range based on Base Fitness.
        """
        seven_day_load = round(sum(recent_daily_loads[-7:]) if recent_daily_loads else (base_fitness * 7.0), 1)
        rec_min = round(max(50.0, base_fitness * 7.0 * 0.85), 1)
        rec_max = round(max(80.0, base_fitness * 7.0 * 1.25), 1)

        if seven_day_load < rec_min:
            status = "BELOW"
        elif seven_day_load <= rec_max:
            status = "RECOMMENDED"
        else:
            status = "EXCESSIVE"

        return seven_day_load, rec_min, rec_max, status

    @staticmethod
    def calculate_running_fitness(threshold_pace_sec_km: int, weekly_hours: float = 8.0) -> RunningFitnessBreakdown:
        """
        Calculate Running Fitness score (40-100) and the 4 physiological pillars:
        - Base: Aerobic Endurance (>30km)
        - Endurance: Lactate Threshold (~10km)
        - Speed: VO2 Max (~3km)
        - Sprint: Neuromuscular Anaerobic (~400m)
        """
        # Linear calibration from threshold pace (e.g. 210s/km = 3:30 -> 78.8, 270s/km = 4:30 -> 65.6, 330s/km = 5:30 -> 52.4)
        raw_fitness = 125.0 - (threshold_pace_sec_km * 0.22)
        overall = max(40.0, min(100.0, round(raw_fitness, 1)))

        # Aerobic base reflects weekly training volume and long runs
        volume_boost = min(6.0, max(0.0, (weekly_hours - 5.0) * 1.2))
        base_score = max(40.0, min(100.0, round(overall * 0.94 + volume_boost, 1)))

        # Endurance reflects threshold capacity
        endurance_score = overall

        # Speed reflects aerobic power and VO2max pace
        speed_score = max(40.0, min(100.0, round(overall + 1.8, 1)))

        # Sprint reflects short anaerobic power
        sprint_score = max(40.0, min(100.0, round(overall - 1.2, 1)))

        return RunningFitnessBreakdown(
            overall_score=overall,
            base_score=base_score,
            endurance_score=endurance_score,
            speed_score=speed_score,
            sprint_score=sprint_score,
            threshold_pace_sec_km=threshold_pace_sec_km,
            threshold_pace_formatted=format_pace(threshold_pace_sec_km),
        )

    @staticmethod
    def predict_races(threshold_pace_sec_km: int, weekly_hours: float = 8.0) -> List[RacePrediction]:
        """
        Predict race times for standard distances using Riegel power-law model calibrated to threshold.
        T_2 = T_1 * (D_2 / D_1) ^ 1.06
        """
        # Baseline: 10k time at threshold pace
        t_10k = threshold_pace_sec_km * 10.0

        targets = [
            ("5K", 5.0, 1.05),
            ("10K", 10.0, 1.06),
            ("Half Marathon", 21.0975, 1.07),
            ("Marathon", 42.195, 1.085),
        ]

        predictions: List[RacePrediction] = []
        for name, dist, exp in targets:
            # Pete Riegel formula
            pred_sec = t_10k * math.pow(dist / 10.0, exp)

            # For marathon, account for aerobic endurance volume factor
            if dist > 30.0 and weekly_hours < 8.0:
                pred_sec *= (1.0 + (8.0 - weekly_hours) * 0.015)

            total_seconds = int(round(pred_sec))
            pace_sec_km = int(round(total_seconds / dist))

            predictions.append(
                RacePrediction(
                    distance_name=name,
                    distance_km=dist,
                    predicted_seconds=total_seconds,
                    predicted_time_formatted=format_time_hms(total_seconds),
                    predicted_pace_formatted=format_pace(pace_sec_km),
                )
            )

        return predictions

    @staticmethod
    def calculate_training_effect(
        duration_seconds: int,
        load_tss: float,
        hr_avg: Optional[int] = None,
        lthr: int = 182,
        fatigue_score: float = 50.0,
        hours_elapsed: float = 0.0,
    ) -> TrainingEffectResult:
        """
        Calculate Aerobic TE (0.0-5.0), Anaerobic TE (0.0-5.0), and Recovery Timer (0-96h).
        """
        if duration_seconds <= 0 or load_tss <= 0:
            return TrainingEffectResult(
                aerobic_te=0.0,
                aerobic_label="Inefficient",
                anaerobic_te=0.0,
                anaerobic_label="Inefficient",
                recovery_hours=0.0,
                recovery_pct=100,
                recovery_state="FRESH",
            )

        # Intensity ratio estimate
        intensity_ratio = (hr_avg / lthr) if (hr_avg and lthr > 0) else 0.85

        # Split load into aerobic and anaerobic components
        if intensity_ratio > 1.0:
            anaerobic_fraction = min(0.65, (intensity_ratio - 1.0) * 2.5 + 0.15)
        else:
            anaerobic_fraction = max(0.05, (intensity_ratio - 0.70) * 0.30)
        aerobic_fraction = 1.0 - anaerobic_fraction

        aero_load = load_tss * aerobic_fraction
        anaero_load = load_tss * anaerobic_fraction

        # Aerobic TE (0.0 - 5.0)
        aero_val = min(5.0, max(0.0, round(0.4 + 2.3 * math.log10(1.0 + aero_load / 16.0), 1)))

        # Anaerobic TE (0.0 - 5.0)
        anaero_val = min(5.0, max(0.0, round(2.7 * math.log10(1.0 + anaero_load / 10.0), 1)))

        labels = {
            (0.0, 1.0): "Inefficient",
            (1.0, 2.0): "Recovery",
            (2.0, 3.0): "Maintaining",
            (3.0, 4.0): "Improving",
            (4.0, 5.0): "Optimized",
            (5.0, 5.1): "Overreaching",
        }

        def get_label(val: float) -> str:
            for (low, high), lbl in labels.items():
                if low <= val < high or (val >= 5.0 and high >= 5.0):
                    return lbl
            return "Maintaining"

        aero_lbl = get_label(aero_val)
        anaero_lbl = get_label(anaero_val)

        # Recovery Timer (0 - 96 hours)
        base_recovery_h = (load_tss * 0.42) * (0.85 + (fatigue_score / 100.0) * 0.35)
        initial_recovery = min(96.0, max(4.0, round(base_recovery_h, 1)))
        remaining_hours = max(0.0, round(initial_recovery - hours_elapsed, 1))

        # Recovery percentage
        recovery_pct = max(0, min(100, int(round((1.0 - remaining_hours / 96.0) * 100.0))))

        if recovery_pct >= 90:
            rec_state = "FRESH"
        elif recovery_pct >= 30:
            rec_state = "TIRED"
        else:
            rec_state = "EXHAUSTED"

        return TrainingEffectResult(
            aerobic_te=aero_val,
            aerobic_label=aero_lbl,
            anaerobic_te=anaero_val,
            anaerobic_label=anaero_lbl,
            recovery_hours=remaining_hours,
            recovery_pct=recovery_pct,
            recovery_state=rec_state,
        )

    @classmethod
    def evaluate_full_hub(
        cls,
        base_fitness: float,
        load_impact: float,
        recent_daily_loads: Optional[List[float]] = None,
        threshold_pace_sec_km: int = 270,
        weekly_hours: float = 8.0,
        last_workout_load: float = 65.0,
        last_workout_duration_secs: int = 3600,
        last_workout_hr: Optional[int] = 155,
        athlete_lthr: int = 182,
        hours_since_last_workout: float = 12.0,
    ) -> Dict[str, Any]:
        """Generate comprehensive COROS Training Hub and EvoLab report."""
        loads = recent_daily_loads or [base_fitness] * 7
        fatigue_score, zone, desc, trend = cls.calculate_fatigue(base_fitness, load_impact)
        seven_day_load, rec_min, rec_max, load_status = cls.calculate_load_recommendation(base_fitness, loads)

        evolab_metrics = EvoLabMetrics(
            base_fitness=round(base_fitness, 1),
            load_impact=round(load_impact, 1),
            fatigue_score=fatigue_score,
            fatigue_zone=zone,
            fatigue_description=desc,
            intensity_trend=trend,
            seven_day_load=seven_day_load,
            recommended_min_load=rec_min,
            recommended_max_load=rec_max,
            load_recommendation_status=load_status,
        )

        running_fitness = cls.calculate_running_fitness(threshold_pace_sec_km, weekly_hours)
        race_predictions = cls.predict_races(threshold_pace_sec_km, weekly_hours)

        training_effect = cls.calculate_training_effect(
            duration_seconds=last_workout_duration_secs,
            load_tss=last_workout_load,
            hr_avg=last_workout_hr,
            lthr=athlete_lthr,
            fatigue_score=fatigue_score,
            hours_elapsed=hours_since_last_workout,
        )

        return {
            "evolab": evolab_metrics.to_dict(),
            "running_fitness": running_fitness.to_dict(),
            "race_predictions": [r.to_dict() for r in race_predictions],
            "training_effect": training_effect.to_dict(),
        }
