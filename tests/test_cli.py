"""
Unit tests for CLI parser, subcommands, and handler functions.
"""

import argparse
import datetime
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from intervals_plan.api_models import IntervalsEvent
from intervals_plan.cli import (
    build_parser,
    handle_adapt,
    handle_analyze,
    handle_coach,
    handle_compliance,
    handle_coros_status,
    handle_delete_by_prefix,
    handle_doctor,
    handle_events_delete,
    handle_events_list,
    handle_events_show,
    handle_export,
    handle_plan_next,
    handle_plan_preview,
    handle_plan_validate,
    handle_profile,
    handle_session_review,
    handle_sync,
    handle_tp_status,
    load_plan,
    main,
)
from intervals_plan.config import Config


def test_cli_parser_subcommands():
    parser = build_parser()
    
    args_ui = parser.parse_args(["ui", "--port", "9000", "--no-browser"])
    assert args_ui.subcommand == "ui"
    assert args_ui.port == 9000
    assert args_ui.no_browser is True

    args_coach = parser.parse_args(["coach", "--json"])
    assert args_coach.subcommand == "coach"
    assert args_coach.json is True

    args_exp = parser.parse_args(["export", "--format", "zwo", "--weeks", "2"])
    assert args_exp.subcommand == "export"
    assert args_exp.format == "zwo"
    assert args_exp.weeks == 2

    args_pnext = parser.parse_args(["plan-next", "--weeks", "1", "--dry-run"])
    assert args_pnext.subcommand == "plan-next"
    assert args_pnext.weeks == 1


@patch("intervals_plan.cli.run_web_server")
def test_cli_main_ui(mock_web):
    with patch.object(sys, "argv", ["intervals-plan", "ui", "--port", "8081", "--no-browser"]):
        main()
        mock_web.assert_called_once_with(host="127.0.0.1", port=8081, open_browser=False)


def test_load_plan_default_and_missing():
    p = load_plan(None)
    assert p.config.total_weeks == 8

    with pytest.raises(FileNotFoundError):
        load_plan("nonexistent_plan.json")

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({
            "title": "Temp Plan",
            "description": "Temp desc",
            "config": {"total_weeks": 1, "start_date": "2026-11-02"},
            "weeks": [
                {
                    "week_number": 1,
                    "phase": "Base",
                    "run_label": "Run",
                    "run_reps": 1,
                    "run_work_min": 30,
                    "run_recovery_sec": 60,
                    "easy_ride_min": 40,
                }
            ]
        }, f)
        temp_path = f.name

    loaded = load_plan(temp_path)
    assert loaded.title == "Temp Plan"
    Path(temp_path).unlink(missing_ok=True)


def test_handle_doctor():
    cfg_no_key = Config(api_key="")
    handle_doctor(cfg_no_key)

    cfg_healthy = Config(api_key="valid_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.doctor.return_value = {
            "status": "HEALTHY",
            "athlete_id": "i123",
            "name": "Runner",
            "timezone": "UTC",
            "resting_hr": 50,
            "lthr": 175,
        }
        mock_cls.return_value = inst
        handle_doctor(cfg_healthy)


def test_handle_plan_validate_and_preview():
    args = argparse.Namespace(file=None)
    handle_plan_validate(args)
    handle_plan_preview(args)


def test_handle_events_list_and_show():
    cfg = Config(api_key="test_key")
    args = argparse.Namespace(from_date="2026-11-02", to_date="2026-11-08")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.list_events.return_value = [
            IntervalsEvent(start_date_local="2026-11-02T07:00:00", name="Morning Run", category="WORKOUT", type="Run")
        ]
        inst.get_event.return_value = IntervalsEvent(
            start_date_local="2026-11-02T07:00:00", name="Single", id=101
        )
        mock_cls.return_value = inst
        handle_events_list(cfg, args)
        handle_events_show(cfg, argparse.Namespace(event_id="101"))


