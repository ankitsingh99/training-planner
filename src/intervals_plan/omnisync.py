"""
OmniSync Pipeline: End-to-end integration and synchronizer for Intervals.icu & COROS.

Aggregates data across:
  - Samsung Health / Health Connect (Watch 4: RHR, HRV, sleep, SpO2, weight, body fat)
  - Google Fit / Health Connect
  - Strava (rides, runs, activities)
  - COROS (DURA / watch workouts, training load, wellness)
  - Intervals.icu (central database of record)

Synchronizes all biometrics, evaluates dynamic physiological readiness,
reconciles the rolling calendar plan, and triggers relays to COROS.
"""

from dataclasses import dataclass, field
import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from intervals_plan.analytics import RollingMetricsAnalyzer
from intervals_plan.athlete_profile import AthleteProfileConfig
from intervals_plan.audit import AuditLogger
from intervals_plan.backup import BackupManager
from intervals_plan.config import Config
from intervals_plan.diff import calculate_diff
from intervals_plan.integrations.coros_client import CorosClient
from intervals_plan.integrations.health_connect import HealthConnectParser
from intervals_plan.intervals_client import IntervalsClient
from intervals_plan.rolling_planner import DynamicRollingPlanner

logger = logging.getLogger(__name__)


@dataclass
class OmniSyncResult:
    """Detailed summary of the OmniSync run."""

    timestamp: str
    status: str  # SUCCESS, PARTIAL, ERROR
    wellness_days_updated: int = 0
    health_connect_processed: bool = False
    activities_analyzed: int = 0
    plan_events_created: int = 0
    plan_events_updated: int = 0
    plan_events_deleted: int = 0
    coros_sync_status: str = "UNKNOWN"
    athlete_name: str = ""
    ctl: Optional[float] = None
    atl: Optional[float] = None
    tsb: Optional[float] = None
    acwr: Optional[float] = None
    readiness_score: Optional[int] = None
    messages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "status": self.status,
            "wellness_days_updated": self.wellness_days_updated,
            "health_connect_processed": self.health_connect_processed,
            "activities_analyzed": self.activities_analyzed,
            "plan_events_created": self.plan_events_created,
            "plan_events_updated": self.plan_events_updated,
            "plan_events_deleted": self.plan_events_deleted,
            "coros_sync_status": self.coros_sync_status,
            "athlete_name": self.athlete_name,
            "ctl": self.ctl,
            "atl": self.atl,
            "tsb": self.tsb,
            "acwr": self.acwr,
            "readiness_score": self.readiness_score,
            "messages": self.messages,
        }


