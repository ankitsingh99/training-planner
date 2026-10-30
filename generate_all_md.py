#!/usr/bin/env python3
"""
Generate a comprehensive markdown document detailing all workouts and notes in the 8-week plan.
"""

from upload_intervals_plan import make_events


def format_duration(seconds):
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    mins = seconds // 60
    secs = seconds % 60
    if mins > 0 and secs > 0:
        return f"{mins}m {secs}s ({seconds}s)"
    elif mins > 0:
        return f"{mins}m ({seconds}s)"
    else:
        return f"{seconds}s"


def format_step_lines(steps, indent_level=0):
    lines = []
    prefix = "  " * indent_level
    for step in steps:
        text = step.get("text", "")
        duration = step.get("duration")
        reps = step.get("reps")
        hr = step.get("hr")

        meta = []
        if duration is not None:
            meta.append(format_duration(duration))
        if hr:
            start = hr.get("start")
            end = hr.get("end")
            units = hr.get("units", "%")
            meta.append(f"HR: {start}–{end} {units}")

        meta_str = f" [{', '.join(meta)}]" if meta else ""

        if reps and "steps" in step:
            lines.append(f"{prefix}- **{reps}x Repeat:** {text}{meta_str}")
            lines.extend(format_step_lines(step["steps"], indent_level + 1))
        else:
            lines.append(f"{prefix}- {text}{meta_str}")
    return lines


def format_event(ev):
    lines = []
    lines.append(f"## {ev.get('name')} — `{ev.get('start_date_local')}`\n")
    lines.append(f"- **Type:** {ev.get('type')}")
    lines.append(f"- **Category:** {ev.get('category')}")
    lines.append(f"- **Duration:** {format_duration(ev.get('moving_time'))}")
    lines.append(f"- **External ID:** `{ev.get('external_id')}`")
    lines.append(f"- **Description:** {ev.get('description')}\n")

    workout_doc = ev.get("workout_doc")
    if workout_doc and "steps" in workout_doc:
        lines.append("### Workout Structure")
        lines.extend(format_step_lines(workout_doc["steps"]))
        lines.append("")

    lines.append("---\n")
    return "\n".join(lines)


def main():
    events = make_events()
    with open("ALL_WORKOUTS.md", "w", encoding="utf-8") as f:
        f.write("# Complete 8-Week Training Plan\n\n")
        f.write(
            "This document contains all 30 planned activities and notes across the 8-week block "
            "(2026-11-02 to 2026-12-27).\n\n---\n\n"
        )
        for ev in events:
            f.write(format_event(ev))
    print(f"Generated ALL_WORKOUTS.md with {len(events)} events.")


if __name__ == "__main__":
    main()
