"""
Audit trail logging for all mutations and sync operations.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        action: str,
        target_ids: List[str],
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append an audit entry to data/audit.log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target_ids": target_ids,
            "status": status,
            "details": details or {},
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def list_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Read and return recent audit entries."""
        if not self.log_path.is_file():
            return []
        entries = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries[-limit:]

