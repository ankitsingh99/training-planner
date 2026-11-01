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
  python3 upload_intervals_plan.py --upload  # Upload events (skips already existing)
  python3 upload_intervals_plan.py --upload --force  # Force re-upload / update
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
EVENTS_QUERY_URL = "https://intervals.icu/api/v1/athlete/0/events"
PREFIX = "chatgpt-8wk-run-bike-2026-11-02"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

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
    recovery_m = recovery_sec // 60
    recovery_s = recovery_sec % 60
    rec_str = f"{recovery_m}m{recovery_s}s" if recovery_s else f"{recovery_m}m"

    steps = [
        duration_step(
            12 * 60,
            "Warmup",
            {"start": 65, "end": 80, "units": "%lthr"},
        ),
        {
            "reps": reps,
            "text": f"{reps}x {label}",
            "steps": [
                duration_step(work_min * 60, "5K Effort (RPE 8-9)"),
                duration_step(recovery_sec, "Easy Recovery"),
            ],
        },
        duration_step(9 * 60, "Cooldown"),
    ]
    coaching_guidance = (
        "Target: 5K race effort (RPE 8-9). "
        "Pacing: Keep reps smooth and even; do not sprint rep 1. "
        "HR lags on short reps, so pace by effort. "
        "Walk or jog slowly between reps to fully recover."
    )
    desc = (
        f"{coaching_guidance}\n\n"
        f"Warmup\n"
        f"- 12m ramp 65-80% LTHR Warmup\n\n"
        f"{reps}x\n"
        f"- {work_min}m 100-112% LTHR 5K Effort (RPE 8-9)\n"
        f"- {rec_str} 60-70% LTHR Easy Recovery\n\n"
        f"Cooldown\n"
        f"- 9m 60-70% LTHR Cooldown\n"
    )
    return {
        "start_date_local": None,
        "category": "WORKOUT",
        "type": "Run",
        "name": f"W{week+1} quality run - {label}",
        "description": desc,
        "moving_time": calc_duration(steps),
        "workout_doc": {"description": coaching_guidance, "steps": steps},
    }


