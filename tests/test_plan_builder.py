"""
Unit tests for plan builder and validation.
"""

from datetime import date
import unittest
from intervals_plan.plan_builder import PlanBuilder, get_default_8wk_plan


class TestPlanBuilder(unittest.TestCase):
    def setUp(self):
        self.plan = get_default_8wk_plan()
        self.builder = PlanBuilder(self.plan)

    def test_plan_validation(self):
        errors = self.plan.validate()
        self.assertEqual(errors, [])

    def test_total_events_count(self):
        events = self.builder.build_all_events()
        # 8 runs + 8 easy rides + 6 optional bike workouts + 8 weekend notes + 1 5k retest = 31 events
        self.assertEqual(len(events), 31)

    def test_date_format_and_continuity(self):
        events = self.builder.build_all_events()
        for ev in events:
            # Must strictly follow YYYY-MM-DDTHH:MM:SS format
            self.assertEqual(len(ev.start_date_local), 19)
            self.assertTrue(ev.start_date_local.endswith("T00:00:00"))
            self.assertTrue("+" not in ev.start_date_local)
            self.assertTrue("Z" not in ev.start_date_local)

    def test_stable_external_ids(self):
        events = self.builder.build_all_events()
        ext_ids = [e.external_id for e in events]
        self.assertEqual(len(ext_ids), len(set(ext_ids)), "External IDs must be completely unique!")
        for ext in ext_ids:
            self.assertTrue(ext.startswith(self.plan.config.prefix))

    def test_week4_deload_policy(self):
        # Week 4 hard bike intervals should be omitted by default for restorative deload
        w4_events = [e for e in self.builder.build_all_events() if "w4-" in (e.external_id or "")]
        bike_workouts = [e for e in w4_events if "thu-optional-bike" in (e.external_id or "")]
        self.assertEqual(len(bike_workouts), 0, "Week 4 should not have high-intensity bike intervals in deload!")

    def test_week8_retest_present(self):
        w8_events = [e for e in self.builder.build_all_events() if "w8-" in (e.external_id or "")]
        retest = [e for e in w8_events if "5k-retest" in (e.external_id or "")]
        self.assertEqual(len(retest), 1, "Week 8 must include the 5 km Time Trial retest!")


if __name__ == "__main__":
    unittest.main()

