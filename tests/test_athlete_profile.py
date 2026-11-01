"""
Tests for AthleteProfileConfig.
"""

import datetime
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


def test_athlete_profile_load_fallback(tmp_path: Path):
    # Non-existent file
    missing_path = tmp_path / "nonexistent.json"
    loaded = AthleteProfileConfig.load(missing_path)
    assert loaded.goal == "dual_sport_hybrid"
    assert missing_path.is_file()  # Auto-saved default

    # Corrupted JSON
    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text("invalid json contents", encoding="utf-8")
    loaded_corrupt = AthleteProfileConfig.load(corrupt_path)
    assert loaded_corrupt.goal == "dual_sport_hybrid"


def test_athlete_profile_periodization_phases():
    today = datetime.date(2026, 11, 2)

    # 1. No race date
    p1 = AthleteProfileConfig(target_race_date=None)
    assert p1.get_periodization_phase(today) == ("maintenance", None)

    # 2. Invalid date
    p2 = AthleteProfileConfig(target_race_date="not-a-date")
    assert p2.get_periodization_phase(today) == ("maintenance", None)

    # 3. Past race date (recovery)
    p3 = AthleteProfileConfig(target_race_date="2026-10-20")
    assert p3.get_periodization_phase(today) == ("recovery", -1)

    # 4. Taper (10 days out)
    p4 = AthleteProfileConfig(target_race_date="2026-11-12")
    phase, weeks = p4.get_periodization_phase(today)
    assert phase == "taper"
    assert weeks <= 2

    # 5. Peak (21 days out)
    p5 = AthleteProfileConfig(target_race_date="2026-11-23")
    assert p5.get_periodization_phase(today)[0] == "peak"

    # 6. Build (45 days out)
    p6 = AthleteProfileConfig(target_race_date="2026-12-17")
    assert p6.get_periodization_phase(today)[0] == "build"

    # 7. Base (80 days out)
    p7 = AthleteProfileConfig(target_race_date="2027-01-21")
    assert p7.get_periodization_phase(today)[0] == "base"


def test_athlete_profile_from_dict_ignores_extra_keys():
    data = {
        "goal": "cycling",
        "weekly_hours": 10.0,
        "unexpected_key": "some_value",
    }
    profile = AthleteProfileConfig.from_dict(data)
    assert profile.goal == "cycling"
    assert profile.weekly_hours == 10.0
