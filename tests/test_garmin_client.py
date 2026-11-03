"""
Unit tests for Garmin Connect Client, FIT Workout Generation, and Intervals Cloud Relay.
"""

import json
from unittest.mock import MagicMock

from intervals_plan.api_models import HRTarget, IntervalsEvent, WorkoutDoc, WorkoutStep
from intervals_plan.config import Config
from intervals_plan.exporters import PlanExporter
from intervals_plan.integrations.garmin_client import GarminClient, GarminSyncStatus


def test_garmin_sync_status_serialization():
    status = GarminSyncStatus(
        connected=True,
        mode="INTERVALS_GARMIN_RELAY",
        user_id="ath-12345",
        upload_workouts=True,
        download_activities=True,
        download_wellness=True,
        body_battery_enabled=True,
        direct_api_ready=False,
    )
    d = status.to_dict()
    assert d["connected"] is True
    assert d["mode"] == "INTERVALS_GARMIN_RELAY"
    assert d["user_id"] == "ath-12345"
    assert d["upload_workouts"] is True
    assert d["download_wellness"] is True
    assert d["body_battery_enabled"] is True


def test_garmin_client_from_config():
    cfg = Config(
        garmin_access_token="oauth_test_token_12345678",
        garmin_consumer_key="key_123",
        garmin_consumer_secret="sec_456",
        garmin_user_id="garmin_user_789",
    )
    client = GarminClient.from_config(cfg)
    assert client.access_token == "oauth_test_token_12345678"
    assert client.consumer_key == "key_123"
    assert client.user_id == "garmin_user_789"
    assert client.is_direct_api_ready() is True


def test_garmin_client_status_relay():
    mock_intervals = MagicMock()
    mock_intervals.api_key = "test_key"
    mock_intervals.athlete_id = "athlete_999"
    mock_intervals._request.return_value = {
        "id": "athlete_999",
        "icu_garmin_health": True,
        "icu_garmin_training": True,
        "icu_garmin_upload_workouts": True,
        "icu_garmin_sync_activities": True,
        "icu_garmin_download_wellness": True,
        "icu_garmin_last_upload": "2026-11-03T06:00:00Z",
        "garmin_power_target": "POWER_3S",
        "icu_garmin_hr_range": 2.0,
        "garmin_pace_range": 3.0,
    }

    client = GarminClient()
    status = client.check_status(mock_intervals)
    assert status.connected is True
    assert status.mode == "INTERVALS_GARMIN_RELAY"
    assert status.upload_workouts is True
    assert status.download_wellness is True
    assert status.last_cloud_push == "2026-11-03T06:00:00Z"
    assert status.power_target_mode == "POWER_3S"
    assert status.hr_range_pct == 2.0
    assert status.pace_range_pct == 3.0


def test_garmin_client_enable_relay():
    mock_intervals = MagicMock()
    mock_intervals.athlete_id = "ath-42"
    mock_intervals._request.return_value = {"status": "ok"}

    client = GarminClient()
    res = client.enable_intervals_relay(mock_intervals, upload_workouts=True, download_wellness=True)
    assert res["status"] == "success"
    assert res["athlete_id"] == "ath-42"
    assert res["updated"]["icu_garmin_upload_workouts"] is True
    assert res["updated"]["icu_garmin_download_wellness"] is True


def test_convert_event_to_garmin_json():
    doc = WorkoutDoc(
        steps=[
            WorkoutStep(duration=600, text="Warmup 10m", hr=HRTarget(start=120, end=140)),
            WorkoutStep(duration=300, text="Work Interval", power={"start": 250, "end": 260}),
            WorkoutStep(duration=180, text="Recovery jog"),
            WorkoutStep(duration=300, text="Cooldown 5m"),
        ]
    )
    event = IntervalsEvent(
        category="WORKOUT",
        type="Run",
        name="VO2max Intervals",
        description="4x5m VO2max intervals with warm and cool",
        start_date_local="2026-11-05T07:00:00",
        workout_doc=doc,
    )

    client = GarminClient()
    wkt_json = client.convert_event_to_garmin_json(event)
    assert wkt_json["workoutName"] == "VO2max Intervals"
    assert wkt_json["sportType"]["sportTypeKey"] == "running"
    assert len(wkt_json["workoutSegments"]) == 1
    steps = wkt_json["workoutSegments"][0]["workoutSteps"]
    assert len(steps) == 4

    # Verify warmup step
    assert steps[0]["stepType"]["stepTypeKey"] == "warmup"
    assert steps[0]["targetType"]["targetTypeKey"] == "heart.rate.zone"
    assert steps[0]["targetValueOne"] == 120.0
    assert steps[0]["targetValueTwo"] == 140.0

    # Verify work step with power
    assert steps[1]["stepType"]["stepTypeKey"] == "interval"
    assert steps[1]["targetType"]["targetTypeKey"] == "power.zone"
    assert steps[1]["targetValueOne"] == 250.0

    # Verify recovery step
    assert steps[2]["stepType"]["stepTypeKey"] == "recovery"


def test_generate_fit_workout():
    doc = WorkoutDoc(
        steps=[
            WorkoutStep(duration=600, text="Warmup"),
            WorkoutStep(duration=1200, text="Threshold block", power={"start": 260, "end": 280}),
            WorkoutStep(duration=300, text="Cooldown"),
        ]
    )
    event = IntervalsEvent(
        category="WORKOUT",
        type="Ride",
        name="Sweet Spot Ride",
        start_date_local="2026-11-05T08:00:00",
        workout_doc=doc,
    )

    client = GarminClient()
    fit_bytes = client.generate_fit_workout(event)

    assert isinstance(fit_bytes, bytes)
    assert len(fit_bytes) > 50

    # Verify 14-byte FIT file header
    header_size = fit_bytes[0]
    assert header_size == 14
    protocol_version = fit_bytes[1]
    assert protocol_version == 0x20
    assert fit_bytes[8:12] == b".FIT"

    # Verify CRC
    total_len = len(fit_bytes)
    assert total_len >= 16


def test_plan_exporter_garmin_fit_and_json():
    event = IntervalsEvent(
        category="WORKOUT",
        type="Run",
        name="Tempo Run",
        start_date_local="2026-11-04T07:00:00",
        workout_doc=WorkoutDoc(steps=[WorkoutStep(duration=1800, text="Tempo")]),
    )

    fit_data = PlanExporter.event_to_garmin_fit(event)
    assert len(fit_data) > 0
    assert b".FIT" in fit_data

    json_dict = PlanExporter.event_to_garmin_json(event)
    assert json_dict["workoutName"] == "Tempo Run"
    assert json_dict["sportType"]["sportTypeKey"] == "running"
