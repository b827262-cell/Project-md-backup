"""Database helper functions for SecMon backend."""

import sqlite3
from pathlib import Path

from backend.config import get_settings


class Database:
    """Database connection and helper functions."""

    def __init__(self, database_path: Path | None = None):
        """Initialize database connection."""
        self.settings = get_settings()
        self.database_path = database_path or self.settings.database_path

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with WAL mode and proper settings."""
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def create_ssh_log_source(self) -> int:
        """Create SSH log source entry in log_sources table.

        Returns:
            ID of the created log source.
        """
        connection = None
        try:
            connection = self.get_connection()

            cursor = connection.execute(
                """INSERT INTO log_sources
                   (name, source_type, source_path, enabled, status)
                   VALUES (?, ?, ?, ?, ?)""",
                ("SSH Journal", "file", str(Path("/var/log/auth.log")), 1, "healthy"),
            )
            connection.commit()

            source_id = cursor.lastrowid
            if source_id is None:
                raise RuntimeError("Failed to create log source: lastrowid is None")
            print(f"Created SSH log source with ID: {source_id}")
            return source_id

        except Exception as e:
            print(f"Error creating SSH log source: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

    def get_log_source_id(self, name: str) -> int | None:
        """Get log source ID by name.

        Args:
            name: Log source name.

        Returns:
            Log source ID or None if not found.
        """
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.execute(
                "SELECT id FROM log_sources WHERE name = ?",
                (name,),
            )
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            if connection:
                connection.close()
