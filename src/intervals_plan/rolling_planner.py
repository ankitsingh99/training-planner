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
from intervals_plan.fueling import calculate_fueling
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
            # Check mesocycle 4th-week deload (25% volume reduction to absorb adaptation)
            week_hours = total_hours * 0.75 if (week_num % 4 == 0) else total_hours
            week_start = cycle_start + datetime.timedelta(days=w_idx * 7)
            week_events = self._build_week_schedule(
                week_num=week_num,
                week_start=week_start,
                total_hours=week_hours,
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
        goal_lower = self.profile.goal.lower()
        is_triathlon = any(w in goal_lower for w in ["triathlon", "ironman"])
        is_duathlon = any(w in goal_lower for w in ["duathlon", "duathlete"])
        is_swimming = any(w in goal_lower for w in ["swim", "swimming"]) and not is_triathlon
        is_running_focus = (goal_lower in ["running", "marathon", "half_marathon", "5k", "10k"]) and not is_duathlon
        is_cycling_focus = (goal_lower in ["cycling", "bike", "gran_fondo"]) and not is_duathlon

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

        if is_triathlon:
            # Multi-sport schedule (Swim / Bike / Run / Brick)
            # Tuesday: Run Quality / 5K-10K intervals
            if is_strained:
                events.append(self._build_strained_tuesday_run(week_num, tue, prefix, readiness))
            else:
                events.append(self._build_quality_tuesday_run(week_num, tue, prefix, scale))

            # Wednesday: Swim CSS Threshold
            events.append(self._build_swim_threshold(week_num, wed, prefix, scale))

            # Thursday: Bike Quality or Recovery Spin
            if is_strained:
                events.append(self._build_strained_thursday_bike(week_num, thu, prefix, readiness))
            else:
                events.append(self._build_quality_thursday_bike(week_num, thu, prefix, scale))

            # Friday: Swim Aerobic Base & Technique
            events.append(self._build_swim_aerobic(week_num, fri, prefix, scale))

            # Saturday: Long Ride + Transition Brick Run
            events.append(self._build_brick_session(week_num, sat, prefix, scale, is_strained))

            # Sunday: Long Aerobic Run
            sun_dur_mins = int(round(70 * (0.85 if is_strained else 1.0) * scale))
            events.append(self._build_long_run(week_num, sun, prefix, sun_dur_mins))

        elif is_duathlon:
            # Duathlete schedule (Run / Bike / Duathlon Brick)
            # Tuesday: Run Quality (VO2max / Threshold track intervals)
            if is_strained:
                events.append(self._build_strained_tuesday_run(week_num, tue, prefix, readiness))
            else:
                events.append(self._build_quality_tuesday_run(week_num, tue, prefix, scale))

            # Wednesday: Aerobic Base Spin
            wed_dur_mins = int(round(60 * scale))
            events.append(self._build_recovery_spin(week_num, wed, prefix, wed_dur_mins))

            # Thursday: Bike Quality (SweetSpot / Threshold)
            if is_strained:
                events.append(self._build_recovery_spin(week_num, thu, prefix, 45))
            else:
                events.append(self._build_cycling_threshold(week_num, thu, prefix, scale))

            # Friday: Easy Recovery Run
            fri_dur_mins = int(round(35 * scale))
            events.append(self._build_aerobic_run(week_num, fri, prefix, fri_dur_mins))

            # Saturday: Duathlon Brick Transition (Bike + Off-the-bike Run)
            events.append(self._build_brick_session(week_num, sat, prefix, scale, is_strained))

            # Sunday: Long Progressive Aerobic Run
            sun_dur_mins = int(round(80 * (0.85 if is_strained else 1.0) * scale))
            events.append(self._build_long_run(week_num, sun, prefix, sun_dur_mins))

        elif is_swimming:
            # Swimmer schedule (Threshold CSS, VO2max Speed, Aerobic Distance, Technique)
            # Tuesday: VO2max Speed Swim (or recovery if strained)
            if is_strained:
                events.append(self._build_swim_recovery(week_num, tue, prefix))
            else:
                events.append(self._build_swim_speed(week_num, tue, prefix, scale))

            # Wednesday: Aerobic Distance Swim & Drills
            events.append(self._build_swim_aerobic(week_num, wed, prefix, scale))

            # Thursday: CSS Threshold Swim (or recovery if strained)
            if is_strained:
                events.append(self._build_swim_recovery(week_num, thu, prefix))
            else:
                events.append(self._build_swim_threshold(week_num, thu, prefix, scale))

            # Friday: Technique & Recovery Swim
            events.append(self._build_swim_recovery(week_num, fri, prefix))

            # Saturday: Long Aerobic Endurance Swim
            events.append(self._build_swim_long(week_num, sat, prefix, scale, is_strained))

            # Sunday: Active Flush Recovery Spin
            events.append(self._build_recovery_spin(week_num, sun, prefix, int(round(40 * scale))))

        elif is_running_focus:
            # Pure Running focus schedule
            if is_strained:
                events.append(self._build_strained_tuesday_run(week_num, tue, prefix, readiness))
            else:
                events.append(self._build_quality_tuesday_run(week_num, tue, prefix, scale))

            # Wednesday: Aerobic Base Run
            wed_dur_mins = int(round(50 * scale))
            events.append(self._build_aerobic_run(week_num, wed, prefix, wed_dur_mins))

            # Thursday: Threshold / Tempo Run or Aerobic Flush if strained
            if is_strained:
                events.append(self._build_aerobic_run(week_num, thu, prefix, int(round(40 * scale))))
            else:
                events.append(self._build_tempo_run(week_num, thu, prefix, int(round(50 * scale))))

            # Friday: Easy Recovery Run
            fri_dur_mins = int(round(35 * scale))
            events.append(self._build_aerobic_run(week_num, fri, prefix, fri_dur_mins))

            # Saturday: Steady Aerobic Run
            sat_dur_mins = int(round(60 * scale))
            events.append(self._build_aerobic_run(week_num, sat, prefix, sat_dur_mins))

            # Sunday: Long Aerobic Run
            sun_dur_mins = int(round(90 * (0.85 if is_strained else 1.0) * scale))
            events.append(self._build_long_run(week_num, sun, prefix, sun_dur_mins))

        elif is_cycling_focus:
            # Pure Cycling focus schedule
            if is_strained:
                events.append(self._build_strained_thursday_bike(week_num, tue, prefix, readiness))
            else:
                events.append(self._build_quality_thursday_bike(week_num, tue, prefix, scale))

            # Wednesday: Aerobic Base Spin
            wed_dur_mins = int(round(65 * scale))
            events.append(self._build_recovery_spin(week_num, wed, prefix, wed_dur_mins))

            # Thursday: SweetSpot / Threshold Ride
            if is_strained:
                events.append(self._build_recovery_spin(week_num, thu, prefix, 45))
            else:
                events.append(self._build_cycling_threshold(week_num, thu, prefix, scale))

            # Friday: Active Recovery Spin
            fri_dur_mins = int(round(45 * scale))
            events.append(self._build_recovery_spin(week_num, fri, prefix, fri_dur_mins))

            # Saturday: Long Endurance Ride
            sat_dur_mins = int(round(210 * (0.8 if is_strained else 1.0) * scale))
            events.append(self._build_long_ride(week_num, sat, prefix, sat_dur_mins, is_strained))

            # Sunday: Mixed Tempo Ride
            sun_dur_mins = int(round(120 * scale))
            events.append(self._build_long_ride(week_num, sun, prefix, sun_dur_mins, is_strained))

        else:
            # Dual-Sport Hybrid (balanced running & cycling)
            # Tuesday: Run Quality
            if is_strained:
                events.append(self._build_strained_tuesday_run(week_num, tue, prefix, readiness))
            else:
                events.append(self._build_quality_tuesday_run(week_num, tue, prefix, scale))

            # Wednesday: Aerobic Base Run
            wed_dur_mins = int(round(50 * scale))
            events.append(self._build_aerobic_run(week_num, wed, prefix, wed_dur_mins))

            # Thursday: Bike Quality
            if is_strained:
                events.append(self._build_strained_thursday_bike(week_num, thu, prefix, readiness))
            else:
                events.append(self._build_quality_thursday_bike(week_num, thu, prefix, scale))

            # Friday: Active Recovery Spin
            fri_dur_mins = int(round(40 * scale))
            events.append(self._build_recovery_spin(week_num, fri, prefix, fri_dur_mins))

            # Saturday: Long Endurance Ride
            sat_dur_mins = int(round(180 * (0.8 if is_strained else 1.0) * scale))
            events.append(self._build_long_ride(week_num, sat, prefix, sat_dur_mins, is_strained))

            # Sunday: Long Aerobic Run
            sun_dur_mins = int(round(75 * (0.85 if is_strained else 1.0) * scale))
            events.append(self._build_long_run(week_num, sun, prefix, sun_dur_mins))

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
        day_code = date.strftime("%a").lower()
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week_num} Seiler 4x8m Intervals",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-{day_code}-bike-quality-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_strained_thursday_bike(
        self, week_num: int, date: datetime.date, prefix: str, readiness: Any
    ) -> IntervalsEvent:
        """Recovery spin when fatigue is elevated."""
        day_code = date.strftime("%a").lower()
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
            external_id=f"{prefix}-w{week_num}-{day_code}-bike-adapted-{date.isoformat()}",
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

    def _build_swim_threshold(
        self, week_num: int, date: datetime.date, prefix: str, scale: float
    ) -> IntervalsEvent:
        """Wednesday Swim Critical Swim Speed (CSS) threshold intervals."""
        steps = [
            create_step(6 * 60, "Warmup Swim", hr_start=60, hr_end=70),
            create_step(4 * 60, "Technique Drills", hr_start=65, hr_end=75),
            create_step(8 * 60, "5x 100m CSS Pace", hr_start=88, hr_end=95),
            create_step(4 * 60, "Cooldown Easy", hr_start=55, hr_end=65),
        ]
        dur_mins = calc_duration(steps) // 60
        fuel = calculate_fueling(dur_mins, sport="Swim", intensity="high")
        coaching = (
            f"Target: Lactate threshold and aerobic velocity development (CSS {self.profile.swim_css_sec_100m}s/100m). "
            "Maintain high elbow catch, tight core rotation, and steady bilateral breathing. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 6m 60-70% LTHR Warmup Swim (300m)\n"
            "- 4m 65-75% LTHR Technique Drills (Catch-up & Fingertip)\n"
            "- 8m 88-95% LTHR 5x 100m CSS Pace (20s rest between 100s)\n"
            "- 4m 55-65% LTHR Cooldown Easy (200m)\n"
        )
        day_code = date.strftime("%a").lower()
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Swim",
            name=f"W{week_num} CSS Threshold Swim",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-{day_code}-swim-css-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_swim_aerobic(
        self, week_num: int, date: datetime.date, prefix: str, scale: float
    ) -> IntervalsEvent:
        """Friday continuous aerobic endurance and technique swim."""
        steps = [
            create_step(5 * 60, "Warmup Swim", hr_start=60, hr_end=68),
            create_step(5 * 60, "Bilateral Drills", hr_start=65, hr_end=72),
            create_step(18 * 60, "Zone 2 Continuous", hr_start=68, hr_end=78),
            create_step(4 * 60, "Easy Cooldown", hr_start=55, hr_end=65),
        ]
        dur_mins = calc_duration(steps) // 60
        fuel = calculate_fueling(dur_mins, sport="Swim", intensity="low")
        coaching = (
            f"Target: Aerobic stroke efficiency and feel for the water ({dur_mins} min). "
            "Smooth, continuous Zone 2 pacing. Focus on minimizing drag and maintaining horizontal body position. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 5m 60-68% LTHR Warmup Swim\n"
            "- 5m 65-72% LTHR Bilateral Drills (3-5-7 breathing pattern)\n"
            "- 18m 68-78% LTHR Zone 2 Continuous Swim\n"
            "- 4m 55-65% LTHR Easy Cooldown\n"
        )
        day_code = date.strftime("%a").lower()
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Swim",
            name=f"W{week_num} Aerobic Base Swim",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-{day_code}-swim-aerobic-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_swim_speed(
        self, week_num: int, date: datetime.date, prefix: str, scale: float
    ) -> IntervalsEvent:
        """Tuesday VO2max speed and interval swim."""
        reps = max(8, int(round(12 * scale)))
        steps = [
            create_step(8 * 60, "Warmup Swim", hr_start=60, hr_end=70),
            create_step(4 * 60, "Speed Build 50s", hr_start=70, hr_end=85),
            create_step(reps * 75, f"{reps}x 50m Fast at CSS-4s", hr_start=92, hr_end=98),
            create_step(6 * 60, "Easy Cooldown", hr_start=55, hr_end=65),
        ]
        dur_mins = calc_duration(steps) // 60
        fuel = calculate_fueling(dur_mins, sport="Swim", intensity="high")
        coaching = (
            f"Target: Neuromuscular turnover and VO2max sprint velocity ({reps}x 50m at CSS-4s). "
            "High elbow catch, aggressive kick, and 25s rest between 50m reps. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 8m 60-70% LTHR Warmup Swim\n"
            "- 4m 70-85% LTHR Speed Build 50s\n"
            f"- {reps * 75 // 60}m 92-98% LTHR {reps}x 50m Fast at CSS-4s (25s rest)\n"
            "- 6m 55-65% LTHR Easy Cooldown\n"
        )
        day_code = date.strftime("%a").lower()
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Swim",
            name=f"W{week_num} VO2max Speed Swim",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-{day_code}-swim-speed-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_swim_long(
        self, week_num: int, date: datetime.date, prefix: str, scale: float, is_strained: bool
    ) -> IntervalsEvent:
        """Saturday Long Aerobic Endurance Swim."""
        dur_mins = int(round(55 * scale * (0.85 if is_strained else 1.0)))
        steps = [
            create_step(6 * 60, "Warmup Swim", hr_start=60, hr_end=68),
            create_step((dur_mins - 12) * 60, "Long Aerobic Zone 2", hr_start=68, hr_end=78),
            create_step(6 * 60, "Cooldown Easy", hr_start=55, hr_end=65),
        ]
        fuel = calculate_fueling(dur_mins, sport="Swim", intensity="moderate")
        coaching = (
            f"Target: Mitochondrial density, stroke efficiency, and pacing stamina ({dur_mins} min). "
            "Hold steady CSS+6-10s pace with minimal rest pauses. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 6m 60-68% LTHR Warmup Swim\n"
            f"- {dur_mins - 12}m 68-78% LTHR Continuous Aerobic Base\n"
            "- 6m 55-65% LTHR Cooldown Easy\n"
        )
        day_code = date.strftime("%a").lower()
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Swim",
            name=f"W{week_num} Long Aerobic Swim",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-{day_code}-swim-long-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_swim_recovery(
        self, week_num: int, date: datetime.date, prefix: str
    ) -> IntervalsEvent:
        """Active recovery and technique swim for strained or recovery days."""
        steps = [
            create_step(10 * 60, "Gentle Warmup", hr_start=55, hr_end=65),
            create_step(15 * 60, "Drill & Sculling", hr_start=60, hr_end=70),
            create_step(10 * 60, "Relaxed Cooldown", hr_start=50, hr_end=60),
        ]
        dur_mins = 35
        fuel = calculate_fueling(dur_mins, sport="Swim", intensity="low")
        coaching = (
            "Target: Active parasympathetic recovery and sensory feel for the water (35 min). "
            "Gentle sculling, single-arm drills, and relaxed bilateral breathing. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 10m 55-65% LTHR Gentle Warmup\n"
            "- 15m 60-70% LTHR Drill & Sculling\n"
            "- 10m 50-60% LTHR Relaxed Cooldown\n"
        )
        day_code = date.strftime("%a").lower()
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T07:00:00",
            category="WORKOUT",
            type="Swim",
            name=f"W{week_num} Technique & Recovery Swim",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-{day_code}-swim-recovery-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_brick_session(
        self, week_num: int, date: datetime.date, prefix: str, scale: float, is_strained: bool
    ) -> IntervalsEvent:
        """Saturday Bike-to-Run Brick workout for multisport race-day transition."""
        ride_mins = int(round(120 * scale * (0.85 if is_strained else 1.0)))
        run_mins = int(round(20 * scale))
        steps = [
            create_step(15 * 60, "Warmup Spin", hr_start=55, hr_end=65),
            create_step((ride_mins - 25) * 60, "Zone 2 Steady Ride", hr_start=68, hr_end=78, p_start=65, p_end=78),
            create_step(10 * 60, "Spin Out T2 Prep", hr_start=60, hr_end=70),
            create_step(run_mins * 60, "Transition Run", hr_start=75, hr_end=85),
        ]
        total_mins = ride_mins + run_mins
        fuel = calculate_fueling(total_mins, sport="Brick", intensity="moderate")
        coaching = (
            f"Target: Multisport race simulation and neuromuscular adaptation ({total_mins} min). "
            f"Ride {ride_mins} min in Zone 2, then immediately transition to a {run_mins} min off-the-bike run at target race pace. "
            "Practice fast cadence (180 spm) off the bike to counteract heavy quads. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            f"- 15m 55-65% LTHR Warmup Spin\n"
            f"- {ride_mins - 25}m 68-78% LTHR Zone 2 Steady Ride\n"
            "- 10m 60-70% LTHR Spin Out T2 Prep\n"
            f"- {run_mins}m 75-85% LTHR Transition Run off the bike\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:00:00",
            category="WORKOUT",
            type="Brick",
            name=f"W{week_num} Brick (Bike + Transition Run)",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-sat-brick-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_tempo_run(
        self, week_num: int, date: datetime.date, prefix: str, dur_mins: int
    ) -> IntervalsEvent:
        """Thursday threshold / tempo run for running-focused microcycle."""
        work_mins = max(15, dur_mins - 20)
        steps = [
            create_step(10 * 60, "Warmup Jog", hr_start=60, hr_end=72),
            create_step(work_mins * 60, "Lactate Threshold", hr_start=88, hr_end=93),
            create_step(10 * 60, "Cool-down Walk", hr_start=55, hr_end=65),
        ]
        fuel = calculate_fueling(dur_mins, sport="Run", intensity="moderate")
        coaching = (
            f"Target: Lactate clearance and threshold stamina ({work_mins} min at 88-93% LTHR). "
            "Comfortably hard effort. Maintain steady rhythmic breathing (2:2 breathing pattern). "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 10m 60-72% LTHR Warmup Jog\n"
            f"- {work_mins}m 88-93% LTHR Lactate Threshold\n"
            "- 10m 55-65% LTHR Cool-down Walk\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week_num} Threshold Tempo Run",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-thu-tempo-run-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )

    def _build_cycling_threshold(
        self, week_num: int, date: datetime.date, prefix: str, scale: float
    ) -> IntervalsEvent:
        """Thursday SweetSpot / Over-Unders for cycling-focused microcycle."""
        steps = [
            create_step(15 * 60, "Warmup Spin", hr_start=55, hr_end=68, p_start=50, p_end=65),
            create_step(10 * 60, "SweetSpot Rep 1", hr_start=88, hr_end=94, p_start=88, p_end=93),
            create_step(4 * 60, "Spin Recovery", hr_start=55, hr_end=65, p_start=50, p_end=55),
            create_step(10 * 60, "SweetSpot Rep 2", hr_start=88, hr_end=94, p_start=88, p_end=93),
            create_step(4 * 60, "Spin Recovery", hr_start=55, hr_end=65, p_start=50, p_end=55),
            create_step(10 * 60, "SweetSpot Rep 3", hr_start=88, hr_end=94, p_start=88, p_end=93),
            create_step(10 * 60, "Cool-down Spin", hr_start=50, hr_end=60, p_start=45, p_end=55),
        ]
        dur_mins = calc_duration(steps) // 60
        fuel = calculate_fueling(dur_mins, sport="Ride", intensity="high")
        coaching = (
            "Target: Aerobic power and SweetSpot muscular endurance (3x10 min at 88-93% FTP). "
            "Keep cadence stable between 90-95 rpm. "
            f"Fueling: {fuel.strategy_summary}"
        )
        desc = (
            f"{coaching}\n\n"
            "- 15m 55-68% LTHR Warmup Spin\n"
            "- 3x\n"
            "- 10m 88-94% LTHR SweetSpot Rep\n"
            "- 4m 55-65% LTHR Spin Recovery\n"
            "- 10m 50-60% LTHR Cool-down Spin\n"
        )
        return IntervalsEvent(
            start_date_local=f"{date.isoformat()}T06:30:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week_num} SweetSpot 3x10m Intervals",
            description=desc,
            moving_time=calc_duration(steps),
            external_id=f"{prefix}-w{week_num}-thu-sweetspot-{date.isoformat()}",
            workout_doc=WorkoutDoc(description=coaching, steps=steps),
        )
