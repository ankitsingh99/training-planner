"""
Unit tests for Sports Science intra-workout nutrition and fueling calculations.
"""

import unittest
from intervals_plan.fueling import calculate_fueling, FuelingRecommendation


class TestFuelingCalculator(unittest.TestCase):
    def test_short_session_under_45m(self):
        rec = calculate_fueling(30, sport="Run", intensity="low")
        self.assertEqual(rec.duration_minutes, 30)
        self.assertEqual(rec.carbs_per_hour_g, 0)
        self.assertEqual(rec.total_carbs_g, 0)
        self.assertEqual(rec.sodium_mg_per_hour, 0)
        self.assertIn("Hydration only", rec.strategy_summary)

        rec_mod = calculate_fueling(40, sport="Ride", intensity="high")
        self.assertEqual(rec_mod.hydration_ml_per_hour, 300)
        self.assertEqual(rec_mod.carbs_per_hour_g, 0)

    def test_medium_session_45_to_75m(self):
        # High intensity
        rec_hi = calculate_fueling(60, sport="Run", intensity="high")
        self.assertEqual(rec_hi.carbs_per_hour_g, 30)
        self.assertEqual(rec_hi.total_carbs_g, 30)
        self.assertEqual(rec_hi.sodium_mg_per_hour, 300)

        # Moderate intensity
        rec_mod = calculate_fueling(60, sport="Ride", intensity="moderate")
        self.assertEqual(rec_mod.carbs_per_hour_g, 15)
        self.assertEqual(rec_mod.sodium_mg_per_hour, 200)

        # Low intensity
        rec_low = calculate_fueling(60, sport="Run", intensity="low")
        self.assertEqual(rec_low.carbs_per_hour_g, 0)
        self.assertEqual(rec_low.sodium_mg_per_hour, 0)

    def test_long_session_75_to_150m_disciplines(self):
        # Cycling
        rec_ride = calculate_fueling(120, sport="Ride", intensity="moderate")
        self.assertEqual(rec_ride.carbs_per_hour_g, 60)
        self.assertEqual(rec_ride.total_carbs_g, 120)
        self.assertEqual(rec_ride.sodium_mg_per_hour, 500)

        rec_ride_hi = calculate_fueling(120, sport="Bike", intensity="high")
        self.assertEqual(rec_ride_hi.carbs_per_hour_g, 75)

        # Running
        rec_run = calculate_fueling(90, sport="Run", intensity="moderate")
        self.assertEqual(rec_run.carbs_per_hour_g, 60)
        self.assertEqual(rec_run.total_carbs_g, 90)

        rec_run_low = calculate_fueling(90, sport="Run", intensity="low")
        self.assertEqual(rec_run_low.carbs_per_hour_g, 45)

        # Brick
        rec_brick = calculate_fueling(120, sport="Brick", intensity="moderate")
        self.assertEqual(rec_brick.carbs_per_hour_g, 65)
        self.assertEqual(rec_brick.sodium_mg_per_hour, 550)

        # Swim
        rec_swim = calculate_fueling(90, sport="Swim", intensity="moderate")
        self.assertEqual(rec_swim.carbs_per_hour_g, 40)

    def test_ultra_session_over_150m(self):
        # Long Ride (Ironman / Gran Fondo)
        rec_ride = calculate_fueling(180, sport="Ride", intensity="high")
        self.assertEqual(rec_ride.carbs_per_hour_g, 90)
        self.assertEqual(rec_ride.total_carbs_g, 270)
        self.assertEqual(rec_ride.sodium_mg_per_hour, 700)
        self.assertIn("Ultra-endurance cycling", rec_ride.strategy_summary)

        rec_ride_mod = calculate_fueling(180, sport="Cycling", intensity="moderate")
        self.assertEqual(rec_ride_mod.carbs_per_hour_g, 80)

        # Long Run
        rec_run = calculate_fueling(180, sport="Run", intensity="moderate")
        self.assertEqual(rec_run.carbs_per_hour_g, 60)
        self.assertEqual(rec_run.total_carbs_g, 180)

        # Long Brick
        rec_brick = calculate_fueling(240, sport="Brick", intensity="moderate")
        self.assertEqual(rec_brick.carbs_per_hour_g, 75)
        self.assertEqual(rec_brick.total_carbs_g, 300)

        # Other sport
        rec_other = calculate_fueling(180, sport="Other", intensity="moderate")
        self.assertEqual(rec_other.carbs_per_hour_g, 50)

    def test_to_dict_serialization(self):
        rec = calculate_fueling(90, sport="Run", intensity="moderate")
        d = rec.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["duration_minutes"], 90)
        self.assertEqual(d["sport"], "Run")
        self.assertIn("carbs_per_hour_g", d)
        self.assertIn("recommendations", d)


if __name__ == "__main__":
    unittest.main()
