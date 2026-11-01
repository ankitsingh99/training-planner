"""
Unit tests for workout schema, step helpers, and duration calculations.
"""

import unittest
from intervals_plan.workout_schema import (
    calc_duration,
    create_repeat,
    create_step,
    format_duration,
    steps_to_intervals_text,
)


class TestWorkoutSchema(unittest.TestCase):
    def test_single_step_duration(self):
        step = create_step(300, "5 min easy")
        self.assertEqual(calc_duration(step), 300)

    def test_nested_repeat_duration(self):
        work = create_step(240, "4 min hard")
        rest = create_step(180, "3 min easy")
        block = create_repeat(4, "4 x 4 min", [work, rest])
        self.assertEqual(calc_duration(block), 1680)

    def test_dict_and_list_duration(self):
        # Dict duration
        d_step = {"duration": 400}
        self.assertEqual(calc_duration(d_step), 400)
        
        # Dict with nested steps
        d_block = {"reps": 3, "steps": [{"duration": 100}, {"duration": 50}]}
        self.assertEqual(calc_duration(d_block), 450)

        # Empty dict or non-step
        self.assertEqual(calc_duration({}), 0)
        self.assertEqual(calc_duration("invalid"), 0)

        # List
        self.assertEqual(calc_duration([d_step, d_block]), 850)

    def test_multi_set_microburst_duration(self):
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

    def test_create_step_with_hr_and_power(self):
        step = create_step(
            seconds=600,
            text="Warmup",
            hr_start=70,
            hr_end=80,
            hr_units="%lthr",
            p_start=65,
            p_end=75,
            p_units="%ftp",
        )
        self.assertEqual(step.duration, 600)
        self.assertIsNotNone(step.hr)
        self.assertEqual(step.hr.start, 70)
        self.assertIsNotNone(step.power)
        self.assertEqual(step.power.get("start"), 65)

    def test_steps_to_intervals_text(self):
        s1 = create_step(300, "Warmup", hr_start=65, hr_end=75)
        s2 = create_step(45, "Strides")
        nested = create_repeat(3, "Intervals", [s1, s2])
        lines = steps_to_intervals_text([nested])
        self.assertTrue(len(lines) >= 3)
        self.assertTrue(any("3x Intervals" in l for l in lines))


if __name__ == "__main__":
    unittest.main()
