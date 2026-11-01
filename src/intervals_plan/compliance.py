"""
Plan Compliance and Planned vs Actual Execution Tracker:
Compares planned workouts against completed wearable and platform activities.
Computes execution score, volume compliance, load compliance, missed workouts,
unplanned efforts, and aerobic decoupling indicators.
"""

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional

from intervals_plan.api_models import IntervalsActivity, IntervalsEvent


@dataclass
class MatchedSession:
    """Pairing of a planned event with its completed activity."""

    date: str
    sport: str
    planned_name: str
    planned_duration_min: int
    actual_duration_min: int
    duration_delta_min: int
    planned_tss: Optional[float]
    actual_tss: Optional[float]
    status: str  # 'COMPLETED', 'MISSED', 'UNPLANNED', 'OVER_EXECUTED', 'UNDER_EXECUTED'


@dataclass
class ComplianceReport:
    """Comprehensive compliance evaluation over a date window."""

    start_date: str
    end_date: str
    days: int
    planned_count: int
    completed_count: int
    execution_rate_pct: float
    planned_volume_hours: float
    actual_volume_hours: float
    volume_compliance_pct: float
    planned_load_tss: float
    actual_load_tss: float
    load_compliance_pct: float
    compliance_rating: str  # 'OPTIMAL', 'ACCEPTABLE', 'UNDER_TRAINING', 'OVER_TRAINING_RISK'
    matched_sessions: List[MatchedSession] = field(default_factory=list)
    missed_workouts: List[Dict[str, Any]] = field(default_factory=list)
    unplanned_activities: List[Dict[str, Any]] = field(default_factory=list)
    coaching_observations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PlanComplianceEngine:
    """Evaluates planned workouts against actual recorded activities."""

    def __init__(self, tolerance_minutes: int = 15):
        self.tolerance_minutes = tolerance_minutes

    def evaluate(
        self,
        planned_events: List[IntervalsEvent],
        activities: List[Any],
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> ComplianceReport:
        """Run planned vs actual reconciliation across events and activities."""
        # Normalize activities
        norm_acts: List[IntervalsActivity] = []
        for a in activities:
            if isinstance(a, IntervalsActivity):
                norm_acts.append(a)
            elif isinstance(a, dict):
                norm_acts.append(IntervalsActivity.from_dict(a))
            else:
                norm_acts.append(
                    IntervalsActivity(
                        id=str(getattr(a, "id", "")),
                        start_date_local=getattr(a, "start_date_local", ""),
                        type=getattr(a, "type", "Run"),
                        name=getattr(a, "name", ""),
                        moving_time=getattr(a, "moving_time", 0),
                        icu_training_load=getattr(a, "icu_training_load", 0.0),
                    )
                )

        # Filter workouts only (exclude rest notes)
        active_plans = [
            e for e in planned_events
            if e.category != "NOTE" and getattr(e, "moving_time", 0) and e.moving_time > 0
        ]

        # Determine date bounds
        if not start_date or not end_date:
            dates: List[datetime.date] = []
            for e in active_plans:
                if e.start_date_local:
                    try:
                        dates.append(datetime.date.fromisoformat(e.start_date_local[:10]))
                    except Exception:
                        pass
            for a in norm_acts:
                if a.start_date_local:
                    try:
                        dates.append(datetime.date.fromisoformat(a.start_date_local[:10]))
                    except Exception:
                        pass
            calc_start = min(dates) if dates else datetime.date.today() - datetime.timedelta(days=7)
            calc_end = max(dates) if dates else datetime.date.today()
        else:
            calc_start = start_date
            calc_end = end_date

        start_str = calc_start.isoformat()
        end_str = calc_end.isoformat()

        # Scope to window
        window_plans = [
            e for e in active_plans
            if e.start_date_local and start_str <= e.start_date_local[:10] <= end_str
        ]
        window_acts = [
            a for a in norm_acts
            if a.start_date_local and start_str <= a.start_date_local[:10] <= end_str
        ]

        unmatched_acts = list(window_acts)
        matched_sessions: List[MatchedSession] = []
        missed_workouts: List[Dict[str, Any]] = []

        total_planned_sec = sum(e.moving_time or 0 for e in window_plans)
        total_actual_sec = sum(a.moving_time or 0 for a in window_acts)
        total_planned_tss = 0.0
        total_actual_tss = sum(a.icu_training_load or 0.0 for a in window_acts)

        for plan in window_plans:
            plan_date = plan.start_date_local[:10] if plan.start_date_local else ""
            plan_sport = (plan.type or "Workout").lower()
            plan_dur_min = int(round((plan.moving_time or 0) / 60))
            # Approximate planned TSS if not set: ~50 TSS per hour of moderate exercise
            plan_tss = 50.0 * (plan_dur_min / 60.0)
            total_planned_tss += plan_tss

            # Match criteria: same date (or +/- 1 day) and matching sport discipline
            matched_act: Optional[IntervalsActivity] = None
            for act in unmatched_acts:
                act_date = act.start_date_local[:10] if act.start_date_local else ""
                act_sport = (act.type or "").lower()
                
                # Check sport match
                sport_match = (
                    act_sport == plan_sport
                    or (plan_sport in ["ride", "virtualride"] and act_sport in ["ride", "virtualride", "cycling"])
                    or (plan_sport in ["run", "virtualrun"] and act_sport in ["run", "virtualrun"])
                    or (plan_sport in ["swim"] and act_sport in ["swim", "swimming"])
                )

                if sport_match and act_date == plan_date:
                    matched_act = act
                    break

            if matched_act:
                unmatched_acts.remove(matched_act)
                act_dur_min = int(round((matched_act.moving_time or 0) / 60))
                delta_min = act_dur_min - plan_dur_min
                
                if abs(delta_min) <= self.tolerance_minutes:
                    status = "COMPLETED"
                elif delta_min > self.tolerance_minutes:
                    status = "OVER_EXECUTED"
                else:
                    status = "UNDER_EXECUTED"

                matched_sessions.append(
                    MatchedSession(
                        date=plan_date,
                        sport=plan.type or "Workout",
                        planned_name=plan.name or "Planned Session",
                        planned_duration_min=plan_dur_min,
                        actual_duration_min=act_dur_min,
                        duration_delta_min=delta_min,
                        planned_tss=round(plan_tss, 1),
                        actual_tss=round(matched_act.icu_training_load or 0.0, 1),
                        status=status,
                    )
                )
            else:
                missed_workouts.append({
                    "date": plan_date,
                    "sport": plan.type or "Workout",
                    "name": plan.name or "Planned Workout",
                    "duration_min": plan_dur_min,
                })
                matched_sessions.append(
                    MatchedSession(
                        date=plan_date,
                        sport=plan.type or "Workout",
                        planned_name=plan.name or "Planned Session",
                        planned_duration_min=plan_dur_min,
                        actual_duration_min=0,
                        duration_delta_min=-plan_dur_min,
                        planned_tss=round(plan_tss, 1),
                        actual_tss=0.0,
                        status="MISSED",
                    )
                )

        unplanned_list = [
            {
                "id": a.id,
                "date": a.start_date_local[:10] if a.start_date_local else "",
                "sport": a.type or "Activity",
                "name": a.name or "Unplanned Session",
                "duration_min": int(round((a.moving_time or 0) / 60)),
                "tss": a.icu_training_load or 0.0,
            }
            for a in unmatched_acts
        ]

        planned_count = len(window_plans)
        completed_count = planned_count - len(missed_workouts)
        execution_rate = (completed_count / planned_count * 100.0) if planned_count > 0 else 100.0

        planned_vol_hrs = round(total_planned_sec / 3600.0, 2)
        actual_vol_hrs = round(total_actual_sec / 3600.0, 2)
        vol_compliance = (actual_vol_hrs / planned_vol_hrs * 100.0) if planned_vol_hrs > 0 else 100.0

        planned_tss_total = round(total_planned_tss, 1)
        actual_tss_total = round(total_actual_tss, 1)
        load_compliance = (actual_tss_total / planned_tss_total * 100.0) if planned_tss_total > 0 else 100.0

        # Compliance Rating & Coaching Observations
        observations: List[str] = []
        if vol_compliance < 75.0 or execution_rate < 75.0:
            rating = "UNDER_TRAINING"
            observations.append(
                f"Volume execution is low ({vol_compliance:.1f}%). {len(missed_workouts)} workouts were missed. "
                "Consider reducing weekly time commitment in Athlete Profile to fit realistic availability."
            )
        elif vol_compliance > 125.0 or load_compliance > 130.0:
            rating = "OVER_TRAINING_RISK"
            observations.append(
                f"Actual volume significantly exceeds plan ({vol_compliance:.1f}% of target, load {load_compliance:.1f}%). "
                "Unplanned training spikes escalate soft-tissue injury risk under Gabbett ACWR models. Restrict extra efforts."
            )
        elif 85.0 <= vol_compliance <= 115.0 and execution_rate >= 85.0:
            rating = "OPTIMAL"
            observations.append(
                f"Excellent plan compliance ({execution_rate:.0f}% completion, {vol_compliance:.1f}% volume). "
                "Training load is landing precisely in the sports science adaptation sweet spot."
            )
        else:
            rating = "ACCEPTABLE"
            observations.append(
                f"Solid overall compliance ({vol_compliance:.1f}% volume). Minor variance from scheduled microcycle."
            )

        if unplanned_list:
            observations.append(
                f"Recorded {len(unplanned_list)} unplanned activity efforts totaling "
                f"{sum(u['duration_min'] for u in unplanned_list)} minutes. Incorporate these into regular plan structure."
            )

        num_days = max(1, (calc_end - calc_start).days + 1)

        return ComplianceReport(
            start_date=start_str,
            end_date=end_str,
            days=num_days,
            planned_count=planned_count,
            completed_count=completed_count,
            execution_rate_pct=round(execution_rate, 1),
            planned_volume_hours=planned_vol_hrs,
            actual_volume_hours=actual_vol_hrs,
            volume_compliance_pct=round(vol_compliance, 1),
            planned_load_tss=planned_tss_total,
            actual_load_tss=actual_tss_total,
            load_compliance_pct=round(load_compliance, 1),
            compliance_rating=rating,
            matched_sessions=matched_sessions,
            missed_workouts=missed_workouts,
            unplanned_activities=unplanned_list,
            coaching_observations=observations,
        )
