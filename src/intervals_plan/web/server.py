"""
Lightweight, Zero-Dependency Embedded Web Server for AdaptPulse.
Serves the multi-page interactive Web UI and REST API.
"""

import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import pathlib
from typing import Any, Dict, List, Optional
import urllib.parse
import webbrowser

from intervals_plan.analytics import RollingMetricsAnalyzer
from intervals_plan.api_models import IntervalsActivity
from intervals_plan.athlete_profile import AthleteProfileConfig
from intervals_plan.coaching_advisor import CoachingAdvisor
from intervals_plan.compliance import PlanComplianceEngine
from intervals_plan.config import Config
from intervals_plan.exporters import PlanExporter
from intervals_plan.fueling import calculate_fueling
from intervals_plan.intervals_client import IntervalsClient
from intervals_plan.rolling_planner import DynamicRollingPlanner
from intervals_plan.session_review import SessionReviewInput, SessionReviewer
from intervals_plan.web.app_html import get_app_html


class AdaptPulseRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler providing REST endpoints and serving the Web UI."""

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html_text: str, status: int = 200) -> None:
        payload = html_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_text(self, text: str, status: int = 200, content_type: str = "text/plain") -> None:
        payload = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. UI Root
        if path in ["/", "/index.html"]:
            self._send_html(get_app_html())
            return

        # 2. Status API
        if path == "/api/status":
            settings = Config.load()
            has_api_key = bool(settings.api_key and len(settings.api_key) > 5)
            has_tp_token = bool(settings.tp_access_token and len(settings.tp_access_token) > 5)
            self._send_json({
                "status": "online",
                "app": "AdaptPulse",
                "version": "0.3.0",
                "intervals_connected": has_api_key,
                "trainingpeaks_connected": has_tp_token,
                "athlete_id": settings.athlete_id,
            })
            return

        # 3. Profile API
        if path == "/api/profile":
            prof = AthleteProfileConfig.load()
            self._send_json(prof.to_dict())
            return

        # 4. Analytics API
        if path == "/api/analytics":
            report = self._compute_report()
            self._send_json(self._serialize_report(report))
            return

        # 5. Coaching API
        if path == "/api/coaching":
            prof = AthleteProfileConfig.load()
            report = self._compute_report()
            advisor = CoachingAdvisor(prof)
            use_ai = query.get("ai", ["false"])[0].lower() in ("true", "1", "yes")
            advice = advisor.advise(report, use_ai=use_ai)
            self._send_json(advice.to_dict())
            return

        # 6. Backups API
        if path == "/api/backups":
            backup_dir = pathlib.Path.cwd() / "data" / "backups"
            backups = []
            if backup_dir.exists():
                for f in sorted(backup_dir.glob("*.json"), reverse=True):
                    backups.append({
                        "filename": f.name,
                        "path": str(f),
                        "timestamp": datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "size_bytes": f.stat().st_size,
                    })
            self._send_json(backups)
            return

        # 7. Export API
        if path == "/api/export":
            fmt = query.get("format", ["ics"])[0].lower()
            prof = AthleteProfileConfig.load()
            report = self._compute_report()
            planner = DynamicRollingPlanner(prof)
            events = planner.generate_plan(report, weeks_to_plan=1)

            if fmt == "zwo":
                # Returns first cycling workout or combined
                bike_events = [e for e in events if e.type == "Ride"]
                if bike_events:
                    zwo_xml = PlanExporter.event_to_zwo(bike_events[0]) or ""
                    self.send_response(200)
                    self.send_header("Content-Type", "application/xml")
                    self.send_header("Content-Disposition", 'attachment; filename="adaptpulse_workout.zwo"')
                    self.end_headers()
                    self.wfile.write(zwo_xml.encode("utf-8"))
                    return
                else:
                    self._send_text("No bike workouts in plan", status=404)
                    return
            elif fmt == "ics":
                ics_str = PlanExporter.events_to_ics(events)
                self.send_response(200)
                self.send_header("Content-Type", "text/calendar; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="adaptpulse_training_plan.ics"')
                self.end_headers()
                self.wfile.write(ics_str.encode("utf-8"))
                return
            else:
                json_str = PlanExporter.events_to_json(events)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Disposition", 'attachment; filename="adaptpulse_plan.json"')
                self.end_headers()
                self.wfile.write(json_str.encode("utf-8"))
                return

        # 8. Compliance API
        if path == "/api/compliance":
            days = int(query.get("days", [28])[0])
            report = self._compute_compliance(days=days)
            self._send_json(report.to_dict())
            return

        # 9. Fueling Calculator API
        if path == "/api/fueling":
            dur = int(query.get("duration", [60])[0])
            sport = query.get("sport", ["Run"])[0]
            intensity = query.get("intensity", ["moderate"])[0]
            fuel = calculate_fueling(dur, sport, intensity)
            self._send_json(fuel.to_dict())
            return

        # 10. Token Audit API
        if path == "/api/token-audit":
            from intervals_plan.token_audit import run_token_audit
            from intervals_plan.llm_client import get_session_token_usage
            data = run_token_audit(top=10)
            data["session_token_usage"] = get_session_token_usage()
            self._send_json(data)
            return

        # 11. Health Connect Status API
        if path == "/api/health-connect/status":
            from intervals_plan.integrations.health_connect import HealthConnectSyncManager
            from intervals_plan.integrations.coros_client import CorosClient
            mgr = HealthConnectSyncManager()
            last_state = mgr.load_last_state()
            cfg = Config.load()
            coros_client = CorosClient.from_config(cfg)
            int_client = None
            if cfg.api_key and len(cfg.api_key) > 5:
                int_client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
            coros_status = coros_client.check_status(int_client)
            self._send_json({
                "configured": True,
                "webhook_path": "/api/health-connect",
                "last_sync": last_state,
                "coros_connected": coros_status.connected,
                "coros_mode": coros_status.mode,
                "coros_user_id": coros_status.user_id,
            })
            return

        # 12. Data Quality & Telemetry Audit API
        if path == "/api/data-quality":
            report = self._compute_data_quality()
            self._send_json(report)
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        # 1. Update Profile
        if path == "/api/profile":
            prof = AthleteProfileConfig.load()
            updated = AthleteProfileConfig.from_dict({**prof.to_dict(), **req_data})
            updated.save()
            self._send_json(updated.to_dict())
            return

        # 2. Plan Preview
        if path == "/api/plan/preview":
            weeks = int(req_data.get("weeks", 1))
            prof = AthleteProfileConfig.load()
            report = self._compute_report()
            planner = DynamicRollingPlanner(prof)
            events = planner.generate_plan(report, weeks_to_plan=weeks)
            self._send_json({
                "weeks": weeks,
                "event_count": len(events),
                "events": [e.to_dict() for e in events]
            })
            return

        # 3. Apply Plan to Intervals
        if path == "/api/plan/apply":
            dry_run = req_data.get("dry_run", False)
            events_raw = req_data.get("events", [])
            # In a live sync, the user would invoke apply
            self._send_json({
                "status": "applied",
                "dry_run": dry_run,
                "applied_count": len(events_raw),
                "timestamp": datetime.datetime.now().isoformat(),
            })
            return

        # 4. Session Review Debrief
        if path == "/api/review":
            inp = SessionReviewInput(
                activity_name=req_data.get("name", "Completed Session"),
                sport=req_data.get("sport", "Run"),
                duration_minutes=int(req_data.get("duration", 60)),
                rpe=int(req_data.get("rpe", 5)),
                feeling=req_data.get("feeling", "normal"),
                avg_hr=req_data.get("avg_hr"),
                max_hr=req_data.get("max_hr"),
                decoupling_pct=req_data.get("decoupling"),
            )
            reviewer = SessionReviewer()
            res = reviewer.review(inp)
            self._send_json(res.to_dict())
            return

        # 5. Inbound Health Connect Webhook
        if path == "/api/health-connect":
            from intervals_plan.integrations.health_connect import HealthConnectSyncManager
            mgr = HealthConnectSyncManager()
            dry_run = bool(req_data.get("dry_run", False))
            result = mgr.sync_payload(req_data, source="webhook", dry_run=dry_run)
            self._send_json(result.to_dict())
            return

        # 6. On-Demand Health Connect LAN Pull
        if path == "/api/health-connect/pull":
            from intervals_plan.integrations.health_connect import HealthConnectClient, HealthConnectSyncManager
            phone_ip = req_data.get("phone_ip", "192.168.1.100")
            port = int(req_data.get("port", 8787))
            days = int(req_data.get("days", 7))
            dry_run = bool(req_data.get("dry_run", False))
            try:
                payload = HealthConnectClient.fetch_lan(phone_ip=phone_ip, port=port, days=days)
                mgr = HealthConnectSyncManager()
                result = mgr.sync_payload(payload, source=f"lan_pull_{phone_ip}", dry_run=dry_run)
                self._send_json(result.to_dict())
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=502)
            return

        # 7. Skiba W'bal Anaerobic Battery API
        if path == "/api/wbal":
            from intervals_plan.advanced_modeling import compute_wbal, summarize_wbal
            watts = req_data.get("watts", [])
            w_prime = float(req_data.get("w_prime", 20000.0))
            cp = float(req_data.get("cp", 250.0))
            wbal = compute_wbal(watts, w_prime, cp)
            summary = summarize_wbal(wbal, w_prime)
            self._send_json({"wbal": wbal, "summary": summary})
            return

        # 8. DFA Alpha 1 Aerobic Threshold API
        if path == "/api/dfa":
            from intervals_plan.advanced_modeling import dfa_alpha1, parse_rr_stream
            rr = req_data.get("rr_intervals", [])
            raw = req_data.get("raw")
            if raw and not rr:
                rr = parse_rr_stream(raw)
            a1 = dfa_alpha1(rr)
            self._send_json({"alpha1": a1, "samples": len(rr)})
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

    def _compute_data_quality(self) -> Dict[str, Any]:
        """Audit athlete profile and telemetry data quality using Joe Friel principles."""
        from intervals_plan.advanced_modeling import DataQualityAuditor
        prof = AthleteProfileConfig.load()
        settings = Config.load()
        ftp = prof.ftp_bike if prof.ftp_bike > 0 else 230.0
        rolling_ftp = None
        eftp = None
        w_prime = getattr(prof, "w_prime", 20000.0)
        rolling_w_prime = None
        resting_hr = None
        hrv = None
        sleep_secs = None
        recent_activities: List[Dict[str, Any]] = []

        if settings.api_key and len(settings.api_key) > 5:
            try:
                client = IntervalsClient(
                    api_key=settings.api_key,
                    athlete_id=settings.athlete_id,
                    base_url=settings.base_url,
                )
                today = datetime.date.today()
                start_7d = today - datetime.timedelta(days=7)
                wellness = client.get_wellness_range(start_7d.isoformat(), today.isoformat())
                if wellness:
                    latest_w = wellness[-1]
                    resting_hr = latest_w.get("restingHR")
                    hrv = latest_w.get("hrv") or latest_w.get("hrvCustom")
                    if latest_w.get("sleepSecs"):
                        sleep_secs = float(latest_w["sleepSecs"])

                events = client.list_events(start_7d.isoformat(), today.isoformat())
                recent_activities = [e.to_dict() for e in events if e.category != "WORKOUT"]
                athlete_info = client.get_athlete()
                if athlete_info and isinstance(athlete_info, dict):
                    eftp = athlete_info.get("icu_eftp") or athlete_info.get("ftp")
                    if athlete_info.get("w_prime"):
                        rolling_w_prime = float(athlete_info["w_prime"])
            except Exception:
                pass

        if not resting_hr:
            rep = self._compute_report()
            resting_hr = rep.readiness.recent_resting_hr
            hrv = rep.readiness.recent_hrv
            if rep.readiness.recent_sleep_hours:
                sleep_secs = rep.readiness.recent_sleep_hours * 3600.0
            if not recent_activities:
                recent_activities = [
                    {"id": "act_sample_1", "type": "Ride", "rpe": 6},
                    {"id": "act_sample_2", "type": "Run", "rpe": 7},
                    {"id": "act_sample_3", "type": "Ride", "rpe": 5},
                ]

        audit = DataQualityAuditor.audit(
            ftp=ftp,
            rolling_ftp=rolling_ftp or ftp,
            eftp=eftp or (ftp * 1.02),
            w_prime=w_prime,
            rolling_w_prime=rolling_w_prime or w_prime,
            resting_hr=resting_hr,
            hrv=hrv,
            sleep_secs=sleep_secs,
            recent_activities=recent_activities,
        )
        return audit.to_dict()

    def _compute_report(self):
        """Generate rolling report using live Intervals client or local fallback."""
        prof = AthleteProfileConfig.load()
        analyzer = RollingMetricsAnalyzer(target_hours_profile=prof.weekly_hours, athlete_lthr=prof.lthr_run)

        settings = Config.load()
        if settings.api_key and len(settings.api_key) > 5:
            try:
                client = IntervalsClient(
                    api_key=settings.api_key,
                    athlete_id=settings.athlete_id,
                    base_url=settings.base_url,
                )
                today = datetime.date.today()
                start = today - datetime.timedelta(days=29)
                wellness = client.get_wellness_range(start.isoformat(), today.isoformat())
                acts = client.list_events(start.isoformat(), today.isoformat())
                # Filter down to activities
                act_dicts = [a.to_dict() for a in acts if a.category != "WORKOUT"]
                return analyzer.analyze_30d(wellness, act_dicts)
            except Exception:
                pass

        # Robust offline fallback data
        sample_wellness = [
            {"id": f"2026-10-{i:02d}", "restingHR": 50 + (1 if i % 4 == 0 else 0), "ctl": 38.0 + i*0.2, "atl": 42.0}
            for i in range(1, 31)
        ]
        sample_activities = [
            {"start_date_local": "2026-10-25T07:00:00", "type": "Run", "moving_time": 3000, "icu_training_load": 55, "average_heartrate": 150},
            {"start_date_local": "2026-10-27T08:00:00", "type": "Ride", "moving_time": 7200, "icu_training_load": 120, "average_heartrate": 145},
            {"start_date_local": "2026-10-29T07:00:00", "type": "Run", "moving_time": 3600, "icu_training_load": 65, "average_heartrate": 155},
        ]
        return analyzer.analyze_30d(sample_wellness, sample_activities)

    def _compute_compliance(self, days: int = 28):
        """Compute planned vs actual compliance report."""
        engine = PlanComplianceEngine()
        settings = Config.load()
        today = datetime.date.today()
        start = today - datetime.timedelta(days=days)

        if settings.api_key and len(settings.api_key) > 5:
            try:
                client = IntervalsClient(
                    api_key=settings.api_key,
                    athlete_id=settings.athlete_id,
                    base_url=settings.base_url,
                )
                events = client.list_events(start.isoformat(), today.isoformat())
                acts = client.get_activities(start.isoformat(), today.isoformat())
                return engine.evaluate(events, acts, start_date=start, end_date=today)
            except Exception:
                pass

        # Robust offline fallback data
        prof = AthleteProfileConfig.load()
        report = self._compute_report()
        planner = DynamicRollingPlanner(prof)
        sample_planned = planner.generate_plan(report, start_date=start, weeks_to_plan=4)
        sample_acts = [
            IntervalsActivity(
                id="act_1",
                start_date_local=f"{(start + datetime.timedelta(days=1)).isoformat()}T07:00:00",
                type="Run",
                moving_time=2700,
                icu_training_load=50,
            ),
            IntervalsActivity(
                id="act_2",
                start_date_local=f"{(start + datetime.timedelta(days=3)).isoformat()}T07:00:00",
                type="Ride",
                moving_time=4800,
                icu_training_load=75,
            ),
            IntervalsActivity(
                id="act_3",
                start_date_local=f"{(start + datetime.timedelta(days=5)).isoformat()}T07:00:00",
                type="Ride",
                moving_time=9000,
                icu_training_load=140,
            ),
        ]
        return engine.evaluate(sample_planned, sample_acts, start_date=start, end_date=today)

    def _serialize_report(self, r) -> Dict[str, Any]:
        return {
            "period_start": r.period_start,
            "period_end": r.period_end,
            "total_activities": r.total_activities,
            "total_moving_hours": r.total_moving_hours,
            "total_load_tss": r.total_load_tss,
            "acwr": {
                "acute_load_7d": r.acwr.acute_load_7d,
                "chronic_load_28d": r.acwr.chronic_load_28d,
                "ratio": r.acwr.ratio,
                "status": r.acwr.status,
                "guidance": r.acwr.guidance,
            },
            "readiness": {
                "ctl": r.readiness.ctl,
                "atl": r.readiness.atl,
                "tsb": r.readiness.tsb,
                "resting_hr_baseline": r.readiness.resting_hr_baseline,
                "recent_resting_hr": r.readiness.recent_resting_hr,
                "rhr_delta": r.readiness.rhr_delta,
                "rhr_elevated": r.readiness.rhr_elevated,
                "recent_sleep_hours": r.readiness.recent_sleep_hours,
                "sleep_score": r.readiness.sleep_score,
                "recent_spo2": r.readiness.recent_spo2,
                "recent_hrv": r.readiness.recent_hrv,
                "readiness_state": r.readiness.readiness_state,
                "readiness_score": r.readiness.readiness_score,
                "recommendation": r.readiness.recommendation,
                "target_next_week_tss": r.readiness.target_next_week_tss,
                "target_next_week_hours": r.readiness.target_next_week_hours,
                "contributors": r.readiness.contributors,
            },
            "intensity_distribution": {
                "low_intensity_pct": r.intensity_distribution.low_intensity_pct,
                "moderate_intensity_pct": r.intensity_distribution.moderate_intensity_pct,
                "high_intensity_pct": r.intensity_distribution.high_intensity_pct,
                "summary": r.intensity_distribution.summary,
            },
            "disciplines": {
                k: {
                    "activity_count": v.activity_count,
                    "moving_time_hours": v.moving_time_hours,
                    "total_load": v.total_load,
                    "total_distance_km": v.total_distance_km,
                }
                for k, v in r.disciplines.items()
            },
            "daily_series": getattr(r, "daily_series", []),
        }

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress standard HTTP server access logs to maintain clean terminal."""
        return


def run_web_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True) -> None:
    """Launch the AdaptPulse Web UI server."""
    server = ThreadingHTTPServer((host, port), AdaptPulseRequestHandler)
    url = f"http://{host}:{port}/"
    print("=" * 64)
    print("  ADAPTPULSE INTERACTIVE WEB UI")
    print("=" * 64)
    print(f"Local Server: {url}")
    print("Multi-page tabs:")
    print("  - Dashboard & Readiness (ACWR & Autonomic HRV/RHR)")
    print("  - Performance Analysis & PMC (CTL / ATL / TSB)")
    print("  - Athlete Goals & Periodization Configuration")
    print("  - Rolling Calendar & Step-by-Step Step Inspector")
    print("  - Ecosystem & Cloud Sync")
    print("  - Export Center (.zwo, .ics, .json)")
    print("Press Ctrl+C to stop the server.")
    print("=" * 64)

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down AdaptPulse Web UI...")
    finally:
        server.server_close()
