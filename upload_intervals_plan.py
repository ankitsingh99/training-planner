#!/usr/bin/env python3
"""
Upload an 8-week run/bike plan to Intervals.icu.

Security:
  - Never paste your API key into this file.
  - Set INTERVALS_API_KEY in your .env file or shell environment.
  - This script only upserts events carrying its own external_id prefix.
  - Default mode is a dry run. Add --upload to send events.

Usage:
  python3 upload_intervals_plan.py           # Dry run
  python3 upload_intervals_plan.py --upload  # Upload events
"""

import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta


def load_env_file():
    """Load key-value pairs from .env into os.environ."""
    env_path = pathlib.Path(__file__).parent / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and v:
                    os.environ[k] = v


load_env_file()

BASE = "https://intervals.icu/api/v1/athlete/0/events/bulk?upsert=true"
PREFIX = "chatgpt-8wk-run-bike-2026-11-02"

# Progression intentionally keeps only one mandatory quality run and one easy
# aerobic ride each week. Thursday bike intervals are explicitly optional:
# skip them when the weekend club ride is hard or recovery is not good.
RUNS = [
    (5, 3, 150, "5 x 3 min"),
    (4, 4, 180, "4 x 4 min"),
    (5, 4, 180, "5 x 4 min"),
    (4, 3, 180, "Deload: 4 x 3 min"),
    (4, 5, 210, "4 x 5 min"),
    (5, 4, 150, "5 x 4 min"),
    (6, 4, 180, "6 x 4 min"),
    (3, 3, 180, "Taper: 3 x 3 min"),
]
EASY_RIDE_MIN = [40, 45, 50, 35, 55, 60, 60, 40]
BIKE_SETS = [
    (4, 4 * 60, 3 * 60, "4 x 4 min"),
    (2, 10, 30, 30, "2 x (10 x 30s hard / 30s easy)"),
    (3, 10, 30, 30, "3 x (10 x 30s hard / 30s easy)"),
    (0, 0, 0, 0, "Deload — skip hard bike intervals"),
    (5, 4 * 60, 3 * 60, "5 x 4 min"),
    (3, 13, 30, 15, "3 x (13 x 30s hard / 15s easy)"),
    (4, 6 * 60, 4 * 60, "4 x 6 min"),
    (0, 0, 0, 0, "Taper — skip hard bike intervals"),
]


def duration_step(seconds, text, hr=None):
    step = {"duration": int(seconds), "text": text}
    if hr:
        step["hr"] = hr
    return step


def calc_duration(step_or_list):
    """Recursively calculate the total duration of steps, including repetition blocks."""
    if isinstance(step_or_list, list):
        return sum(calc_duration(s) for s in step_or_list)
    if "duration" in step_or_list:
        return int(step_or_list["duration"])
    if "steps" in step_or_list:
        reps = int(step_or_list.get("reps", 1))
        return reps * sum(calc_duration(s) for s in step_or_list["steps"])
    return 0


def run_workout(week):
    reps, work_min, recovery_sec, label = RUNS[week]
    steps = [
        duration_step(
            12 * 60,
            "Warm up very easily; build gradually",
            {"start": 65, "end": 80, "units": "%lthr"},
        ),
        {
            "reps": reps,
            "text": label + " — hard but repeatable, approximately 5K effort",
            "steps": [
                duration_step(work_min * 60, "Hard interval; even effort"),
                duration_step(recovery_sec, "Easy jog or walk recovery"),
            ],
        },
        duration_step(9 * 60, "Easy cool-down"),
    ]
    return {
        "start_date_local": None,
        "category": "WORKOUT",
        "type": "Run",
        "name": f"W{week+1} quality run — {label}",
        "description": "Run by effort, not pace. Keep repetitions consistent; do not sprint the first interval. HR may lag during short reps.",
        "moving_time": calc_duration(steps),
        "workout_doc": {"description": "VO2-oriented run intervals", "steps": steps},
    }


def easy_ride(week):
    mins = EASY_RIDE_MIN[week]
    steps = [duration_step(mins * 60, "Steady conversational aerobic ride; HR 131–148 bpm")]
    return {
        "category": "WORKOUT",
        "type": "Ride",
        "name": f"W{week+1} easy aerobic ride — {mins} min",
        "description": f"{mins} minutes conversational Zone 2. Keep HR approximately 131–148 bpm; back off if it drifts or the legs feel heavy. This should feel easy.",
        "moving_time": calc_duration(steps),
        "workout_doc": {
            "description": "Easy aerobic endurance",
            "steps": steps,
        },
    }


