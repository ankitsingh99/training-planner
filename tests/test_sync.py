"""
Unit tests for SyncManager: diff, manifest update, and read-back verification.
"""

from pathlib import Path
import tempfile
from unittest.mock import MagicMock
import unittest

from intervals_plan.api_models import IntervalsEvent
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
        # Live matches desired
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
        # First list: empty (new)
        # Second list (post-write read-back): contains event with ID 202
        saved_live = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run New", external_id="test-1", moving_time=1800, id=202)
        ]
        self.mock_client.list_events.side_effect = [[], saved_live]
        self.mock_client.bulk_upsert_events.return_value = saved_live

        res = self.sync_mgr.apply_sync(desired, "2026-11-02", "2026-11-08")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["created"], 1)

        # Verify manifest recorded the verified event ID
        manifest = self.sync_mgr.load_manifest()
        self.assertIn("test-1", manifest["records"])
        self.assertEqual(manifest["records"]["test-1"]["intervals_id"], 202)


if __name__ == "__main__":
    unittest.main()
