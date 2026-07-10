"""Log source service using the P1 canonical schema."""

from datetime import datetime
from pathlib import Path
from typing import Any

from backend.database import Database
from backend.models import LogSource


class LogSourcesService:
    def __init__(self, database_path: Path | None = None):
        self.db = Database(database_path)

    @staticmethod
    def _model(row: tuple[Any, ...]) -> LogSource:
        return LogSource(**dict(zip(
            ("id", "name", "source_type", "source_path", "config_json", "enabled",
             "status", "last_event_at", "last_error", "events_today",
             "parse_errors_today", "created_at", "updated_at"), row, strict=True
        )))

    def create_log_source(self, name: str, device_path: str, parser_type: str,
                          status: str = "unknown") -> int:
        import sqlite3
        status = {"active": "healthy", "inactive": "disabled"}.get(status, status)
        try:
            with self.db.get_connection() as conn:
                cur = conn.execute(
                    "INSERT INTO log_sources (name, source_type, source_path, status) "
                    "VALUES (?, ?, ?, ?)",
                    (name, parser_type, device_path, status),
                )
                if cur.lastrowid is None:
                    raise RuntimeError("Failed to create log source")
                return cur.lastrowid
        except sqlite3.IntegrityError as e:
            raise RuntimeError(f"Failed to create log source: {e}") from e

    def _get(self, clause: str, value: object) -> LogSource | None:
        columns = (
            "id, name, source_type, source_path, config_json, enabled, status, "
            "last_event_at, last_error, events_today, parse_errors_today, created_at, updated_at"
        )
        with self.db.get_connection() as conn:
            row = conn.execute(
                f"SELECT {columns} FROM log_sources " + clause,
                (value,),
            ).fetchone()
        return self._model(row) if row else None

    def get_log_source(self, log_source_id: int) -> LogSource | None:
        return self._get("WHERE id = ?", log_source_id)

    def get_log_source_by_name(self, name: str) -> LogSource | None:
        return self._get("WHERE name = ?", name)

    def get_all_log_sources(self) -> list[LogSource]:
        columns = (
            "id, name, source_type, source_path, config_json, enabled, status, "
            "last_event_at, last_error, events_today, parse_errors_today, created_at, updated_at"
        )
        with self.db.get_connection() as conn:
            rows = conn.execute(
                f"SELECT {columns} FROM log_sources ORDER BY id"
            ).fetchall()
        return [self._model(row) for row in rows]

    def update_log_source(self, log_source_id: int, name: str | None = None,
                          device_path: str | None = None, parser_type: str | None = None,
                          status: str | None = None) -> bool:
        fields: dict[str, Any] = {}
        if name is not None:
            fields["name"] = name
        if device_path is not None:
            fields["source_path"] = device_path
        if parser_type is not None:
            fields["source_type"] = parser_type
        if status is not None:
            fields["status"] = {"active": "healthy", "inactive": "disabled"}.get(status, status)

        if not fields:
            return True
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "UPDATE log_sources SET " + ", ".join(f"{key} = ?" for key in fields.keys()) +
                ", updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                list(fields.values()) + [log_source_id],
            )
            return cur.rowcount > 0

    def delete_log_source(self, log_source_id: int) -> bool:
        with self.db.get_connection() as conn:
            return conn.execute(
                "DELETE FROM log_sources WHERE id = ?",
                (log_source_id,)
            ).rowcount > 0

    def set_last_scanned(self, log_source_id: int, timestamp: datetime | None = None) -> bool:
        ts_val = (timestamp or datetime.now()).isoformat()
        with self.db.get_connection() as conn:
            return conn.execute(
                "UPDATE log_sources SET last_event_at = ?, "
                "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (ts_val, log_source_id),
            ).rowcount > 0

    def get_default_log_sources(self) -> list[LogSource]:
        return [LogSource(id=i, name=name, source_type="file", source_path=path,
                          status="unknown", created_at=datetime.now().isoformat(),
                          updated_at=datetime.now().isoformat())
                for i, (name, path) in enumerate((
                    ("SSH Journal", "/var/log/auth.log"),
                    ("Privileged Logs", "/var/log/authpriv.log"),
                    ("Secure Logs", "/var/log/secure")), 1)]

    def ensure_default_log_sources_exist(self) -> list[LogSource]:
        for source in self.get_default_log_sources():
            if self.get_log_source_by_name(source.name) is None:
                self.create_log_source(source.name, source.source_path or "", source.source_type)
        return self.get_all_log_sources()
