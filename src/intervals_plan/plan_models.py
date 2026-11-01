"""
Domain models and validation for multi-week training plans.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class PlanConfig:
    start_date: str = "2026-11-02"
    total_weeks: int = 8
    prefix: str = "chatgpt-8wk-run-bike-2026-11-02"
    athlete_lthr: int = 164
    athlete_max_hr: int = 193
    athlete_resting_hr: int = 52
    athlete_endurance_hr_min: int = 131
    athlete_endurance_hr_max: int = 148
    include_w4_bike: bool = False  # Resolves W4 deload discrepancy
    include_w8_retest: bool = True # Resolves W8 retest requirement
    club_ride_default_day: str = "Saturday" # Saturday or Sunday


@dataclass
class WeekSpec:
    week_number: int
    phase: str
    run_reps: int
    run_work_min: int
    run_recovery_sec: int
    run_label: str
    easy_ride_min: int
    bike_spec: Optional[Dict[str, Any]] = None
    is_deload: bool = False
    is_taper: bool = False
    has_5k_retest: bool = False


@dataclass
class TrainingPlan:
    title: str
    description: str
    config: PlanConfig = field(default_factory=PlanConfig)
    weeks: List[WeekSpec] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Validate plan constraints and return list of validation errors/warnings."""
        errors: List[str] = []
        if self.config.total_weeks <= 0 or self.config.total_weeks > 52:
            errors.append(f"Invalid total_weeks: {self.config.total_weeks}")

        try:
            date.fromisoformat(self.config.start_date)
        except ValueError:
            errors.append(f"Invalid start_date format: {self.config.start_date}")

        if len(self.weeks) != self.config.total_weeks:
            errors.append(
                f"Mismatch: config specifies {self.config.total_weeks} weeks, but {len(self.weeks)} weeks defined."
            )

        for w in self.weeks:
            if w.run_reps <= 0:
                errors.append(f"Week {w.week_number}: run_reps must be > 0")
            if w.run_work_min <= 0:
                errors.append(f"Week {w.week_number}: run_work_min must be > 0")
            if w.easy_ride_min < 20 or w.easy_ride_min > 180:
                errors.append(f"Week {w.week_number}: easy_ride_min ({w.easy_ride_min}) outside safe aerobic range (20-180m)")

        # Deload check
        deload_weeks = [w.week_number for w in self.weeks if w.is_deload]
        if not deload_weeks:
            errors.append("Plan lacks a scheduled deload week (expected week 4).")

        return errors