def test_handle_events_delete_guards():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.get_event.return_value = IntervalsEvent(
            start_date_local="2026-11-02T07:00:00", name="Target", id=101
        )
        mock_cls.return_value = inst

        # Dry run
        args_dry = argparse.Namespace(event_id="101", confirm_delete=False)
        handle_events_delete(cfg, args_dry)

        # Confirmed
        args_confirm = argparse.Namespace(event_id="101", confirm_delete=True)
        handle_events_delete(cfg, args_confirm)


def test_handle_delete_by_prefix():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.list_events.return_value = [
            IntervalsEvent(start_date_local="2026-11-02T07:00:00", name="P1", external_id="pref-1", id=201)
        ]
        mock_cls.return_value = inst

        # Dry run
        args_dry = argparse.Namespace(prefix="pref", from_date="2026-11-01", to_date="2026-11-07", confirm_phrase=None)
        handle_delete_by_prefix(cfg, args_dry)

        # Confirmed
        args_confirm = argparse.Namespace(prefix="pref", from_date="2026-11-01", to_date="2026-11-07", confirm_phrase="DELETE 1 EVENTS")
        handle_delete_by_prefix(cfg, args_confirm)


def test_handle_sync():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls, \
         patch("intervals_plan.cli.SyncManager") as mock_sync_cls:
        inst = MagicMock()
        mock_cls.return_value = inst
        sync_inst = MagicMock()
        diff_mock = MagicMock()
        diff_mock.summary.return_value = "No changes"
        sync_inst.preview_sync.return_value = (diff_mock, [])
        mock_sync_cls.return_value = sync_inst

        # Dry run
        args_dry = argparse.Namespace(file=None, dry_run=True, apply=False, force=False)
        handle_sync(cfg, args_dry)


def test_handle_adapt():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.AdaptiveEngine") as mock_ad_cls:
        ad_inst = MagicMock()
        ad_inst.evaluate_fatigue_intervention.return_value = []
        ad_inst.apply_club_ride_adaptation.return_value = []
        mock_ad_cls.return_value = ad_inst

        args_auto = argparse.Namespace(auto=True, club_ride_hard=False, week=1, apply=False)
        handle_adapt(cfg, args_auto)

        args_club = argparse.Namespace(auto=False, club_ride_hard=True, week=1, apply=False)
        handle_adapt(cfg, args_club)


def test_handle_coros_status():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst._request.return_value = {
            "coros_user_id": "u123",
            "coros_upload_workouts": True,
            "coros_sync_activities": True,
            "coros_download_wellness": True,
            "coros_last_upload": "2026-11-01T12:00:00",
        }
        mock_cls.return_value = inst
        handle_coros_status(cfg)


def test_handle_tp_status():
    cfg_unconf = Config(tp_access_token="")
    with patch("intervals_plan.cli.TrainingPeaksClient") as mock_cls:
        inst = MagicMock()
        inst.check_connection.return_value = {
            "status": "UNCONFIGURED",
            "message": "TRAININGPEAKS_ACCESS_TOKEN is not configured",
        }
        mock_cls.return_value = inst
        handle_tp_status(cfg_unconf)

    cfg_healthy = Config(tp_access_token="valid_token")
    with patch("intervals_plan.cli.TrainingPeaksClient") as mock_cls:
        inst = MagicMock()
        inst.check_connection.return_value = {
            "status": "HEALTHY",
            "athlete_id": "ath_123",
            "first_name": "Alex",
            "last_name": "Rider",
            "email": "alex@example.com",
        }
        inst.get_athlete_zones.return_value = [{"zone": 1}, {"zone": 2}]
        mock_cls.return_value = inst
        handle_tp_status(cfg_healthy)

        # Zones failure handled gracefully
        inst.get_athlete_zones.side_effect = Exception("Zone fetch failed")
        handle_tp_status(cfg_healthy)

    cfg_err = Config(tp_access_token="bad_token")
    with patch("intervals_plan.cli.TrainingPeaksClient") as mock_cls:
        inst = MagicMock()
        inst.check_connection.return_value = {
            "status": "ERROR",
            "error": "HTTP 401 Unauthorized",
        }
        mock_cls.return_value = inst
        handle_tp_status(cfg_err)


def test_handle_coach_cli():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.get_wellness_range.return_value = [
            {"id": f"2026-10-{i:02d}", "restingHR": 50} for i in range(1, 25)
        ]
        inst.list_events.return_value = []
        mock_cls.return_value = inst

        args_text = argparse.Namespace(json=False)
        handle_coach(cfg, args_text)

        args_json = argparse.Namespace(json=True)
        handle_coach(cfg, args_json)


def test_handle_export_cli(tmp_path: Path):
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.get_wellness_range.return_value = []
        inst.list_events.return_value = []
        mock_cls.return_value = inst

        out_dir = str(tmp_path / "export_test")

        args_all = argparse.Namespace(format="all", out_dir=out_dir, weeks=1)
        handle_export(cfg, args_all)

        args_ics = argparse.Namespace(format="ics", out_dir=out_dir, weeks=1)
        handle_export(cfg, args_ics)

        args_json = argparse.Namespace(format="json", out_dir=out_dir, weeks=1)
        handle_export(cfg, args_json)

        args_zwo = argparse.Namespace(format="zwo", out_dir=out_dir, weeks=1)
        handle_export(cfg, args_zwo)


def test_handle_profile_cli(tmp_path: Path):
    p_file = tmp_path / "profile.json"
    cfg = Config(data_dir=tmp_path)

    args_show = argparse.Namespace(show=True, edit=False, goal=None, hours=None, philosophy=None, horizon=None, race_dist=None, css=None)
    handle_profile(cfg, args_show)

    args_update = argparse.Namespace(show=False, edit=False, goal="running", hours=9.0, philosophy="pyramidal", horizon="2_weeks", race_dist="half_marathon", css=102)
    handle_profile(cfg, args_update)


def test_handle_analyze_cli():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.get_wellness_range.return_value = [
            {"id": f"2026-10-{i:02d}", "restingHR": 50, "ctl": 40.0, "atl": 42.0} for i in range(1, 25)
        ]
        inst.list_events.return_value = []
        mock_cls.return_value = inst

        args_text = argparse.Namespace(days=30, json=False)
        handle_analyze(cfg, args_text)

        args_json = argparse.Namespace(days=30, json=True)
        handle_analyze(cfg, args_json)


def test_handle_plan_next_dry_run():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls, \
         patch("intervals_plan.cli.SyncManager") as mock_sync_cls:
        inst = MagicMock()
        inst.get_wellness_range.return_value = []
        inst.list_events.return_value = []
        mock_cls.return_value = inst

        sync_inst = MagicMock()
        diff_mock = MagicMock()
        diff_mock.summary.return_value = "1 to create"
        sync_inst.preview_sync.return_value = (diff_mock, [])
        mock_sync_cls.return_value = sync_inst

        args = argparse.Namespace(
            weeks=1,
            hours=None,
            goal=None,
            start_date="2026-11-02",
            dry_run=True,
            apply=False,
            force=False,
        )
        handle_plan_next(cfg, args)


