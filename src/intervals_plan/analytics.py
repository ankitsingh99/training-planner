"""
Sports Science Analytics Engine:
Analyzes 30-day rolling wellness, completed activities, training impulse,
Performance Management (CTL/ATL/TSB), Tim Gabbett's ACWR, Stephen Seiler's 80/20
polarization, and Kiviniemi/Plews/Buchheit HRV & resting heart rate readiness.
"""

from dataclasses import dataclass, field
import datetime
import math
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ACWRMetric:
    """Acute:Chronic Workload Ratio metrics and injury risk assessment (Tim Gabbett)."""
    acute_load_7d: float
    chronic_load_28d: float
    chronic_weekly_avg: float
    ratio: float
    status: str  # "UNDER_TRAINING", "SWEET_SPOT", "ELEVATED_LOAD", "DANGER_ZONE"
    guidance: str


@dataclass
class PhysiologicalReadiness:
    """Readiness verdict based on Banister/Coggan PMC and Kiviniemi/Plews HRV & RHR decision trees."""
    ctl: float  # Fitness (42d EWMA)
    atl: float  # Fatigue (7d EWMA)
    tsb: float  # Form (CTL - ATL)
    resting_hr_baseline: Optional[float]
    recent_resting_hr: Optional[float]
    rhr_delta: Optional[float]
    rhr_elevated: bool
    readiness_state: str  # "OPTIMAL_OVERLOAD", "PRODUCTIVE_MAINTENANCE", "ELEVATED_FATIGUE", "RECOVERY_MANDATORY"
    readiness_score: int  # 0 to 100
    recommendation: str
    target_next_week_tss: float
    target_next_week_hours: float


@dataclass
class IntensityDistribution:
    """Stephen Seiler 3-Zone intensity distribution analysis."""
    low_intensity_pct: float   # Zone 1/2 (<83% LTHR / <75% MaxHR)
    moderate_intensity_pct: float  # Zone 3 (84-94% LTHR)
    high_intensity_pct: float  # Zone 4/5 (>=95% LTHR)
    total_moving_time_hours: float
    is_polarized: bool
    summary: str


@dataclass
class DisciplineSummary:
    """Aggregated volume and load by sport."""
    sport: str
    activity_count: int
    moving_time_hours: float
    total_load: float
    total_distance_km: float


