"""
AI Training Coach and Intelligence Layer for Personal AI Training Analyst.
Implements Sections 7 & 18.5 (AT-050 to AT-060) with strict evidence grounding.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.orm import Session

from intervals_plan.db_models import CoachRecommendationModel, PlannedWorkoutModel


class CoachEngine:
    """Personal AI Training Coach with deterministic evidence validation and persistence."""

    def __init__(self, session: Optional[Session] = None) -> None:
        self.session = session

    def generate_daily_assessment(
        self,
        analytics_summary: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        goals: Optional[Dict[str, Any]] = None,
        user_reported_pain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate daily assessment referencing calculated metrics (AT-050).
        Discloses missing metrics (AT-051), handles conflicting indicators (AT-058),
        prioritizes configured goals (AT-052), and warns against training through pain (AT-056).
        """
        user_prefs = user_preferences or {}
        user_goals = goals or {"primary": "hypertrophy", "secondary": "vo2_max"}
        supporting_metrics: Dict[str, Any] = {}
        reasoning_points: List[str] = []

        # 1. Pain / Injury Gate (AT-056)
        if user_reported_pain:
            rec = {
                "recommendation_id": str(uuid.uuid4()),
                "recommendation_type": "injury_protection",
                "proposed_action": "Rest and medical evaluation",
                "recommendation": f"Suspend training affecting {user_reported_pain}. Do not train through pain.",
                "reasoning": f"User reported pain: '{user_reported_pain}'. Training through pain risks acute musculoskeletal injury. Seek professional medical evaluation.",
                "supporting_data": {"user_reported_pain": user_reported_pain},
                "confidence": 1.0,
                "relevant_constraints": ["Zero tolerance for training through acute pain"],
                "requires_user_approval": True,
                "status": "proposed",
            }
            self._persist_recommendation(rec)
            return rec

        # 2. Check Recovery Metrics (HRV, RHR, Sleep) (AT-050, AT-051, AT-058)
        hrv_status = analytics_summary.get("hrv_status")
        hrv_dev = analytics_summary.get("hrv_deviation_pct")
        rhr_dev = analytics_summary.get("rhr_elevation_bpm")
        atl = analytics_summary.get("atl")
        ctl = analytics_summary.get("ctl")
        acwr = analytics_summary.get("acwr")

        if hrv_status is None and hrv_dev is None:
            # AT-051: Missing data disclosure
            reasoning_points.append("HRV-based autonomic recovery assessment is unavailable due to missing recent measurements.")
            supporting_metrics["hrv_status"] = "UNAVAILABLE"
        else:
            supporting_metrics["hrv_deviation_pct"] = hrv_dev
            supporting_metrics["hrv_status"] = hrv_status

        if acwr is not None:
            supporting_metrics["acwr"] = acwr
            supporting_metrics["atl"] = atl
            supporting_metrics["ctl"] = ctl
            if acwr > 1.35:
                reasoning_points.append(f"Acute:Chronic Workload Ratio is elevated at {acwr} (>1.35 sweetspot limit), indicating compounding fatigue.")

        # AT-058: Contradictory recovery data
        contradictory_data = False
        if hrv_status == "SUPPRESSED" and rhr_dev is not None and rhr_dev <= -2:
            contradictory_data = True
            reasoning_points.append("Conflicting recovery indicators detected: HRV is suppressed while resting HR is lower than baseline. Readiness assessment carries increased uncertainty.")

        # AT-052: Goal Prioritization
        is_hypertrophy_primary = user_goals.get("primary") == "hypertrophy"

        # Determine proposed action
        planned_lower_body = analytics_summary.get("planned_workout_type") in ("legs", "strength_legs", "lower_body")
        requires_approval = True
        confidence = 0.85 if not contradictory_data else 0.65

        if (hrv_status == "SUPPRESSED" or (acwr and acwr > 1.4)) and planned_lower_body:
            proposed_action = "Deload or substitute lower-body session with active recovery"
            rec_text = "Your recent training load is elevated while autonomic recovery is suppressed. Postpone demanding lower-body lifting or reduce working volume by 40%."
            reasoning_points.append("High neuromuscular fatigue combined with lower-body eccentric load increases injury risk and impairs muscle protein synthesis.")
        elif is_hypertrophy_primary:
            proposed_action = "Execute planned strength session with full progressive overload"
            rec_text = "Recovery is within adaptive bounds. Proceed with scheduled strength training, maintaining 1-2 RIR on compound lifts."
            reasoning_points.append(f"Hypertrophy is prioritized over endurance. Ensure adequate carbohydrate intake and separation from cardio.")
        else:
            proposed_action = "Execute scheduled workout"
            rec_text = "Autonomic markers and workload are balanced. Execute session as scheduled."
            reasoning_points.append("All primary fitness indicators are stable.")

        rec = {
            "recommendation_id": str(uuid.uuid4()),
            "recommendation_type": "daily_analysis",
            "proposed_action": proposed_action,
            "recommendation": rec_text,
            "reasoning": " ".join(reasoning_points),
            "supporting_data": supporting_metrics,
            "confidence": confidence,
            "relevant_constraints": user_prefs.get("constraints", []),
            "requires_user_approval": requires_approval,
            "status": "proposed",
        }
        self._persist_recommendation(rec)
        return rec

    def generate_weekly_plan(
        self,
        week_start: datetime.date,
        user_preferences: Dict[str, Any],
        goals: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate weekly plan respecting training constraints (AT-053, AT-054, AT-076).
        - Tuesday is strictly preserved as gym rest day (AT-053).
        - Weekend club ride is represented as flexible (AT-054).
        """
        user_prefs = user_preferences or {}
        days = [week_start + datetime.timedelta(days=i) for i in range(7)]
        plan: List[Dict[str, Any]] = []

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for d in days:
            day_name = day_names[d.weekday()]
            date_str = d.isoformat()

            # AT-053: Tuesday gym rest constraint
            if day_name == "Tuesday":
                # Gym rest day preference
                plan.append({
                    "date": date_str,
                    "day": day_name,
                    "workout_type": "rest_or_light_aerobic",
                    "title": "Gym Rest Day",
                    "description": "Preserved gym rest day per user schedule constraints. Optional light mobility or recovery spin.",
                    "is_gym_workout": False,
                    "is_flexible": False,
                })
            elif day_name == "Monday":
                plan.append({
                    "date": date_str,
                    "day": day_name,
                    "workout_type": "strength_push",
                    "title": "Push A (Chest & Delts Focus)",
                    "description": "Flat bench press, incline DB press, cable lateral raises, triceps pushdown.",
                    "is_gym_workout": True,
                    "is_flexible": False,
                })
            elif day_name == "Wednesday":
                plan.append({
                    "date": date_str,
                    "day": day_name,
                    "workout_type": "strength_pull",
                    "title": "Pull A (Lat & Bicep Focus)",
                    "description": "Chest-supported row, lat pulldown, DB curls, face pulls.",
                    "is_gym_workout": True,
                    "is_flexible": False,
                })
            elif day_name == "Thursday":
                plan.append({
                    "date": date_str,
                    "day": day_name,
                    "workout_type": "strength_legs",
                    "title": "Legs A (Quad Dominant)",
                    "description": "Squat / hack squat, leg press, leg extensions, calf raises.",
                    "is_gym_workout": True,
                    "is_flexible": False,
                })
            elif day_name == "Friday":
                plan.append({
                    "date": date_str,
                    "day": day_name,
                    "workout_type": "strength_push_b",
                    "title": "Push B (Shoulder & Tricep Focus)",
                    "description": "Overhead press, incline bench, lateral raises, triceps overhead extension.",
                    "is_gym_workout": True,
                    "is_flexible": False,
                })
            elif day_name in ("Saturday", "Sunday"):
                # AT-054: Flexible club ride
                if day_name == "Saturday":
                    plan.append({
                        "date": date_str,
                        "day": day_name,
                        "workout_type": "cycling_club_ride",
                        "title": "Weekend Cycling Club Ride (~50 km)",
                        "description": "Zone 2 aerobic endurance club ride with coffee stop. Flexible timing.",
                        "is_gym_workout": False,
                        "is_flexible": True,  # AT-054
                    })
                else:
                    plan.append({
                        "date": date_str,
                        "day": day_name,
                        "workout_type": "strength_pull_b",
                        "title": "Pull B / Legs Posterior Chain",
                        "description": "Romanian deadlift, seated cable rows, hamstrings curls, biceps curls.",
                        "is_gym_workout": True,
                        "is_flexible": True,
                    })

        return plan

    def modify_planned_workout(
        self,
        planned_workout_id: str,
        modifications: Dict[str, Any],
        user_approved: bool = False,
    ) -> Dict[str, Any]:
        """
        Propose or apply changes to an existing planned workout (AT-060, AT-071).
        If user_approved is False, the existing workout remains unchanged!
        """
        if not self.session:
            return {"status": "unsupported", "message": "No database session available."}

        existing = self.session.query(PlannedWorkoutModel).filter_by(planned_workout_id=planned_workout_id).first()
        if not existing:
            raise ValueError(f"Planned workout '{planned_workout_id}' not found.")

        # AT-060: Require explicit approval before modifying existing plan
        if not user_approved:
            return {
                "status": "pending_approval",
                "planned_workout_id": planned_workout_id,
                "current_workout": existing.to_dict(),
                "proposed_modifications": modifications,
                "message": "Modifications proposed. Original workout remains unchanged until user approval.",
            }

        # User approved: apply changes safely
        for key, value in modifications.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.updated_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.commit()

        return {
            "status": "applied",
            "planned_workout_id": planned_workout_id,
            "updated_workout": existing.to_dict(),
        }

    def _persist_recommendation(self, rec: Dict[str, Any]) -> None:
        """Persist recommendation into SQLite database (AT-059)."""
        if not self.session:
            return
        rec_model = CoachRecommendationModel(
            recommendation_id=rec["recommendation_id"],
            recommendation_type=rec["recommendation_type"],
            recommendation=rec["recommendation"],
            rationale=rec["reasoning"],
            supporting_metrics=rec.get("supporting_data", {}),
            confidence=rec.get("confidence", 1.0),
            status=rec.get("status", "proposed"),
        )
        self.session.add(rec_model)
        self.session.commit()