def easy_ride(week):
    mins = EASY_RIDE_MIN[week]
    steps = [duration_step(mins * 60, "Zone 2 Steady")]
    coaching_guidance = (
        f"Target: Conversational Zone 2 (HR 131-148 bpm). "
        f"Pacing: True talk-test effort: speak full sentences easily. "
        f"Back off if HR drifts. Tuesday is gym rest day to protect hypertrophy."
    )
    desc = (
        f"{coaching_guidance}\n\n"
        f"- {mins}m 60-72% LTHR Zone 2 Steady\n"
    )
    return {
        "category": "WORKOUT",
        "type": "Ride",
        "name": f"W{week+1} easy aerobic ride - {mins} min",
        "description": desc,
        "moving_time": calc_duration(steps),
        "workout_doc": {
            "description": coaching_guidance,
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
            duration_step(10 * 60, "Warmup"),
            {
                "reps": sets,
                "text": f"{sets}x Sets",
                "steps": [
                    {
                        "reps": reps,
                        "text": f"{reps}x ({work}s Hard / {rest}s Easy)",
                        "steps": [
                            duration_step(work, "Microburst (RPE 8-9)"),
                            duration_step(rest, "Spin Recovery"),
                        ],
                    },
                    duration_step(5 * 60, "Set Break Spin"),
                ],
            },
            duration_step(8 * 60, "Cooldown"),
        ]
        coaching_guidance = (
            f"Target: High-cadence VO2 microbursts (95-105 rpm, RPE 8-9). "
            f"Hard effort on reps, light spin between. Spin 5m easy between sets. "
            f"OPTIONAL: skip or swap to easy spin if weekend ride is hard."
        )
        desc = (
            f"{coaching_guidance}\n\n"
            f"Warmup\n"
            f"- 10m ramp 50-75% LTHR Warmup\n\n"
            f"{sets}x\n"
            f"{reps}x\n"
            f"- {work}s 115-125% LTHR Microburst (RPE 8-9)\n"
            f"- {rest}s 50-60% LTHR Spin Recovery\n\n"
            f"- 5m 50-60% LTHR Set Break Spin\n\n"
            f"Cooldown\n"
            f"- 8m 50% LTHR Cooldown\n"
        )
    else:
        reps, work, rest, label = spec
        work_m = work // 60
        rest_m = rest // 60
        steps = [
            duration_step(10 * 60, "Warmup"),
            {
                "reps": reps,
                "text": f"{reps}x {label}",
                "steps": [
                    duration_step(work, "Hard VO2 (RPE 8-9)"),
                    duration_step(rest, "Spin Recovery"),
                ],
            },
            duration_step(8 * 60, "Cooldown"),
        ]
        coaching_guidance = (
            f"Target: Sustained VO2 intervals (RPE 8-9). "
            f"Even, controlled power across all reps. Spin easily to recover. "
            f"OPTIONAL: do only if fresh and weekend club ride is moderate; skip if ride is hard."
        )
        desc = (
            f"{coaching_guidance}\n\n"
            f"Warmup\n"
            f"- 10m ramp 50-75% LTHR Warmup\n\n"
            f"{reps}x\n"
            f"- {work_m}m 105-115% LTHR Hard VO2 (RPE 8-9)\n"
            f"- {rest_m}m 50-60% LTHR Spin Recovery\n\n"
            f"Cooldown\n"
            f"- 8m 50% LTHR Cooldown\n"
        )
    return {
        "category": "WORKOUT",
        "type": "Ride",
        "name": f"W{week+1} OPTIONAL bike VO2 - {spec[-1]}",
        "description": desc,
        "moving_time": calc_duration(steps),
        "workout_doc": {"description": coaching_guidance, "steps": steps},
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


def fetch_existing_events(key, start_date_str, end_date_str):
    """Fetch existing calendar events from Intervals.icu within the given date window."""
    token = base64.b64encode(("API_KEY:" + key).encode()).decode()
    url = f"{EVENTS_QUERY_URL}?oldest={start_date_str}&newest={end_date_str}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": "Basic " + token,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"Notice: Could not check existing events ({exc}); proceeding with bulk upsert.")
        return None


def main():
    parser = argparse.ArgumentParser(description="Upload or preview 8-week Intervals.icu plan.")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Actually upload events to Intervals.icu; otherwise runs in dry-run mode.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force upload and overwrite even if events already exist on the calendar.",
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

    # Duplicate prevention: Check if events already exist on the athlete's calendar
    existing = fetch_existing_events(key, "2026-11-02", "2026-12-27")
    events_to_upload = events

    if existing is not None:
        existing_ext_ids = {
            e.get("external_id")
            for e in existing
            if e.get("external_id") and e.get("external_id", "").startswith(PREFIX)
        }

        if not args.force:
            events_to_upload = [e for e in events if e.get("external_id") not in existing_ext_ids]
            if not events_to_upload:
                print(
                    f"\n All {len(events)} events are already present on your Intervals.icu calendar!\n"
                    "No duplicate workouts created. Upload skipped.\n"
                    "Tip: Run with '--force' to overwrite / re-upload the existing workouts."
                )
                return
            elif len(events_to_upload) < len(events):
                print(
                    f"\nFound {len(existing_ext_ids)} existing events on your calendar.\n"
                    f"Uploading only the {len(events_to_upload)} missing event(s)..."
                )
        else:
            print(f"\nForce flag enabled: re-uploading / updating all {len(events)} events...")

    token = base64.b64encode(("API_KEY:" + key).encode()).decode()
    body = json.dumps(events_to_upload).encode("utf-8")

    # Use a browser-like User-Agent to satisfy Cloudflare bot protection.
    req = urllib.request.Request(
        BASE,
        data=body,
        method="POST",
        headers={
            "Authorization": "Basic " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
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

    print(f"\n Intervals.icu accepted the upload! Returned {len(result)} event records.")
    print("First few uploaded events:")
    for event in result[:5]:
        print(f" - {event.get('start_date_local')} | {event.get('name')} | ID: {event.get('id')}")


if __name__ == "__main__":
    main()
