"""
Unit tests for workout schema and duration calculations.
"""

import unittest
from intervals_plan.workout_schema import (
    calc_duration,
    create_repeat,
    create_step,
    format_duration,
)


class TestWorkoutSchema(unittest.TestCase):
    def test_single_step_duration(self):
        step = create_step(300, "5 min easy")
        self.assertEqual(calc_duration(step), 300)

    def test_nested_repeat_duration(self):
        # 4 x (4 min hard + 3 min recovery) = 4 * 420 = 1680s
        work = create_step(240, "4 min hard")
        rest = create_step(180, "3 min easy")
        block = create_repeat(4, "4 x 4 min", [work, rest])
        self.assertEqual(calc_duration(block), 1680)

    def test_multi_set_microburst_duration(self):
        # 2 sets of [ 10 x (30s on + 30s off) = 600s + 300s rest ] = 2 * 900 = 1800s
        on = create_step(30, "Hard")
        off = create_step(30, "Easy")
        reps = create_repeat(10, "10 reps", [on, off])
        set_rest = create_step(300, "Between sets")
        multi_set = create_repeat(2, "2 sets", [reps, set_rest])

        self.assertEqual(calc_duration(multi_set), 1800)

    def test_format_duration(self):
        self.assertEqual(format_duration(None), "N/A")
        self.assertEqual(format_duration(2400), "40m")
        self.assertEqual(format_duration(2910), "48m 30s")
        self.assertEqual(format_duration(45), "45s")


if __name__ == "__main__":
    unittest.main()

