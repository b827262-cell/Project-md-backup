from pathlib import Path

from backend.config import Settings


def test_settings_are_safe_by_default() -> None:
    settings = Settings()
    assert settings.auto_block_enabled is False
    assert settings.database_path == Path("var/secmon.db")
