"""Apply ordered SQLite migrations without requiring an external migration tool."""

import argparse
import sqlite3
from pathlib import Path


def migrate(database: Path, migrations_dir: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        
        # Ensure schema_migrations table exists
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "    version TEXT PRIMARY KEY,"
            "    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        
        # Get applied migrations
        applied = {
            row[0]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
        
        for migration in sorted(migrations_dir.glob("*.sql")):
            version = migration.stem
            if version not in applied:
                connection.executescript(migration.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
                    (version,),
                )


def migrate_latest(database: Path, migrations_dir: Path) -> None:
    """Compatibility API for tests and callers that apply all migrations."""
    migrate(database, migrations_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("./var/secmon.db"))
    parser.add_argument("--migrations", type=Path, default=Path("database/migrations"))
    args = parser.parse_args()
    migrate(args.database, args.migrations)


if __name__ == "__main__":
    main()
