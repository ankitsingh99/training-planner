"""
Unit Tests for COROS Training Hub & EvoLab Engine.
Verifies fatigue score calculations, zone mapping, load recommendations,
Running Fitness 4-pillar breakdowns, race predictions, and Training Effect.
"""

from intervals_plan.coros_evolab import (
    CorosEvoLabEngine,
    CorosFatigueZone,
    format_pace,
    format_time_hms,
)


def test_format_helpers():
    assert format_time_hms(125) == "02:05"
    assert format_time_hms(3665) == "01:01:05"
    assert format_pace(270) == "4:30 /km"
    assert format_pace(315) == "5:15 /km"


def test_calculate_fatigue_zones():
    # 1. Balanced: Load Impact == Base Fitness -> 50.0 (OPTIMIZED)
    score, zone, desc, trend = CorosEvoLabEngine.calculate_fatigue(base_fitness=50.0, load_impact=50.0)
    assert score == 50.0
    assert zone == CorosFatigueZone.OPTIMIZED
    assert "sweet spot" in desc.lower()

    # 2. Tapered / Fresh: Load Impact < Base Fitness -> (PERFORMANCE)
    score, zone, _, _ = CorosEvoLabEngine.calculate_fatigue(base_fitness=50.0, load_impact=35.0)
    assert score < 40.0
    assert zone == CorosFatigueZone.PERFORMANCE

    # 3. Minimal: Very low load impact -> (MINIMAL)
    score, zone, _, _ = CorosEvoLabEngine.calculate_fatigue(base_fitness=60.0, load_impact=20.0)
    assert score < 20.0
    assert zone == CorosFatigueZone.MINIMAL

    # 4. Overreaching / High: Load Impact > Base Fitness -> (HIGH)
    score, zone, _, _ = CorosEvoLabEngine.calculate_fatigue(base_fitness=40.0, load_impact=52.0)
    assert 60.0 <= score < 80.0
    assert zone == CorosFatigueZone.HIGH

    # 5. Excessive: Huge acute spike -> (EXCESSIVE)
    score, zone, _, _ = CorosEvoLabEngine.calculate_fatigue(base_fitness=30.0, load_impact=60.0)
    assert score >= 80.0
    assert zone == CorosFatigueZone.EXCESSIVE


def test_load_recommendation_bounds():
    base = 45.0
    # Recommended range: 45 * 7 * 0.85 = 267.75, 45 * 7 * 1.25 = 393.75
    load, rec_min, rec_max, status = CorosEvoLabEngine.calculate_load_recommendation(base, [45.0] * 7)
    assert status == "RECOMMENDED"
    assert rec_min <= load <= rec_max

    # Below recommendation
    load_low, _, _, status_low = CorosEvoLabEngine.calculate_load_recommendation(base, [20.0] * 7)
    assert status_low == "BELOW"
    assert load_low < rec_min

    # Excessive load
    load_high, _, _, status_high = CorosEvoLabEngine.calculate_load_recommendation(base, [70.0] * 7)
    assert status_high == "EXCESSIVE"
    assert load_high > rec_max


def test_running_fitness_four_pillars():
    # 4:30 /km threshold pace = 270s
    rf = CorosEvoLabEngine.calculate_running_fitness(threshold_pace_sec_km=270, weekly_hours=8.0)
    assert 60.0 <= rf.overall_score <= 75.0
    assert 40.0 <= rf.base_score <= 100.0
    assert 40.0 <= rf.endurance_score <= 100.0
    assert 40.0 <= rf.speed_score <= 100.0
    assert 40.0 <= rf.sprint_score <= 100.0
    assert rf.threshold_pace_formatted == "4:30 /km"


def test_race_predictor_monotonicity():
    preds = CorosEvoLabEngine.predict_races(threshold_pace_sec_km=270, weekly_hours=8.0)
    assert len(preds) == 4
    names = [p.distance_name for p in preds]
    assert names == ["5K", "10K", "Half Marathon", "Marathon"]

    # Verify time strictly increases with distance
    times = [p.predicted_seconds for p in preds]
    assert times[0] < times[1] < times[2] < times[3]
    # Check 10k is ~45 min (2700s)
    assert 2500 <= times[1] <= 2900


def test_training_effect_and_recovery():
    # Hard threshold session
    res = CorosEvoLabEngine.calculate_training_effect(
        duration_seconds=3600,
        load_tss=75.0,
        hr_avg=170,
        lthr=182,
        fatigue_score=55.0,
        hours_elapsed=6.0,
    )
    assert 2.0 <= res.aerobic_te <= 5.0
    assert res.aerobic_label in ("Maintaining", "Improving", "Optimized", "Overreaching")
    assert 0.0 <= res.anaerobic_te <= 5.0
    assert res.recovery_hours > 0.0
    assert res.recovery_state in ("FRESH", "TIRED", "EXHAUSTED")

    # Zero duration guard
    zero_res = CorosEvoLabEngine.calculate_training_effect(duration_seconds=0, load_tss=0)
    assert zero_res.aerobic_te == 0.0
    assert zero_res.recovery_hours == 0.0
    assert zero_res.recovery_pct == 100
    assert zero_res.recovery_state == "FRESH"


def test_full_hub_evaluation():
    hub = CorosEvoLabEngine.evaluate_full_hub(
        base_fitness=42.0,
        load_impact=46.0,
        recent_daily_loads=[35.0, 40.0, 50.0, 45.0, 60.0, 30.0, 48.0],
        threshold_pace_sec_km=270,
        weekly_hours=8.5,
        last_workout_load=65.0,
        last_workout_duration_secs=3600,
        last_workout_hr=158,
        athlete_lthr=182,
        hours_since_last_workout=10.0,
    )
    assert "evolab" in hub
    assert "running_fitness" in hub
    assert "race_predictions" in hub
    assert "training_effect" in hub
    assert hub["evolab"]["fatigue_zone"] == CorosFatigueZone.OPTIMIZED
    assert len(hub["race_predictions"]) == 4
