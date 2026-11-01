"""
Plan builder: constructs structured IntervalsEvent instances with full coaching guidance
and Intervals.icu workout DSL text in the description.
"""

from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

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
                    create_step(week.run_work_min * 60, "Hard interval; even effort", hr_start=100, hr_end=112),
                    create_step(week.run_recovery_sec, "Easy jog or walk recovery", hr_start=60, hr_end=70),
                ],
            ),
            create_step(9 * 60, "Easy cool-down", hr_start=60, hr_end=70),
        ]
        duration = calc_duration(steps)
        recovery_m = week.run_recovery_sec // 60
        recovery_s = week.run_recovery_sec % 60
        rec_str = f"{recovery_m}m{recovery_s}s" if recovery_s else f"{recovery_m}m"

        desc = (
            f"🎯 Focus: VO2 max interval progression ({week.phase} phase).\n"
            f"💡 How to execute: Run by effort (approx. 5K race pace / RPE 8–9). Keep repetitions consistent—do NOT sprint the first rep. "
            f"Heart rate lags during short reps; trust your perceived effort. Recover completely with easy jogging or walking.\n\n"
            f"Warmup\n"
            f"- 12m ramp 65-80% LTHR Warm up very easily; build gradually\n\n"
            f"{week.run_reps}x\n"
            f"- {week.run_work_min}m 100-112% LTHR Hard interval; even 5K effort (RPE 8-9)\n"
            f"- {rec_str} 60-70% LTHR Easy jog or walk recovery\n\n"
            f"Cooldown\n"
            f"- 9m 60-70% LTHR Easy cool-down jog / walk\n"
        )

        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week.week_number} quality run — {week.run_label}",
            description=desc,
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-mon-run",
            workout_doc=WorkoutDoc(description="VO2-oriented run intervals", steps=steps),
        )

    def build_easy_ride(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        steps = [
            create_step(
                week.easy_ride_min * 60,
                f"Steady conversational aerobic ride; HR {self.plan.config.athlete_endurance_hr_min}–{self.plan.config.athlete_endurance_hr_max} bpm",
                hr_start=60,
                hr_end=72,
            )
        ]
        duration = calc_duration(steps)

        desc = (
            f"🎯 Focus: Aerobic base development & active recovery (Zone 2).\n"
            f"💡 How to execute: True conversational effort (Talk Test). You should be able to speak in full sentences without gasping. "
            f"Keep heart rate strictly in the endurance zone ({self.plan.config.athlete_endurance_hr_min}–{self.plan.config.athlete_endurance_hr_max} bpm). "
            f"If heart rate drifts upward or legs feel heavy, back off immediately.\n\n"
            f"⚠️ Gym Note: Tuesday is a dedicated gym rest day to ensure full muscular recovery for hypertrophy.\n\n"
            f"- {week.easy_ride_min}m 60-72% LTHR Steady conversational Zone 2 (HR {self.plan.config.athlete_endurance_hr_min}-{self.plan.config.athlete_endurance_hr_max} bpm)\n"
        )

        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week.week_number} easy aerobic ride — {week.easy_ride_min} min",
            description=desc,
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-tue-easy-ride",
            workout_doc=WorkoutDoc(description="Easy aerobic endurance", steps=steps),
        )

    def build_optional_bike(self, week: WeekSpec, start_date: date) -> Optional[IntervalsEvent]:
        spec = week.bike_spec
        if not spec:
            return None

        steps = [create_step(10 * 60, "Warm up gradually", hr_start=50, hr_end=75)]
        
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
                    create_step(work, "Hard, controlled effort; RPE 8–9", hr_start=110, hr_end=125),
                    create_step(rest, "Very easy spinning", hr_start=50, hr_end=60),
                ],
            )
            set_block = create_repeat(
                sets,
                f"{label} — repeat sets",
                [interval_block, create_step(set_rest, "Easy spin between blocks", hr_start=50, hr_end=60)],
            )
            steps.append(set_block)

            desc = (
                f"🎯 Focus: Anaerobic capacity & high-cadence VO2 microbursts ({label}).\n"
                f"💡 How to execute: 30 seconds hard effort (cadence 95-105 rpm, RPE 8-9) alternating with brief recoveries. "
                f"Take the full 5-minute easy spin between blocks.\n\n"
                f"⚠️ Strictly Optional: Do this session ONLY if your legs feel fresh and the weekend club ride will be moderate. "
                f"If the weekend ride is hard, skip this session or replace it with a 30-minute easy recovery spin.\n\n"
                f"Warmup\n"
                f"- 10m ramp 50-75% LTHR Warm up gradually\n\n"
                f"{sets}x\n"
                f"{reps}x\n"
                f"- {work}s 115-125% LTHR Hard, controlled effort (RPE 8-9)\n"
                f"- {rest}s 50-60% LTHR Very easy spinning recovery\n\n"
                f"- 5m 50-60% LTHR Easy spin between blocks\n\n"
                f"Cooldown\n"
                f"- 8m 50% LTHR Easy cool-down\n"
            )
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
                        create_step(work, "Hard but repeatable; RPE 8–9", hr_start=105, hr_end=115),
                        create_step(rest, "Very easy spinning", hr_start=50, hr_end=60),
                    ],
                )
            )
            work_m = work // 60
            rest_m = rest // 60

            desc = (
                f"🎯 Focus: Sustained aerobic power / VO2 intervals ({label}).\n"
                f"💡 How to execute: Smooth, controlled high power (RPE 8-9). Aim for even power/effort across all reps—do not blow up on rep 1. "
                f"Spin very lightly during recoveries to clear lactate.\n\n"
                f"⚠️ Strictly Optional: Do this session ONLY if your legs feel fresh and the weekend club ride will be moderate. "
                f"If the weekend ride is hard, skip this session entirely.\n\n"
                f"Warmup\n"
                f"- 10m ramp 50-75% LTHR Warm up gradually\n\n"
                f"{reps}x\n"
                f"- {work_m}m 105-115% LTHR Hard but repeatable interval (RPE 8-9)\n"
                f"- {rest_m}m 50-60% LTHR Very easy spinning recovery\n\n"
                f"Cooldown\n"
                f"- 8m 50% LTHR Easy cool-down\n"
            )

        steps.append(create_step(8 * 60, "Easy cool-down", hr_start=50, hr_end=60))
        duration = calc_duration(steps)

        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Ride",
            name=f"W{week.week_number} OPTIONAL bike VO2 — {spec['label']}",
            description=desc,
            moving_time=duration,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-thu-optional-bike",
            workout_doc=WorkoutDoc(description="Optional bike VO2 intervals", steps=steps),
        )

    def build_club_ride_note(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        desc = (
            f"🎯 Focus: Endurance volume, group skills, and social riding.\n"
            f"📍 Route Target: Approximately 50 km, roughly 3 hours total time including coffee and regrouping stops.\n"
            f"💡 Execution Guidelines: Group pace will vary. Stay tucked in the draft on headwinds/flats to conserve energy. "
            f"Keep fueling (30-60g carbs/hour) and stay hydrated.\n\n"
            f"⚠️ Replacement Rule: If the club ride turns hard (lots of surging/threshold climbing), "
            f"it replaces Thursday's optional hard bike intervals. Move this reminder to Sunday if that is your group's ride day."
        )
        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="NOTE",
            type="Ride",
            name=f"W{week.week_number} weekend club ride — flexible day",
            description=desc,
            external_id=f"{self.plan.config.prefix}-w{week.week_number}-weekend-club-ride",
        )

    def build_5k_retest(self, week: WeekSpec, start_date: date) -> IntervalsEvent:
        steps = [
            create_step(10 * 60, "Warm up easily; build gradually", hr_start=60, hr_end=75),
            create_step(30 * 60, "5 km Time Trial — best sustainable effort", hr_start=100, hr_end=115),
            create_step(10 * 60, "Easy jog/walk cool-down", hr_start=50, hr_end=60),
        ]
        duration = calc_duration(steps)

        desc = (
            f"🏁 BENCHMARK RETEST: 5 km Time Trial (End of Block Assessment).\n"
            f"🎯 Objective: Evaluate changes in VO2 max, threshold pace, and cardiovascular durability after 8 weeks.\n"
            f"💡 Pacing Strategy: Break the 5 km into three parts:\n"
            f"  - Km 1–2: Controlled, disciplined pacing at targeted 5K threshold effort. Do not sprint off the line.\n"
            f"  - Km 3–4: Settle into high cognitive focus; maintain rhythm as fatigue sets in.\n"
            f"  - Km 5: Progressively increase effort and finish strong.\n\n"
            f"Warmup\n"
            f"- 10m ramp 60-75% LTHR Warm up very easily\n"
            f"- 4x 30s 100% LTHR Strides / gentle accelerations with 30s walk recovery\n\n"
            f"5 km Time Trial\n"
            f"- 5km 100-115% LTHR Best sustainable 5 km race effort\n\n"
            f"Cooldown\n"
            f"- 10m 50-60% LTHR Easy cool-down walk and stretch\n"
        )

        return IntervalsEvent(
            start_date_local=f"{start_date.isoformat()}T00:00:00",
            category="WORKOUT",
            type="Run",
            name=f"W{week.week_number} 5 km Time Trial Retest",
            description=desc,
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
            events.append(self.build_run_workout(w, monday))

            tuesday = monday + timedelta(days=1)
            events.append(self.build_easy_ride(w, tuesday))

            thursday = monday + timedelta(days=3)
            bike = self.build_optional_bike(w, thursday)
            if bike:
                events.append(bike)

            sat_offset = 6 if self.plan.config.club_ride_default_day.lower() == "sunday" else 5
            weekend_day = monday + timedelta(days=sat_offset)

            if w.has_5k_retest and self.plan.config.include_w8_retest:
                retest_day = monday + timedelta(days=5)
                events.append(self.build_5k_retest(w, retest_day))

            events.append(self.build_club_ride_note(w, weekend_day))

        return events
