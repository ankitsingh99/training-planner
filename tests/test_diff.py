"""
Unit tests for diff calculation, conflict detection, and summary formatting.
"""

import unittest
from intervals_plan.api_models import IntervalsEvent
from intervals_plan.diff import calculate_diff, compute_event_hash


class TestDiff(unittest.TestCase):
    def test_detect_addition(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run 1", external_id="test-1")
        ]
        live = []
        diff = calculate_diff(desired, live)
        self.assertEqual(len(diff.to_create), 1)
        self.assertEqual(len(diff.to_update), 0)
        self.assertEqual(len(diff.unchanged), 0)
        self.assertTrue(diff.has_mutations)
        self.assertIn("Plan Diff Summary", diff.summary())

    def test_detect_event_without_external_id(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Unmanaged", external_id=None)
        ]
        diff = calculate_diff(desired, [])
        self.assertEqual(len(diff.to_create), 1)

    def test_detect_unchanged(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run 1", external_id="test-1", moving_time=1800)
        ]
        live = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Run 1", external_id="test-1", moving_time=1800, id=101)
        ]
        diff = calculate_diff(desired, live)
        self.assertEqual(len(diff.to_create), 0)
        self.assertEqual(len(diff.to_update), 0)
        self.assertEqual(len(diff.unchanged), 1)

    def test_detect_field_update(self):
        desired = [
            IntervalsEvent(
                start_date_local="2026-11-02T08:00:00",
                name="Run 1 Updated",
                description="New desc",
                external_id="test-1",
                moving_time=2400,
            )
        ]
        live = [
            IntervalsEvent(
                start_date_local="2026-11-02T07:00:00",
                name="Run 1",
                description="Old desc",
                external_id="test-1",
                moving_time=1800,
                id=101,
            )
        ]
        diff = calculate_diff(desired, live)
        self.assertEqual(len(diff.to_update), 1)
        up = diff.to_update[0]
        self.assertIn("name", up.changes)
        self.assertIn("moving_time", up.changes)
        self.assertIn("start_date_local", up.changes)
        self.assertIn("description", up.changes)

    def test_detect_manual_conflict(self):
        desired = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="Original Name", external_id="test-1")
        ]
        live = [
            IntervalsEvent(start_date_local="2026-11-02T00:00:00", name="User Edited Name", external_id="test-1", id=101)
        ]
        manifest = {
            "records": {
                "test-1": {
                    "intervals_id": 101,
                    "last_known_hash": compute_event_hash(desired[0]),
                }
            }
        }
        diff = calculate_diff(desired, live, manifest=manifest)
        self.assertEqual(len(diff.conflicts), 1)
        self.assertIn("modified directly on Intervals.icu", diff.conflicts[0].conflict_reason)


if __name__ == "__main__":
    unittest.main()
