"""Settings loader. TOML on disk, env overrides, validated by pydantic."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_config_dir
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable runtime config.

    Env overrides use the `MEALPLAN_` prefix, e.g. `MEALPLAN_LOG_LEVEL=DEBUG`.
    """

    model_config = SettingsConfigDict(
        env_prefix="MEALPLAN_",
        env_file=".env",
        extra="ignore",
    )

    log_level: str = "INFO"
    redact_keys: bool = True
    no_network: bool = False
    llm_endpoint: str = "https://api.local.invalid/v1/plan"
    llm_api_key: str = Field(default="", repr=False)
    nutrition_db_url: str = "https://nutrition.local.invalid/v2"
    data_dir: Path = Field(default_factory=lambda: Path(user_config_dir("ai-meal-plan-generator")))
    default_days: int = 7
    default_meals_per_day: int = 3
    planner_seed: int = 6767


def load_settings() -> Settings:
    """Load settings from env + optional TOML in the user config dir.

    TOML is read first, env wins on conflict. Missing TOML is not an error —
    a fresh install has no config file yet.
    """
    toml_path = Path(user_config_dir("ai-meal-plan-generator")) / "config.toml"
    if toml_path.exists():
        os.environ.setdefault("MEALPLAN_CONFIG_FILE", str(toml_path))
    return Settings()