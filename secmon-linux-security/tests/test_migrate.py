import sqlite3
from pathlib import Path

from database.migrate import migrate


def test_initial_migration_creates_schema(tmp_path: Path) -> None:
    database = tmp_path / "secmon.db"
    migrate(database, Path("database/migrations"))
    with sqlite3.connect(database) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"schema_migrations", "attack_events", "attackers", "audit_logs"} <= tables
        assert connection.execute("PRAGMA quick_check").fetchone() == ("ok",)
