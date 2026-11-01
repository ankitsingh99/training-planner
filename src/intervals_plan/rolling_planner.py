"""
Dynamic Rolling Training Planner:
Translates 30-day physiological readiness, Banister/Coggan load metrics,
Tim Gabbett ACWR boundaries, and Stephen Seiler 80/20 polarization into
personalized, COROS-compatible next 1-week or 2-week training plans.
"""

import datetime
from typing import Any, Dict, List, Optional

from intervals_plan.analytics import RollingAnalysisReport
from intervals_plan.api_models import HRTarget, IntervalsEvent, WorkoutDoc, WorkoutStep
from intervals_plan.athlete_profile import AthleteProfileConfig
from intervals_plan.workout_schema import calc_duration, create_step


class DynamicRollingPlanner:
    """Builds personalized upcoming 1-week or 2-week training schedules based on live analytics."""

    def __init__(self, profile: AthleteProfileConfig):
        self.profile = profile

    @staticmethod
    def get_upcoming_monday(from_date: Optional[datetime.date] = None) -> datetime.date:
        """Find the start date of the next weekly cycle (next Monday)."""
        d = from_date or datetime.date.today()
        # weekday: 0 = Mon, 6 = Sun
        days_ahead = (0 - d.weekday()) % 7
        if days_ahead == 0:
            # If today is Monday, schedule starting today
            return d
        return d + datetime.timedelta(days=days_ahead)

    def generate_plan(
        self,
        report: RollingAnalysisReport,
        start_date: Optional[datetime.date] = None,
        weeks_to_plan: int = 1,
        prefix: str = "dynamic-plan",
    ) -> List[IntervalsEvent]:
        """Generate a personalized rolling training plan for 1 or 2 weeks."""
        cycle_start = start_date or self.get_upcoming_monday()
        events: List[IntervalsEvent] = []

        total_hours = report.readiness.target_next_week_hours
        readiness = report.readiness
        is_strained = readiness.rhr_elevated or readiness.readiness_state in ["ELEVATED_FATIGUE", "RECOVERY_MANDATORY"]
        
        # Check periodization phase and life constraints
        phase, weeks_out = self.profile.get_periodization_phase(cycle_start)
        if phase == "taper":
            total_hours = max(4.0, total_hours * 0.65)
        elif phase == "peak":
            total_hours = total_hours * 1.05

        for w_idx in range(weeks_to_plan):
            week_num = w_idx + 1
            week_start = cycle_start + datetime.timedelta(days=w_idx * 7)
            week_events = self._build_week_schedule(
                week_num=week_num,
                week_start=week_start,
                total_hours=total_hours,
                is_strained=is_strained,
                readiness=readiness,
                prefix=prefix,
            )
            events.extend(week_events)

        return events

    def _build_week_schedule(
        self,
        week_num: int,
        week_start: datetime.date,
        total_hours: float,
        is_strained: bool,
        readiness: Any,
        prefix: str,
    ) -> List[IntervalsEvent]:
        """Construct the 7 days of workouts for a single week adhering to 80/20 polarization."""
        events: List[IntervalsEvent] = []

        # Day dates (Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6)
        mon = week_start
        tue = week_start + datetime.timedelta(days=1)
        wed = week_start + datetime.timedelta(days=2)
        thu = week_start + datetime.timedelta(days=3)
        fri = week_start + datetime.timedelta(days=4)
        sat = week_start + datetime.timedelta(days=5)
        sun = week_start + datetime.timedelta(days=6)

        # Scale durations proportionally if weekly budget is higher (e.g. 8+ hours)
        scale = max(0.6, min(1.6, total_hours / 8.0))

        # --- MONDAY: Rest / Regeneration ---
        mon_note = IntervalsEvent(
            start_date_local=f"{mon.isoformat()}T07:00:00",
            category="NOTE",
            type="Other",
            name=f"W{week_num} Rest & Regeneration",
            description=(
                "Target: Complete physiological rest and parasympathetic recovery. "
                "Hydrate, prioritize 8+ hours of sleep, and perform optional light mobility or stretching."
            ),
            external_id=f"{prefix}-w{week_num}-mon-rest-{mon.isoformat()}",
        )
        events.append(mon_note)

        # --- TUESDAY: Run Quality (VO2max / 5K-10K intervals OR Aerobic Strides if strained) ---
        if is_strained:
            tue_event = self._build_strained_tuesday_run(week_num, tue, prefix, readiness)
        else:
            tue_event = self._build_quality_tuesday_run(week_num, tue, prefix, scale)
        events.append(tue_event)

        # --- WEDNESDAY: Aerobic Base Run (Zone 2 Conversational) ---
        wed_dur_mins = int(round(50 * scale))
        wed_event = self._build_aerobic_run(week_num, wed, prefix, wed_dur_mins)
        events.append(wed_event)

        # --- THURSDAY: Bike Quality (Seiler 4x8m VO2/Sweet-Spot OR Recovery Spin if strained) ---
        if is_strained:
            thu_event = self._build_strained_thursday_bike(week_num, thu, prefix, readiness)
        else:
            thu_event = self._build_quality_thursday_bike(week_num, thu, prefix, scale)
        events.append(thu_event)

        # --- FRIDAY: Active Recovery Spin or Rest ---
        fri_dur_mins = int(round(40 * scale))
        fri_event = self._build_recovery_spin(week_num, fri, prefix, fri_dur_mins)
        events.append(fri_event)

        # --- SATURDAY: Long Endurance Ride / Club Ride ---
        sat_dur_mins = int(round(180 * (0.8 if is_strained else 1.0) * scale))
        sat_event = self._build_long_ride(week_num, sat, prefix, sat_dur_mins, is_strained)
        events.append(sat_event)

        # --- SUNDAY: Long Aerobic Run ---
        sun_dur_mins = int(round(75 * (0.85 if is_strained else 1.0) * scale))
        sun_event = self._build_long_run(week_num, sun, prefix, sun_dur_mins)
        events.append(sun_event)

        return events

    def _build_quality_tuesday_run(
        self, week_num: int, date: datetime.date, prefix: str, scale: float
    ) -> IntervalsEvent:
        """Stephen Seiler / Jack Daniels 5K-10K intervals."""
        reps = 6 if scale >= 1.0 else 5
        steps = [
            create_step(12 * 60, "Warmup Jog", hr_start=60, hr_end=72),
            create_step(4 * 60, "Dynamic Drills", hr_start=65, hr_end=75),
        ]
        for _ in range(reps):
            steps.append(create_step(3 * 60, "5K Pace Effort", hr_start=95, hr_end=102))
            steps.append(create_step(2 * 60, "Recovery Jog", hr_start=60, hr_end=70))
        steps.append(create_step(10 * 60, "Cool-down Jog", hr_start=60, hr_end=70))

        coaching = (
            f"Target: VO2max and aerobic power development ({reps}x3 min at 5K-10K race pace). "
            "Stephen Seiler Zone 3 / Jack Daniels Interval pace. "
            "Focus on relaxed shoulders, tall posture, and controlled breathing. "
            "Jog recoveries gently to clear blood lactate before the next repetition."
        )
        desc = (
            f"{coaching}\n\n"
            "- 12m 60-72% LTHR Warmup Jog\n"
            "- 4m 65-75% LTHR Dynamic Drills\n"
            f"- {reps}x\n"
            "- 3m 95-102% LTHR 5K Pace Effort\n"
            "- 2m 60-70% LTHR Recovery Jog\n"
            "- 10m 60-70% LTHR Cool-down Jog\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week_num} 5K Pace Intervals",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-tue-run-quality-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_strained_tuesday_run(
        self, week_num: int, date: datetime.date, prefix: str, readiness: Any
    ) -> IntervalsEvent:
        """Downgraded session when body metrics show fatigue/stress."""
        steps = [
            create_step(10 * 60, "Gentle Warmup", hr_start=55, hr_end=65),
            create_step(30 * 60, "Zone 2 Steady", hr_start=65, hr_end=75),
            create_step(5 * 60, "Cool-down Walk", hr_start=50, hr_end=60),
        ]
        coaching = (
            f"AUTONOMIC ADAPTATION: Downshifted from intervals due to elevated fatigue/RHR "
            f"(Readiness: {readiness.readiness_state}, Score: {readiness.readiness_score}/100). "
            "In accordance with Kiviniemi HRV protocols, intense intervals are substituted with "
            "conversational aerobic work to facilitate recovery without taxing the nervous system."
        )
        desc = (
            f"{coaching}\n\n"
            "- 10m 55-65% LTHR Gentle Warmup\n"
            "- 30m 65-75% LTHR Zone 2 Steady\n"
            "- 5m 50-60% LTHR Cool-down Walk\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week_num} Aerobic Flush (Substituted)",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-tue-run-adapted-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_aerobic_run(
        self, week_num: int, date: datetime.date, prefix: str, dur_mins: int
    ) -> IntervalsEvent:
        """Conversational aerobic base run."""
        steps = [
            create_step(8 * 60, "Warmup Jog", hr_start=60, hr_end=68),
            create_step((dur_mins - 14) * 60, "Zone 2 Steady", hr_start=68, hr_end=80),
            create_step(6 * 60, "Cool-down Walk", hr_start=55, hr_end=65),
        ]
        coaching = (
            f"Target: Pure aerobic base endurance ({dur_mins} min). "
            "Stephen Seiler Zone 1 low-intensity foundation. Strictly conversational pace. "
            "If your breathing becomes labored or HR drifts above 80% LTHR, slow your pace down."
        )
        desc = (
            f"{coaching}\n\n"
            "- 8m 60-68% LTHR Warmup Jog\n"
            f"- {dur_mins - 14}m 68-80% LTHR Zone 2 Steady\n"
            "- 6m 55-65% LTHR Cool-down Walk\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week_num} Aerobic Base Run - {dur_mins}m",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-wed-run-aerobic-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_quality_thursday_bike(
        self, week_num: int, date: datetime.date, prefix: str, scale: float
    ) -> IntervalsEvent:
        """Stephen Seiler 4x8min VO2max / Sweet-spot bike workout."""
        steps = [
            create_step(15 * 60, "Warmup Spin", hr_start=55, hr_end=68, p_start=50, p_end=65),
            create_step(8 * 60, "8m Sweet-Spot", hr_start=88, hr_end=94, p_start=88, p_end=95),
            create_step(3 * 60, "Active Spin", hr_start=55, hr_end=65, p_start=50, p_end=55),
            create_step(8 * 60, "8m Sweet-Spot", hr_start=88, hr_end=94, p_start=88, p_end=95),
            create_step(3 * 60, "Active Spin", hr_start=55, hr_end=65, p_start=50, p_end=55),
            create_step(8 * 60, "8m Sweet-Spot", hr_start=88, hr_end=94, p_start=88, p_end=95),
            create_step(3 * 60, "Active Spin", hr_start=55, hr_end=65, p_start=50, p_end=55),
            create_step(8 * 60, "8m Sweet-Spot", hr_start=88, hr_end=94, p_start=88, p_end=95),
            create_step(12 * 60, "Cool-down Spin", hr_start=50, hr_end=60, p_start=45, p_end=55),
        ]
        coaching = (
            "Target: Aerobic threshold and fatigue resistance (4x8 min at 88-95% FTP / 88-94% LTHR). "
            "Dr. Stephen Seiler's optimal endurance interval format. "
            "Maintain steady 88-92 rpm cadence. Resist the urge to surge during the first 2 minutes."
        )
        desc = (
            f"{coaching}\n\n"
            "- 15m 55-68% LTHR Warmup Spin\n"
            "- 4x\n"
            "- 8m 88-94% LTHR 8m Sweet-Spot\n"
            "- 3m 55-65% LTHR Active Spin\n"
            "- 12m 50-60% LTHR Cool-down Spin\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week_num} Seiler 4x8m Intervals",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-thu-bike-quality-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_strained_thursday_bike(
        self, week_num: int, date: datetime.date, prefix: str, readiness: Any
    ) -> IntervalsEvent:
        """Recovery spin when fatigue is elevated."""
        steps = [
            create_step(40 * 60, "Recovery Spin", hr_start=50, hr_end=60, p_start=45, p_end=55),
        ]
        coaching = (
            f"AUTONOMIC ADAPTATION: Intense intervals substituted with active recovery spin. "
            f"Readiness state is {readiness.readiness_state}. "
            "Keep resistance low and pedal smoothly at 90 rpm to stimulate capillary circulation."
        )
        desc = (
            f"{coaching}\n\n"
            "- 40m 50-60% LTHR Recovery Spin\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week_num} Recovery Spin (Substituted)",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-thu-bike-adapted-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_recovery_spin(
        self, week_num: int, date: datetime.date, prefix: str, dur_mins: int
    ) -> IntervalsEvent:
        """Friday active recovery spin."""
        steps = [
            create_step(dur_mins * 60, "Recovery Spin", hr_start=50, hr_end=60, p_start=45, p_end=55),
        ]
        coaching = (
            f"Target: Active recovery and lactate clearing ({dur_mins} min). "
            "Zone 1 low-stress spinning. Very light pedal pressure, high cadence (85-95 rpm)."
        )
        desc = (
            f"{coaching}\n\n"
            f"- {dur_mins}m 50-60% LTHR Recovery Spin\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week_num} Recovery Spin - {dur_mins}m",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-fri-recovery-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_long_ride(
        self, week_num: int, date: datetime.date, prefix: str, dur_mins: int, is_strained: bool
    ) -> IntervalsEvent:
        """Saturday endurance ride or club ride slot."""
        steps = [
            create_step(15 * 60, "Warmup Spin", hr_start=55, hr_end=65),
            create_step((dur_mins - 25) * 60, "Zone 2 Endurance", hr_start=65, hr_end=78),
            create_step(10 * 60, "Cool-down Spin", hr_start=50, hr_end=60),
        ]
        hours = dur_mins / 60.0
        coaching = (
            f"Target: Aerobic durability and mitochondrial density ({hours:.1f} hours). "
            "Stephen Seiler Zone 1 long endurance ride. Steady effort, 65-78% LTHR. "
            "Fuel consistently with 40-60g carbohydrates and fluids per hour."
        )
        desc = (
            f"{coaching}\n\n"
            "- 15m 55-65% LTHR Warmup Spin\n"
            f"- {dur_mins - 25}m 65-78% LTHR Zone 2 Endurance\n"
            "- 10m 50-60% LTHR Cool-down Spin\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:00:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week_num} Long Endurance Ride - {hours:.1f}h",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-sat-long-ride-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_long_run(
        self, week_num: int, date: datetime.date, prefix: str, dur_mins: int
    ) -> IntervalsEvent:
        """Sunday long aerobic run."""
        steps = [
            create_step(10 * 60, "Warmup Jog", hr_start=60, hr_end=68),
            create_step((dur_mins - 18) * 60, "Zone 2 Steady", hr_start=68, hr_end=80),
            create_step(8 * 60, "Cool-down Walk", hr_start=55, hr_end=65),
        ]
        coaching = (
            f"Target: Musculoskeletal fatigue resistance and aerobic capacity ({dur_mins} min). "
            "Conversational Zone 2 endurance run. "
            "Do not race this run. Maintain smooth cadence (170-180 spm) and relax your upper body."
        )
        desc = (
            f"{coaching}\n\n"
            "- 10m 60-68% LTHR Warmup Jog\n"
            f"- {dur_mins - 18}m 68-80% LTHR Zone 2 Steady\n"
            "- 8m 55-65% LTHR Cool-down Walk\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week_num} Long Aerobic Run - {dur_mins}m",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-sun-long-run-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )
