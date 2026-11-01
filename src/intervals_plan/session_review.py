"""
Post-Workout Session Review & Debrief Engine:
Provides deep qualitative and biometric debriefs for completed workouts.
Analyzes Rate of Perceived Exertion (RPE), cardiac drift / aerobic decoupling (Pw:HR, Pa:HR),
intensity discipline, and provides next-day recovery adjustments.
Inspired by Joe Friel aerobic decoupling and sports psychology feedback models.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionReviewInput:
    """Athlete submission for a post-workout review."""

    activity_name: str
    sport: str  # 'Run', 'Ride', 'Swim', 'Brick'
    duration_minutes: int
    rpe: int  # 1 to 10 (Borg CR10 Scale)
    feeling: str  # 'strong', 'normal', 'heavy_legs', 'exhausted', 'pain_or_niggle'
    avg_hr: Optional[int] = None
    max_hr: Optional[int] = None
    target_hr_min: Optional[int] = None
    target_hr_max: Optional[int] = None
    decoupling_pct: Optional[float] = None  # Pw:HR or Pa:HR % drift
    notes: str = ""


@dataclass
class SessionReviewResult:
    """Synthesized coaching debrief for a completed workout."""

    activity_name: str
    sport: str
    duration_minutes: int
    rpe: int
    execution_score: int  # 0 to 100
    intensity_discipline: str  # 'ON_TARGET', 'DISCIPLINED_EASY', 'OVER_EXERTED', 'UNDER_EXERTED'
    aerobic_efficiency: str  # 'EFFICIENT', 'CARDIO_DRIFT_ELEVATED', 'UNRATED'
    next_day_recommendation: str
    fueling_critique: str
    coaching_feedback: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SessionReviewer:
    """Evaluates completed sessions and generates coaching debriefs."""

    def review(self, inp: SessionReviewInput) -> SessionReviewResult:
        score = 85
        feedback: List[str] = []

        # 1. Evaluate Intensity Discipline & Heart Rate
        is_easy_session = "easy" in inp.activity_name.lower() or "recovery" in inp.activity_name.lower() or "zone 2" in inp.activity_name.lower()
        is_hard_session = "interval" in inp.activity_name.lower() or "quality" in inp.activity_name.lower() or "vo2" in inp.activity_name.lower() or "tempo" in inp.activity_name.lower()

        if is_easy_session:
            if inp.rpe > 5 or (inp.avg_hr and inp.target_hr_max and inp.avg_hr > inp.target_hr_max + 4):
                discipline = "OVER_EXERTED"
                score -= 20
                feedback.append(
                    f"RPE of {inp.rpe}/10 is too high for an aerobic/recovery session. "
                    "Stephen Seiler's 80/20 model dictates keeping easy days truly easy to avoid systemic autonomic fatigue."
                )
            else:
                discipline = "DISCIPLINED_EASY"
                score += 10
                feedback.append("Excellent intensity discipline: kept heart rate and effort strictly within base aerobic bounds.")
        elif is_hard_session:
            if inp.rpe >= 7:
                discipline = "ON_TARGET"
                score += 10
                feedback.append(f"Strong mental focus and target execution (RPE {inp.rpe}/10). Lactate clearance achieved.")
            else:
                discipline = "UNDER_EXERTED"
                score -= 10
                feedback.append(f"Reported RPE {inp.rpe}/10 is below intended quality threshold. If fatigue prevented high effort, log as recovery.")
        else:
            discipline = "ON_TARGET"

        # 2. Aerobic Decoupling / Cardiac Drift
        if inp.decoupling_pct is not None:
            if inp.decoupling_pct <= 5.0:
                aerobic_eff = "EFFICIENT"
                feedback.append(
                    f"Aerobic Decoupling is {inp.decoupling_pct:.1f}% (< 5.0% threshold). "
                    "Outstanding mitochondrial efficiency and capillary density; minimal cardiac drift."
                )
            else:
                aerobic_eff = "CARDIO_DRIFT_ELEVATED"
                score -= 10
                feedback.append(
                    f"Aerobic Decoupling is elevated at {inp.decoupling_pct:.1f}% (> 5.0%). "
                    "Cardiac drift indicates fatigue, muscle glycogen depletion, or progressive dehydration."
                )
        else:
            aerobic_eff = "UNRATED"

        # 3. Subjective Feeling & Next-Day Prescription
        feeling_norm = inp.feeling.lower()
        if feeling_norm == "pain_or_niggle":
            score = min(score, 60)
            next_day = "MANDATORY REST / PHYSIOTHERAPY: Pain or acute niggle flagged. Do not run or stress affected tendons tomorrow."
            feedback.append("Immediate stop: Consult physical therapist or cross-train gently in non-impact pool swimming.")
        elif feeling_norm == "exhausted" or inp.rpe >= 9:
            score = max(50, score - 15)
            next_day = "ACTIVE RECOVERY: 30-min gentle spin or rest. Downshift any planned high-intensity intervals tomorrow."
            feedback.append("Central nervous system fatigue detected. Prioritize 8+ hours of sleep and high-glycemic carbohydrates.")
        elif feeling_norm == "heavy_legs":
            next_day = "EASY BASE: Stick to Zone 1/2 conversational pacing. Postpone intervals if heavy legs persist."
            feedback.append("Muscular fatigue present. Perform foam rolling and elevate legs.")
        else:
            next_day = "EXECUTE AS PLANNED: Green light for tomorrow's scheduled session."
            feedback.append("Physiological readiness maintained. Ready for subsequent training stimuli.")

        # 4. Fueling Critique
        if inp.duration_minutes >= 90:
            fuel_critique = (
                f"For this {inp.duration_minutes}-minute effort, ensure you replenished with 1.0-1.2g carbohydrate "
                "per kg body weight within 45 minutes of completion, along with 25-30g protein for muscle protein synthesis."
            )
        else:
            fuel_critique = "Standard recovery meal with balanced protein (20-25g) and complex carbohydrates."

        final_score = max(40, min(100, score))

        return SessionReviewResult(
            activity_name=inp.activity_name,
            sport=inp.sport,
            duration_minutes=inp.duration_minutes,
            rpe=inp.rpe,
            execution_score=final_score,
            intensity_discipline=discipline,
            aerobic_efficiency=aerobic_eff,
            next_day_recommendation=next_day,
            fueling_critique=fuel_critique,
            coaching_feedback=feedback,
        )
