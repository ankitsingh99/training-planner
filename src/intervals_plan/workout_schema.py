"""
Workout schema validation, step creation, and duration calculation.
"""

from typing import Any, Dict, List, Optional, Union
from intervals_plan.api_models import HRTarget, WorkoutDoc, WorkoutStep


def calc_duration(step_or_list: Union[WorkoutStep, List[WorkoutStep], Dict[str, Any], List[Dict[str, Any]]]) -> int:
    """Recursively calculate total duration in seconds for steps and repeat blocks."""
    if isinstance(step_or_list, list):
        return sum(calc_duration(s) for s in step_or_list)
    
    # If it's a WorkoutStep instance
    if isinstance(step_or_list, WorkoutStep):
        if step_or_list.duration is not None:
            return int(step_or_list.duration)
        if step_or_list.steps:
            reps = int(step_or_list.reps or 1)
            return reps * sum(calc_duration(s) for s in step_or_list.steps)
        return 0

    # If it's a dict
    if isinstance(step_or_list, dict):
        if "duration" in step_or_list and step_or_list["duration"] is not None:
            return int(step_or_list["duration"])
        if "steps" in step_or_list and isinstance(step_or_list["steps"], list):
            reps = int(step_or_list.get("reps", 1))
            return reps * sum(calc_duration(s) for s in step_or_list["steps"])
        return 0

    return 0


def format_duration(seconds: Optional[int]) -> str:
    """Convert seconds into a clean human-readable duration like '48m 30s'."""
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    mins = seconds // 60
    secs = seconds % 60
    if mins > 0 and secs > 0:
        return f"{mins}m {secs}s"
    elif mins > 0:
        return f"{mins}m"
    return f"{seconds}s"


def create_step(
    seconds: int,
    text: str,
    hr_start: Optional[float] = None,
    hr_end: Optional[float] = None,
    hr_units: str = "%lthr",
    p_start: Optional[float] = None,
    p_end: Optional[float] = None,
    p_units: str = "%ftp",
) -> WorkoutStep:
    """Helper to create a single duration-based step with optional HR and Power targets."""
    hr = None
    if hr_start is not None or hr_end is not None:
        hr = HRTarget(start=hr_start, end=hr_end, units=hr_units)

    power = None
    if p_start is not None or p_end is not None:
        power = {"units": p_units}
        if p_start is not None:
            power["start"] = p_start
        if p_end is not None:
            power["end"] = p_end

    return WorkoutStep(duration=int(seconds), text=text, hr=hr, power=power)


def create_repeat(reps: int, text: str, sub_steps: List[WorkoutStep]) -> WorkoutStep:
    """Helper to create a repetition block of steps."""
    return WorkoutStep(reps=int(reps), text=text, steps=sub_steps)


def steps_to_intervals_text(steps: List[WorkoutStep], indent: int = 0) -> List[str]:
    """Generate textual representation of steps matching Intervals.icu workout syntax."""
    lines: List[str] = []
    prefix = "  " * indent
    for s in steps:
        dur_str = f"{s.duration // 60}m" if (s.duration and s.duration % 60 == 0) else f"{s.duration}s"
        hr_str = f" {s.hr.start}-{s.hr.end}{s.hr.units}" if (s.hr and s.hr.start and s.hr.end) else ""
        if s.reps and s.steps:
            lines.append(f"{prefix}- {s.reps}x {s.text}")
            lines.extend(steps_to_intervals_text(s.steps, indent + 1))
        elif s.duration:
            lines.append(f"{prefix}- {dur_str}{hr_str} {s.text}".strip())
        else:
            lines.append(f"{prefix}- {s.text}".strip())
    return lines

