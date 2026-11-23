"""
Strength Training & Hypertrophy Engine for Concurrent / Hybrid Athletes.
Implements:
  - Renaissance Periodization (RP / Dr. Mike Israetel) volume landmarks (MEV, MAV, MRV).
  - Strava / Intervals.icu gym workout & weight training activity parser.
  - Anatomical muscle group volume tracking and fatigue recovery modeling.
  - Molecular interference auditor (AMPK vs mTORC1 separation rules).
  - 6-Day Push / Pull / Legs personalized hybrid bodybuilding program generator.
"""

from dataclasses import dataclass, field
import datetime
import math
import re
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class VolumeLandmark:
    """Hypertrophy volume landmarks (weekly direct working sets)."""

    mv: int   # Maintenance Volume
    mev: int  # Minimum Effective Volume
    mav: int  # Maximum Adaptive Volume (target midpoint)
    mrv: int  # Maximum Recoverable Volume


# Empirical baseline volume landmarks for intermediate lifters (RP / Helms / Schoenfeld)
DEFAULT_VOLUME_LANDMARKS: Dict[str, VolumeLandmark] = {
    "chest": VolumeLandmark(mv=4, mev=8, mav=14, mrv=22),
    "lats": VolumeLandmark(mv=4, mev=10, mav=16, mrv=24),
    "upper_back": VolumeLandmark(mv=4, mev=8, mav=14, mrv=22),
    "shoulders_side": VolumeLandmark(mv=6, mev=10, mav=18, mrv=26),
    "shoulders_rear": VolumeLandmark(mv=4, mev=8, mav=14, mrv=22),
    "shoulders_front": VolumeLandmark(mv=0, mev=4, mav=8, mrv=14),
    "biceps": VolumeLandmark(mv=4, mev=8, mav=14, mrv=20),
    "triceps": VolumeLandmark(mv=4, mev=8, mav=14, mrv=20),
    "quads": VolumeLandmark(mv=4, mev=8, mav=14, mrv=20),
    "hamstrings": VolumeLandmark(mv=3, mev=6, mav=12, mrv=18),
    "glutes": VolumeLandmark(mv=2, mev=4, mav=12, mrv=18),
    "calves": VolumeLandmark(mv=4, mev=8, mav=14, mrv=22),
    "abs": VolumeLandmark(mv=2, mev=6, mav=12, mrv=20),
}

MUSCLE_DISPLAY_NAMES: Dict[str, str] = {
    "chest": "Pectoralis Major & Minor",
    "lats": "Latissimus Dorsi",
    "upper_back": "Traps & Rhomboids",
    "shoulders_side": "Lateral Deltoids",
    "shoulders_rear": "Posterior Deltoids",
    "shoulders_front": "Anterior Deltoids",
    "biceps": "Biceps Brachii & Brachialis",
    "triceps": "Triceps Brachii",
    "quads": "Quadriceps Femoris",
    "hamstrings": "Hamstrings (Biceps Femoris)",
    "glutes": "Gluteus Maximus & Medius",
    "calves": "Gastrocnemius & Soleus",
    "abs": "Rectus Abdominis & Core",
}

