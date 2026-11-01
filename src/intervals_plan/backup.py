"""
Backup management for calendar events and plan state.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from intervals_plan.api_models import IntervalsEvent


class BackupManager:
    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, events: List[IntervalsEvent], tag: str = "sync") -> Path:
        """Save a snapshot of events to a timestamped JSON file."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{ts}_{tag}.json"
        dest = self.backup_dir / filename
        payload = [e.to_dict() for e in events]
        dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return dest

    def list_backups(self) -> List[Path]:
        """Return a sorted list of existing backup files (newest first)."""
        backups = list(self.backup_dir.glob("backup_*.json"))
        return sorted(backups, reverse=True)

    def load_backup(self, backup_path_or_id: str) -> List[IntervalsEvent]:
        """Load and return events from a backup file."""
        path = Path(backup_path_or_id)
        if not path.is_file():
            # Check within backup directory
            matches = list(self.backup_dir.glob(f"*{backup_path_or_id}*.json"))
            if matches:
                path = matches[0]
            else:
                raise FileNotFoundError(f"Backup file not found: {backup_path_or_id}")

        data = json.loads(path.read_text(encoding="utf-8"))
        return [IntervalsEvent.from_dict(item) for item in data]
