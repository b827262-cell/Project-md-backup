from pathlib import Path

from backend.config import Settings


def test_settings_are_safe_by_default() -> None:
    settings = Settings()
    assert settings.auto_block_enabled is False
    assert settings.database_path == Path("var/secmon.db")
    assert settings.ssh_log_path == Path("/var/log/auth.log")
    assert settings.ssh_cursor_path == Path("./var/ssh_cursor.position")
    assert settings.collect_interval_seconds == 5.0
    assert settings.telegram_enabled is False
    assert settings.telegram_timeout_seconds == 5.0
    assert settings.telegram_min_severity == 3
    assert settings.telegram_cooldown_seconds == 60
