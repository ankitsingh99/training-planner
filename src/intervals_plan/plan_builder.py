"""
Plan builder: constructs structured IntervalsEvent instances from Plan specifications.
"""

from datetime import date, timedelta
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
try:
    import yaml
except ImportError:
    yaml = None  # Fallback handled

from intervals_plan.api_models import IntervalsEvent, WorkoutDoc
from intervals_plan.plan_models import PlanConfig, TrainingPlan, WeekSpec
from intervals_plan.workout_schema import (
    calc_duration,
    create_repeat,
    create_step,
    format_duration,
)


def get_default_8wk_plan() -> TrainingPlan:
    """Construct the official 8-week dual-sport plan matching the engineering brief."""
    config = PlanConfig(
        start_date="2026-11-02",
        total_weeks=8,
        prefix="chatgpt-8wk-run-bike-2026-11-02",
        athlete_lthr=164,
        athlete_max_hr=193,
        athlete_resting_hr=52,
        athlete_endurance_hr_min=131,
        athlete_endurance_hr_max=148,
        include_w4_bike=False,  # Deload policy: suppress hard Thursday bike
        include_w8_retest=True, # Explicit 5km time trial retest in Week 8
    )

    weeks = [
        WeekSpec(
            week_number=1,
            phase="Progression",
            run_reps=5,
            run_work_min=3,
            run_recovery_sec=150,
            run_label="5 x 3 min",
            easy_ride_min=40,
            bike_spec={"type": "standard", "reps": 4, "work_sec": 240, "rest_sec": 180, "label": "4 x 4 min"},
        ),
        WeekSpec(
            week_number=2,
            phase="Progression",
            run_reps=4,
            run_work_min=4,
            run_recovery_sec=180,
            run_label="4 x 4 min",
            easy_ride_min=45,
            bike_spec={"type": "microburst", "sets": 2, "reps": 10, "work_sec": 30, "rest_sec": 30, "set_rest_sec": 300, "label": "2 x (10 x 30s hard / 30s easy)"},
        ),
        WeekSpec(
            week_number=3,
            phase="Progression",
            run_reps=5,
            run_work_min=4,
            run_recovery_sec=180,
            run_label="5 x 4 min",
            easy_ride_min=50,
            bike_spec={"type": "microburst", "sets": 3, "reps": 10, "work_sec": 30, "rest_sec": 30, "set_rest_sec": 300, "label": "3 x (10 x 30s hard / 30s easy)"},
        ),
        WeekSpec(
            week_number=4,
            phase="Deload",
            run_reps=4,
            run_work_min=3,
            run_recovery_sec=180,
            run_label="Deload: 4 x 3 min",
            easy_ride_min=35,
            bike_spec=None,  # W4 deload resolved: omit hard intervals to absorb stress
            is_deload=True,
        ),
        WeekSpec(
            week_number=5,
            phase="Progression",
            run_reps=4,
            run_work_min=5,
            run_recovery_sec=210,
            run_label="4 x 5 min",
            easy_ride_min=55,
            bike_spec={"type": "standard", "reps": 5, "work_sec": 240, "rest_sec": 180, "label": "5 x 4 min"},
        ),
        WeekSpec(
            week_number=6,
            phase="Progression",
            run_reps=5,
            run_work_min=4,
            run_recovery_sec=150,
            run_label="5 x 4 min",
            easy_ride_min=60,
            bike_spec={"type": "microburst", "sets": 3, "reps": 13, "work_sec": 30, "rest_sec": 15, "set_rest_sec": 300, "label": "3 x (13 x 30s hard / 15s easy)"},
        ),
        WeekSpec(
            week_number=7,
            phase="Peak",
            run_reps=6,
            run_work_min=4,
            run_recovery_sec=180,
            run_label="6 x 4 min",
            easy_ride_min=60,
            bike_spec={"type": "standard", "reps": 4, "work_sec": 360, "rest_sec": 240, "label": "4 x 6 min"},
        ),
        WeekSpec(
            week_number=8,
            phase="Taper",
            run_reps=3,
            run_work_min=3,
            run_recovery_sec=180,
            run_label="Taper: 3 x 3 min",
            easy_ride_min=40,
            bike_spec=None,  # Taper week: no hard bike intervals
            is_taper=True,
            has_5k_retest=True,  # Explicit 5km retest
        ),
    ]

    return TrainingPlan(
        title="8-Week VO2max + Hypertrophy-Friendly Run/Bike Plan",
        description=(
            "Structured dual-sport progression targeting VO2max and aerobic durability "
            "while respecting strength training recovery and gym rest on Tuesdays."
        ),
        config=config,
        weeks=weeks,
    )


