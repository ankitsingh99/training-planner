"""
Unit tests for SyncManager: diff, manifest update, read-back verification, and error handling.
"""

from pathlib import Path
import tempfile
from unittest.mock import MagicMock
import unittest

from intervals_plan.api_models import IntervalsEvent
from intervals_plan.diff import compute_event_hash
from intervals_plan.sync import SyncManager


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmpdir.name)
        self.mock_client = MagicMock()
        self.sync_mgr = SyncManager(client=self.mock_client, data_dir=self.data_dir, managed_prefix="test")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_sync_idempotency_when_up_to_date(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run", external_id="test-1", moving_time=1800)
        ]
        live = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run", external_id="test-1", moving_time=1800, id=101)
        ]
        self.mock_client.list_events.return_value = live

        res = self.sync_mgr.apply_sync(desired, "2026-11-02", "2026-11-08")
        self.assertEqual(res["status"], "UP_TO_DATE")
        self.mock_client.bulk_upsert_events.assert_not_called()

    def test_sync_applies_and_verifies_read_back(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run New", external_id="test-1", moving_time=1800)
        ]
        saved_live = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run New", external_id="test-1", moving_time=1800, id=202)
        ]
        self.mock_client.list_events.side_effect = [[], saved_live]
        self.mock_client.bulk_upsert_events.return_value = saved_live

        res = self.sync_mgr.apply_sync(desired, "2026-11-02", "2026-11-08")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["created"], 1)

        manifest = self.sync_mgr.load_manifest()
        self.assertIn("test-1", manifest["records"])
        self.assertEqual(manifest["records"]["test-1"]["intervals_id"], 202)

    def test_corrupt_manifest_loads_empty(self):
        manifest_file = self.data_dir / "manifest.json"
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text("corrupted json {", encoding="utf-8")
        data = self.sync_mgr.load_manifest()
        self.assertEqual(data["records"], {})

    def test_conflict_raises_error_without_force(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Original", external_id="test-1")
        ]
        live = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Edited on Web", external_id="test-1", id=101)
        ]
        # Manifest has original hash
        self.sync_mgr.save_manifest({
            "records": {
                "test-1": {
                    "intervals_id": 101,
                    "last_known_hash": compute_event_hash(desired[0]),
                }
            }
        })
        self.mock_client.list_events.return_value = live

        with self.assertRaises(RuntimeError):
            self.sync_mgr.apply_sync(desired, "2026-11-02", "2026-11-08", force=False)

    def test_unverified_events_raises_error(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Ghost Workout", external_id="test-missing")
        ]
        # First list is empty, write occurs, but second list is still empty (read-back failed)
        self.mock_client.list_events.side_effect = [[], []]
        self.mock_client.bulk_upsert_events.return_value = []

        with self.assertRaises(RuntimeError):
            self.sync_mgr.apply_sync(desired, "2026-11-02", "2026-11-08")


if __name__ == "__main__":
    unittest.main()
