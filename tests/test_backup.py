"""
Tests for BackupManager.
"""

from pathlib import Path
import pytest
import tempfile

from intervals_plan.api_models import IntervalsEvent
from intervals_plan.backup import BackupManager


def test_backup_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        b_dir = Path(tmpdir)
        mgr = BackupManager(b_dir)

        assert mgr.list_backups() == []

        events = [
            IntervalsEvent(start_date_local="2026-11-02T07:00:00", name="Run", id=101)
        ]
        b_path = mgr.create_backup(events, tag="presync")
        assert b_path.is_file()

        backups = mgr.list_backups()
        assert len(backups) == 1

        # Load by exact path
        loaded = mgr.load_backup(str(b_path))
        assert len(loaded) == 1
        assert loaded[0].id == 101

        # Load by partial ID
        loaded_partial = mgr.load_backup("presync")
        assert len(loaded_partial) == 1

        # Error on missing
        with pytest.raises(FileNotFoundError):
            mgr.load_backup("nonexistent_backup")