class OmniSyncEngine:
    """
    Automated omni-synchronizer and training plan orchestrator.
    """

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or Config.load()
        self.intervals = IntervalsClient(
            api_key=self.cfg.api_key,
            athlete_id=self.cfg.athlete_id,
            base_url=self.cfg.base_url,
        )
        self.coros = CorosClient.from_config(self.cfg)
        self.audit = AuditLogger(self.cfg.data_dir / "audit.log")
        self.backup_mgr = BackupManager(self.cfg.data_dir / "backups")

    def run_sync(
        self,
        apply: bool = False,
        sync_plan: bool = True,
        weeks: int = 1,
        health_connect_file: Optional[Path] = None,
    ) -> OmniSyncResult:
        """
        Execute full cross-platform sync:
        1. Ingest Samsung Health / Health Connect vitals (excluding duplicate steps).
        2. Query Intervals.icu wellness and activities (from Strava, COROS, Google Fit).
        3. Re-read athlete profile & verify COROS cloud bridge.
        4. Calculate rolling 30d analytics (ACWR, CTL, ATL, TSB, Autonomic readiness).
        5. Dynamically regenerate and reconcile the rolling training plan.
        6. Apply updates and record audit trails.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result = OmniSyncResult(timestamp=now_iso, status="SUCCESS")

        # 1. Athlete verification
        try:
            athlete = self.intervals.get_athlete()
            result.athlete_name = athlete.name
            result.messages.append(f"Authenticated as athlete {athlete.name} ({athlete.id})")
        except Exception as exc:
            result.status = "ERROR"
            result.messages.append(f"Failed to connect to Intervals.icu: {exc}")
            return result

        # 2. Ingest Health Connect / Samsung Health data if file present
        hc_file = health_connect_file or (self.cfg.data_dir / "health_connect_latest.json")
        if hc_file.exists():
            try:
                raw_hc = json.loads(hc_file.read_text(encoding="utf-8"))
                parser = HealthConnectParser()
                # Enforce: exclude steps to prevent duplicate step counts
                daily_wellness = parser.parse_wellness(raw_hc, include_steps=False)
                updated_days = 0
                for date_str, vitals in sorted(daily_wellness.items()):
                    if apply:
                        self.intervals.put_wellness(date_str, vitals)
                    updated_days += 1
                result.wellness_days_updated = updated_days
                result.health_connect_processed = True
                mode_str = "APPLIED" if apply else "SIMULATED"
                result.messages.append(f"Health Connect {mode_str}: merged {updated_days} days of vitals (steps excluded)")
            except Exception as exc:
                result.messages.append(f"Warning: Health Connect ingestion issue: {exc}")

        # 3. Fetch rolling 30-day data
        today_date = datetime.date.today()
        start_date = today_date - datetime.timedelta(days=30)
        end_date = today_date + datetime.timedelta(days=7 * weeks)

        start_str = start_date.strftime("%Y-%m-%d")
        today_str = today_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        try:
            wellness_records = self.intervals._request(
                "GET",
                f"/athlete/{self.cfg.athlete_id}/wellness?oldest={start_str}&newest={today_str}",
            ) or []
            activities = self.intervals.get_activities(start_str, today_str) or []
            result.activities_analyzed = len(activities)
        except Exception as exc:
            result.status = "ERROR"
            result.messages.append(f"Failed to fetch rolling data: {exc}")
            return result

        # 4. Run Analytics & Readiness evaluation
        prof = AthleteProfileConfig.load()
        analyzer = RollingMetricsAnalyzer(
            target_hours_profile=prof.weekly_hours,
            athlete_lthr=prof.lthr_bike or prof.lthr_run or 172,
        )
        report = analyzer.analyze_30d(wellness_records, activities, end_date_str=today_str)
        result.ctl = report.readiness.ctl
        result.atl = report.readiness.atl
        result.tsb = report.readiness.tsb
        result.acwr = report.acwr.ratio
        result.readiness_score = report.readiness.readiness_score

        result.messages.append(
            f"Readiness: {report.readiness.readiness_state} (Score {report.readiness.readiness_score}/100) | "
            f"CTL: {report.readiness.ctl:.1f} | ATL: {report.readiness.atl:.1f} | ACWR: {report.acwr.ratio:.2f} [{report.acwr.status}]"
        )

        # 5. Check COROS Cloud Bridge
        coros_status = self.coros.check_status(self.intervals)
        result.coros_sync_status = coros_status.mode
        result.messages.append(
            f"COROS Bridge: {coros_status.mode} (Upload Workouts: {coros_status.upload_workouts})"
        )

        # 6. Reconcile Dynamic Rolling Plan
        if sync_plan:
            try:
                planner = DynamicRollingPlanner(prof)
                # Determine cycle start date (upcoming Monday or today if Monday)
                cycle_start = today_date if today_date.weekday() == 0 else planner.get_upcoming_monday(today_date)
                cycle_start_str = cycle_start.strftime("%Y-%m-%d")

                desired_events = planner.generate_plan(
                    report=report,
                    weeks_to_plan=weeks,
                    start_date=cycle_start,
                )

                live_events = self.intervals.list_events(start_date=cycle_start_str, end_date=end_str)
                managed_prefix = f"dynamic-{prof.goal}"

                # Calculate differential sync
                manifest_path = self.cfg.data_dir / "manifest.json"
                manifest = {}
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    except Exception:
                        manifest = {}

                diff = calculate_diff(desired_events, live_events, manifest, managed_prefix=managed_prefix)

                result.plan_events_created = len(diff.to_create)
                result.plan_events_updated = len(diff.to_update)
                result.plan_events_deleted = len(diff.to_delete)

                if apply:
                    # Backup live events before mutating
                    if diff.to_create or diff.to_update or diff.to_delete:
                        backup_file = self.backup_mgr.create_backup(live_events, tag="omnisync_presync")
                        result.messages.append(f"Safety backup saved: {backup_file.name}")

                    # 1. Deletions
                    for ev in diff.to_delete:
                        if ev.id:
                            self.intervals.delete_event(ev.id)
                            manifest.pop(str(ev.id), None)

                    # 2. Updates
                    for ev in diff.to_update:
                        if ev.id:
                            self.intervals.update_event(ev)

                    # 3. Creations
                    created_events = []
                    for ev in diff.to_create:
                        created = self.intervals.create_event(ev)
                        created_events.append(created)
                        if created.id:
                            manifest[str(created.id)] = created.to_dict()

                    # Save updated manifest
                    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

                    self.audit.log(
                        action="OMNISYNC_RUN",
                        target_ids=[str(e.id) for e in created_events if e.id],
                        status="SUCCESS",
                        details=result.to_dict(),
                    )
                    result.messages.append(
                        f"Plan Applied: +{len(diff.to_create)} created, ~{len(diff.to_update)} updated, -{len(diff.to_delete)} deleted"
                    )
                else:
                    result.messages.append(
                        f"Plan Dry-Run: {len(diff.to_create)} to create, {len(diff.to_update)} to update, {len(diff.to_delete)} to delete"
                    )
            except Exception as exc:
                result.messages.append(f"Warning: Dynamic plan sync issue: {exc}")

        return result
