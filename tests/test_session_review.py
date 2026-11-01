"""
Unit tests for SessionReviewer post-workout debriefs and aerobic decoupling analysis.
"""

import unittest
from intervals_plan.session_review import SessionReviewInput, SessionReviewer


class TestSessionReviewer(unittest.TestCase):
    def setUp(self):
        self.reviewer = SessionReviewer()

    def test_disciplined_easy_session(self):
        inp = SessionReviewInput(
            activity_name="Recovery Spin",
            sport="Ride",
            duration_minutes=40,
            rpe=3,
            feeling="normal",
            avg_hr=120,
            target_hr_max=135,
            decoupling_pct=2.1,
        )
        res = self.reviewer.review(inp)
        self.assertEqual(res.intensity_discipline, "DISCIPLINED_EASY")
        self.assertEqual(res.aerobic_efficiency, "EFFICIENT")
        self.assertGreaterEqual(res.execution_score, 85)
        self.assertIn("EXECUTE AS PLANNED", res.next_day_recommendation)

    def test_over_exerted_easy_session(self):
        inp = SessionReviewInput(
            activity_name="Zone 2 Easy Base Run",
            sport="Run",
            duration_minutes=60,
            rpe=7,  # Way too hard for an easy run
            feeling="normal",
            avg_hr=165,
            target_hr_max=145,
        )
        res = self.reviewer.review(inp)
        self.assertEqual(res.intensity_discipline, "OVER_EXERTED")
        self.assertLess(res.execution_score, 85)
        self.assertTrue(any("80/20 model dictates keeping easy days truly easy" in f for f in res.coaching_feedback))

    def test_quality_session_on_target_and_elevated_drift(self):
        inp = SessionReviewInput(
            activity_name="5K Pace Intervals",
            sport="Run",
            duration_minutes=55,
            rpe=8,
            feeling="strong",
            decoupling_pct=6.5,  # Cardiac drift elevated
        )
        res = self.reviewer.review(inp)
        self.assertEqual(res.intensity_discipline, "ON_TARGET")
        self.assertEqual(res.aerobic_efficiency, "CARDIO_DRIFT_ELEVATED")

    def test_pain_or_niggle_safety_gate(self):
        inp = SessionReviewInput(
            activity_name="Long Aerobic Run",
            sport="Run",
            duration_minutes=90,
            rpe=6,
            feeling="pain_or_niggle",
        )
        res = self.reviewer.review(inp)
        self.assertLessEqual(res.execution_score, 60)
        self.assertIn("MANDATORY REST / PHYSIOTHERAPY", res.next_day_recommendation)
        self.assertIn("1.0-1.2g carbohydrate", res.fueling_critique)

    def test_exhaustion_and_heavy_legs(self):
        # Exhausted
        inp_ex = SessionReviewInput(
            activity_name="Tempo Ride",
            sport="Ride",
            duration_minutes=75,
            rpe=9,
            feeling="exhausted",
        )
        res_ex = self.reviewer.review(inp_ex)
        self.assertIn("ACTIVE RECOVERY", res_ex.next_day_recommendation)

        # Heavy legs
        inp_legs = SessionReviewInput(
            activity_name="Midweek Base Run",
            sport="Run",
            duration_minutes=45,
            rpe=5,
            feeling="heavy_legs",
        )
        res_legs = self.reviewer.review(inp_legs)
        self.assertIn("EASY BASE", res_legs.next_day_recommendation)

    def test_to_dict_serialization(self):
        inp = SessionReviewInput(
            activity_name="Recovery Jog",
            sport="Run",
            duration_minutes=30,
            rpe=3,
            feeling="strong",
        )
        res = self.reviewer.review(inp)
        d = res.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["activity_name"], "Recovery Jog")
        self.assertIn("execution_score", d)


if __name__ == "__main__":
    unittest.main()