# Exercise to muscle group mapping dictionary
EXERCISE_MUSCLE_MAPPING: Dict[str, List[Tuple[str, float]]] = {
    # Chest
    "bench press": [("chest", 1.0), ("triceps", 0.5), ("shoulders_front", 0.5)],
    "incline bench": [("chest", 1.0), ("shoulders_front", 0.75), ("triceps", 0.5)],
    "dumbbell press": [("chest", 1.0), ("triceps", 0.5), ("shoulders_front", 0.5)],
    "incline dumbbell": [("chest", 1.0), ("shoulders_front", 0.75), ("triceps", 0.5)],
    "cable fly": [("chest", 1.0)],
    "pec deck": [("chest", 1.0)],
    "chest dip": [("chest", 0.75), ("triceps", 0.75), ("shoulders_front", 0.5)],
    "pushup": [("chest", 0.75), ("triceps", 0.5)],

    # Back
    "pullup": [("lats", 1.0), ("upper_back", 0.5), ("biceps", 0.5)],
    "chinup": [("lats", 1.0), ("biceps", 0.75)],
    "lat pulldown": [("lats", 1.0), ("biceps", 0.5)],
    "barbell row": [("upper_back", 1.0), ("lats", 0.75), ("biceps", 0.5)],
    "cable row": [("upper_back", 1.0), ("lats", 0.75), ("biceps", 0.5)],
    "dumbbell row": [("lats", 1.0), ("upper_back", 0.75), ("biceps", 0.5)],
    "face pull": [("shoulders_rear", 1.0), ("upper_back", 0.75)],
    "shrug": [("upper_back", 1.0)],

    # Shoulders
    "overhead press": [("shoulders_front", 1.0), ("triceps", 0.5), ("shoulders_side", 0.5)],
    "military press": [("shoulders_front", 1.0), ("triceps", 0.5), ("shoulders_side", 0.5)],
    "lateral raise": [("shoulders_side", 1.0)],
    "cable lateral raise": [("shoulders_side", 1.0)],
    "reverse fly": [("shoulders_rear", 1.0), ("upper_back", 0.5)],

    # Arms
    "barbell curl": [("biceps", 1.0)],
    "dumbbell curl": [("biceps", 1.0)],
    "hammer curl": [("biceps", 1.0)],
    "preacher curl": [("biceps", 1.0)],
    "tricep pushdown": [("triceps", 1.0)],
    "skull crusher": [("triceps", 1.0)],
    "overhead tricep": [("triceps", 1.0)],

    # Legs
    "barbell squat": [("quads", 1.0), ("glutes", 0.75)],
    "front squat": [("quads", 1.0), ("glutes", 0.5)],
    "leg press": [("quads", 1.0), ("glutes", 0.5)],
    "hack squat": [("quads", 1.0), ("glutes", 0.5)],
    "leg extension": [("quads", 1.0)],
    "romanian deadlift": [("hamstrings", 1.0), ("glutes", 0.75), ("upper_back", 0.5)],
    "rdl": [("hamstrings", 1.0), ("glutes", 0.75), ("upper_back", 0.5)],
    "deadlift": [("hamstrings", 0.75), ("glutes", 0.75), ("upper_back", 0.75), ("quads", 0.5)],
    "leg curl": [("hamstrings", 1.0)],
    "seated leg curl": [("hamstrings", 1.0)],
    "bulgarian split squat": [("quads", 1.0), ("glutes", 0.75)],
    "hip thrust": [("glutes", 1.0), ("hamstrings", 0.5)],
    "standing calf raise": [("calves", 1.0)],
    "seated calf raise": [("calves", 1.0)],

    # Core
    "hanging leg raise": [("abs", 1.0)],
    "cable crunch": [("abs", 1.0)],
    "plank": [("abs", 1.0)],
    "ab rollout": [("abs", 1.0)],
}


@dataclass
class MuscleGroupStatus:
    """Detailed telemetry and volume tracking for an individual muscle group."""

    name: str
    display_name: str
    weekly_sets: float
    mv: int
    mev: int
    mav: int
    mrv: int
    landmark_state: str  # BELOW_MEV, OPTIMAL_MAV, NEAR_MRV, OVER_MRV
    recovery_pct: int    # 0 to 100
    hours_since_trained: Optional[float] = None
    last_trained_date: Optional[str] = None
    interference_risk: str = "NONE"  # NONE, LOW, MODERATE, HIGH
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "weekly_sets": round(self.weekly_sets, 1),
            "mv": self.mv,
            "mev": self.mev,
            "mav": self.mav,
            "mrv": self.mrv,
            "landmark_state": self.landmark_state,
            "recovery_pct": self.recovery_pct,
            "hours_since_trained": round(self.hours_since_trained, 1) if self.hours_since_trained is not None else None,
            "last_trained_date": self.last_trained_date,
            "interference_risk": self.interference_risk,
            "notes": self.notes,
        }