class PlanBuilder:
    def __init__(self, plan: TrainingPlan):
        self.plan = plan

    def build_run_workout(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        steps = [
            create_step(12 * 60, "Warm up very easily; build gradually", hr_start=65, hr_end=80),
            create_repeat(
                week.run_reps,
                f"{week.run_label} — hard but repeatable, approximately 5K effort",
                [
                    create_step(week.run_work_min * 60, "Hard interval; even effort"),
                    create_step(week.run_recovery_sec, "Easy jog or walk recovery"),
                ],
            ),
            create_step(9 * 60, "Easy cool-down"),
        ]
        duration = calc_duration(steps)
        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week.week_number} quality run — {week.run_label}",
            description="Run by effort, not pace. Keep repetitions consistent; do not sprint the first interval. HR may lag during short reps.",
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-mon-run",
            workout_doc=WorkoutDoc(description="VO2-oriented run intervals", steps=steps),
        )

    def build_easy_ride(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        steps = [
            create_step(
                week.easy_ride_min * 60,
                f"Steady conversational aerobic ride; HR {self.plan.config.athlete_endurance_hr_min}–{self.plan.config.athlete_endurance_hr_max} bpm",
            )
        ]
        duration = calc_duration(steps)
        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week.week_number} easy aerobic ride — {week.easy_ride_min} min",
            description=(
                f"{week.easy_ride_min} minutes conversational Zone 2. Keep HR approximately "
                f"{self.plan.config.athlete_endurance_hr_min}–{self.plan.config.athlete_endurance_hr_max} bpm; "
                "back off if it drifts or legs feel heavy. Tuesday is also a gym rest day."
            ),
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-tue-easy-ride",
            workout_doc=WorkoutDoc(description="Easy aerobic endurance", steps=steps),
        )

    def build_optional_bike(self, week: WeekSpec, start_date: date) -> Optional[IntervalsEvent]:
        spec = week.bike_spec
        if not spec:
            return None

        steps = [create_step(10 * 60, "Warm up gradually")]
        if spec.get("type") == "microburst":
            sets = spec["sets"]
            reps = spec["reps"]
            work = spec["work_sec"]
            rest = spec["rest_sec"]
            set_rest = spec.get("set_rest_sec", 300)
            label = spec["label"]

            interval_block = create_repeat(
                reps,
                "Interval block",
                [
                    create_step(work, "Hard, controlled effort; RPE 8–9"),
                    create_step(rest, "Very easy spinning"),
                ],
            )
            set_block = create_repeat(
                sets,
                f"{label} — repeat sets",
                [interval_block, create_step(set_rest, "Easy spin between blocks")],
            )
            steps.append(set_block)
        else:
            reps = spec["reps"]
            work = spec["work_sec"]
            rest = spec["rest_sec"]
            label = spec["label"]
            steps.append(
                create_repeat(
                    reps,
                    label,
                    [
                        create_step(work, "Hard but repeatable; RPE 8–9"),
                        create_step(rest, "Very easy spinning"),
                    ],
                )
            )

        steps.append(create_step(8 * 60, "Easy cool-down"))
        duration = calc_duration(steps)
        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week.week_number} OPTIONAL bike VO2 — {spec['label']}",
            description=(
                "OPTIONAL, not an extra obligation. Do this only if the weekend club ride "
                "will be easy/moderate and recovery is good. If the club ride is hard, skip "
                "this session entirely. Keep efforts repeatable, not all-out."
            ),
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-thu-optional-bike",
            workout_doc=WorkoutDoc(description="Optional bike VO2 intervals", steps=steps),
        )

    def build_club_ride_note(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="NOTE",
            type="Ride",
            name=f"W{week.week_number} weekend club ride — flexible day",
            description=(
                "Target: approximately 50 km, about 3 hours including stops. "
                "Move this reminder to Sunday if that is the club ride day. "
                "If the ride is hard, it replaces Thursday's optional bike intervals; "
                "do not do both hard sessions."
            ),
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-weekend-club-ride",
        )

    def build_5k_retest(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        steps = [
            create_step(10 * 60, "Warm up easily; 3-4 gentle accelerations"),
            create_step(30 * 60, "5 km Time Trial — even pace, best sustainable effort"),
            create_step(10 * 60, "Easy jog/walk cool-down"),
        ]
        duration = calc_duration(steps)
        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week.week_number} 5 km Time Trial Retest",
            description=(
                "Benchmark run to evaluate VO2max and threshold progression after 8 weeks. "
                "Aim for consistent pacing through the first 3 km, then finish strong."
            ),
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-sat-5k-retest",
            workout_doc=WorkoutDoc(description="5 km benchmark retest", steps=steps),
        )

    def build_all_events(self) -> List[IntervalsEvent]:
        """Generate all planned events across all weeks."""
        start = date.fromisoformat(self.plan.config.start_date)
        events: List[IntervalsEvent] = []

        for w in self.plan.weeks:
            monday = start + timedelta(days=7 * (w.week_number - 1))
            
            # Monday quality run
            events.append(self.build_run_workout(w, monday))

            # Tuesday easy ride
            tuesday = monday + timedelta(days=1)
            events.append(self.build_easy_ride(w, tuesday))

            # Thursday optional bike intervals
            thursday = monday + timedelta(days=3)
            bike = self.build_optional_bike(w, thursday)
            if bike:
                events.append(bike)

            # Weekend club ride
            sat_offset = 6 if self.plan.config.club_ride_default_day.lower() == "sunday" else 5
            weekend_day = monday + timedelta(days=sat_offset)
            
            # If Week 8 has 5k retest, schedule retest on Saturday and flexible ride/rest
            if w.has_5k_retest and self.plan.config.include_w8_retest:
                retest_day = monday + timedelta(days=5) # Saturday
                events.append(self.build_5k_retest(w, retest_day))
            
            events.append(self.build_club_ride_note(w, weekend_day))

        return events

