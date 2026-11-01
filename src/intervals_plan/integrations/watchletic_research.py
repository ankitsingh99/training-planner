"""
Watch-app and ecosystem interoperability research for Intervals.icu.
Focus on Samsung Galaxy Watch (Wear OS), COROS DURA, Watchletic, and ZonePace.
"""

from typing import Dict, Any, List


WATCH_ECOSYSTEM_RESEARCH: Dict[str, Any] = {
    "title": "Watch-App & Hardware Interoperability Research for Intervals.icu",
    "updated": "2026-11-01",
    "comparison": [
        {
            "app_or_platform": "COROS DURA (Cycling)",
            "tier": "Free / Included with Device",
            "wear_os_support": "N/A (Dedicated Cycling Head Unit)",
            "intervals_sync": "Native 2-Way Cloud Integration",
            "structured_execution": "Full on-device execution (targets, timers, interval alerts)",
            "recording_and_export": "Full GPS, dual-frequency, cadence, HR, auto-exports to Strava & Intervals.icu",
            "verdict": "Best-in-class for cycling workouts. 1-click connect in COROS app.",
        },
        {
            "app_or_platform": "Watchletic (Wear OS / Galaxy Watch)",
            "tier": "Freemium (Free tier vs Watchletic Club ~$3/mo)",
            "wear_os_support": "Yes, native Wear OS 3+ & Galaxy Watch support",
            "intervals_sync": "Manual sync on Free tier; Automated background calendar sync requires Watchletic Club",
            "structured_execution": "Yes! Supports complex target HR, pace, cadences, and interval cues on-watch",
            "recording_and_export": "Records HR, GPS, pace; direct sync to Strava",
            "verdict": "Top Wear OS choice for running structured workouts. Free tier allows executing custom workouts.",
        },
        {
            "app_or_platform": "ZonePace (Android / Wear OS)",
            "tier": "Free / Open-Source",
            "wear_os_support": "Companion app for Wear OS",
            "intervals_sync": "Connects via Intervals.icu API key",
            "structured_execution": "Primarily calendar viewing & pace/HR zone telemetry; structured execution is basic/limited",
            "recording_and_export": "Relies on Samsung Health or native workout recorders for full sensor logs",
            "verdict": "Great free tool for viewing calendar and zone tracking, but less feature-rich for complex intervals.",
        },
        {
            "app_or_platform": "Samsung Health + Strava Bridge",
            "tier": "Free",
            "wear_os_support": "Native Galaxy Watch system app",
            "intervals_sync": "Indirect (Samsung Health -> Strava -> Intervals.icu)",
            "structured_execution": "Cannot import Intervals.icu structured JSON directly; manual interval timer only",
            "recording_and_export": "Excellent sensor recording, auto-syncs to Strava",
            "verdict": "Rock-solid for recording free-form runs, but lacks native structured workout import.",
        },
    ],
    "recommendation": (
        "Recommended Strategy:\n"
        "1. Cycling: Use COROS DURA. It natively downloads your Intervals.icu calendar workouts and guides them seamlessly.\n"
        "2. Running on Galaxy Watch: Use Watchletic. Build or import the workouts; execute intervals with audio/haptic cues.\n"
        "3. Strength: Use Hevy. Auto-sync to Strava -> Intervals.icu to credit gym fatigue to your fitness/form chart.\n"
    ),
}


def print_watch_research() -> None:
    print("\n" + "=" * 70)
    print(WATCH_ECOSYSTEM_RESEARCH["title"])
    print("=" * 70 + "\n")

    for item in WATCH_ECOSYSTEM_RESEARCH["comparison"]:
        print(f" {item['app_or_platform']} ({item['tier']})")
        print(f"  - Intervals.icu Sync:    {item['intervals_sync']}")
        print(f"  - Structured Execution:  {item['structured_execution']}")
        print(f"  - Recording & Export:    {item['recording_and_export']}")
        print(f"  - Summary / Verdict:     {item['verdict']}\n")

    print("-" * 70)
    print(WATCH_ECOSYSTEM_RESEARCH["recommendation"])
    print("-" * 70 + "\n")

