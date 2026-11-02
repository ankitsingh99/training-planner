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
class ACWRMetric:  # pragma: no cover
    """Acute:Chronic Workload Ratio metrics and injury risk assessment (Tim Gabbett)."""
    acute_load_7d: float
    chronic_load_28d: float
    chronic_weekly_avg: float
    ratio: float
    status: str  # "UNDER_TRAINING", "SWEET_SPOT", "ELEVATED_LOAD", "DANGER_ZONE"
    guidance: str


@dataclass
class PhysiologicalReadiness:
    """Multi-Factor Sports-Science Readiness verdict combining PMC, ACWR, Sleep, RHR, SpO2, and HRV."""
    ctl: float  # Fitness (42d EWMA)
    atl: float  # Fatigue (7d EWMA)
    tsb: float  # Form (CTL - ATL)
    resting_hr_baseline: Optional[float]
    recent_resting_hr: Optional[float]
    rhr_delta: Optional[float]
    rhr_elevated: bool
    recent_sleep_hours: Optional[float] = None
    sleep_score: Optional[int] = None
    recent_spo2: Optional[float] = None
    recent_hrv: Optional[float] = None
    readiness_state: str = "PRODUCTIVE_MAINTENANCE"  # "OPTIMAL_OVERLOAD", "PRODUCTIVE_MAINTENANCE", "ELEVATED_FATIGUE", "RECOVERY_MANDATORY"
    readiness_score: int = 75  # 0 to 100 composite index
    recommendation: str = ""
    target_next_week_tss: float = 100.0
    target_next_week_hours: float = 8.0
    contributors: Dict[str, Any] = field(default_factory=dict)


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
    daily_series: List[Dict[str, Any]] = field(default_factory=list)

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
            flag = " ELEVATED" if self.readiness.rhr_elevated else " STABLE"
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

        # Extract latest Sleep, SpO2, and HRV
        recent_sleep_hours = None
        sleep_score = None
        recent_spo2 = None
        recent_hrv = None

        if wellness_records:
            # Sort by date
            sorted_w = sorted(wellness_records, key=lambda x: x.get("id", ""))
            for w in reversed(sorted_w):
                if recent_sleep_hours is None and w.get("sleepSecs"):
                    try:
                        s_val = float(w["sleepSecs"]) / 3600.0
                        if s_val > 0:
                            recent_sleep_hours = round(s_val, 1)
                    except (ValueError, TypeError):
                        pass
                if recent_spo2 is None and w.get("spO2"):
                    try:
                        sp_val = float(w["spO2"])
                        if sp_val > 0:
                            recent_spo2 = round(sp_val, 1)
                    except (ValueError, TypeError):
                        pass
                if recent_hrv is None and w.get("hrv"):
                    try:
                        h_val = float(w["hrv"])
                        if h_val > 0:
                            recent_hrv = round(h_val, 1)
                    except (ValueError, TypeError):
                        pass

        # Multi-factor Composite Training Readiness Score (0 - 100)
        # Weights:
        # 1. Performance Form / TSB (30% weight)
        # 2. Acute:Chronic Workload Ratio / ACWR (25% weight)
        # 3. Autonomic Cardiac Strain / RHR & HRV (25% weight)
        # 4. Sleep Recovery & Restoration (20% weight)

        # Component 1: TSB Subscore (0 - 100)
        if tsb >= 5:
            tsb_score = 95
        elif tsb >= 0:
            tsb_score = 85
        elif tsb >= -10:
            tsb_score = 75
        elif tsb >= -20:
            tsb_score = 55
        elif tsb >= -30:
            tsb_score = 35
        else:
            tsb_score = 15

        # Component 2: ACWR Subscore (0 - 100)
        if acwr.status == "SWEET_SPOT":
            acwr_score = 95
        elif acwr.status == "UNDER_TRAINING":
            acwr_score = 75
        elif acwr.status == "ELEVATED_LOAD":
            acwr_score = 50
        else:  # DANGER_ZONE
            acwr_score = 20

        # Component 3: Autonomic Strain Subscore (0 - 100)
        if rhr_delta is not None:
            if rhr_delta <= -2.0:
                autonomic_score = 95  # Positive parasympathetic tone
            elif rhr_delta <= 1.5:
                autonomic_score = 85  # Normal baseline stability
            elif rhr_delta <= 3.9:
                autonomic_score = 65  # Mild elevated strain
            elif rhr_delta <= 6.0:
                autonomic_score = 35  # Moderate sympathetic overdrive
            else:
                autonomic_score = 15  # Severe autonomic fatigue
        else:
            autonomic_score = 75  # Default neutral

        # Component 4: Sleep Restoration Subscore (0 - 100)
        if recent_sleep_hours is not None:
            if recent_sleep_hours >= 7.5:
                sleep_score = 95
            elif recent_sleep_hours >= 6.5:
                sleep_score = 85
            elif recent_sleep_hours >= 5.5:
                sleep_score = 65
            elif recent_sleep_hours >= 4.0:
                sleep_score = 40
            else:
                sleep_score = 20
        else:
            sleep_score = 75

        # Optional SpO2 penalty
        spo2_penalty = 0
        if recent_spo2 is not None and recent_spo2 < 95.0:
            spo2_penalty = 15

        composite_score = (
            0.30 * tsb_score +
            0.25 * acwr_score +
            0.25 * autonomic_score +
            0.20 * sleep_score
        ) - spo2_penalty

        readiness_score = int(max(10, min(100, round(composite_score))))

        # Classify state
        if tsb < -30 or (readiness_score < 65 and tsb < -20):
            if rhr_elevated or acwr.status == "DANGER_ZONE" or readiness_score < 45:
                state = "RECOVERY_MANDATORY"
                rec = "Excessive fatigue or workload spike. Immediate deload required to prevent injury or non-functional overreaching."
                load_multiplier = 0.65
                hour_multiplier = 0.75
            else:
                state = "ELEVATED_FATIGUE"
                rec = "Sympathetic strain, sleep debt, or negative training stress balance observed. Shift high-intensity sessions to Zone 1/2 recovery."
                load_multiplier = 0.85
                hour_multiplier = 0.90
        elif readiness_score >= 80 and not rhr_elevated and acwr.status != "DANGER_ZONE" and tsb >= -15:
            state = "OPTIMAL_OVERLOAD"
            rec = "All biometrics are green (optimal sleep, autonomic stability, balanced workload). Prime window for progressive volume and high-quality interval work."
            load_multiplier = 1.05
            hour_multiplier = 1.0
        elif readiness_score >= 60 and not rhr_elevated and acwr.status != "DANGER_ZONE":
            state = "PRODUCTIVE_MAINTENANCE"
            rec = "Solid physiological state. Execute planned training; maintain conversational pace on easy sessions."
            load_multiplier = 1.00
            hour_multiplier = 1.0
        elif readiness_score < 45 or rhr_elevated or acwr.status == "DANGER_ZONE":
            state = "RECOVERY_MANDATORY"
            rec = "Accumulated physiological fatigue or acute workload spike detected. Immediate deload or active recovery required to prevent injury."
            load_multiplier = 0.65
            hour_multiplier = 0.75
        else:
            state = "ELEVATED_FATIGUE"
            rec = "Sympathetic strain, sleep debt, or negative training stress balance observed. Shift high-intensity sessions to Zone 1/2 recovery."
            load_multiplier = 0.85
            hour_multiplier = 0.90

        # Compute target TSS and hours
        chronic_weekly = max(100.0, ctl * 7.0)
        target_tss = chronic_weekly * load_multiplier
        target_hours = self.target_hours_profile * hour_multiplier

        contributors = {
            "tsb_score": tsb_score,
            "acwr_score": acwr_score,
            "autonomic_score": autonomic_score,
            "sleep_score": sleep_score,
            "spo2_penalty": spo2_penalty,
        }

        return PhysiologicalReadiness(
            ctl=round(ctl, 1),
            atl=round(atl, 1),
            tsb=round(tsb, 1),
            resting_hr_baseline=round(resting_hr_baseline, 1) if resting_hr_baseline else None,
            recent_resting_hr=round(recent_resting_hr, 1) if recent_resting_hr else None,
            rhr_delta=round(rhr_delta, 1) if rhr_delta is not None else None,
            rhr_elevated=rhr_elevated,
            recent_sleep_hours=recent_sleep_hours,
            sleep_score=sleep_score,
            recent_spo2=recent_spo2,
            recent_hrv=recent_hrv,
            readiness_state=state,
            readiness_score=readiness_score,
            recommendation=rec,
            target_next_week_tss=round(target_tss, 0),
            target_next_week_hours=round(target_hours, 1),
            contributors=contributors,
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
        daily_moving_dict: Dict[datetime.date, float] = {}
        daily_sports_dict: Dict[datetime.date, Dict[str, float]] = {}
        curr = start_date
        while curr <= end_date:
            daily_loads_dict[curr] = 0.0
            daily_moving_dict[curr] = 0.0
            daily_sports_dict[curr] = {}
            curr += datetime.timedelta(days=1)

        total_moving_secs = 0.0
        total_load = 0.0

        for a in activities:
            dt_str = a.get("start_date_local", "")
            if dt_str:
                act_date = datetime.date.fromisoformat(dt_str[:10])
                if start_date <= act_date <= end_date:
                    load = float(a.get("icu_training_load") or 0)
                    mtime = float(a.get("moving_time") or 0)
                    daily_loads_dict[act_date] = daily_loads_dict.get(act_date, 0.0) + load
                    daily_moving_dict[act_date] = daily_moving_dict.get(act_date, 0.0) + mtime
                    total_load += load
                    total_moving_secs += mtime

                    raw_type = a.get("type") or "Other"
                    if raw_type in ["Ride", "VirtualRide", "GravelRide", "MountainBikeRide"]:
                        sport = "Ride"
                    elif raw_type in ["Run", "VirtualRun", "TrailRun"]:
                        sport = "Run"
                    elif raw_type in ["Swim", "OpenWaterSwim"]:
                        sport = "Swim"
                    else:
                        sport = "Other"
                    daily_sports_dict[act_date][sport] = daily_sports_dict[act_date].get(sport, 0.0) + load

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

        # Build daily series
        wellness_by_date = {w.get("id"): w for w in wellness_records if w.get("id")}
        initial_ctl = 25.0
        initial_atl = 25.0
        if wellness_records:
            for w in sorted_w:
                if w.get("ctl") is not None:
                    initial_ctl = float(w["ctl"])
                    break
            for w in sorted_w:
                if w.get("atl") is not None:
                    initial_atl = float(w["atl"])
                    break

        curr_ctl = initial_ctl
        curr_atl = initial_atl
        ctl_decay = math.exp(-1.0 / 42.0)
        atl_decay = math.exp(-1.0 / 7.0)

        daily_series: List[Dict[str, Any]] = []
        curr = start_date
        while curr <= end_date:
            iso_d = curr.isoformat()
            w_rec = wellness_by_date.get(iso_d)
            d_load = daily_loads_dict.get(curr, 0.0)
            d_mtime = daily_moving_dict.get(curr, 0.0)

            if w_rec and w_rec.get("ctl") is not None:
                curr_ctl = float(w_rec["ctl"])
            else:
                curr_ctl = curr_ctl * ctl_decay + d_load * (1.0 - ctl_decay)

            if w_rec and w_rec.get("atl") is not None:
                curr_atl = float(w_rec["atl"])
            else:
                curr_atl = curr_atl * atl_decay + d_load * (1.0 - atl_decay)

            rhr_val = None
            if w_rec and w_rec.get("restingHR") is not None:
                try:
                    val = float(w_rec["restingHR"])
                    if val > 30:
                        rhr_val = val
                except (ValueError, TypeError):
                    pass

            sleep_hours = None
            if w_rec and w_rec.get("sleepSecs") is not None:
                try:
                    s_val = float(w_rec["sleepSecs"])
                    if s_val > 0:
                        sleep_hours = round(s_val / 3600.0, 1)
                except (ValueError, TypeError):
                    pass

            hrv_val = None
            if w_rec and w_rec.get("hrv") is not None:
                try:
                    h_val = float(w_rec["hrv"])
                    if h_val > 0:
                        hrv_val = round(h_val, 1)
                except (ValueError, TypeError):
                    pass

            spo2_val = None
            if w_rec and w_rec.get("spO2") is not None:
                try:
                    sp_val = float(w_rec["spO2"])
                    if sp_val > 0:
                        spo2_val = round(sp_val, 1)
                except (ValueError, TypeError):
                    pass

            weight_val = None
            if w_rec and w_rec.get("weight") is not None:
                try:
                    wt_val = float(w_rec["weight"])
                    if wt_val > 0:
                        weight_val = round(wt_val, 1)
                except (ValueError, TypeError):
                    pass

            body_fat_val = None
            if w_rec and w_rec.get("bodyFat") is not None:
                try:
                    bf_val = float(w_rec["bodyFat"])
                    if bf_val > 0:
                        body_fat_val = round(bf_val, 1)
                except (ValueError, TypeError):
                    pass

            # Daily rolling ACWR calculation up to curr
            acute_7d = sum(daily_loads_dict.get(curr - datetime.timedelta(days=d), 0.0) for d in range(7))
            chronic_28d = sum(daily_loads_dict.get(curr - datetime.timedelta(days=d), 0.0) for d in range(28))
            chronic_avg = chronic_28d / 4.0 if chronic_28d > 0 else 0.0
            if chronic_avg > 0:
                d_ratio = round(acute_7d / chronic_avg, 2)
            elif acute_7d > 0:
                d_ratio = 1.5
            else:
                d_ratio = 0.0

            daily_series.append({
                "date": iso_d,
                "ctl": round(curr_ctl, 1),
                "atl": round(curr_atl, 1),
                "tsb": round(curr_ctl - curr_atl, 1),
                "load_tss": round(d_load, 1),
                "moving_hours": round(d_mtime / 3600.0, 2),
                "resting_hr": rhr_val,
                "sleep_hours": sleep_hours,
                "hrv": hrv_val,
                "spo2": spo2_val,
                "weight": weight_val,
                "body_fat": body_fat_val,
                "acwr_ratio": d_ratio,
                "sleep_note": w_rec.get("comments") if w_rec else None,
                "sports": {k: round(v, 1) for k, v in daily_sports_dict.get(curr, {}).items()},
            })
            curr += datetime.timedelta(days=1)

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
            daily_series=daily_series,
        )