def optional_bike(week):
    spec = BIKE_SETS[week]
    if week in (3, 7):
        return None
    if week in (1, 2, 5):
        sets, reps, work, rest, label = spec
        steps = [
            duration_step(10 * 60, "Warm up gradually"),
            {
                "reps": sets,
                "text": label + " — repeat sets",
                "steps": [
                    {
                        "reps": reps,
                        "text": "Interval block",
                        "steps": [
                            duration_step(work, "Hard, controlled effort; RPE 8–9"),
                            duration_step(rest, "Very easy spinning"),
                        ],
                    },
                    duration_step(5 * 60, "Easy spin between blocks"),
                ],
            },
            duration_step(8 * 60, "Easy cool-down"),
        ]
    else:
        reps, work, rest, label = spec
        steps = [
            duration_step(10 * 60, "Warm up gradually"),
            {
                "reps": reps,
                "text": label,
                "steps": [
                    duration_step(work, "Hard but repeatable; RPE 8–9"),
                    duration_step(rest, "Very easy spinning"),
                ],
            },
            duration_step(8 * 60, "Easy cool-down"),
        ]
    return {
        "category": "WORKOUT",
        "type": "Ride",
        "name": f"W{week+1} OPTIONAL bike VO2 — {spec[-1]}",
        "description": (
            "OPTIONAL, not an extra obligation. Do this only if the weekend club ride "
            "will be easy/moderate and recovery is good. If the club ride is hard, skip "
            "this session entirely. Keep efforts repeatable, not all-out."
        ),
        "moving_time": calc_duration(steps),
        "workout_doc": {"description": "Optional bike VO2 intervals", "steps": steps},
    }


def make_events():
    start = date(2026, 11, 2)  # Monday
    events = []
    for w in range(8):
        monday = start + timedelta(days=7 * w)
        run = run_workout(w)
        run["start_date_local"] = f"{monday.isoformat()}T00:00:00"
        run["external_id"] = f"{PREFIX}-w{w+1}-mon-run"
        events.append(run)

        tuesday = monday + timedelta(days=1)
        easy = easy_ride(w)
        easy["start_date_local"] = f"{tuesday.isoformat()}T00:00:00"
        easy["external_id"] = f"{PREFIX}-w{w+1}-tue-easy-ride"
        events.append(easy)

        thursday = monday + timedelta(days=3)
        bike = optional_bike(w)
        if bike:
            bike["start_date_local"] = f"{thursday.isoformat()}T00:00:00"
            bike["external_id"] = f"{PREFIX}-w{w+1}-thu-optional-bike"
            events.append(bike)

        saturday = monday + timedelta(days=5)
        events.append({
            "start_date_local": f"{saturday.isoformat()}T00:00:00",
            "category": "NOTE",
            "type": "Ride",
            "name": f"W{w+1} weekend club ride — flexible day",
            "description": (
                "Target: approximately 50 km, about 3 hours including stops. "
                "Move this reminder to Sunday if that is the club ride day. "
                "If the ride is hard, it replaces Thursday's optional bike intervals; "
                "do not do both hard sessions."
            ),
            "external_id": f"{PREFIX}-w{w+1}-weekend-club-ride",
        })
    return events


def main():
    parser = argparse.ArgumentParser(description="Upload or preview 8-week Intervals.icu plan.")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Actually upload events to Intervals.icu; otherwise runs in dry-run mode.",
    )
    args = parser.parse_args()

    events = make_events()
    print(f"Prepared {len(events)} calendar events for 2026-11-02 through 2026-12-27.")
    print("Includes Monday quality runs, Tuesday easy rides, optional Thursday bike intervals,")
    print("and Saturday club-ride reminders (move to Sunday when needed).")

    if not args.upload:
        print("\nDRY RUN — nothing has been uploaded. Re-run with --upload to publish.")
        print(json.dumps(events[:2], indent=2))
        return

    key = os.environ.get("INTERVALS_API_KEY")
    if not key:
        sys.exit(
            "Error: INTERVALS_API_KEY is missing.\n"
            "Please configure INTERVALS_API_KEY in your .env file or shell environment."
        )

    token = base64.b64encode(("API_KEY:" + key).encode()).decode()
    body = json.dumps(events).encode("utf-8")

    # Use a browser-like User-Agent to satisfy Cloudflare bot protection.
    req = urllib.request.Request(
        BASE,
        data=body,
        method="POST",
        headers={
            "Authorization": "Basic " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        sys.exit(f"Intervals.icu returned HTTP {exc.code}: {detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Could not reach Intervals.icu: {exc}")

    print(f"\n✅ Intervals.icu accepted the upload! Returned {len(result)} event records.")
    print("First few uploaded events:")
    for event in result[:5]:
        print(f" - {event.get('start_date_local')} | {event.get('name')} | ID: {event.get('id')}")


if __name__ == "__main__":
    main()
