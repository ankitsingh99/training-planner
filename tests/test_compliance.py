"""
Unit tests for PlanComplianceEngine and planned vs actual execution reporting.
"""

import datetime
import unittest

from intervals_plan.api_models import IntervalsActivity, IntervalsEvent
from intervals_plan.compliance import MatchedSession, PlanComplianceEngine


class TestPlanCompliance(unittest.TestCase):
    def setUp(self):
        self.engine = PlanComplianceEngine(tolerance_minutes=15)

    def test_empty_events_and_activities(self):
        report = self.engine.evaluate([], [])
        self.assertEqual(report.planned_count, 0)
        self.assertEqual(report.completed_count, 0)
        self.assertEqual(report.execution_rate_pct, 100.0)
        self.assertEqual(report.volume_compliance_pct, 100.0)
        self.assertEqual(report.compliance_rating, "OPTIMAL")

    def test_optimal_execution_matching(self):
        planned = [
            IntervalsEvent(
                id="e1",
                start_date_local="2026-11-03T07:00:00",
                type="Run",
                moving_time=3600,
                name="W1 5K Intervals",
            ),
            IntervalsEvent(
                id="e2",
                start_date_local="2026-11-05T07:00:00",
                type="Ride",
                moving_time=4800,
                name="W1 Seiler 4x8m",
            ),
            IntervalsEvent(
                id="e3",
                start_date_local="2026-11-02T07:00:00",
                category="NOTE",
                name="Rest Day",
            ),
        ]
        activities = [
            IntervalsActivity(
                id="a1",
                start_date_local="2026-11-03T07:15:00",
                type="Run",
                moving_time=3540,
                icu_training_load=55.0,
            ),
            IntervalsActivity(
                id="a2",
                start_date_local="2026-11-05T07:10:00",
                type="Ride",
                moving_time=4900,
                icu_training_load=70.0,
            ),
        ]
        report = self.engine.evaluate(
            planned,
            activities,
            start_date=datetime.date(2026, 11, 2),
            end_date=datetime.date(2026, 11, 8),
        )
        self.assertEqual(report.planned_count, 2)
        self.assertEqual(report.completed_count, 2)
        self.assertEqual(report.execution_rate_pct, 100.0)
        self.assertEqual(len(report.missed_workouts), 0)
        self.assertEqual(report.compliance_rating, "OPTIMAL")
        self.assertEqual(len(report.matched_sessions), 2)
        self.assertEqual(report.matched_sessions[0].status, "COMPLETED")

    def test_under_training_and_missed_sessions(self):
        planned = [
            IntervalsEvent(id="e1", start_date_local="2026-11-03T07:00:00", type="Run", moving_time=3600),
            IntervalsEvent(id="e2", start_date_local="2026-11-04T07:00:00", type="Run", moving_time=3000),
            IntervalsEvent(id="e3", start_date_local="2026-11-05T07:00:00", type="Ride", moving_time=4800),
            IntervalsEvent(id="e4", start_date_local="2026-11-07T07:00:00", type="Ride", moving_time=7200),
        ]
        activities = [
            IntervalsActivity(id="a1", start_date_local="2026-11-03T07:00:00", type="Run", moving_time=1800),
        ]
        report = self.engine.evaluate(planned, activities)
        self.assertEqual(report.planned_count, 4)
        self.assertEqual(report.completed_count, 1)
        self.assertLess(report.execution_rate_pct, 50.0)
        self.assertEqual(len(report.missed_workouts), 3)
        self.assertEqual(report.compliance_rating, "UNDER_TRAINING")
        self.assertTrue(any("Volume execution is low" in o for o in report.coaching_observations))

    def test_over_training_risk_and_unplanned(self):
        planned = [
            IntervalsEvent(id="e1", start_date_local="2026-11-03T07:00:00", type="Run", moving_time=3000),
        ]
        activities = [
            IntervalsActivity(id="a1", start_date_local="2026-11-03T07:00:00", type="Run", moving_time=6000, icu_training_load=110),
            IntervalsActivity(id="a2", start_date_local="2026-11-04T07:00:00", type="Ride", moving_time=7200, icu_training_load=150),
        ]
        report = self.engine.evaluate(planned, activities)
        self.assertEqual(report.compliance_rating, "OVER_TRAINING_RISK")
        self.assertEqual(len(report.unplanned_activities), 1)
        self.assertTrue(any("Actual volume significantly exceeds plan" in o for o in report.coaching_observations))

    def test_acceptable_compliance_bounds(self):
        planned = [
            IntervalsEvent(id="e1", start_date_local="2026-11-03T07:00:00", type="Run", moving_time=3600),
            IntervalsEvent(id="e2", start_date_local="2026-11-05T07:00:00", type="Ride", moving_time=3600),
        ]
        activities = [
            IntervalsActivity(id="a1", start_date_local="2026-11-03T07:00:00", type="Run", moving_time=3600),
            IntervalsActivity(id="a2", start_date_local="2026-11-05T07:00:00", type="Ride", moving_time=2900),
        ]
        report = self.engine.evaluate(planned, activities)
        self.assertIn(report.compliance_rating, ["ACCEPTABLE", "OPTIMAL"])
        d = report.to_dict()
        self.assertIn("execution_rate_pct", d)
        self.assertIn("matched_sessions", d)


if __name__ == "__main__":
    unittest.main()
