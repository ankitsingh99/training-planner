"""
Sync engine: orchestrates safe, idempotent synchronization with Intervals.icu.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intervals_plan.api_models import IntervalsEvent
from intervals_plan.audit import AuditLogger
from intervals_plan.backup import BackupManager
from intervals_plan.diff import calculate_diff, compute_event_hash, PlanDiff
from intervals_plan.intervals_client import IntervalsClient


class SyncManager:
    def __init__(
        self,
        client: IntervalsClient,
        data_dir: Path,
        managed_prefix: str = "chatgpt-8wk-run-bike-2026-11-02",
    ):
        self.client = client
        self.data_dir = data_dir
        self.managed_prefix = managed_prefix
        self.manifest_file = data_dir / "manifest.json"
        self.backup_mgr = BackupManager(data_dir / "backups")
        self.audit_logger = AuditLogger(data_dir / "audit.log")

    def load_manifest(self) -> Dict[str, Any]:
        """Load manifest data from data/manifest.json."""
        if not self.manifest_file.is_file():
            return {"last_updated": None, "records": {}}
        try:
            return json.loads(self.manifest_file.read_text(encoding="utf-8"))
        except Exception:
            return {"last_updated": None, "records": {}}

    def save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Save manifest data to data/manifest.json."""
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest["last_updated"] = datetime.now().isoformat()
        self.manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def preview_sync(
        self,
        desired_events: List[IntervalsEvent],
        start_date: str,
        end_date: str,
    ) -> Tuple[PlanDiff, List[IntervalsEvent]]:
        """Fetch live state and compute plan diff without mutation."""
        live_events = self.client.list_events(start_date, end_date)
        manifest = self.load_manifest()
        diff = calculate_diff(desired_events, live_events, manifest, self.managed_prefix)
        return diff, live_events

    def apply_sync(
        self,
        desired_events: List[IntervalsEvent],
        start_date: str,
        end_date: str,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Safely execute synchronization:
        1. Pre-flight diff & conflict check.
        2. Create backup snapshot.
        3. Execute bulk upsert.
        4. Re-read back and verify every write.
        5. Update manifest and audit log.
        """
        diff, live_events = self.preview_sync(desired_events, start_date, end_date)

        if diff.conflicts and not force:
            raise RuntimeError(
                f"Sync aborted: {len(diff.conflicts)} manual conflict(s) detected on Intervals.icu! "
                "Use --force to overwrite external modifications, or edit the plan."
            )

        # 1. Backup live state
        backup_path = self.backup_mgr.create_backup(live_events, tag="presync")

        events_to_upload = desired_events if force else (diff.to_create + [d.event for d in diff.to_update])

        if not events_to_upload and not force:
            return {
                "status": "UP_TO_DATE",
                "message": "All events are already synchronized.",
                "created": 0,
                "updated": 0,
                "backup_path": str(backup_path),
            }

        # 2. Bulk upsert
        upserted = self.client.bulk_upsert_events(events_to_upload)

        # 3. Post-write read-back verification
        verified_live = self.client.list_events(start_date, end_date)
        verified_by_ext_id = {e.external_id: e for e in verified_live if e.external_id}

        unverified = []
        for target in events_to_upload:
            if target.external_id not in verified_by_ext_id:
                unverified.append(target.name)

        if unverified:
            raise RuntimeError(
                f"Verification warning: {len(unverified)} event(s) could not be verified on Intervals.icu after write: {unverified}"
            )

        # 4. Update manifest
        manifest = self.load_manifest()
        for ev in verified_live:
            if ev.external_id and ev.external_id.startswith(self.managed_prefix):
                manifest["records"][ev.external_id] = {
                    "intervals_id": ev.id,
                    "name": ev.name,
                    "date": ev.start_date_local,
                    "type": ev.type,
                    "last_known_hash": compute_event_hash(ev),
                    "last_sync_time": datetime.now().isoformat(),
                }
        self.save_manifest(manifest)

        # 5. Log audit trail
        self.audit_logger.log(
            action="SYNC_APPLY",
            target_ids=[e.external_id or e.name for e in events_to_upload],
            status="SUCCESS",
            details={
                "backup_file": str(backup_path),
                "created_count": len(diff.to_create),
                "updated_count": len(diff.to_update),
                "verified_count": len(events_to_upload),
            },
        )

        return {
            "status": "SUCCESS",
            "created": len(diff.to_create),
            "updated": len(diff.to_update),
            "total_verified": len(events_to_upload),
            "backup_path": str(backup_path),
        }
