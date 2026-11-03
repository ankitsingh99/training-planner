"""
Configuration management for intervals-plan.
"""

from dataclasses import dataclass, field
import os
import pathlib
from typing import Optional
from intervals_plan.security import get_secure_key, redact_secret


def find_env_file() -> Optional[pathlib.Path]:
    """Search for .env file starting from current working directory upwards."""
    curr = pathlib.Path.cwd()
    for parent in [curr] + list(curr.parents):
        env_f = parent / ".env"
        if env_f.is_file():
            return env_f
    return None


def load_env_file(path: Optional[pathlib.Path] = None) -> None:
    """Load key-value pairs from .env into os.environ."""
    target = path or find_env_file()
    if not target or not target.is_file():
        return
    
    with open(target, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and v:
                    os.environ[k] = v


@dataclass
class Config:
    api_key: str = field(default="")
    athlete_id: str = field(default="0")
    base_url: str = field(default="https://intervals.icu/api/v1")
    default_prefix: str = field(default="chatgpt-8wk-run-bike-2026-11-02")
    data_dir: pathlib.Path = field(default_factory=lambda: pathlib.Path.cwd() / "data")
    user_agent: str = field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    # TrainingPeaks API settings
    tp_access_token: str = field(default="")
    tp_client_id: str = field(default="")
    tp_client_secret: str = field(default="")
    tp_athlete_id: str = field(default="")
    tp_base_url: str = field(default="https://api.trainingpeaks.com")
    # OpenRouter API settings (Token-Lean & Zero-Cost)
    openrouter_api_key: str = field(default="")
    openrouter_model: str = field(default="openrouter/free")
    openrouter_base_url: str = field(default="https://openrouter.ai/api/v1")
    # Garmin Connect API settings
    garmin_access_token: str = field(default="")
    garmin_consumer_key: str = field(default="")
    garmin_consumer_secret: str = field(default="")
    garmin_user_id: str = field(default="")
    garmin_base_url: str = field(default="https://connectapi.garmin.com")

    @classmethod
    def load(cls, prompt_if_missing: bool = False) -> "Config":
        load_env_file()
        key = os.environ.get("INTERVALS_API_KEY", "").strip().strip("'\"")
        if not key and prompt_if_missing:
            key = get_secure_key("INTERVALS_API_KEY")
        
        athlete_id = os.environ.get("INTERVALS_ATHLETE_ID", "0").strip()
        prefix = os.environ.get("INTERVALS_PREFIX", "chatgpt-8wk-run-bike-2026-11-02").strip()
        data_dir_env = os.environ.get("INTERVALS_DATA_DIR")
        data_dir = pathlib.Path(data_dir_env) if data_dir_env else pathlib.Path.cwd() / "data"

        # TrainingPeaks settings
        tp_token = os.environ.get("TRAININGPEAKS_ACCESS_TOKEN", "").strip().strip("'\"")
        tp_client_id = os.environ.get("TRAININGPEAKS_CLIENT_ID", "").strip().strip("'\"")
        tp_client_secret = os.environ.get("TRAININGPEAKS_CLIENT_SECRET", "").strip().strip("'\"")
        tp_athlete_id = os.environ.get("TRAININGPEAKS_ATHLETE_ID", "").strip().strip("'\"")
        tp_base_url = os.environ.get("TRAININGPEAKS_BASE_URL", "https://api.trainingpeaks.com").strip().strip("'\"")

        # OpenRouter settings
        or_key = os.environ.get("OPENROUTER_API_KEY", "").strip().strip("'\"")
        or_model = os.environ.get("OPENROUTER_MODEL", "openrouter/free").strip().strip("'\"")
        or_base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip().strip("'\"")

        # Garmin settings
        garmin_token = os.environ.get("GARMIN_ACCESS_TOKEN", "").strip().strip("'\"")
        garmin_key = os.environ.get("GARMIN_CONSUMER_KEY", "").strip().strip("'\"")
        garmin_sec = os.environ.get("GARMIN_CONSUMER_SECRET", "").strip().strip("'\"")
        garmin_uid = os.environ.get("GARMIN_USER_ID", "").strip().strip("'\"")
        garmin_base = os.environ.get("GARMIN_BASE_URL", "https://connectapi.garmin.com").strip().strip("'\"")

        cfg = cls(
            api_key=key,
            athlete_id=athlete_id,
            default_prefix=prefix,
            data_dir=data_dir,
            tp_access_token=tp_token,
            tp_client_id=tp_client_id,
            tp_client_secret=tp_client_secret,
            tp_athlete_id=tp_athlete_id,
            tp_base_url=tp_base_url,
            openrouter_api_key=or_key,
            openrouter_model=or_model,
            openrouter_base_url=or_base_url,
            garmin_access_token=garmin_token,
            garmin_consumer_key=garmin_key,
            garmin_consumer_secret=garmin_sec,
            garmin_user_id=garmin_uid,
            garmin_base_url=garmin_base,
        )
        cfg.ensure_dirs()
        return cfg

    def ensure_dirs(self) -> None:
        """Ensure necessary data, backup, and cache directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "backups").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "cache").mkdir(parents=True, exist_ok=True)

    def summary(self) -> str:
        """Safe representation of active configuration."""
        return (
            f"Athlete ID:           {self.athlete_id}\n"
            f"Base URL:             {self.base_url}\n"
            f"Managed Prefix:       {self.default_prefix}\n"
            f"Data Directory:       {self.data_dir}\n"
            f"Intervals Key:        {redact_secret(self.api_key)}\n"
            f"TrainingPeaks Token:  {redact_secret(self.tp_access_token)}\n"
            f"OpenRouter Model:     {self.openrouter_model}\n"
            f"OpenRouter Key:       {redact_secret(self.openrouter_api_key)}\n"
            f"Garmin Access Token:  {redact_secret(self.garmin_access_token)}"
        )