class StravaGymWorkoutParser:
    """
    Parses Strava / Intervals.icu gym activities (WeightTraining, Workout)
    extracting exercises, working sets, and muscle group volume.
    """

    @classmethod
    def parse_activity(cls, activity: Dict[str, Any]) -> Dict[str, float]:
        """
        Parses an activity dict, returning a map of muscle_group -> estimated sets.
        Supports:
          1. Explicit exercise names and sets in description / notes (Hevy, Strong, text).
          2. Title-based heuristic allocation (Push, Pull, Legs, Upper, Lower, Chest, etc.).
          3. Duration-based set scaling if sets are not itemized.
        """
        name = str(activity.get("name", "")).lower()
        desc = str(activity.get("description", "")).lower()
        moving_secs = float(activity.get("moving_time", 0) or activity.get("elapsed_time", 0))

        muscle_sets: Dict[str, float] = {m: 0.0 for m in DEFAULT_VOLUME_LANDMARKS}
        combined_text = f"{name}\n{desc}"

        # 1. Search for explicit exercise matches in description
        explicit_matches = 0
        for ex_pattern, targets in EXERCISE_MUSCLE_MAPPING.items():
            if ex_pattern in combined_text:
                # Try to extract set count near exercise (e.g., '4x10', '4 sets', '3 * 8')
                sets_match = re.search(rf"{ex_pattern}.*?(\d+)\s*(?:x|\*|sets)", combined_text)
                sets = int(sets_match.group(1)) if sets_match and int(sets_match.group(1)) <= 10 else 3
                for muscle, weight in targets:
                    muscle_sets[muscle] += sets * weight
                explicit_matches += 1

        if explicit_matches > 0:
            return {k: v for k, v in muscle_sets.items() if v > 0}

        # 2. Heuristic allocation based on workout split name
        estimated_total_sets = max(10, min(24, int(moving_secs / 180))) if moving_secs > 0 else 18

        if any(w in name for w in ["push", "chest", "bench", "press"]):
            # Push Day: Chest, Shoulders (front/side), Triceps
            muscle_sets["chest"] += estimated_total_sets * 0.45
            muscle_sets["shoulders_side"] += estimated_total_sets * 0.25
            muscle_sets["triceps"] += estimated_total_sets * 0.20
            muscle_sets["shoulders_front"] += estimated_total_sets * 0.10

        elif any(w in name for w in ["pull", "back", "lat", "row", "bicep"]):
            # Pull Day: Lats, Upper Back, Rear Delts, Biceps
            muscle_sets["lats"] += estimated_total_sets * 0.35
            muscle_sets["upper_back"] += estimated_total_sets * 0.30
            muscle_sets["biceps"] += estimated_total_sets * 0.25
            muscle_sets["shoulders_rear"] += estimated_total_sets * 0.10

        elif any(w in name for w in ["leg", "squat", "lower", "quad", "hamstring"]):
            # Leg Day: Quads, Hamstrings, Glutes, Calves
            muscle_sets["quads"] += estimated_total_sets * 0.40
            muscle_sets["hamstrings"] += estimated_total_sets * 0.30
            muscle_sets["glutes"] += estimated_total_sets * 0.20
            muscle_sets["calves"] += estimated_total_sets * 0.10

        elif any(w in name for w in ["upper"]):
            # Upper Body Day
            muscle_sets["chest"] += estimated_total_sets * 0.25
            muscle_sets["lats"] += estimated_total_sets * 0.25
            muscle_sets["upper_back"] += estimated_total_sets * 0.20
            muscle_sets["shoulders_side"] += estimated_total_sets * 0.15
            muscle_sets["biceps"] += estimated_total_sets * 0.08
            muscle_sets["triceps"] += estimated_total_sets * 0.07

        elif any(w in name for w in ["arm", "shoulder", "delt"]):
            muscle_sets["shoulders_side"] += estimated_total_sets * 0.35
            muscle_sets["biceps"] += estimated_total_sets * 0.35
            muscle_sets["triceps"] += estimated_total_sets * 0.30

        else:
            # General full body gym session
            muscle_sets["chest"] += estimated_total_sets * 0.18
            muscle_sets["lats"] += estimated_total_sets * 0.18
            muscle_sets["quads"] += estimated_total_sets * 0.20
            muscle_sets["hamstrings"] += estimated_total_sets * 0.14
            muscle_sets["upper_back"] += estimated_total_sets * 0.12
            muscle_sets["shoulders_side"] += estimated_total_sets * 0.10
            muscle_sets["biceps"] += estimated_total_sets * 0.04
            muscle_sets["triceps"] += estimated_total_sets * 0.04

        return {k: v for k, v in muscle_sets.items() if v > 0}


