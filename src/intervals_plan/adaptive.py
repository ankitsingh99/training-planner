"""
Adaptive training engine: adjusts workouts based on recovery, fatigue, and club ride rules.
"""

from typing import Any, Dict, List, Optional
from intervals_plan.api_models import IntervalsEvent, WorkoutDoc
from intervals_plan.workout_schema import calc_duration, create_step


class AdaptiveEngine:
    """Implements user constraints and adaptive training rules."""

    @staticmethod
    def adapt_for_hard_club_ride(events: List[IntervalsEvent], week_number: int) -> List[IntervalsEvent]:
        """
        Rule: If the weekend club ride is hard, suppress Thursday's optional bike intervals
        to avoid stacking two high-intensity cycling sessions in the same week.
        """
        adapted = []
        target_thu_ext_id = f"w{week_number}-thu-optional-bike"

        for ev in events:
            if ev.external_id and target_thu_ext_id in ev.external_id:
                # Replace high-intensity VO2 bike intervals with an easy recovery spin
                easy_steps = [
                    create_step(30 * 60, "Easy recovery spin; high cadence, minimal resistance")
                ]
                desc = (
                    "🎯 Focus: Active recovery & metabolic flush.\n"
                    "💡 How to execute: Substituted due to hard weekend club ride. Keep resistance minimal and cadence high (85-95 rpm). "
                    "This session is designed to promote blood flow and tissue healing without CNS or muscular fatigue.\n\n"
                    "- 30m 50-60% LTHR Active recovery spin; high cadence, minimal resistance\n"
                )
                converted = IntervalsEvent(
                    start_date_local=ev.start_date_local,
                    category="WORKOUT",
                    type="Ride",
                    name=f"W{week_number} Recovery Spin (Substituted for hard VO2)",
                    description=desc,
                    moving_time=calc_duration(easy_steps),
                    external_id=ev.external_id,
                    workout_doc=WorkoutDoc(description="Active recovery spin", steps=easy_steps),
                )
                adapted.append(converted)
            else:
                adapted.append(ev)
        return adapted

    @staticmethod
    def reschedule_club_ride(
        events: List[IntervalsEvent], week_number: int, target_date_str: str
    ) -> List[IntervalsEvent]:
        """Move the weekend club ride reminder to target date (e.g. Sunday instead of Saturday)."""
        adapted = []
        target_club_ext_id = f"w{week_number}-weekend-club-ride"

        for ev in events:
            if ev.external_id and target_club_ext_id in ev.external_id:
                moved = IntervalsEvent(
                    start_date_local=f"{target_date_str}T00:00:00",
                    category="NOTE",
                    type="Ride",
                    name=ev.name,
                    description=ev.description,
                    external_id=ev.external_id,
                )
                adapted.append(moved)
            else:
                adapted.append(ev)
        return adapted

    @staticmethod
    def adjust_aerobic_duration(events: List[IntervalsEvent], delta_minutes: int) -> List[IntervalsEvent]:
        """Bulk adjust duration of easy aerobic rides by delta_minutes."""
        adapted = []
        for ev in events:
            if ev.type == "Ride" and "easy-ride" in (ev.external_id or ""):
                curr_mins = (ev.moving_time or 2400) // 60
                new_mins = max(20, curr_mins + delta_minutes)
                steps = [
                    create_step(new_mins * 60, f"Steady conversational aerobic ride; {new_mins} min")
                ]
                updated = IntervalsEvent(
                    start_date_local=ev.start_date_local,
                    category=ev.category,
                    type=ev.type,
                    name=f"{ev.name.split('—')[0].strip()} — {new_mins} min",
                    description=ev.description,
                    moving_time=new_mins * 60,
                    external_id=ev.external_id,
                    workout_doc=WorkoutDoc(description="Adjusted easy aerobic endurance", steps=steps),
                )
                adapted.append(updated)
            else:
                adapted.append(ev)
        return adapted

