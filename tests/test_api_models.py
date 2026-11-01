"""
Tests for Intervals.icu API Data Models.
"""

from intervals_plan.api_models import AthleteProfile, HRTarget, IntervalsActivity, IntervalsEvent, WorkoutDoc, WorkoutStep


def test_hr_target_serialization():
    hr = HRTarget(start=70.0, end=80.0, value=75.0, units="bpm")
    d = hr.to_dict()
    assert d["start"] == 70.0
    assert d["end"] == 80.0
    assert d["value"] == 75.0
    assert d["units"] == "bpm"


def test_workout_step_and_doc_roundtrip():
    step1 = WorkoutStep(
        duration=300,
        text="Warmup",
        reps=1,
        hr=HRTarget(start=60, end=70),
        power={"start": 50, "end": 60},
        cadence={"start": 85, "end": 95},
    )
    nested = WorkoutStep(
        reps=3,
        text="Intervals",
        steps=[step1],
    )
    doc = WorkoutDoc(description="Test doc", steps=[nested])
    d = doc.to_dict()
    assert "description" in d
    assert len(d["steps"]) == 1

    # Deserialization from dict
    restored = WorkoutDoc.from_dict(d)
    assert restored.description == "Test doc"
    assert len(restored.steps) == 1
    assert restored.steps[0].reps == 3
    assert len(restored.steps[0].steps) == 1
    assert restored.steps[0].steps[0].duration == 300


def test_intervals_event_roundtrip():
    doc = WorkoutDoc(description="Ride", steps=[WorkoutStep(duration=1800, text="Steady")])
    event = IntervalsEvent(
        start_date_local="2026-11-02T07:00:00",
        category="WORKOUT",
        type="Ride",
        name="Long Ride",
        description="Steady base",
        moving_time=1800,
        external_id="ride-101",
        workout_doc=doc,
        id=555,
        color="#06b6d4",
    )
    d = event.to_dict()
    assert d["id"] == 555
    assert d["color"] == "#06b6d4"
    assert "workout_doc" in d

    restored = IntervalsEvent.from_dict(d)
    assert restored.id == 555
    assert restored.name == "Long Ride"
    assert restored.workout_doc is not None
    assert restored.workout_doc.steps[0].duration == 1800


def test_athlete_profile_model():
    p = AthleteProfile(id="i999", name="Athlete", restingHR=48, lthr=178)
    assert p.id == "i999"
    assert p.restingHR == 48


def test_intervals_activity_model():
    act = IntervalsActivity(
        id="act_123",
        start_date_local="2026-11-01T07:00:00",
        type="Run",
        name="Morning 10k",
        moving_time=3600,
        icu_training_load=65.5,
        average_heartrate=152.0,
    )
    d = act.to_dict()
    assert d["id"] == "act_123"
    assert d["icu_training_load"] == 65.5
    restored = IntervalsActivity.from_dict(d)
    assert restored.name == "Morning 10k"
    assert restored.moving_time == 3600

