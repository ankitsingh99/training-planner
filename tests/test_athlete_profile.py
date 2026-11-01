"""
Tests for AthleteProfileConfig.
"""

import json
from pathlib import Path
from intervals_plan.athlete_profile import AthleteProfileConfig


def test_athlete_profile_defaults():
    profile = AthleteProfileConfig.default()
    assert profile.goal == "dual_sport_hybrid"
    assert profile.weekly_hours == 8.0
    assert profile.philosophy == "polarized_80_20"
    assert profile.planning_horizon == "1_week"
    assert profile.lthr_run == 182
    assert profile.ftp_bike == 250


def test_athlete_profile_save_and_load(tmp_path: Path):
    path = tmp_path / "test_profile.json"
    profile = AthleteProfileConfig(
        goal="running",
        weekly_hours=6.5,
        philosophy="pyramidal",
        planning_horizon="2_weeks",
        target_race_distance="half_marathon",
    )
    profile.save(path)

    loaded = AthleteProfileConfig.load(path)
    assert loaded.goal == "running"
    assert loaded.weekly_hours == 6.5
    assert loaded.philosophy == "pyramidal"
    assert loaded.planning_horizon == "2_weeks"
    assert loaded.target_race_distance == "half_marathon"


def test_athlete_profile_from_dict_ignores_extra_keys():
    data = {
        "goal": "cycling",
        "weekly_hours": 10.0,
        "unexpected_key": "some_value",
    }
    profile = AthleteProfileConfig.from_dict(data)
    assert profile.goal == "cycling"
    assert profile.weekly_hours == 10.0
