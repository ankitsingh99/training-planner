"""
Athlete Profile and Training Goals Configuration.
Allows full customization of goals, weekly hours, intensity distribution, and schedule preferences.
"""

from dataclasses import asdict, dataclass, field
import datetime
import json
import pathlib
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AthleteProfileConfig:
    """Configurable athlete parameters and training preferences."""

    # Primary athletic focus: dual_sport_hybrid, running, cycling, general_fitness
    goal: str = "dual_sport_hybrid"
    
    # Weekly commitment in hours (e.g. 8.0)
    weekly_hours: float = 8.0
    
    # Training philosophy: polarized_80_20, pyramidal, hrv_governed
    philosophy: str = "polarized_80_20"
    
    # Planning lookahead window: 1_week or 2_weeks
    planning_horizon: str = "1_week"
    
    # Event / Target race specifics (optional)
    target_event_name: Optional[str] = None
    target_race_distance: Optional[str] = "10k"
    target_race_date: Optional[str] = None
    
    # Physiological benchmarks (auto-populated from Intervals or custom)
    lthr_run: int = 182
    lthr_bike: int = 182
    max_hr: int = 200
    ftp_bike: int = 250
    resting_hr_baseline: Optional[int] = 50
    
    # Life constraints & schedule notes (e.g. "no_thursday_bike", "achilles_niggle", "travel_weekend")
    constraints: List[str] = field(default_factory=list)

    # Preferred weekly schedule slots
    # day-of-week (0=Mon, 6=Sun) or name: session role
    schedule_preference: Dict[str, str] = field(default_factory=lambda: {
        "Monday": "rest",
        "Tuesday": "run_quality",
        "Wednesday": "run_aerobic",
        "Thursday": "bike_quality",
        "Friday": "recovery_or_rest",
        "Saturday": "long_ride",
        "Sunday": "long_run",
    })

    # Safety limits
    max_safe_acwr: float = 1.35
    max_ctl_ramp_per_week: float = 6.0
    rhr_alert_elevation_bpm: int = 4

    def get_periodization_phase(self, current_date: Optional[datetime.date] = None) -> Tuple[str, Optional[int]]:
        """
        Determine periodization phase based on target race date:
        - > 8 weeks out: 'base'
        - 4 to 8 weeks out: 'build'
        - 2 to 4 weeks out: 'peak'
        - 0 to 2 weeks out: 'taper'
        - < 0 weeks: 'recovery'
        - No date: 'maintenance'
        Returns: (phase_name, weeks_remaining)
        """
        if not self.target_race_date:
            return "maintenance", None

        try:
            target = datetime.date.fromisoformat(self.target_race_date)
            today = current_date or datetime.date.today()
            days_out = (target - today).days
            weeks_out = max(0, days_out // 7)

            if days_out < 0:
                return "recovery", -1
            elif weeks_out <= 2:
                return "taper", weeks_out
            elif weeks_out <= 4:
                return "peak", weeks_out
            elif weeks_out <= 8:
                return "build", weeks_out
            else:
                return "base", weeks_out
        except Exception:
            return "maintenance", None

    @classmethod
    def default(cls) -> "AthleteProfileConfig":
        return cls()

    @classmethod
    def load(cls, path: Optional[pathlib.Path] = None) -> "AthleteProfileConfig":
        """Load profile from json file or return defaults if not found."""
        profile_path = path or (pathlib.Path.cwd() / "data" / "athlete_profile.json")
        if not profile_path.exists():
            default_inst = cls.default()
            default_inst.save(profile_path)
            return default_inst

        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls.default()

    def save(self, path: Optional[pathlib.Path] = None) -> None:
        """Persist profile to JSON."""
        profile_path = path or (pathlib.Path.cwd() / "data" / "athlete_profile.json")
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AthleteProfileConfig":
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

