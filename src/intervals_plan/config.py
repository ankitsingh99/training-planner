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

        cfg = cls(
            api_key=key,
            athlete_id=athlete_id,
            default_prefix=prefix,
            data_dir=data_dir,
        )
        cfg.ensure_dirs()
        return cfg

    def ensure_dirs(self) -> None:
        """Ensure necessary data and backup directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "backups").mkdir(parents=True, exist_ok=True)

    def summary(self) -> str:
        """Safe representation of active configuration."""
        return (
            f"Athlete ID:     {self.athlete_id}\n"
            f"Base URL:       {self.base_url}\n"
            f"Managed Prefix: {self.default_prefix}\n"
            f"Data Directory: {self.data_dir}\n"
            f"API Key:        {redact_secret(self.api_key)}"
        )
