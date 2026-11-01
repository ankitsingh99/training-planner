"""
Tests for AuditLogger.
"""

from pathlib import Path
import tempfile

from intervals_plan.audit import AuditLogger


def test_audit_logger():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "audit.log"
        logger = AuditLogger(log_file)

        # Initially empty
        assert logger.list_entries() == []

        # Log entries
        logger.log("CREATE_EVENT", ["101"], "SUCCESS", {"name": "Run"})
        logger.log("DELETE_EVENT", ["102"], "SUCCESS", {})

        # Add a corrupted line to test exception handling
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("corrupted line that is not json\n")

        entries = logger.list_entries(limit=10)
        assert len(entries) == 2
        assert entries[0]["action"] == "CREATE_EVENT"
        assert entries[1]["action"] == "DELETE_EVENT"
