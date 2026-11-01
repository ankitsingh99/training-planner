"""
Intelligent Coaching Advisor:
Synthesizes sports-science telemetry (ACWR, PMC, HRV/RHR autonomic status),
target event goals, periodization phase, and life constraints into actionable,
personalized training guidance.
"""

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional

from intervals_plan.analytics import RollingAnalysisReport
from intervals_plan.athlete_profile import AthleteProfileConfig


@dataclass
class CoachingAdvice:
    """Holistic coaching guidance for the athlete's upcoming microcycle."""
    headline: str
    periodization_phase: str
    weeks_to_event: Optional[int]
    readiness_state: str
    readiness_score: int
    training_focus: str
    key_recommendations: List[str]
    alerts: List[str]
    target_weekly_hours: float
    target_weekly_tss: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_lines(self) -> List[str]:
        lines = []
        lines.append("=" * 64)
        lines.append("  ADAPTPULSE COACHING BRIEFING & PERIODIZATION GUIDANCE")
        lines.append("=" * 64)
        lines.append(f"Status: {self.headline}")
        lines.append(f"Phase:  {self.periodization_phase.upper()} ({self.weeks_to_event} weeks to target)" if self.weeks_to_event is not None else f"Phase:  {self.periodization_phase.upper()}")
        lines.append(f"Readiness: {self.readiness_state} (Score: {self.readiness_score}/100)")
        lines.append(f"Budget:    {self.target_weekly_hours:.1f} Hours / ~{self.target_weekly_tss:.0f} TSS")
        
        lines.append("\n[TRAINING FOCUS]")
        lines.append(f"  {self.training_focus}")

        if self.alerts:
            lines.append("\n[SAFETY & BIOMETRIC ALERTS]")
            for alert in self.alerts:
                lines.append(f"  - {alert}")

        lines.append("\n[ACTIONABLE COACHING RECOMMENDATIONS]")
        for rec in self.key_recommendations:
            lines.append(f"  * {rec}")
        lines.append("=" * 64)
        return lines