class StrengthEngine:
    """
    Coordinates hypertrophy volume tracking, muscle map synthesis,
    and concurrent endurance-interference auditing.
    """

    def __init__(self, volume_landmarks: Optional[Dict[str, VolumeLandmark]] = None):
        self.landmarks = volume_landmarks or DEFAULT_VOLUME_LANDMARKS

    def evaluate_muscle_map(
        self,
        activities: List[Dict[str, Any]],
        now_dt: Optional[datetime.datetime] = None,
    ) -> Dict[str, Any]:
        """
        Aggregates past 7-day and 30-day activities to compute:
          - Weekly sets per muscle group.
          - Hypertrophy landmark classification (Below MEV, Optimal MAV, Near MRV, Over MRV).
          - Hours since last trained and recovery percentage (0-100%).
          - Concurrent interference risk with endurance training.
        """
        now = now_dt or datetime.datetime.now(datetime.timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=datetime.timezone.utc)
        seven_days_ago = now - datetime.timedelta(days=7)

        weekly_sets: Dict[str, float] = {m: 0.0 for m in self.landmarks}
        last_trained_dt: Dict[str, datetime.datetime] = {}
        last_trained_sets: Dict[str, float] = {}

        gym_activities: List[Dict[str, Any]] = []
        endurance_leg_activities: List[Dict[str, Any]] = []

        # Partition activities
        for act in activities:
            sport = act.get("type", "")
            raw_start = act.get("start_date_local") or act.get("start_date")
            act_dt = None
            if raw_start:
                try:
                    s_str = str(raw_start).replace("Z", "+00:00")
                    act_dt = datetime.datetime.fromisoformat(s_str)
                    if act_dt.tzinfo is None:
                        act_dt = act_dt.replace(tzinfo=datetime.timezone.utc)
                except Exception:
                    act_dt = None

            if sport in ["WeightTraining", "Gym", "StrengthTraining", "WeightLifting", "Workout"]:
                gym_activities.append(act)
                parsed = StravaGymWorkoutParser.parse_activity(act)

                # Check if in 7-day rolling window
                if act_dt and act_dt >= seven_days_ago:
                    for m, sets in parsed.items():
                        weekly_sets[m] += sets

                # Track most recent training date per muscle
                if act_dt:
                    for m, sets in parsed.items():
                        if sets > 0 and (m not in last_trained_dt or act_dt > last_trained_dt[m]):
                            last_trained_dt[m] = act_dt
                            last_trained_sets[m] = sets

            elif sport in ["Run", "Ride"]:
                # High-load endurance activity targeting quads/hamstrings/calves
                load_val = float(act.get("icu_training_load") or 0)
                mtime_val = float(act.get("moving_time") or 0)
                if load_val >= 40 or mtime_val >= 2700:
                    endurance_leg_activities.append(act)

        # Build MuscleGroupStatus models
        muscle_statuses: Dict[str, MuscleGroupStatus] = {}

        for m, lm in self.landmarks.items():
            sets = weekly_sets.get(m, 0.0)

            # Landmark state classification
            if sets < lm.mev:
                state = "BELOW_MEV"
                notes = f"Under-stimulated ({sets:.1f} / {lm.mev} sets MEV). Maintenance or detraining."
            elif sets <= lm.mav:
                state = "OPTIMAL_MAV"
                notes = f"Optimal hypertrophy stimulus ({sets:.1f} sets). In progressive overload sweet spot."
            elif sets <= lm.mrv:
                state = "NEAR_MRV"
                notes = f"Approaching maximum recoverable ceiling ({sets:.1f} / {lm.mrv} sets MRV). Near deload limit."
            else:
                state = "OVER_MRV"
                notes = f"Exceeded recovery capacity ({sets:.1f} > {lm.mrv} sets MRV). High overtraining & joint risk."

            # Recovery calculation based on hours elapsed and session intensity
            hours_elapsed = None
            last_date_str = None
            recovery_pct = 100

            if m in last_trained_dt:
                trained_time = last_trained_dt[m]
                hours_elapsed = max(0.0, (now - trained_time).total_seconds() / 3600.0)
                last_date_str = trained_time.strftime("%Y-%m-%d %H:%M")

                # Recovery curve: baseline full recovery takes 48-72 hours depending on volume
                needed_hours = 48.0 if last_trained_sets.get(m, 3.0) <= 6 else 72.0
                recovery_pct = min(100, int((hours_elapsed / needed_hours) * 100))

            # Concurrent interference audit for lower-body muscles
            interference = "NONE"
            if m in ["quads", "hamstrings", "calves", "glutes"] and hours_elapsed is not None:
                for end_act in endurance_leg_activities:
                    raw_s = end_act.get("start_date_local") or end_act.get("start_date")
                    if raw_s:
                        try:
                            s_e = str(raw_s).replace("Z", "+00:00")
                            e_dt = datetime.datetime.fromisoformat(s_e)
                            if e_dt.tzinfo is None:
                                e_dt = e_dt.replace(tzinfo=datetime.timezone.utc)
                            diff_hours = abs((last_trained_dt[m] - e_dt).total_seconds() / 3600.0)
                            if diff_hours < 6.0:
                                interference = "HIGH" if diff_hours < 3.0 else "MODERATE"
                                notes += f" Warning: High endurance leg activity within {diff_hours:.1f}h blunts mTORC1 signaling."
                                break
                        except Exception:
                            pass

            muscle_statuses[m] = MuscleGroupStatus(
                name=m,
                display_name=MUSCLE_DISPLAY_NAMES.get(m, m.title()),
                weekly_sets=sets,
                mv=lm.mv,
                mev=lm.mev,
                mav=lm.mav,
                mrv=lm.mrv,
                landmark_state=state,
                recovery_pct=recovery_pct,
                hours_since_trained=hours_elapsed,
                last_trained_date=last_date_str,
                interference_risk=interference,
                notes=notes,
            )

        # Calculate systemic bodybuilding readiness score (0-100)
        avg_recovery = sum(s.recovery_pct for s in muscle_statuses.values()) / max(1, len(muscle_statuses))
        systemic_score = round(avg_recovery)

        return {
            "timestamp": now.isoformat(),
            "gym_sessions_analyzed": len(gym_activities),
            "systemic_muscle_recovery_score": systemic_score,
            "muscle_groups": {k: v.to_dict() for k, v in muscle_statuses.items()},
        }

    @classmethod
    def get_personalized_6day_ppl(cls) -> Dict[str, Any]:
        """
        Generates the customized 6-Day Push / Pull / Legs (PPL x 2)
        bodybuilding program tailored for concurrent endurance athletes.
        Incorporates exercise tempo, rep ranges, target RIR (Reps in Reserve),
        and AMPK/mTOR endurance separation rules.
        """
        return {
            "program_name": "6-Day Hybrid PPL (Hypertrophy + Concurrent Endurance)",
            "structure": "Push A / Pull A / Legs A / Push B / Pull B / Legs B / Active Recovery",
            "weekly_frequency": "6 Days Resistance + 3-4 Days Low-Impact Cardio",
            "interference_protocol": "Separate heavy leg sessions from hard runs/rides by >= 6-8 hours. Perform lifting first if hypertrophy is priority.",
            "sessions": [
                {
                    "day": "Day 1 (Monday)",
                    "title": "Push A (Chest & Front/Side Delts Dominant)",
                    "focus": "Horizontal pressing mechanical tension & upper chest fiber recruitment",
                    "exercises": [
                        {"name": "Barbell Incline Bench Press", "sets": 4, "reps": "6-8", "rir": "2 RIR", "rest": "2.5-3 mins", "primary": "Upper Chest / Front Delts"},
                        {"name": "Flat Dumbbell Press", "sets": 3, "reps": "8-10", "rir": "1-2 RIR", "rest": "2 mins", "primary": "Mid Chest"},
                        {"name": "Standing Dumbbell Lateral Raise", "sets": 4, "reps": "12-15", "rir": "1 RIR", "rest": "90 secs", "primary": "Lateral Delts"},
                        {"name": "Cable Crossover (Low to High)", "sets": 3, "reps": "12-15", "rir": "1 RIR", "rest": "90 secs", "primary": "Upper Chest"},
                        {"name": "Overhead Cable Triceps Extension", "sets": 3, "reps": "10-12", "rir": "1-2 RIR", "rest": "90 secs", "primary": "Triceps Long Head"},
                        {"name": "Triceps Rope Pushdown", "sets": 3, "reps": "12-15", "rir": "0-1 RIR", "rest": "60 secs", "primary": "Triceps Lateral Head"}
                    ],
                    "endurance_guidance": "Easy Zone 2 cycling (30-45 mins) in afternoon or evening (>=6h separation)."
                },
                {
                    "day": "Day 2 (Tuesday)",
                    "title": "Pull A (Lat Width & Upper Back Density)",
                    "focus": "Vertical pulling & scapular retraction with deep stretch",
                    "exercises": [
                        {"name": "Neutral-Grip Lat Pulldown / Pullups", "sets": 4, "reps": "8-10", "rir": "1-2 RIR", "rest": "2 mins", "primary": "Lats"},
                        {"name": "Chest-Supported T-Bar Row", "sets": 4, "reps": "8-10", "rir": "1-2 RIR", "rest": "2 mins", "primary": "Upper Back / Rhomboids"},
                        {"name": "Single-Arm Dumbbell Row", "sets": 3, "reps": "10-12", "rir": "1 RIR", "rest": "90 secs", "primary": "Lats"},
                        {"name": "Incline Dumbbell Rear Delt Fly", "sets": 4, "reps": "12-15", "rir": "1 RIR", "rest": "75 secs", "primary": "Rear Delts"},
                        {"name": "Incline Dumbbell Biceps Curl", "sets": 3, "reps": "10-12", "rir": "1-2 RIR", "rest": "90 secs", "primary": "Biceps Long Head"},
                        {"name": "Standing Cable Hammer Curl", "sets": 3, "reps": "12-15", "rir": "0-1 RIR", "rest": "75 secs", "primary": "Brachialis & Forearms"}
                    ],
                    "endurance_guidance": "Rest from high-intensity running; light mobility or 30-min recovery spin."
                },
                {
                    "day": "Day 3 (Wednesday)",
                    "title": "Legs A (Quad Dominant & Knee Extension)",
                    "focus": "Deep knee flexion and quad hypertrophy (avoiding joint shear for runners)",
                    "exercises": [
                        {"name": "Barbell High-Bar Back Squat or Hack Squat", "sets": 4, "reps": "6-8", "rir": "2 RIR", "rest": "3 mins", "primary": "Quads / Glutes"},
                        {"name": "Leg Press (Feet Low on Platform)", "sets": 3, "reps": "10-12", "rir": "1-2 RIR", "rest": "2 mins", "primary": "Quads"},
                        {"name": "Seated Leg Curl", "sets": 4, "reps": "10-12", "rir": "1 RIR", "rest": "90 secs", "primary": "Hamstrings"},
                        {"name": "Walking Dumbbell Lunges", "sets": 3, "reps": "12 steps/leg", "rir": "1-2 RIR", "rest": "90 secs", "primary": "Quads / Glutes"},
                        {"name": "Standing Single-Leg Calf Raise", "sets": 4, "reps": "12-15", "rir": "1 RIR", "rest": "60 secs", "primary": "Calves (Gastrocnemius)"},
                        {"name": "Hanging Knee / Leg Raise", "sets": 3, "reps": "12-15", "rir": "1 RIR", "rest": "60 secs", "primary": "Abs / Core"}
                    ],
                    "endurance_guidance": "DO NOT RUN TODAY. Running on acute quad fatigue damages connective tissue. Keep cardio to passive recovery."
                },
                {
                    "day": "Day 4 (Thursday)",
                    "title": "Push B (Shoulder Delts & Triceps Focus)",
                    "focus": "Vertical pressing power, medial delt expansion, and chest pump",
                    "exercises": [
                        {"name": "Seated Dumbbell Overhead Press", "sets": 4, "reps": "8-10", "rir": "1-2 RIR", "rest": "2 mins", "primary": "Front & Side Delts"},
                        {"name": "Incline Dumbbell Bench Press", "sets": 3, "reps": "10-12", "rir": "1-2 RIR", "rest": "2 mins", "primary": "Upper Chest"},
                        {"name": "Cable Lateral Raise (Behind Back)", "sets": 4, "reps": "12-15", "rir": "1 RIR", "rest": "75 secs", "primary": "Lateral Delts"},
                        {"name": "Dips (Chest / Tricep focus)", "sets": 3, "reps": "8-12", "rir": "1-2 RIR", "rest": "90 secs", "primary": "Triceps / Lower Chest"},
                        {"name": "Cable Tricep V-Bar Pushdown", "sets": 3, "reps": "12-15", "rir": "0-1 RIR", "rest": "60 secs", "primary": "Triceps"}
                    ],
                    "endurance_guidance": "Zone 2 aerobic base run (30-40 mins) separated by >= 6 hours."
                },
                {
                    "day": "Day 5 (Friday)",
                    "title": "Pull B (Upper Back Thickness & Bicep Peak)",
                    "focus": "Horizontal rows, rear delt development, and elbow flexion volume",
                    "exercises": [
                        {"name": "Barbell Bent-Over Row (Overhand)", "sets": 4, "reps": "6-8", "rir": "2 RIR", "rest": "2.5 mins", "primary": "Upper Back / Lats"},
                        {"name": "Close-Grip Seated Cable Row", "sets": 3, "reps": "10-12", "rir": "1 RIR", "rest": "90 secs", "primary": "Lats"},
                        {"name": "Rope Face Pulls to Forehead", "sets": 4, "reps": "15-20", "rir": "1 RIR", "rest": "60 secs", "primary": "Rear Delts / Rotator Cuff"},
                        {"name": "EZ-Bar Preacher Curl", "sets": 3, "reps": "10-12", "rir": "1 RIR", "rest": "75 secs", "primary": "Biceps Short Head"},
                        {"name": "Dumbbell Hammer Curls", "sets": 3, "reps": "12-15", "rir": "0-1 RIR", "rest": "60 secs", "primary": "Brachialis"}
                    ],
                    "endurance_guidance": "Optional 45-min endurance ride or swim."
                },
                {
                    "day": "Day 6 (Saturday)",
                    "title": "Legs B (Hamstring & Posterior Chain Dominant)",
                    "focus": "Hip hinge mechanical tension, glute power, and calf resilience",
                    "exercises": [
                        {"name": "Romanian Deadlift (Dumbbell or Barbell)", "sets": 4, "reps": "8-10", "rir": "2 RIR", "rest": "2.5 mins", "primary": "Hamstrings / Glutes"},
                        {"name": "Bulgarian Split Squat", "sets": 3, "reps": "10-12 / leg", "rir": "1-2 RIR", "rest": "90 secs", "primary": "Quads / Glutes"},
                        {"name": "Lying or Seated Leg Curl", "sets": 3, "reps": "12-15", "rir": "1 RIR", "rest": "75 secs", "primary": "Hamstrings"},
                        {"name": "Barbell / Dumbbell Hip Thrust", "sets": 3, "reps": "10-12", "rir": "1 RIR", "rest": "2 mins", "primary": "Glutes"},
                        {"name": "Seated Calf Raise (Soleus Focus)", "sets": 4, "reps": "15-20", "rir": "1 RIR", "rest": "60 secs", "primary": "Calves (Soleus for running)"},
                        {"name": "Ab Rollout or Cable Crunch", "sets": 3, "reps": "12-15", "rir": "1 RIR", "rest": "60 secs", "primary": "Core"}
                    ],
                    "endurance_guidance": "No hard running post-leg day. Keep Sunday for recovery."
                },
                {
                    "day": "Day 7 (Sunday)",
                    "title": "Active Recovery & Autonomic Regeneration",
                    "focus": "Full systemic recovery, muscle protein synthesis, and joint decompression",
                    "exercises": [
                        {"name": "Foam Rolling & Mobility Sequence", "sets": 1, "reps": "20 mins", "rir": "0", "rest": "N/A", "primary": "Myofascial Release"},
                        {"name": "Light Walk or Casual Zone 1 Spin", "sets": 1, "reps": "30-45 mins", "rir": "0", "rest": "N/A", "primary": "Capillary Blood Flow"}
                    ],
                    "endurance_guidance": "Optional easy Z1 aerobic flush. Focus on high protein intake (2.0 g/kg) and 8+ hours sleep."
                }
            ]
        }
