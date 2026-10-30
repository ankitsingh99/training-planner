#!/usr/bin/env python3
"""
Upload an 8-week run/bike plan to Intervals.icu.

Security:
  - Never paste your API key into this file.
  - Set INTERVALS_API_KEY in your shell environment.
  - This script only upserts events carrying its own external_id prefix.
  - Default mode is a dry run. Add --upload to send events.

Usage:
  export INTERVALS_API_KEY='YOUR_NEW_KEY'
  python3 upload_intervals_plan.py
  python3 upload_intervals_plan.py --upload
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta

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
    (4, 4*60, 3*60, "4 x 4 min"),
    (2, 10, 30, 30, "2 x (10 x 30s hard / 30s easy)"),
    (3, 10, 30, 30, "3 x (10 x 30s hard / 30s easy)"),
    (0, 0, 0, 0, "Deload — skip hard bike intervals"),
    (5, 4*60, 3*60, "5 x 4 min"),
    (3, 13, 30, 15, "3 x (13 x 30s hard / 15s easy)"),
    (4, 6*60, 4*60, "4 x 6 min"),
    (0, 0, 0, 0, "Taper — skip hard bike intervals"),
]

def duration_step(seconds, text, hr=None):
    step = {"duration": int(seconds), "text": text}
    if hr:
        step["hr"] = hr
    return step

def run_workout(week):
    reps, work_min, recovery_sec, label = RUNS[week]
    steps = [
        duration_step(12*60, "Warm up very easily; build gradually",
                      {"start": 65, "end": 80, "units": "%lthr"})
    ]
    steps.append({
        "reps": reps,
        "text": label + " — hard but repeatable, approximately 5K effort",
        "steps": [
            duration_step(work_min*60, "Hard interval; even effort"),
            duration_step(recovery_sec, "Easy jog or walk recovery")
        ]
    })
    steps.append(duration_step(9*60, "Easy cool-down"))
    return {
        "start_date_local": None,
        "category": "WORKOUT",
        "type": "Run",
        "name": f"W{week+1} quality run — {label}",
        "description": "Run by effort, not pace. Keep repetitions consistent; do not sprint the first interval. HR may lag during short reps.",
        "moving_time": 12*60 + reps*(work_min*60+recovery_sec) + 9*60,
        "workout_doc": {"description": "VO2-oriented run intervals", "steps": steps}
    }

def easy_ride(week):
    mins = EASY_RIDE_MIN[week]
    return {
        "category": "WORKOUT",
        "type": "Ride",
        "name": f"W{week+1} easy aerobic ride — {mins} min",
        "description": f"{mins} minutes conversational Zone 2. Keep HR approximately 131–148 bpm; back off if it drifts or the legs feel heavy. This should feel easy.",
        "moving_time": mins*60,
        "workout_doc": {
            "description": "Easy aerobic endurance",
            "steps": [duration_step(mins*60, "Steady conversational aerobic ride; HR 131–148 bpm")]
        }
    }

def optional_bike(week):
    spec = BIKE_SETS[week]
    if week in (3, 7):
        return None
    if week in (1, 2, 5):
        sets, reps, work, rest, label = spec
        interval = {
            "reps": reps,
            "text": label,
            "steps": [
                duration_step(work, "Hard, controlled effort; RPE 8–9"),
                duration_step(rest, "Very easy spinning")
            ]
        }
        steps = [duration_step(10*60, "Warm up gradually"), interval]
        if sets > 1:
            # Multi-set short intervals: include a 5-minute easy set break.
            steps = [duration_step(10*60, "Warm up gradually"),
                     {"reps": sets, "text": label + " — repeat sets",
                      "steps": [
                          {"reps": reps, "text": "Interval block", "steps": [
                              duration_step(work, "Hard, controlled effort; RPE 8–9"),
                              duration_step(rest, "Very easy spinning")
                          ]},
                          duration_step(5*60, "Easy spin between blocks")
                      ]}]
    else:
        reps, work, rest, label = spec
        steps = [
            duration_step(10*60, "Warm up gradually"),
            {"reps": reps, "text": label, "steps": [
                duration_step(work, "Hard but repeatable; RPE 8–9"),
                duration_step(rest, "Very easy spinning")
            ]}
        ]
    steps.append(duration_step(8*60, "Easy cool-down"))
    return {
        "category": "WORKOUT",
        "type": "Ride",
        "name": f"W{week+1} OPTIONAL bike VO2 — {spec[-1]}",
        "description": (
            "OPTIONAL, not an extra obligation. Do this only if the weekend club ride "
            "will be easy/moderate and recovery is good. If the club ride is hard, skip "
            "this session entirely. Keep efforts repeatable, not all-out."
        ),
        "moving_time": sum(s.get("duration", 0) for s in steps) + 0,
        "workout_doc": {"description": "Optional bike VO2 intervals", "steps": steps}
    }

def make_events():
    start = date(2026, 11, 2)  # Monday
    events = []
    for w in range(8):
        monday = start + timedelta(days=7*w)
        run = run_workout(w)
        run["start_date_local"] = monday.isoformat()
        run["external_id"] = f"{PREFIX}-w{w+1}-mon-run"
        events.append(run)

        tuesday = monday + timedelta(days=1)
        easy = easy_ride(w)
        easy["start_date_local"] = tuesday.isoformat()
        easy["external_id"] = f"{PREFIX}-w{w+1}-tue-easy-ride"
        events.append(easy)

        thursday = monday + timedelta(days=3)
        bike = optional_bike(w)
        if bike:
            bike["start_date_local"] = thursday.isoformat()
            bike["external_id"] = f"{PREFIX}-w{w+1}-thu-optional-bike"
            events.append(bike)

        saturday = monday + timedelta(days=5)
        events.append({
            "start_date_local": saturday.isoformat(),
            "category": "NOTE",
            "type": "Ride",
            "name": f"W{w+1} weekend club ride — flexible day",
            "description": (
                "Target: approximately 50 km, about 3 hours including stops. "
                "Move this reminder to Sunday if that is the club ride day. "
                "If the ride is hard, it replaces Thursday's optional bike intervals; "
                "do not do both hard sessions."
            ),
            "external_id": f"{PREFIX}-w{w+1}-weekend-club-ride"
        })
    return events

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true",
                        help="Actually upload; otherwise print a dry-run preview.")
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
        sys.exit("Missing INTERVALS_API_KEY. Set it in your shell; do not put it in this file.")

    token = base64.b64encode(("API_KEY:" + key).encode()).decode()
    body = json.dumps(events).encode()
    req = urllib.request.Request(
        BASE, data=body, method="POST",
        headers={"Authorization": "Basic " + token,
                 "Content-Type": "application/json",
                 "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        sys.exit(f"Intervals.icu returned HTTP {exc.code}: {detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Could not reach Intervals.icu: {exc}")

    print(f"\nIntervals.icu accepted the upload. Returned {len(result)} event records.")
    print("First few returned events:")
    for event in result[:5]:
        print(f"- {event.get('start_date_local')} | {event.get('name')} | ID {event.get('id')}")

if __name__ == "__main__":
    main()
