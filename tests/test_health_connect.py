"""
Unit and integration tests for Samsung Health & Health Connect Webhook Integration.
Tests parsing, data transformation, LAN pull client, Intervals/COROS sync, and CLI.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error

import pytest

from intervals_plan.config import Config
from intervals_plan.integrations.coros_client import CorosClient, CorosSyncStatus
from intervals_plan.integrations.health_connect import (
    HealthConnectClient,
    HealthConnectParser,
    HealthConnectSyncManager,
    HealthConnectSyncResult,
)
from intervals_plan.intervals_client import IntervalsClient


@pytest.fixture
def sample_hc_payload():
    return {
        "timestamp": "2026-11-02T12:00:00Z",
        "app_version": "1.9.28",
        "steps": [
            {"count": 4200, "start_time": "2026-11-01T08:00:00Z", "end_time": "2026-11-01T09:00:00Z"},
            {"count": 3800, "start_time": "2026-11-01T14:00:00Z", "end_time": "2026-11-01T15:00:00Z"},
            {"count": 5100, "start_time": "2026-11-02T08:00:00Z", "end_time": "2026-11-02T09:00:00Z"},
        ],
        "resting_heart_rate": [
            {"bpm": 50, "time": "2026-11-01T06:30:00Z"},
            {"bpm": 48, "time": "2026-11-02T06:30:00Z"},
        ],
        "heart_rate": [
            {"bpm": 54, "min": 49, "time": "2026-11-01T05:00:00Z"},
        ],
        "heart_rate_variability": [
            {"rmssd_millis": 68.5, "time": "2026-11-01T06:00:00Z"},
            {"rmssd_millis": 72.0, "time": "2026-11-02T06:00:00Z"},
        ],
        "sleep": [
            {
                "session_end_time": "2026-11-01T06:30:00Z",
                "duration_seconds": 27000,
                "stages": [
                    {"stage": "DEEP", "duration_seconds": 5400},
                    {"stage": "REM", "duration_seconds": 6300},
                    {"stage": "LIGHT", "duration_seconds": 15300},
                ],
            },
        ],
        "weight": [
            {"weight_kg": 73.2, "time": "2026-11-01T07:00:00Z"},
        ],
        "body_fat": [
            {"percentage": 14.5, "time": "2026-11-01T07:00:00Z"},
        ],
        "blood_pressure": [
            {"systolic_mmhg": 118, "diastolic_mmhg": 76, "time": "2026-11-01T07:05:00Z"},
        ],
        "oxygen_saturation": [
            {"percentage": 98.5, "time": "2026-11-01T06:00:00Z"},
        ],
        "respiratory_rate": [
            {"rate": 14.2, "time": "2026-11-01T06:00:00Z"},
        ],
        "blood_glucose": [
            {"level_milligrams_per_deciliter": 92.0, "time": "2026-11-01T07:15:00Z"},
        ],
        "hydration": [
            {"volume_liters": 2.2, "time": "2026-11-01T20:00:00Z"},
        ],
        "nutrition": [
            {"calories": 2650, "time": "2026-11-01T21:00:00Z"},
        ],
        "exercise_sessions": [
            {
                "title": "Morning Tempo Run",
                "exercise_type": "RUNNING",
                "start_time": "2026-11-01T07:00:00Z",
                "end_time": "2026-11-01T07:50:00Z",
                "duration_seconds": 3000,
                "distance_meters": 9500,
                "calories_burned": 620,
            },
            {
                "title": "Endurance Spin",
                "exercise_type": "BIKING",
                "start_time": "2026-11-02T08:00:00Z",
                "end_time": "2026-11-02T09:30:00Z",
                "duration_seconds": 5400,
                "distance_meters": 35000,
                "calories_burned": 900,
            },
        ],
    }


def test_health_connect_parser_wellness(sample_hc_payload):
    parser = HealthConnectParser()
    wellness = parser.parse_wellness(sample_hc_payload)

    assert "2026-11-01" in wellness
    assert "2026-11-02" in wellness

    d1 = wellness["2026-11-01"]
    assert d1["steps"] == 8000
    assert d1["restingHR"] == 50
    assert d1["hrv"] == 68.5
    assert d1["sleepSecs"] == 27000
    assert "Deep" in d1["comments"]
    assert d1["weight"] == 73.2
    assert d1["bodyFat"] == 14.5
    assert d1["systolic"] == 118
    assert d1["diastolic"] == 76
    assert d1["spO2"] == 98.5
    assert d1["respiration"] == 14.2
    assert d1["bloodGlucose"] == 92.0
    assert d1["hydration"] == 2.2
    assert d1["kcalConsumed"] == 2650

    d2 = wellness["2026-11-02"]
    assert d2["steps"] == 5100
    assert d2["restingHR"] == 48
    assert d2["hrv"] == 72.0


def test_health_connect_parser_activities(sample_hc_payload):
    parser = HealthConnectParser()
    acts = parser.parse_activities(sample_hc_payload)

    assert len(acts) == 2
    a1 = acts[0]
    assert a1["name"] == "Morning Tempo Run"
    assert a1["type"] == "Run"
    assert a1["moving_time"] == 3000
    assert a1["distance"] == 9500.0
    assert a1["icu_training_load"] > 0

    a2 = acts[1]
    assert a2["name"] == "Endurance Spin"
    assert a2["type"] == "Ride"
    assert a2["moving_time"] == 5400
    assert a2["distance"] == 35000.0


def test_health_connect_lan_client():
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"timestamp": "2026-11-02T12:00:00Z", "steps": []}).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        data = HealthConnectClient.fetch_lan("192.168.1.50", port=8787, days=3)
        assert data["timestamp"] == "2026-11-02T12:00:00Z"

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Network unreachable")):
        with pytest.raises(ConnectionError):
            HealthConnectClient.fetch_lan("192.168.1.50", port=8787)


def test_coros_client_status():
    cfg = Config(api_key="valid_key", athlete_id="i123")
    client = CorosClient(access_token="valid_coros_token_12345", user_id="u_999")
    assert client.is_direct_api_ready() is True

    # Test with IntervalsClient mock
    mock_int = MagicMock(spec=IntervalsClient)
    mock_int.api_key = "valid_key"
    mock_int.athlete_id = "i123"
    mock_int._request.return_value = {
        "coros_user_id": "coros_user_abc",
        "coros_upload_workouts": True,
        "coros_sync_activities": True,
        "coros_download_wellness": True,
        "coros_last_upload": "2026-11-02T08:00:00Z",
    }

    status = client.check_status(mock_int)
    assert status.connected is True
    assert status.mode == "DIRECT_OPEN_API"
    assert status.user_id == "coros_user_abc"
    assert status.upload_workouts is True

    # Test without direct token
    client_no_token = CorosClient()
    status_relay = client_no_token.check_status(mock_int)
    assert status_relay.mode == "INTERVALS_RELAY"
    assert status_relay.connected is True


def test_coros_client_upload_workout():
    client = CorosClient(access_token="valid_token_12345")
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"code": "0000", "message": "OK"}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = client.upload_workout_direct({"title": "Interval Run"})
        assert res["code"] == "0000"

    # Test skipped when no token
    client_no_token = CorosClient()
    skipped = client_no_token.upload_workout_direct({"title": "Test"})
    assert skipped["status"] == "skipped"


def test_health_connect_sync_manager(tmp_path, sample_hc_payload):
    cfg = Config(api_key="valid_test_key", athlete_id="i123", data_dir=tmp_path)
    mgr = HealthConnectSyncManager(cfg)
    mgr.STATE_FILE = tmp_path / "health_connect_sync.json"

    # 1. Dry run
    dry_res = mgr.sync_payload(sample_hc_payload, source="test_run", dry_run=True)
    assert dry_res.wellness_records_updated == 2
    assert dry_res.activities_uploaded == 2
    assert dry_res.details["dry_run"] is True

    last_state = mgr.load_last_state()
    assert last_state is not None
    assert last_state["wellness_records_updated"] == 2

    # 2. Live apply with mocked IntervalsClient
    with patch("intervals_plan.intervals_client.IntervalsClient.update_wellness") as mock_update_w, \
         patch("intervals_plan.intervals_client.IntervalsClient.upload_activity") as mock_upload_act:
        live_res = mgr.sync_payload(sample_hc_payload, source="test_live", dry_run=False)
        assert live_res.wellness_records_updated == 2
        assert mock_update_w.call_count == 2
        assert mock_upload_act.call_count == 2
