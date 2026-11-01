"""
Unit tests for adaptive training rules and dynamic adjustments.
"""

import unittest
from intervals_plan.adaptive import AdaptiveEngine
from intervals_plan.plan_builder import PlanBuilder, get_default_8wk_plan


class TestAdaptiveEngine(unittest.TestCase):
    def setUp(self):
        self.plan = get_default_8wk_plan()
        self.builder = PlanBuilder(self.plan)
        self.events = self.builder.build_all_events()

    def test_club_ride_hard_suppresses_thursday_bike(self):
        # Week 1 Thursday was 4 x 4 min hard VO2
        w1_thu = next(e for e in self.events if "w1-thu-optional-bike" in (e.external_id or ""))
        self.assertIn("VO2", w1_thu.name)

        adapted = AdaptiveEngine.adapt_for_hard_club_ride(self.events, week_number=1)
        w1_thu_adapted = next(e for e in adapted if "w1-thu-optional-bike" in (e.external_id or ""))

        self.assertIn("Recovery Spin", w1_thu_adapted.name)
        self.assertEqual(w1_thu_adapted.moving_time, 1800)  # 30 min recovery spin
        self.assertIn("Substituted due to hard weekend club ride", w1_thu_adapted.description)

    def test_reschedule_club_ride_day(self):
        # Move W1 weekend ride from Saturday (2026-11-07) to Sunday (2026-11-08)
        adapted = AdaptiveEngine.reschedule_club_ride(self.events, week_number=1, target_date_str="2026-11-08")
        w1_ride = next(e for e in adapted if "w1-weekend-club-ride" in (e.external_id or ""))
        self.assertEqual(w1_ride.start_date_local, "2026-11-08T00:00:00")

    def test_adjust_aerobic_duration(self):
        # Add +10 minutes to all easy aerobic rides
        adapted = AdaptiveEngine.adjust_aerobic_duration(self.events, delta_minutes=10)
        w1_easy = next(e for e in adapted if "w1-tue-easy-ride" in (e.external_id or ""))
        self.assertEqual(w1_easy.moving_time, 3000)  # 40m -> 50m (3000s)
        self.assertIn("50 min", w1_easy.name)


if __name__ == "__main__":
    unittest.main()

