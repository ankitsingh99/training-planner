"""
Unit tests for Strength & Hypertrophy Engine, Muscle Map, and Strava Parser.
"""

import datetime
from intervals_plan.strength_engine import (
    DEFAULT_VOLUME_LANDMARKS,
    StravaGymWorkoutParser,
    StrengthEngine,
    VolumeLandmark,
)


def test_volume_landmarks_defaults():
    assert "chest" in DEFAULT_VOLUME_LANDMARKS
    assert "quads" in DEFAULT_VOLUME_LANDMARKS
    assert "lats" in DEFAULT_VOLUME_LANDMARKS

    chest_lm = DEFAULT_VOLUME_LANDMARKS["chest"]
    assert chest_lm.mv < chest_lm.mev < chest_lm.mav < chest_lm.mrv
    assert chest_lm.mav == 14


def test_strava_gym_workout_parser_explicit_exercises():
    activity = {
        "name": "Evening Upper Body Session",
        "description": "Incline bench 4x8, Cable fly 3x12, Barbell curl 3x10",
        "moving_time": 3000,
    }
    parsed = StravaGymWorkoutParser.parse_activity(activity)
    assert "chest" in parsed
    assert parsed["chest"] >= 5.0  # 4 sets incline + 3 sets cable fly
    assert "biceps" in parsed
    assert parsed["biceps"] >= 3.0


def test_strava_gym_workout_parser_split_name_heuristics():
    # Push Day heuristic
    push_act = {
        "name": "Push Day Hypertrophy",
        "description": "",
        "moving_time": 3600,
    }
    parsed_push = StravaGymWorkoutParser.parse_activity(push_act)
    assert "chest" in parsed_push
    assert "shoulders_side" in parsed_push
    assert "triceps" in parsed_push

    # Leg Day heuristic
    leg_act = {
        "name": "Heavy Squats & Legs",
        "description": "",
        "moving_time": 3600,
    }
    parsed_legs = StravaGymWorkoutParser.parse_activity(leg_act)
    assert "quads" in parsed_legs
    assert "hamstrings" in parsed_legs
    assert "glutes" in parsed_legs


def test_strength_engine_evaluate_muscle_map():
    engine = StrengthEngine()
    now = datetime.datetime(2026, 11, 23, 12, 0, 0, tzinfo=datetime.timezone.utc)

    activities = [
        {
            "id": "gym_1",
            "name": "Push Day A",
            "type": "WeightTraining",
            "start_date_local": "2026-11-22T17:00:00Z",
            "moving_time": 3600,
            "description": "Bench press 4x8, Incline dumbbell 4x10, Lateral raise 4x15, Cable fly 3x12"
        },
        {
            "id": "run_1",
            "name": "Hard Threshold Run",
            "type": "Run",
            "start_date_local": "2026-11-22T18:00:00Z",  # Within 1 hour of gym!
            "moving_time": 3000,
            "icu_training_load": 65,
        }
    ]

    res = engine.evaluate_muscle_map(activities, now_dt=now)
    assert "muscle_groups" in res
    assert "systemic_muscle_recovery_score" in res
    assert res["systemic_muscle_recovery_score"] > 0

    chest = res["muscle_groups"]["chest"]
    assert chest["weekly_sets"] > 0
    assert chest["hours_since_trained"] is not None
    assert chest["recovery_pct"] >= 0


def test_strength_engine_concurrent_interference_detection():
    engine = StrengthEngine()
    # Leg workout at 14:00, Run at 16:00 (2 hours apart = HIGH interference)
    activities = [
        {
            "id": "gym_legs",
            "name": "Heavy Leg Day - Squats & Deadlifts",
            "type": "WeightTraining",
            "start_date_local": "2026-11-22T14:00:00Z",
            "moving_time": 3600,
            "description": "Barbell squat 4x8, Romanian deadlift 4x8"
        },
        {
            "id": "run_intervals",
            "name": "Threshold Intervals 5x1k",
            "type": "Run",
            "start_date_local": "2026-11-22T16:00:00Z",
            "moving_time": 3600,
            "icu_training_load": 75,
        }
    ]
    now = datetime.datetime(2026, 11, 23, 10, 0, 0, tzinfo=datetime.timezone.utc)
    res = engine.evaluate_muscle_map(activities, now_dt=now)

    quads = res["muscle_groups"]["quads"]
    assert quads["interference_risk"] in ("HIGH", "MODERATE")
    assert "Warning" in quads["notes"]


def test_personalized_6day_ppl_program():
    ppl = StrengthEngine.get_personalized_6day_ppl()
    assert "sessions" in ppl
    assert len(ppl["sessions"]) == 7  # 6 days PPL + 1 recovery

    day1 = ppl["sessions"][0]
    assert "Push A" in day1["title"]
    assert len(day1["exercises"]) >= 5
    assert "endurance_guidance" in day1
