"""
Sports Science Nutrition & Intra-Workout Fueling Calculator:
Calculates carbohydrate, hydration, and electrolyte targets for running,
cycling, swimming, and multisport brick sessions based on duration and intensity.
References Asker Jeukendrup carbohydrate intake guidelines and ACSM fluid replacement standards.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class FuelingRecommendation:
    """Nutritional and hydration prescription for an endurance training session."""

    duration_minutes: int
    sport: str
    intensity: str
    carbs_per_hour_g: int
    total_carbs_g: int
    hydration_ml_per_hour: int
    total_hydration_ml: int
    sodium_mg_per_hour: int
    total_sodium_mg: int
    strategy_summary: str
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def calculate_fueling(
    duration_minutes: int,
    sport: str = "Run",
    intensity: str = "moderate",
) -> FuelingRecommendation:
    """
    Calculate evidence-based intra-workout fueling requirements.

    Parameters:
        duration_minutes: Session length in minutes.
        sport: Discipline ('Run', 'Ride', 'Swim', 'Brick', 'Strength', 'Other').
        intensity: 'low' (Zone 1/2), 'moderate' (Zone 3 tempo), or 'high' (Zone 4/5 VO2max).
    """
    sport_normalized = sport.strip().capitalize()
    intensity_normalized = intensity.strip().lower()
    dur_hours = duration_minutes / 60.0

    if duration_minutes < 45:
        # Short sessions: no exogeneous carbohydrate needed
        carbs_hr = 0
        hydro_hr = 300 if intensity_normalized != "low" else 200
        sodium_hr = 0
        summary = "Hydration only: No carbohydrate supplementation required for sessions under 45 minutes."
        recs = [
            "Start session well-hydrated with 300-500 mL water 1-2 hours prior.",
            "Sip water as needed to alleviate thirst.",
            "Optional carbohydrate mouth rinse during high-intensity track/sprint reps.",
        ]

    elif duration_minutes <= 75:
        # 45 to 75 minutes: small amounts or mouth rinse
        if intensity_normalized == "high":
            carbs_hr = 30
            hydro_hr = 500
            sodium_hr = 300
            summary = "Target 30g carbs/hour for high-intensity efforts (single gel or isotonic sports drink)."
            recs = [
                "Consume 1 energy gel or 500 mL isotonic drink at the 30-minute mark.",
                "Maintain fluid intake of 400-500 mL to prevent dehydration.",
            ]
        else:
            carbs_hr = 15 if intensity_normalized == "moderate" else 0
            hydro_hr = 450
            sodium_hr = 200 if carbs_hr > 0 else 0
            summary = "Minimal carbohydrate needed; focus on fluid maintenance and electrolyte balance."
            recs = [
                "Drink 400-500 mL water or light electrolyte mix.",
                "Carbohydrate optional unless training in a fasted state.",
            ]

    elif duration_minutes <= 150:
        # 75 to 150 minutes: 45-75g carbs/hour
        if sport_normalized in ["Ride", "Cycling", "Bike"]:
            carbs_hr = 60 if intensity_normalized != "high" else 75
            hydro_hr = 650
            sodium_hr = 500
            summary = f"Cycling fueling: {carbs_hr}g carbs/hour via liquid mix, chews, or gels."
            recs = [
                "Aim for 1 bottle (600-750 mL) sports drink per hour with 40-50g carbs.",
                "Supplement with 1 energy chew or gel every 45 minutes.",
                "Consume 500 mg sodium per hour to prevent hyponatremia and cramps.",
            ]
        elif sport_normalized in ["Run", "Running"]:
            carbs_hr = 45 if intensity_normalized == "low" else 60
            hydro_hr = 550
            sodium_hr = 450
            summary = f"Running fueling: {carbs_hr}g carbs/hour with careful gastric tolerance pacing."
            recs = [
                "Take 1 isotonic gel (20-25g carbs) every 25-30 minutes with water.",
                "Avoid high-fiber, high-fat, or concentrated solids while running.",
                "Target 500-600 mL fluids per hour; adjust upward in hot conditions.",
            ]
        elif sport_normalized in ["Brick", "Multisport"]:
            carbs_hr = 65
            hydro_hr = 650
            sodium_hr = 550
            summary = "Brick transition fueling: 70g carbs/hr on bike; shift to gels/fluids on transition run."
            recs = [
                "Front-load nutrition on the bike leg where digestion is easiest.",
                "Take a gel with 150 mL water 10 minutes before transitioning to the run.",
                "Practice race-day gut comfort under elevated heart rate.",
            ]
        else:  # Swim or other
            carbs_hr = 40
            hydro_hr = 500
            sodium_hr = 350
            summary = "Poolside hydration bottle with carbohydrate-electrolyte mix between interval sets."
            recs = [
                "Keep a bottle at the pool edge; sip 100-150 mL every 1,000 meters or during rest intervals.",
                "Electrolytes help prevent calf and arch cramps in chlorinated water.",
            ]

    else:
        # Over 150 minutes (Long endurance, 70.3 / Ironman simulation)
        if sport_normalized in ["Ride", "Cycling", "Bike"]:
            carbs_hr = 80 if intensity_normalized != "high" else 90
            hydro_hr = 750
            sodium_hr = 700
            summary = f"Ultra-endurance cycling: {carbs_hr}g carbs/hour (multiple transportable carbs, 2:1 glucose:fructose)."
            recs = [
                "Utilize dual-source carbohydrates (maltodextrin + fructose 2:1 or 1:0.8) for maximum gut absorption.",
                "Target 700-800 mL fluids per hour containing 600-800 mg sodium.",
                "Alternate between liquid fuel, gels, and solid ride snacks (rice cakes, stroopwafels) in early hours.",
            ]
        elif sport_normalized in ["Run", "Running"]:
            carbs_hr = 60
            hydro_hr = 650
            sodium_hr = 600
            summary = "Long run fueling: 60g carbs/hour; practice race-day gel and electrolyte schedule."
            recs = [
                "Standardize on 2-3 gels per hour washed down with plain water from handheld or hydration vest.",
                "Do not drink carbohydrate drink simultaneously with concentrated gels to avoid hypertonic GI distress.",
                "Electrolyte salt caps recommended if running in temperature > 24 C (75 F).",
            ]
        elif sport_normalized in ["Brick", "Multisport"]:
            carbs_hr = 75
            hydro_hr = 700
            sodium_hr = 650
            summary = "Long brick simulation: 80g/hr on bike downshifted to 50g/hr on run."
            recs = [
                "Complete the bike leg fully hydrated and carb-saturated.",
                "Downshift carb intake in the final 15 minutes of the bike to let stomach settle.",
                "Rely on easily absorbed isotonic gels during the transition run.",
            ]
        else:
            carbs_hr = 50
            hydro_hr = 600
            sodium_hr = 500
            summary = "Sustained fueling protocol: 50g carbs/hour with balanced electrolyte replacement."
            recs = [
                "Maintain steady intake at 20-minute intervals.",
                "Monitor urine color post-workout; pale straw indicates adequate hydration.",
            ]

    total_carbs = int(round(carbs_hr * dur_hours))
    total_hydro = int(round(hydro_hr * dur_hours))
    total_sodium = int(round(sodium_hr * dur_hours))

    return FuelingRecommendation(
        duration_minutes=duration_minutes,
        sport=sport_normalized,
        intensity=intensity_normalized,
        carbs_per_hour_g=carbs_hr,
        total_carbs_g=total_carbs,
        hydration_ml_per_hour=hydro_hr,
        total_hydration_ml=total_hydro,
        sodium_mg_per_hour=sodium_hr,
        total_sodium_mg=total_sodium,
        strategy_summary=summary,
        recommendations=recs,
    )