def test_cli_main_subcommand_dispatch():
    # Test no args
    with patch.object(sys, "argv", ["intervals-plan"]):
        main()

    # Test doctor
    with patch.object(sys, "argv", ["intervals-plan", "doctor"]), \
         patch("intervals_plan.cli.handle_doctor") as mock_doc:
        main()
        mock_doc.assert_called_once()

    # Test auth test & athlete show
    with patch.object(sys, "argv", ["intervals-plan", "auth", "test"]), \
         patch("intervals_plan.cli.handle_doctor") as mock_doc:
        main()
        mock_doc.assert_called_once()

    with patch.object(sys, "argv", ["intervals-plan", "athlete", "show"]), \
         patch("intervals_plan.cli.handle_doctor") as mock_doc:
        main()
        mock_doc.assert_called_once()

    # Test watch-research directly and via main
    from intervals_plan.integrations.watchletic_research import print_watch_research
    print_watch_research()

    with patch.object(sys, "argv", ["intervals-plan", "watch-research"]), \
         patch("intervals_plan.cli.print_watch_research") as mock_wr:
        main()
        mock_wr.assert_called_once()

    # Test manifest show
    with patch.object(sys, "argv", ["intervals-plan", "manifest", "show"]):
        main()

    # Test audit list
    with patch.object(sys, "argv", ["intervals-plan", "audit", "list"]):
        main()

    # Test plan subcommands
    with patch.object(sys, "argv", ["intervals-plan", "plan", "validate"]), \
         patch("intervals_plan.cli.handle_plan_validate") as mock_val:
        main()
        mock_val.assert_called_once()

    with patch.object(sys, "argv", ["intervals-plan", "plan", "preview"]), \
         patch("intervals_plan.cli.handle_plan_preview") as mock_prev:
        main()
        mock_prev.assert_called_once()

    with patch.object(sys, "argv", ["intervals-plan", "plan", "export-json"]):
        main()

    # Test events subcommands
    with patch.object(sys, "argv", ["intervals-plan", "events", "list"]), \
         patch("intervals_plan.cli.handle_events_list") as mock_list:
        main()
        mock_list.assert_called_once()

    with patch.object(sys, "argv", ["intervals-plan", "events", "show", "101"]), \
         patch("intervals_plan.cli.handle_events_show") as mock_show:
        main()
        mock_show.assert_called_once()

    with patch.object(sys, "argv", ["intervals-plan", "events", "delete", "101"]), \
         patch("intervals_plan.cli.handle_events_delete") as mock_del:
        main()
        mock_del.assert_called_once()

    with patch.object(sys, "argv", ["intervals-plan", "events", "delete-by-prefix", "test"]), \
         patch("intervals_plan.cli.handle_delete_by_prefix") as mock_del_pref:
        main()
        mock_del_pref.assert_called_once()

    # Test sync, adapt, analyze, profile, plan-next, coros-status, coach, export
    for sub, handler_name in [
        (["intervals-plan", "sync"], "handle_sync"),
        (["intervals-plan", "adapt"], "handle_adapt"),
        (["intervals-plan", "analyze"], "handle_analyze"),
        (["intervals-plan", "profile"], "handle_profile"),
        (["intervals-plan", "plan-next"], "handle_plan_next"),
        (["intervals-plan", "coros-status"], "handle_coros_status"),
        (["intervals-plan", "coach"], "handle_coach"),
        (["intervals-plan", "export"], "handle_export"),
        (["intervals-plan", "tp-status"], "handle_tp_status"),
        (["intervals-plan", "compliance"], "handle_compliance"),
        (["intervals-plan", "review-session"], "handle_session_review"),
    ]:
        with patch.object(sys, "argv", sub), \
             patch(f"intervals_plan.cli.{handler_name}") as mock_handler:
            main()
            mock_handler.assert_called_once()


def test_handle_compliance_cli():
    cfg = Config(api_key="test_key")
    with patch("intervals_plan.cli.IntervalsClient") as mock_cls:
        inst = MagicMock()
        inst.list_events.return_value = [
            IntervalsEvent(id="e1", start_date_local="2026-11-01T07:00:00", type="Run", moving_time=3600)
        ]
        inst.get_activities.return_value = []
        mock_cls.return_value = inst

        args_text = argparse.Namespace(days=28, json=False)
        handle_compliance(cfg, args_text)

        args_json = argparse.Namespace(days=28, json=True)
        handle_compliance(cfg, args_json)

        # Exception test
        inst.list_events.side_effect = Exception("API error")
        handle_compliance(cfg, args_text)


def test_handle_session_review_cli():
    args_text = argparse.Namespace(
        name="Intervals Run",
        sport="Run",
        duration=45,
        rpe=8,
        feeling="strong",
        avg_hr=165,
        max_hr=180,
        decoupling=3.2,
        json=False,
    )
    handle_session_review(args_text)

    args_json = argparse.Namespace(
        name="Intervals Run",
        sport="Run",
        duration=45,
        rpe=8,
        feeling="strong",
        avg_hr=165,
        max_hr=180,
        decoupling=3.2,
        json=True,
    )
    handle_session_review(args_json)