@dataclass
class RollingAnalysisReport:
    """Comprehensive 30-day physiological and training load report."""
    period_start: str
    period_end: str
    total_activities: int
    total_moving_hours: float
    total_load_tss: float
    disciplines: Dict[str, DisciplineSummary]
    acwr: ACWRMetric
    readiness: PhysiologicalReadiness
    intensity_distribution: IntensityDistribution
    raw_wellness_count: int

    def summary_lines(self) -> List[str]:
        lines = []
        lines.append("=" * 64)
        lines.append(f"  PHYSIOLOGICAL & TRAINING LOAD REPORT ({self.period_start} to {self.period_end})")
        lines.append("=" * 64)
        lines.append(f"Total Completed Workouts: {self.total_activities}")
        lines.append(f"Total Moving Volume:     {self.total_moving_hours:.1f} hours ({self.total_load_tss:.0f} TSS)")
        
        lines.append("\n[1] PERFORMANCE MANAGEMENT CHART (Banister / Coggan PMC):")
        lines.append(f"  - Fitness (CTL 42d):   {self.readiness.ctl:.1f}")
        lines.append(f"  - Fatigue (ATL 7d):    {self.readiness.atl:.1f}")
        lines.append(f"  - Form (TSB):          {self.readiness.tsb:+.1f}")
        
        lines.append("\n[2] ACUTE:CHRONIC WORKLOAD RATIO (Tim Gabbett):")
        lines.append(f"  - Acute Load (7-Day):  {self.acwr.acute_load_7d:.0f} TSS")
        lines.append(f"  - Chronic Load (28-Day Avg): {self.acwr.chronic_weekly_avg:.0f} TSS/week")
        lines.append(f"  - ACWR Ratio:          {self.acwr.ratio:.2f} [{self.acwr.status}]")
        lines.append(f"  - Assessment:          {self.acwr.guidance}")

        lines.append("\n[3] AUTONOMIC READINESS (Plews & Kiviniemi HRV/RHR):")
        if self.readiness.recent_resting_hr is not None and self.readiness.resting_hr_baseline is not None:
            delta_str = f"{self.readiness.rhr_delta:+.1f} bpm" if self.readiness.rhr_delta is not None else "N/A"
            flag = "⚠️ ELEVATED" if self.readiness.rhr_elevated else "✅ STABLE"
            lines.append(f"  - Resting HR (3d vs 30d): {self.readiness.recent_resting_hr:.0f} bpm vs {self.readiness.resting_hr_baseline:.0f} bpm (Delta: {delta_str}) [{flag}]")
        else:
            lines.append("  - Resting HR:          Limited data in wellness logs")
        lines.append(f"  - Readiness State:     {self.readiness.readiness_state} (Score: {self.readiness.readiness_score}/100)")
        lines.append(f"  - Coaching Guidance:   {self.readiness.recommendation}")

        lines.append("\n[4] INTENSITY POLARIZATION (Stephen Seiler 80/20):")
        lines.append(f"  - Low (Zone 1-2 Aerobic):  {self.intensity_distribution.low_intensity_pct:.1f}%")
        lines.append(f"  - Mod (Zone 3 Threshold):  {self.intensity_distribution.moderate_intensity_pct:.1f}%")
        lines.append(f"  - High (Zone 4-5 VO2max):  {self.intensity_distribution.high_intensity_pct:.1f}%")
        lines.append(f"  - Profile:                 {self.intensity_distribution.summary}")

        lines.append("\n[5] SPORT DISCIPLINE BREAKDOWN:")
        for sp, d in self.disciplines.items():
            lines.append(f"  - {sp:<10}: {d.activity_count:>2} sessions | {d.moving_time_hours:>5.1f} hrs | {d.total_load:>5.0f} TSS | {d.total_distance_km:>5.1f} km")

        lines.append("\n[6] NEXT-WEEK RECOMMENDED PRESCRIPTION:")
        lines.append(f"  - Target Training Load: {self.readiness.target_next_week_tss:.0f} TSS")
        lines.append(f"  - Target Moving Volume: {self.readiness.target_next_week_hours:.1f} hours")
        lines.append("=" * 64)
        return lines


