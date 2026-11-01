#!/usr/bin/env python3
"""
Generate a complete, beautiful Markdown document containing all workouts in the 8-week plan.

Outputs by default to both PLAN.md and ALL_WORKOUTS.md.
"""

import argparse
import pathlib
import re
import sys
from datetime import datetime

# Add src to path to import intervals_plan
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

try:
    from intervals_plan.plan_builder import PlanBuilder, get_default_8wk_plan
    USE_SRC_BUILDER = True
except ImportError:
    from upload_intervals_plan import make_events
    USE_SRC_BUILDER = False


def format_duration(seconds):
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    mins = seconds // 60
    secs = seconds % 60
    if mins > 0 and secs > 0:
        return f"{mins}m {secs}s"
    elif mins > 0:
        return f"{mins}m"
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


def build_markdown_document(events):
    lines = []
    lines.append("# 8-Week Run & Bike Comprehensive Training Plan\n")
    lines.append(
        "A structured 8-week dual-sport progression designed to build VO2 max, aerobic endurance, "
        "and durability without accumulated burnout.\n"
    )

    # Summary table
    lines.append("## Overview Schedule\n")
    lines.append("| Week | Monday (Quality Run) | Tuesday (Aerobic Ride) | Thursday (Optional VO2 Bike) | Weekend (Club Ride) |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")

    weeks = {}
    for ev in events:
        w = int(ev["name"].split()[0][1:])
        weeks.setdefault(w, []).append(ev)

    for w in sorted(weeks.keys()):
        evs = weeks[w]
        mon = next((f"{re.split(r'[-—:]', e['name'])[-1].strip()} ({format_duration(e.get('moving_time'))})" for e in evs if "mon-run" in e.get("external_id", "")), "Rest")
        tue = next((f"Zone 2 ({format_duration(e.get('moving_time'))})" for e in evs if "tue-easy-ride" in e.get("external_id", "")), "Rest")
        thu = next((f"{re.split(r'[-—:]', e['name'])[-1].strip()} ({format_duration(e.get('moving_time'))})" for e in evs if "thu-optional-bike" in e.get("external_id", "")), "*Rest / Recovery*")
        sat = next(("~50 km (~3h flexible)" for e in evs if "weekend-club-ride" in e.get("external_id", "")), "None")
        
        note = " (Deload)" if w == 4 else (" (Peak)" if w == 7 else (" (Taper)" if w == 8 else ""))
        lines.append(f"| **Week {w}{note}** | {mon} | {tue} | {thu} | {sat} |")

    lines.append("\n---\n")

    # Intensity & Training Guidelines
    lines.append("## Training Guidelines & Intensity Zones\n")
    lines.append("- **Monday Quality Runs:** VO2 max intervals. Run by effort (approx. 5K race pace / RPE 8–9). HR may lag on short reps—do not sprint the first rep.")
    lines.append("- **Tuesday Easy Aerobic Rides:** True conversational Zone 2 (HR ~131–148 bpm). Back off immediately if heart rate drifts.")
    lines.append("- **Thursday Optional Bike Intervals:** High-intensity VO2 intervals. **Strictly optional:** skip this workout if your weekend club ride is hard or if overall fatigue is elevated.")
    lines.append("- **Weekend Club Ride:** ~50 km endurance ride (approx. 3 hours including coffee/group stops). Can be moved between Saturday and Sunday as needed.")
    lines.append("- **Deload & Taper (Weeks 4 & 8):** Hard Thursday bike sessions are removed to absorb training stress and allow supercompensation.")
    lines.append("\n---\n")

    # Detailed Weekly Breakdown
    lines.append("## Detailed Workouts by Week\n")

    for w in sorted(weeks.keys()):
        evs = weeks[w]
        phase = "Deload Phase" if w == 4 else ("Peak Training Phase" if w == 7 else ("Taper Phase" if w == 8 else "Progression Phase"))
        lines.append(f"### Week {w} — {phase}\n")

        for ev in evs:
            dt = ev.get("start_date_local", "").split("T")[0]
            weekday = datetime.strptime(dt, "%Y-%m-%d").strftime("%A")
            name = ev.get("name")
            category = ev.get("category")
            sport = ev.get("type")
            duration = format_duration(ev.get("moving_time"))

            lines.append(f"#### {weekday}, {dt}: {name}\n")
            lines.append(f"- **Type:** {sport}")
            lines.append(f"- **Category:** {category}")
            if ev.get("moving_time"):
                lines.append(f"- **Total Duration:** {duration} ({ev.get('moving_time')}s)")
            lines.append(f"- **Focus:** {ev.get('description')}\n")

            workout_doc = ev.get("workout_doc")
            if workout_doc and "steps" in workout_doc:
                lines.append("**Workout Structure:**")
                lines.extend(format_step_lines(workout_doc["steps"]))
                lines.append("")

        lines.append("---\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate complete Markdown training plan document.")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Specific output markdown file path. If omitted, writes to both PLAN.md and ALL_WORKOUTS.md.",
    )
    args = parser.parse_args()

    if USE_SRC_BUILDER:
        builder = PlanBuilder(get_default_8wk_plan())
        raw_events = builder.build_all_events()
        events = [e.to_dict() for e in raw_events]
    else:
        events = make_events()
    content = build_markdown_document(events)

    if args.output:
        targets = [pathlib.Path(args.output)]
    else:
        root = pathlib.Path(__file__).parent
        targets = [root / "PLAN.md", root / "ALL_WORKOUTS.md"]

    for target in targets:
        target.write_text(content, encoding="utf-8")
        print(f" Generated {target.name} ({len(events)} workouts included).")


if __name__ == "__main__":
    main()
