"""Typed application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def validate_production_storage_paths(
    environment: str,
    database_path: Path,
    cursor_path: Path,
) -> None:
    """Reject repository-local storage when the collector runs in production."""
    if environment != "production":
        return

    repository_root = Path(__file__).resolve().parents[1]
    for setting_name, path in (
        ("SECMON_DATABASE_PATH", database_path),
        ("SECMON_SSH_CURSOR_PATH", cursor_path),
    ):
        resolved_path = path.expanduser().resolve()
        if not path.is_absolute() or resolved_path.is_relative_to(repository_root):
            raise ValueError(
                f"{setting_name} must be an absolute path outside the repository in production"
            )


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
    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None
    telegram_timeout_seconds: float = Field(default=5.0, ge=0.1)
    telegram_min_severity: int = Field(default=3, ge=1, le=5)
    telegram_cooldown_seconds: int = Field(default=60, ge=0)

    @model_validator(mode="after")
    def _validate_production_paths(self) -> Settings:
        validate_production_storage_paths(
            self.environment,
            self.database_path,
            self.ssh_cursor_path,
        )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
