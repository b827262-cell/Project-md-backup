"""Typed application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings; secrets are supplied by the environment, never committed."""

    model_config = SettingsConfigDict(env_prefix="SECMON_", env_file=".env", extra="ignore")

    app_name: str = "SecMon"
    environment: str = Field(default="development", pattern="^(development|test|production)$")
    database_path: Path = Path("./var/secmon.db")
    ssh_log_path: Path = Path("/var/log/auth.log")
    ssh_cursor_path: Path = Path("./var/ssh_cursor.position")
    collect_interval_seconds: float = Field(default=5.0, ge=0.5)
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    trusted_proxy_cidrs: tuple[str, ...] = ()
    auto_block_enabled: bool = False
    telegram_enabled: bool = False
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_timeout_seconds: float = Field(default=5.0, ge=0.1)
    telegram_min_severity: int = Field(default=3, ge=1, le=5)
    telegram_cooldown_seconds: int = Field(default=60, ge=0)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