class CoachingAdvisor:
    """Evaluates telemetry, profiles, and goals to produce high-value coaching advice."""

    def __init__(self, profile: AthleteProfileConfig):
        self.profile = profile

    def advise(
        self,
        report: RollingAnalysisReport,
        current_date: Optional[datetime.date] = None,
    ) -> CoachingAdvice:
        """Generate structured coaching advice."""
        today = current_date or datetime.date.today()
        phase, weeks_out = self.profile.get_periodization_phase(today)
        readiness = report.readiness
        acwr = report.acwr
        alerts: List[str] = []
        recommendations: List[str] = []

        # 1. Biometric Alerts
        if readiness.rhr_elevated:
            delta_val = f"+{readiness.rhr_delta:.1f}" if readiness.rhr_delta and readiness.rhr_delta > 0 else "elevated"
            alerts.append(f"Elevated Resting HR ({delta_val} bpm vs 30d baseline). Sympathetic stress detected; substitute high-intensity intervals with recovery spins.")
        elif readiness.recent_resting_hr and readiness.resting_hr_baseline:
            alerts.append(f"Resting HR stable at {readiness.recent_resting_hr:.0f} bpm (30d baseline: {readiness.resting_hr_baseline:.0f} bpm). Parasympathetic balance healthy.")

        if acwr.status == "DANGER_ZONE":
            alerts.append(f"ACWR Acute Spike Alert ({acwr.ratio:.2f} > 1.50). High risk of non-contact soft-tissue injury. Force volume reduction.")
        elif acwr.status == "UNDER_TRAINING":
            alerts.append(f"ACWR Under-Training ({acwr.ratio:.2f} < 0.80). Chronic training stimulus declining; maintain consistent aerobic base frequency.")
        else:
            alerts.append(f"ACWR in Optimal Sweet Spot ({acwr.ratio:.2f}). Safe progressive overload achievable.")

        # Check user constraints
        if self.profile.constraints:
            for c in self.profile.constraints:
                alerts.append(f"Constraint Active: {c.replace('_', ' ').capitalize()}")

        # 2. Phase-Specific Focus and Recommendations
        if phase == "taper":
            headline = "Taper & Sharpening: Shed Fatigue While Preserving Neuromuscular Pop"
            focus = (
                f"Tapering for {self.profile.target_event_name or 'Target Event'} ({weeks_out} week(s) out). "
                "Reduce total volume by 40-50%, preserve interval intensity with short bursts (30s-60s), "
                "and maximize sleep bank and carbohydrate glycogen storage."
            )
            recommendations.append("Do not attempt to 'bank fitness' in the final 14 days. Fitness is already earned.")
            recommendations.append("Prioritize 8.5+ hours of sleep per night and high-glycemic carbohydrates post-workout.")
            recommendations.append("Keep stride cadence crisp and execute race-pace drills without accumulating lactate.")

        elif phase == "peak":
            headline = "Peak Phase: High-Specificity Race Pace Simulations"
            focus = (
                f"Peak specificity for {self.profile.target_event_name or 'Target Event'} ({weeks_out} weeks out). "
                "Simulate exact race conditions, nutrition timing, and sustained race-pace efforts."
            )
            recommendations.append("Practice race-morning breakfast timing and on-bike/on-run fueling at target effort.")
            recommendations.append("Focus Tuesday quality on specific race-pace segments with complete aerobic recoveries.")
            recommendations.append("Inspect equipment, shoes, and bike tires this week to avoid race-week surprises.")

        elif phase == "build":
            headline = "Build Phase: Threshold Expansion & VO2max Power Development"
            focus = (
                "Progressive overload targeting lactate threshold expansion, VO2max velocity, "
                "and sustained aerobic resistance."
            )
            recommendations.append("Ensure Tuesday quality intervals reach Zone 4-5 without compromising interval 4 and 5 execution.")
            recommendations.append("Keep Wednesday and Sunday long aerobic sessions strictly below 75% LTHR (Zone 2).")
            recommendations.append("Fuel all workouts lasting longer than 60 minutes with 45-60g carbs per hour.")

        elif phase == "base":
            headline = "Base Foundation: Building Mitochondrial Density & Capillarization"
            focus = (
                "Aerobic volume accumulation adhering to Seiler 80/20 polarization. "
                "Strengthen tendons, ligaments, and fat-oxidation metabolism."
            )
            recommendations.append("Commit 80%+ of weekly volume to conversational Zone 1-2 aerobic base.")
            recommendations.append("Perform 4-6 strides or short 20s spin-ups at the end of easy sessions to preserve leg turnover.")
            recommendations.append("Integrate 2x weekly mobility and strength routines (core, glutes, calf resilience).")

        else:
            headline = f"Balanced Training: {readiness.readiness_state.replace('_', ' ').title()}"
            focus = (
                "Sustaining fitness and maintaining dual-sport aerobic engine with dynamic weekly adjustments."
            )
            recommendations.append("Listen to morning resting HR and subjective fatigue before deciding interval depth.")
            recommendations.append("Keep the weekend long ride aerobic and sociable; avoid uncontrolled group surges if fatigue is elevated.")

        # Autonomic adjustments
        if readiness.rhr_elevated or readiness.readiness_state in ["ELEVATED_FATIGUE", "RECOVERY_MANDATORY"]:
            headline = "Recovery Intervention: Sympathetic Strain Detected"
            recommendations.insert(0, "Downshift today's planned intensity: switch to easy Zone 1 spin or take full rest.")

        return CoachingAdvice(
            headline=headline,
            periodization_phase=phase,
            weeks_to_event=weeks_out,
            readiness_state=readiness.readiness_state,
            readiness_score=readiness.readiness_score,
            training_focus=focus,
            key_recommendations=recommendations,
            alerts=alerts,
            target_weekly_hours=readiness.target_next_week_hours,
            target_weekly_tss=readiness.target_next_week_tss,
        )