class RollingMetricsAnalyzer:
    """Analyzes athlete activity history and wellness to derive sports-science training metrics."""

    def __init__(self, target_hours_profile: float = 8.0, athlete_lthr: int = 182):
        self.target_hours_profile = target_hours_profile
        self.athlete_lthr = athlete_lthr

    def compute_acwr(self, daily_loads: List[Tuple[datetime.date, float]], end_date: datetime.date) -> ACWRMetric:
        """Calculate Acute:Chronic Workload Ratio over the last 28 days."""
        # Acute: last 7 days (end_date - 6 to end_date)
        # Chronic: last 28 days (end_date - 27 to end_date)
        acute_start = end_date - datetime.timedelta(days=6)
        chronic_start = end_date - datetime.timedelta(days=27)

        acute_total = 0.0
        chronic_total = 0.0

        for day, load in daily_loads:
            if acute_start <= day <= end_date:
                acute_total += load
            if chronic_start <= day <= end_date:
                chronic_total += load

        chronic_weekly_avg = chronic_total / 4.0 if chronic_total > 0 else 0.0

        if chronic_weekly_avg > 0:
            ratio = acute_total / chronic_weekly_avg
        elif acute_total > 0:
            ratio = 1.5  # High relative spike from zero chronic baseline
        else:
            ratio = 0.0

        if ratio < 0.8:
            status = "UNDER_TRAINING"
            guidance = "Workload has dropped below baseline. Fitness may decline; gradually ramp up volume."
        elif 0.8 <= ratio <= 1.3:
            status = "SWEET_SPOT"
            guidance = "Optimal adaptation range. Low injury risk, progressive fitness build."
        elif 1.3 < ratio <= 1.5:
            status = "ELEVATED_LOAD"
            guidance = "Workload ramping rapidly. Monitor recovery and prevent stacking hard days."
        else:
            status = "DANGER_ZONE"
            guidance = "Acute spike (>1.5)! Non-contact injury risk elevated. Immediate recovery needed."

        return ACWRMetric(
            acute_load_7d=round(acute_total, 1),
            chronic_load_28d=round(chronic_total, 1),
            chronic_weekly_avg=round(chronic_weekly_avg, 1),
            ratio=round(ratio, 2),
            status=status,
            guidance=guidance,
        )

    def analyze_autonomic_readiness(
        self,
        wellness_records: List[Dict[str, Any]],
        acwr: ACWRMetric,
        ctl: float,
        atl: float,
    ) -> PhysiologicalReadiness:
        """Evaluate physiological readiness using PMC + Kiviniemi/Plews RHR/HRV rules."""
        tsb = ctl - atl

        # Extract resting HR values
        valid_rhrs: List[Tuple[str, float]] = []
        for w in wellness_records:
            rhr = w.get("restingHR")
            if rhr is not None and isinstance(rhr, (int, float)) and rhr > 30:
                valid_rhrs.append((w.get("id", ""), float(rhr)))

        resting_hr_baseline = None
        recent_resting_hr = None
        rhr_delta = None
        rhr_elevated = False

        if len(valid_rhrs) >= 5:
            # Baseline = average of all available points in 30d
            baseline_vals = [val for _, val in valid_rhrs]
            resting_hr_baseline = sum(baseline_vals) / len(baseline_vals)
            # Recent = average of last 3 available points
            recent_vals = [val for _, val in valid_rhrs[-3:]]
            recent_resting_hr = sum(recent_vals) / len(recent_vals)
            rhr_delta = recent_resting_hr - resting_hr_baseline
            if rhr_delta >= 4.0:
                rhr_elevated = True
        elif len(valid_rhrs) > 0:
            resting_hr_baseline = valid_rhrs[0][1]
            recent_resting_hr = valid_rhrs[-1][1]
            rhr_delta = recent_resting_hr - resting_hr_baseline
            if rhr_delta >= 4.0:
                rhr_elevated = True

        # Decision Tree Logic
        readiness_score = 75  # Neutral baseline
        if tsb >= 0:
            readiness_score += 15
        elif tsb >= -15:
            readiness_score += 5
        elif tsb >= -30:
            readiness_score -= 15
        else:
            readiness_score -= 30

        if acwr.status == "SWEET_SPOT":
            readiness_score += 10
        elif acwr.status == "DANGER_ZONE":
            readiness_score -= 25
        elif acwr.status == "ELEVATED_LOAD":
            readiness_score -= 10

        if rhr_elevated:
            readiness_score -= 25

        readiness_score = max(10, min(100, readiness_score))

        # Classify state
        if readiness_score >= 80 and not rhr_elevated and acwr.status != "DANGER_ZONE":
            state = "OPTIMAL_OVERLOAD"
            rec = "Physiological markers are green. Ready for progressive volume and high-quality interval work."
            load_multiplier = 1.05
            hour_multiplier = 1.0
        elif readiness_score >= 60 and not rhr_elevated:
            state = "PRODUCTIVE_MAINTENANCE"
            rec = "Stable training state. Execute planned sessions; ensure easy sessions stay strictly conversational."
            load_multiplier = 1.00
            hour_multiplier = 1.0
        elif readiness_score >= 40 or rhr_elevated:
            state = "ELEVATED_FATIGUE"
            rec = "Sympathetic strain or accumulated fatigue detected. Downshift high-intensity intervals to Zone 1 active recovery."
            load_multiplier = 0.85
            hour_multiplier = 0.90
        else:
            state = "RECOVERY_MANDATORY"
            rec = "Excessive fatigue or workload spike. Immediate deload required to prevent injury or non-functional overreaching."
            load_multiplier = 0.65
            hour_multiplier = 0.75

        # Compute target TSS and hours
        # Chronic weekly base is CTL * 7
        chronic_weekly = max(100.0, ctl * 7.0)
        target_tss = chronic_weekly * load_multiplier
        target_hours = self.target_hours_profile * hour_multiplier

        return PhysiologicalReadiness(
            ctl=round(ctl, 1),
            atl=round(atl, 1),
            tsb=round(tsb, 1),
            resting_hr_baseline=round(resting_hr_baseline, 1) if resting_hr_baseline else None,
            recent_resting_hr=round(recent_resting_hr, 1) if recent_resting_hr else None,
            rhr_delta=round(rhr_delta, 1) if rhr_delta is not None else None,
            rhr_elevated=rhr_elevated,
            readiness_state=state,
            readiness_score=readiness_score,
            recommendation=rec,
            target_next_week_tss=round(target_tss, 0),
            target_next_week_hours=round(target_hours, 1),
        )

    def analyze_intensity_distribution(self, activities: List[Dict[str, Any]]) -> IntensityDistribution:
        """Estimate Stephen Seiler 3-zone polarization across completed activities."""
        low_secs = 0.0
        mod_secs = 0.0
        high_secs = 0.0
        total_moving_secs = 0.0

        for a in activities:
            dur = float(a.get("moving_time") or a.get("elapsed_time") or 0)
            if dur <= 0:
                continue
            total_moving_secs += dur
            avg_hr = a.get("average_heartrate")

            if avg_hr and avg_hr > 0 and self.athlete_lthr > 0:
                hr_pct = (avg_hr / self.athlete_lthr) * 100.0
                if hr_pct < 84.0:
                    low_secs += dur
                elif hr_pct < 95.0:
                    mod_secs += dur
                else:
                    high_secs += dur
            else:
                # Name-based heuristic if HR is missing
                name = (a.get("name") or "").lower()
                if any(w in name for w in ["easy", "recovery", "spin", "base", "z2", "commute", "walk"]):
                    low_secs += dur
                elif any(w in name for w in ["tempo", "sweet", "sst", "club", "group"]):
                    mod_secs += dur
                elif any(w in name for w in ["interval", "vo2", "speed", "track", "race", "5k", "sprint"]):
                    high_secs += dur
                else:
                    low_secs += dur * 0.8
                    high_secs += dur * 0.2

        if total_moving_secs > 0:
            low_pct = (low_secs / total_moving_secs) * 100.0
            mod_pct = (mod_secs / total_moving_secs) * 100.0
            high_pct = (high_secs / total_moving_secs) * 100.0
        else:
            low_pct = 80.0
            mod_pct = 5.0
            high_pct = 15.0

        is_polarized = low_pct >= 75.0 and mod_pct <= 15.0
        if is_polarized:
            summary = "Well-polarized (~80% low aerobic base, minimal threshold grey-zone)."
        elif mod_pct > 20.0:
            summary = "Pyramidal or Threshold-heavy (significant time in moderate grey zone)."
        else:
            summary = "Mixed distribution."

        return IntensityDistribution(
            low_intensity_pct=round(low_pct, 1),
            moderate_intensity_pct=round(mod_pct, 1),
            high_intensity_pct=round(high_pct, 1),
            total_moving_time_hours=round(total_moving_secs / 3600.0, 1),
            is_polarized=is_polarized,
            summary=summary,
        )

    def analyze_disciplines(self, activities: List[Dict[str, Any]]) -> Dict[str, DisciplineSummary]:
        """Aggregate activities by sport."""
        disciplines: Dict[str, Dict[str, float]] = {}

        for a in activities:
            raw_type = a.get("type") or "Other"
            if raw_type in ["Ride", "VirtualRide", "GravelRide", "MountainBikeRide"]:
                sport = "Ride"
            elif raw_type in ["Run", "VirtualRun", "TrailRun"]:
                sport = "Run"
            elif raw_type in ["Swim", "OpenWaterSwim"]:
                sport = "Swim"
            else:
                sport = "Other"

            if sport not in disciplines:
                disciplines[sport] = {"count": 0, "moving_time": 0.0, "load": 0.0, "distance": 0.0}

            disciplines[sport]["count"] += 1
            disciplines[sport]["moving_time"] += float(a.get("moving_time") or 0)
            disciplines[sport]["load"] += float(a.get("icu_training_load") or 0)
            disciplines[sport]["distance"] += float(a.get("distance") or 0)

        result = {}
        for sp, d in disciplines.items():
            result[sp] = DisciplineSummary(
                sport=sp,
                activity_count=int(d["count"]),
                moving_time_hours=round(d["moving_time"] / 3600.0, 1),
                total_load=round(d["load"], 1),
                total_distance_km=round(d["distance"] / 1000.0, 1),
            )
        return result

    def analyze_30d(
        self,
        wellness_records: List[Dict[str, Any]],
        activities: List[Dict[str, Any]],
        end_date_str: Optional[str] = None,
    ) -> RollingAnalysisReport:
        """Run full 30-day physiological and training load analysis."""
        if end_date_str:
            end_date = datetime.date.fromisoformat(end_date_str)
        else:
            end_date = datetime.date.today()

        start_date = end_date - datetime.timedelta(days=29)

        # Build daily load map from activities
        daily_loads_dict: Dict[datetime.date, float] = {}
        curr = start_date
        while curr <= end_date:
            daily_loads_dict[curr] = 0.0
            curr += datetime.timedelta(days=1)

        total_moving_secs = 0.0
        total_load = 0.0

        for a in activities:
            dt_str = a.get("start_date_local", "")
            if dt_str:
                act_date = datetime.date.fromisoformat(dt_str[:10])
                if start_date <= act_date <= end_date:
                    load = float(a.get("icu_training_load") or 0)
                    daily_loads_dict[act_date] = daily_loads_dict.get(act_date, 0.0) + load
                    total_load += load
                    total_moving_secs += float(a.get("moving_time") or 0)

        # Also incorporate load from wellness ctlLoad/atlLoad if activity list was incomplete
        daily_loads_list = sorted(daily_loads_dict.items(), key=lambda x: x[0])
        acwr = self.compute_acwr(daily_loads_list, end_date)

        # Get latest CTL and ATL from wellness or fallback
        latest_ctl = 15.0
        latest_atl = 15.0
        if wellness_records:
            # Sort by id (date)
            sorted_w = sorted(wellness_records, key=lambda x: x.get("id", ""))
            for w in reversed(sorted_w):
                if w.get("ctl") is not None and w.get("atl") is not None:
                    latest_ctl = float(w["ctl"])
                    latest_atl = float(w["atl"])
                    break

        readiness = self.analyze_autonomic_readiness(wellness_records, acwr, latest_ctl, latest_atl)
        intensity_dist = self.analyze_intensity_distribution(activities)
        disciplines = self.analyze_disciplines(activities)

        return RollingAnalysisReport(
            period_start=start_date.isoformat(),
            period_end=end_date.isoformat(),
            total_activities=len(activities),
            total_moving_hours=round(total_moving_secs / 3600.0, 1),
            total_load_tss=round(total_load, 0),
            disciplines=disciplines,
            acwr=acwr,
            readiness=readiness,
            intensity_distribution=intensity_dist,
            raw_wellness_count=len(wellness_records),
        )
