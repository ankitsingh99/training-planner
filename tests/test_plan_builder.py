"""
Unit tests for plan builder and validation.
"""

from datetime import date
import unittest
from intervals_plan.plan_builder import PlanBuilder, get_default_8wk_plan
from intervals_plan.plan_models import PlanConfig, TrainingPlan, WeekSpec


class TestPlanBuilder(unittest.TestCase):
    def setUp(self):
        self.plan = get_default_8wk_plan()
        self.builder = PlanBuilder(self.plan)

    def test_plan_validation(self):
        errors = self.plan.validate()
        self.assertEqual(errors, [])

    def test_plan_validation_errors(self):
        bad_config = PlanConfig(total_weeks=0, start_date="bad-date")
        bad_week = WeekSpec(
            week_number=1,
            phase="Base",
            run_label="Run",
            run_reps=0,
            run_work_min=0,
            run_recovery_sec=120,
            easy_ride_min=10,  # < 20
        )
        invalid_plan = TrainingPlan(
            title="Invalid",
            description="Test",
            config=bad_config,
            weeks=[bad_week],
        )
        errs = invalid_plan.validate()
        self.assertTrue(any("Invalid total_weeks" in e for e in errs))
        self.assertTrue(any("Invalid start_date format" in e for e in errs))
        self.assertTrue(any("Mismatch: config specifies" in e for e in errs))
        self.assertTrue(any("run_reps must be > 0" in e for e in errs))
        self.assertTrue(any("run_work_min must be > 0" in e for e in errs))
        self.assertTrue(any("outside safe aerobic range" in e for e in errs))
        self.assertTrue(any("Plan lacks a scheduled deload week" in e for e in errs))

    def test_total_events_count(self):
        events = self.builder.build_all_events()
        self.assertEqual(len(events), 31)

    def test_date_format_and_continuity(self):
        events = self.builder.build_all_events()
        for ev in events:
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
        w4_events = [e for e in self.builder.build_all_events() if "w4-" in (e.external_id or "")]
        bike_workouts = [e for e in w4_events if "thu-optional-bike" in (e.external_id or "")]
        self.assertEqual(len(bike_workouts), 0)

    def test_week8_retest_present(self):
        w8_events = [e for e in self.builder.build_all_events() if "w8-" in (e.external_id or "")]
        retest = [e for e in w8_events if "5k-retest" in (e.external_id or "")]
        self.assertEqual(len(retest), 1)


if __name__ == "__main__":
    unittest.main()
