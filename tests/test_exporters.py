"""
Tests for Multi-Platform Plan Exporters (Zwift .zwo, iCalendar .ics, JSON).
"""

import pathlib
import tempfile

from intervals_plan.api_models import HRTarget, IntervalsEvent, WorkoutDoc, WorkoutStep
from intervals_plan.exporters import PlanExporter


def test_event_to_zwo_cycling():
    doc = WorkoutDoc(
        steps=[
            WorkoutStep(duration=600, power={"start": 50, "end": 75, "units": "%"}, text="Warmup 10m"),
            WorkoutStep(duration=240, power={"start": 105, "end": 105, "units": "%"}, text="4m VO2 Interval"),
            WorkoutStep(duration=120, power={"start": 50, "end": 50, "units": "%"}, text="2m Recovery"),
            WorkoutStep(duration=300, power={"start": 70, "end": 50, "units": "%"}, text="Cooldown 5m"),
            WorkoutStep(duration=600, power={"start": 180, "end": 180, "units": "W"}, text="10m Steady"),
        ]
    )
    event = IntervalsEvent(
        start_date_local="2026-11-05T07:00:00",
        category="WORKOUT",
        type="Ride",
        name="W1 Threshold Bike",
        description="4x8 min threshold efforts",
        workout_doc=doc,
    )

    xml = PlanExporter.event_to_zwo(event)
    assert xml is not None
    assert "<workout_file>" in xml
    assert "<Warmup" in xml
    assert "<Cooldown" in xml
    assert "<SteadyState" in xml
    assert "W1 Threshold Bike" in xml


def test_event_to_zwo_non_bike():
    event = IntervalsEvent(
        start_date_local="2026-11-03T07:00:00",
        category="WORKOUT",
        type="Run",
        name="Tuesday Quality Run",
    )
    xml = PlanExporter.event_to_zwo(event)
    assert xml is None


def test_event_to_zwo_fallback():
    event = IntervalsEvent(
        start_date_local="2026-11-07T08:00:00",
        category="WORKOUT",
        type="Ride",
        name="Generic Ride",
        workout_doc=None,
    )
    xml = PlanExporter.event_to_zwo(event)
    assert xml is not None
    assert 'SteadyState Duration="2400"' in xml


def test_events_to_ics():
    events = [
        IntervalsEvent(
            category="WORKOUT",
            type="Run",
            name="VO2max Intervals",
            description="5x3 min hard intervals",
            start_date_local="2026-11-03T07:00:00",
            external_id="run-1",
            workout_doc=WorkoutDoc(steps=[WorkoutStep(duration=1800, text="Work")]),
        ),
        IntervalsEvent(
            category="NOTE",
            type="Other",
            name="Rest Day",
            description="Active recovery",
            start_date_local="2026-11-02T07:00:00",
            external_id="rest-1",
        ),
    ]

    ics_content = PlanExporter.events_to_ics(events)
    assert "BEGIN:VCALENDAR" in ics_content
    assert "BEGIN:VEVENT" in ics_content
    assert "SUMMARY:VO2max Intervals" in ics_content
    assert "SUMMARY:Rest Day" in ics_content
    assert "END:VCALENDAR" in ics_content


def test_events_to_json():
    events = [
        IntervalsEvent(start_date_local="2026-11-03T07:00:00", name="Test Run", type="Run")
    ]
    json_str = PlanExporter.events_to_json(events)
    assert "Test Run" in json_str


def test_export_all():
    events = [
        IntervalsEvent(
            category="WORKOUT",
            type="Ride",
            name="Interval Bike",
            start_date_local="2026-11-05T07:00:00",
            workout_doc=WorkoutDoc(steps=[WorkoutStep(duration=600, text="Warmup")]),
        )
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        out = pathlib.Path(tmpdir)
        results = PlanExporter.export_all(events, out, base_name="test_plan")
        assert pathlib.Path(results["ics"]).is_file()
        assert pathlib.Path(results["json"]).is_file()
        assert int(results["zwo_count"]) >= 1
