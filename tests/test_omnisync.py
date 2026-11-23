"""
Unit tests for the OmniSync pipeline engine.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from intervals_plan.api_models import IntervalsActivity, IntervalsEvent
from intervals_plan.config import Config
from intervals_plan.integrations.coros_client import CorosSyncStatus
from intervals_plan.omnisync import OmniSyncEngine, OmniSyncResult


def test_omnisync_result_to_dict():
    res = OmniSyncResult(
        timestamp="2026-11-23T00:00:00Z",
        status="SUCCESS",
        wellness_days_updated=5,
        health_connect_processed=True,
        activities_analyzed=10,
        plan_events_created=7,
        coros_sync_status="INTERVALS_RELAY",
        athlete_name="Athlete",
        ctl=20.0,
        atl=25.0,
        tsb=-5.0,
        acwr=0.8,
        readiness_score=85,
        messages=["Test message"],
    )
    d = res.to_dict()
    assert d["status"] == "SUCCESS"
    assert d["wellness_days_updated"] == 5
    assert d["ctl"] == 20.0
    assert d["acwr"] == 0.8
    assert "Test message" in d["messages"]


def test_omnisync_dry_run_flow(tmp_path: Path):
    cfg = Config(
        api_key="test_api_key",
        athlete_id="i12345",
        data_dir=tmp_path / "data",
    )
    cfg.ensure_dirs()

    # Create dummy health connect file
    hc_payload = {
        "resting_heart_rate": [{"bpm": 55, "time": "2026-11-20T00:00:00Z"}],
        "weight": [{"kilograms": 78.5, "time": "2026-11-20T00:00:00Z"}],
    }
    hc_file = cfg.data_dir / "health_connect_latest.json"
    hc_file.write_text(json.dumps(hc_payload))

    engine = OmniSyncEngine(cfg)

    # Mock IntervalsClient methods
    mock_ath = MagicMock()
    mock_ath.id = "i12345"
    mock_ath.name = "Test Athlete"
    engine.intervals.get_athlete = MagicMock(return_value=mock_ath)
    engine.intervals.get_activities = MagicMock(return_value=[])
    engine.intervals._request = MagicMock(return_value=[
        {"id": "2026-11-20", "restingHR": 55, "ctl": 20.0, "atl": 22.0}
    ])
    engine.intervals.list_events = MagicMock(return_value=[])

    # Mock CorosClient status
    engine.coros.check_status = MagicMock(return_value=CorosSyncStatus(
        connected=True,
        mode="INTERVALS_RELAY",
        user_id="coros_uid_123",
        upload_workouts=True,
    ))

    result = engine.run_sync(apply=False, sync_plan=True, weeks=1)

    assert result.status == "SUCCESS"
    assert result.athlete_name == "Test Athlete"
    assert result.health_connect_processed is True
    assert result.wellness_days_updated == 1
    assert result.coros_sync_status == "INTERVALS_RELAY"
    assert any("SIMULATED" in m for m in result.messages)


def test_omnisync_live_apply_flow(tmp_path: Path):
    cfg = Config(
        api_key="test_api_key",
        athlete_id="i12345",
        data_dir=tmp_path / "data",
    )
    cfg.ensure_dirs()

    hc_file = cfg.data_dir / "health_connect_latest.json"
    hc_file.write_text(json.dumps({"resting_heart_rate": [{"bpm": 52, "time": "2026-11-21T00:00:00Z"}]}))

    engine = OmniSyncEngine(cfg)

    mock_ath = MagicMock(id="i12345", name="Live Athlete")
    engine.intervals.get_athlete = MagicMock(return_value=mock_ath)
    engine.intervals.put_wellness = MagicMock(return_value={"id": "2026-11-21"})
    engine.intervals.get_activities = MagicMock(return_value=[])
    engine.intervals._request = MagicMock(return_value=[{"id": "2026-11-21", "ctl": 18.0, "atl": 20.0}])
    engine.intervals.list_events = MagicMock(return_value=[])

    dummy_created = IntervalsEvent(id=999, name="Test Workout", type="Ride", start_date_local="2026-11-24")
    engine.intervals.bulk_upsert_events = MagicMock(return_value=[dummy_created])

    engine.coros.check_status = MagicMock(return_value=CorosSyncStatus(
        connected=True,
        mode="INTERVALS_RELAY",
        upload_workouts=True,
    ))

    result = engine.run_sync(apply=True, sync_plan=True, weeks=1)

    assert result.status == "SUCCESS"
    assert engine.intervals.put_wellness.called
    assert result.plan_events_created > 0
    assert (cfg.data_dir / "manifest.json").exists()
