"""
Tests for AdaptPulse Embedded Web Server and REST API.
"""

from http.server import ThreadingHTTPServer
import json
import threading
import time
from unittest.mock import patch
import urllib.request

from intervals_plan.web.server import AdaptPulseRequestHandler


def start_test_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), AdaptPulseRequestHandler)
    port = server.server_port
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.05)
    return server, f"http://127.0.0.1:{port}"


def test_web_ui_endpoints():
    server, base_url = start_test_server()
    try:
        # 1. Root HTML
        with urllib.request.urlopen(f"{base_url}/") as res:
            assert res.status == 200
            content = res.read().decode("utf-8")
            assert "<!DOCTYPE html>" in content
            assert "AdaptPulse" in content

        # 2. Status API
        with urllib.request.urlopen(f"{base_url}/api/status") as res:
            assert res.status == 200
            data = json.loads(res.read().decode("utf-8"))
            assert data["app"] == "AdaptPulse"
            assert data["status"] == "online"
            assert "trainingpeaks_connected" in data
            assert "intervals_connected" in data

        # 3. Profile API (GET)
        with urllib.request.urlopen(f"{base_url}/api/profile") as res:
            assert res.status == 200
            prof = json.loads(res.read().decode("utf-8"))
            assert "goal" in prof

        # 4. Profile API (POST)
        post_data = json.dumps({"weekly_hours": 9.5, "target_event_name": "Autumn 10k"}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/profile",
            data=post_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            saved = json.loads(res.read().decode("utf-8"))
            assert saved["weekly_hours"] == 9.5
            assert saved["target_event_name"] == "Autumn 10k"

        # 5. Analytics API
        with urllib.request.urlopen(f"{base_url}/api/analytics") as res:
            assert res.status == 200
            ana = json.loads(res.read().decode("utf-8"))
            assert "acwr" in ana
            assert "readiness" in ana
            assert "daily_series" in ana
            assert len(ana["daily_series"]) == 30

        # 6. Coaching API
        with urllib.request.urlopen(f"{base_url}/api/coaching") as res:
            assert res.status == 200
            coach = json.loads(res.read().decode("utf-8"))
            assert "headline" in coach
            assert "training_focus" in coach

        # 7. Backups API
        with urllib.request.urlopen(f"{base_url}/api/backups") as res:
            assert res.status == 200
            backups = json.loads(res.read().decode("utf-8"))
            assert isinstance(backups, list)

        # 8. Plan Preview API (POST)
        preview_req = urllib.request.Request(
            f"{base_url}/api/plan/preview",
            data=json.dumps({"weeks": 1}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(preview_req) as res:
            assert res.status == 200
            plan = json.loads(res.read().decode("utf-8"))
            assert plan["event_count"] >= 5

        # 9. Plan Apply API (POST)
        apply_req = urllib.request.Request(
            f"{base_url}/api/plan/apply",
            data=json.dumps({"dry_run": True, "events": []}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(apply_req) as res:
            assert res.status == 200
            applied = json.loads(res.read().decode("utf-8"))
            assert applied["status"] == "applied"

        # 10. Export API (ICS, JSON, ZWO)
        with urllib.request.urlopen(f"{base_url}/api/export?format=ics") as res:
            assert res.status == 200
            ics_text = res.read().decode("utf-8")
            assert "BEGIN:VCALENDAR" in ics_text

        with urllib.request.urlopen(f"{base_url}/api/export?format=json") as res:
            assert res.status == 200
            json_text = res.read().decode("utf-8")
            assert "[" in json_text

        with urllib.request.urlopen(f"{base_url}/api/export?format=zwo") as res:
            assert res.status == 200
            zwo_text = res.read().decode("utf-8")
            assert "<workout_file>" in zwo_text

        # 11. Compliance API
        with urllib.request.urlopen(f"{base_url}/api/compliance?days=28") as res:
            assert res.status == 200
            comp = json.loads(res.read().decode("utf-8"))
            assert "compliance_rating" in comp
            assert "execution_rate_pct" in comp

        # 12. Fueling API
        with urllib.request.urlopen(f"{base_url}/api/fueling?duration=90&sport=Ride&intensity=high") as res:
            assert res.status == 200
            fuel = json.loads(res.read().decode("utf-8"))
            assert fuel["carbs_per_hour_g"] > 0
            assert fuel["hydration_ml_per_hour"] > 0

        # 13. Session Review API (POST)
        review_post = json.dumps({
            "name": "Tempo 10k",
            "sport": "Run",
            "duration": 50,
            "rpe": 7,
            "feeling": "strong",
            "decoupling": 2.5
        }).encode("utf-8")
        rev_req = urllib.request.Request(
            f"{base_url}/api/review",
            data=review_post,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(rev_req) as res:
            assert res.status == 200
            review_res = json.loads(res.read().decode("utf-8"))
            assert review_res["execution_score"] >= 80
            assert review_res["intensity_discipline"] == "ON_TARGET"

        # 14. Token Audit API
        with urllib.request.urlopen(f"{base_url}/api/token-audit") as res:
            assert res.status == 200
            tok_audit = json.loads(res.read().decode("utf-8"))
            assert "always_on_tokens" in tok_audit
            assert "session_token_usage" in tok_audit

        # 15. Coaching with AI flag
        with urllib.request.urlopen(f"{base_url}/api/coaching?ai=false") as res:
            assert res.status == 200
            coach_data = json.loads(res.read().decode("utf-8"))
            assert "headline" in coach_data

        # 16. OPTIONS test
        req_options = urllib.request.Request(f"{base_url}/api/profile", method="OPTIONS")
        with urllib.request.urlopen(req_options) as res:
            assert res.status == 200

        # 12. Malformed JSON POST test
        req_bad_json = urllib.request.Request(
            f"{base_url}/api/profile",
            data=b"not-json",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_bad_json) as res:
            assert res.status == 200

        # 13. Health Connect Status API (GET)
        with urllib.request.urlopen(f"{base_url}/api/health-connect/status") as res:
            assert res.status == 200
            hc_stat = json.loads(res.read().decode("utf-8"))
            assert hc_stat["configured"] is True
            assert "webhook_path" in hc_stat

        # 14. Health Connect Webhook Ingestion (POST)
        hc_payload = json.dumps({
            "steps": [{"count": 3000, "start_time": "2026-11-02T08:00:00Z"}],
            "resting_heart_rate": [{"bpm": 49, "time": "2026-11-02T06:00:00Z"}],
            "dry_run": True,
        }).encode("utf-8")
        req_hc = urllib.request.Request(
            f"{base_url}/api/health-connect",
            data=hc_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_hc) as res:
            assert res.status == 200
            hc_res = json.loads(res.read().decode("utf-8"))
            assert hc_res["wellness_records_updated"] >= 1

        # 15. Health Connect LAN Pull (POST)
        with patch("intervals_plan.integrations.health_connect.HealthConnectClient.fetch_lan", return_value={"steps": []}):
            pull_payload = json.dumps({"phone_ip": "192.168.1.15", "port": 8787, "dry_run": True}).encode("utf-8")
            req_pull = urllib.request.Request(
                f"{base_url}/api/health-connect/pull",
                data=pull_payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req_pull) as res:
                assert res.status == 200

        # 16. 404 test on GET and POST
        req_404 = urllib.request.Request(f"{base_url}/api/nonexistent")
        try:
            urllib.request.urlopen(req_404)
        except urllib.error.HTTPError as e:
            assert e.code == 404

        req_post_404 = urllib.request.Request(
            f"{base_url}/api/nonexistent",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req_post_404)
        except urllib.error.HTTPError as e:
            assert e.code == 404

    finally:
        server.shutdown()
        server.server_close()


def test_run_web_server_function():
    from unittest.mock import MagicMock, patch
    from intervals_plan.web.server import run_web_server

    with patch("intervals_plan.web.server.ThreadingHTTPServer") as mock_srv_cls, \
         patch("intervals_plan.web.server.webbrowser.open") as mock_open:
        mock_srv = MagicMock()
        mock_srv.serve_forever.side_effect = KeyboardInterrupt
        mock_srv_cls.return_value = mock_srv

        run_web_server(host="127.0.0.1", port=8999, open_browser=True)
        mock_open.assert_called_once_with("http://127.0.0.1:8999/")
        mock_srv.server_close.assert_called_once()
