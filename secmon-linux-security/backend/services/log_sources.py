"""Log sources management service."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from backend.database import Database
from backend.models import LogSource


class LogSourcesService:
    """Service for managing log sources."""

    def __init__(self, database_path: Optional[Path] = None):
        """Initialize log sources service.

        Args:
            database_path: Optional custom database path.
        """
        self.db = Database(database_path)

    def create_log_source(
        self,
        name: str,
        device_path: str,
        parser_type: str,
        status: str = "active",
    ) -> int:
        """Create a new log source.

        Args:
            name: Log source name (must be unique).
            device_path: Path to the log file/device.
            parser_type: Type of parser to use.
            status: Status of the log source (active/inactive/error).

        Returns:
            ID of the created log source.
        """
        connection = None
        try:
            connection = self.db.get_connection()

            cursor = connection.execute(
                """INSERT INTO log_sources
                   (name, device_path, parser_type, status, last_scanned)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, device_path, parser_type, status, None),
            )
            connection.commit()

            source_id = cursor.lastrowid
            if source_id is None:
                raise RuntimeError("Failed to create log source: lastrowid is None")

            print(f"Created log source '{name}' with ID: {source_id}")
            return source_id

        except Exception as e:
            print(f"Error creating log source '{name}': {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

    def get_log_source(self, log_source_id: int) -> Optional[LogSource]:
        """Get a log source by ID.

        Args:
            log_source_id: Log source ID.

        Returns:
            LogSource object or None if not found.
        """
        connection = None
        try:
            connection = self.db.get_connection()
            cursor = connection.execute(
                "SELECT id, name, device_path, parser_type, status, last_scanned, created_at FROM log_sources WHERE id = ?",
                (log_source_id,),
            )
            result = cursor.fetchone()

            if not result:
                return None

            return LogSource(
                id=result[0],
                name=result[1],
                source_type=result[2],  # device_path is used as source_type
                source_path=result[3],
                config_json=None,
                enabled=1,  # Default enabled
                status=result[4],
                last_event_at=None,
                last_error=None,
                events_today=0,
                parse_errors_today=0,
                created_at=result[5],
                updated_at=result[5],
            )

        finally:
            if connection:
                connection.close()

    def get_log_source_by_name(self, name: str) -> Optional[LogSource]:
        """Get a log source by name.

        Args:
            name: Log source name.

        Returns:
            LogSource object or None if not found.
        """
        connection = None
        try:
            connection = self.db.get_connection()
            cursor = connection.execute(
                "SELECT id, name, device_path, parser_type, status, last_scanned, created_at FROM log_sources WHERE name = ?",
                (name,),
            )
            result = cursor.fetchone()

            if not result:
                return None

            return LogSource(
                id=result[0],
                name=result[1],
                source_type=result[2],
                source_path=result[3],
                config_json=None,
                enabled=1,
                status=result[4],
                last_event_at=None,
                last_error=None,
                events_today=0,
                parse_errors_today=0,
                created_at=result[5],
                updated_at=result[5],
            )

        finally:
            if connection:
                connection.close()

    def get_all_log_sources(self) -> List[LogSource]:
        """Get all log sources.

        Returns:
            List of LogSource objects.
        """
        connection = None
        try:
            connection = self.db.get_connection()
            cursor = connection.execute(
                "SELECT id, name, device_path, parser_type, status, last_scanned, created_at FROM log_sources ORDER BY id",
            )
            results = cursor.fetchall()

            return [
                LogSource(
                    id=row[0],
                    name=row[1],
                    source_type=row[2],
                    source_path=row[3],
                    config_json=None,
                    enabled=1,
                    status=row[4],
                    last_event_at=None,
                    last_error=None,
                    events_today=0,
                    parse_errors_today=0,
                    created_at=row[5],
                    updated_at=row[5],
                )
                for row in results
            ]

        finally:
            if connection:
                connection.close()

    def update_log_source(
        self,
        log_source_id: int,
        name: Optional[str] = None,
        device_path: Optional[str] = None,
        parser_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        """Update a log source.

        Args:
            log_source_id: Log source ID.
            name: New name (optional).
            device_path: New device path (optional).
            parser_type: New parser type (optional).
            status: New status (optional).

        Returns:
            True if updated successfully, False otherwise.
        """
        connection = None
        try:
            connection = self.db.get_connection()

            # Build dynamic update query
            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if device_path is not None:
                updates.append("device_path = ?")
                params.append(device_path)
            if parser_type is not None:
                updates.append("parser_type = ?")
                params.append(parser_type)
            if status is not None:
                updates.append("status = ?")
                params.append(status)

            if not updates:
                return True  # Nothing to update

            params.append(log_source_id)
            query = f"UPDATE log_sources SET {', '.join(updates)} WHERE id = ?"
            cursor = connection.execute(query, params)
            connection.commit()

            print(f"Updated log source ID {log_source_id}")
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error updating log source ID {log_source_id}: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                connection.close()

    def delete_log_source(self, log_source_id: int) -> bool:
        """Delete a log source.

        Args:
            log_source_id: Log source ID.

        Returns:
            True if deleted successfully, False otherwise.
        """
        connection = None
        try:
            connection = self.db.get_connection()
            cursor = connection.execute(
                "DELETE FROM log_sources WHERE id = ?",
                (log_source_id,),
            )
            connection.commit()

            deleted = cursor.rowcount > 0
            if deleted:
                print(f"Deleted log source ID {log_source_id}")

            return deleted

        except Exception as e:
            print(f"Error deleting log source ID {log_source_id}: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                connection.close()

    def set_last_scanned(
        self,
        log_source_id: int,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Update the last scanned timestamp for a log source.

        Args:
            log_source_id: Log source ID.
            timestamp: Timestamp to set (defaults to now).

        Returns:
            True if updated successfully, False otherwise.
        """
        if timestamp is None:
            timestamp = datetime.now()

        connection = None
        try:
            connection = self.db.get_connection()
            cursor = connection.execute(
                "UPDATE log_sources SET last_scanned = ? WHERE id = ?",
                (timestamp.isoformat(), log_source_id),
            )
            connection.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error updating last_scanned for log source ID {log_source_id}: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                connection.close()

    def get_default_log_sources(self) -> List[LogSource]:
        """Get default log sources.

        Returns:
            List of default LogSource objects.
        """
        return [
            LogSource(
                id=1,
                name="SSH Journal",
                source_type="/var/log/auth.log",
                source_path="/var/log/auth.log",
                config_json=None,
                enabled=1,
                status="active",
                last_event_at=None,
                last_error=None,
                events_today=0,
                parse_errors_today=0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
            LogSource(
                id=2,
                name="Privileged Logs",
                source_type="/var/log/authpriv.log",
                source_path="/var/log/authpriv.log",
                config_json=None,
                enabled=1,
                status="active",
                last_event_at=None,
                last_error=None,
                events_today=0,
                parse_errors_today=0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
            LogSource(
                id=3,
                name="Secure Logs",
                source_type="/var/log/secure",
                source_path="/var/log/secure",
                config_json=None,
                enabled=1,
                status="active",
                last_event_at=None,
                last_error=None,
                events_today=0,
                parse_errors_today=0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            ),
        ]

    def ensure_default_log_sources_exist(self) -> List[LogSource]:
        """Ensure default log sources exist in the database.

        Returns:
            List of existing LogSource objects.
        """
        existing = self.get_all_log_sources()

        # Check if we need to create default sources
        names = {log_source.name for log_source in existing}

        defaults = self.get_default_log_sources()
        created = []

        for default in defaults:
            if default.name not in names:
                self.create_log_source(
                    name=default.name,
                    device_path=default.source_type,
                    parser_type="default",
                    status=default.status,
                )
                created.append(default)

        return self.get_all_log_sources()
