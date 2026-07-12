"""SSH Journal Collector for SecMon backend.

This module collects SSH authentication events from /var/log/auth.log,
parses them, and stores them in the database with deduplication.
"""

from __future__ import annotations

import logging
import socket
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.config import Settings, get_settings
from backend.models import AttackEvent
from backend.notifiers import TelegramNotifier
from backend.parsers.ssh_parser import SSHLogEntry, SSHParser

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Batch:
    """Represents a batch of parsed SSH log entries."""

    entries: list[AttackEvent] = field(default_factory=list)


class SSHCollector:
    """Collect SSH authentication failures from auth.log."""

    _source_name = "SSH Journal"

    def __init__(
        self,
        database_path: Path | None = None,
        cursor_path: Path | None = None,
        notifier: TelegramNotifier | None = None,
    ) -> None:
        """Initialize the collector and ensure the SSH log source exists."""
        self.settings = get_settings()
        self.database_path = Path(
            database_path or self._setting_value("database_path", Path("./var/secmon.db"))
        )
        self.parser = SSHParser()
        self.cursor_position_file = Path(
            cursor_path or self._setting_value(
                "ssh_cursor_path",
                Path("./var/ssh_cursor.position"),
            )
        )
        self.batch_size = 100
        self.notifier = notifier
        self._source_id: int | None = None
        self._hostname = socket.gethostname()
        self._last_inserted_events: list[AttackEvent] = []
        self._ssh_log_path = Path(
            self._setting_value("ssh_log_path", Path("/var/log/auth.log"))
        )
        self._telegram_min_severity = int(self._setting_value("telegram_min_severity", 3))
        self._initialize_log_source()

    def _setting_value(self, name: str, default: Any) -> Any:
        """Read a setting while remaining compatible with mocked settings objects."""
        if isinstance(self.settings, Settings):
            return getattr(self.settings, name)
        return vars(self.settings).get(name, default)

    def parse_ssh_line(self, line: str) -> SSHLogEntry | None:
        """Parse SSH line using the internal parser (compatibility method)."""
        return self.parser.parse_line(line)

    def _initialize_log_source(self) -> None:
        """Ensure the SSH log source exists in the database."""
        conn: sqlite3.Connection | None = None
        try:
            conn = sqlite3.connect(self.database_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")

            row = conn.execute(
                "SELECT id FROM log_sources WHERE name = ?",
                (self._source_name,),
            ).fetchone()
            if row is not None:
                self._source_id = int(row[0])
                logger.debug("SSH log source already exists with ID: %d", self._source_id)
                return

            cursor = conn.execute(
                """INSERT INTO log_sources
                   (name, source_type, source_path, enabled, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    self._source_name,
                    "file",
                    str(self._ssh_log_path),
                    1,
                    "healthy",
                ),
            )
            conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to create SSH log source")
            self._source_id = int(cursor.lastrowid)
            logger.info("Created SSH log source with ID: %d", self._source_id)
        except Exception:
            logger.exception("Failed to initialize SSH log source")
            if conn is not None:
                conn.rollback()
            raise
        finally:
            if conn is not None:
                conn.close()

    def _get_last_cursor_position(self) -> int:
        """Get the last cursor position from persistent storage."""
        try:
            if self.cursor_position_file.exists():
                position = int(self.cursor_position_file.read_text().strip())
                logger.debug("Loaded cursor position: %d", position)
                return position
            return 0
        except (OSError, ValueError) as exc:
            logger.warning("Failed to read cursor position: %s", exc)
            return 0

    def _save_cursor_position(self, position: int) -> None:
        """Save cursor position to persistent storage."""
        try:
            self.cursor_position_file.parent.mkdir(parents=True, exist_ok=True)
            self.cursor_position_file.write_text(str(position))
            logger.debug("Saved cursor position: %d", position)
        except OSError as exc:
            logger.error("Failed to save cursor position: %s", exc)
            raise

    def _get_upsert_events_query(self) -> str:
        """Get SQL query for upserting attack events."""
        return """INSERT OR IGNORE INTO attack_events
            (event_key, detected_at, sensor_host, source_id, source_type, src_ip,
             src_port, dst_port, protocol, attack_type, severity, signature, username,
             raw_log, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    def _get_upsert_attacker_query(self) -> str:
        """Get SQL query for upserting attacker information."""
        return """INSERT INTO attackers
            (src_ip, first_seen, last_seen, total_events, ssh_failures,
             threat_score, highest_severity, last_attack_type, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'observed', CURRENT_TIMESTAMP)
            ON CONFLICT(src_ip) DO UPDATE SET
              last_seen=excluded.last_seen,
              total_events=attackers.total_events+excluded.total_events,
              ssh_failures=attackers.ssh_failures+excluded.ssh_failures,
              threat_score=MIN(1000, attackers.threat_score+excluded.threat_score),
              highest_severity=MIN(attackers.highest_severity, excluded.highest_severity),
              last_attack_type=excluded.last_attack_type,
              updated_at=CURRENT_TIMESTAMP"""

    def _parse_log_lines(self, lines: list[str]) -> list[AttackEvent]:
        """Parse multiple log lines into AttackEvent objects."""
        events: list[AttackEvent] = []
        for line in lines:
            if not line.strip():
                continue

            try:
                entry = self.parser.parse_line(line)
            except ValueError as exc:
                logger.warning("Skipping malformed SSH line: %s", exc)
                continue

            if entry is None:
                continue

            attack_type = (
                "ssh_invalid_user"
                if entry.failure_reason in {"Invalid user", "Failed password for invalid user"}
                else "ssh_failed_password"
            )
            events.append(
                AttackEvent(
                    event_key=entry.event_key,
                    detected_at=entry.timestamp,
                    sensor_host=self._hostname,
                    source_id=self._source_id,
                    source_type="file",
                    src_ip=entry.source_ip,
                    src_port=entry.src_port,
                    dst_port=22,
                    protocol="tcp",
                    attack_type=attack_type,
                    severity=3,
                    signature=entry.failure_reason,
                    username=entry.username,
                    raw_log=line.rstrip("\n"),
                    created_at=datetime.now().isoformat(),
                )
            )

        return events

    def _collect_batch(self, lines: list[str]) -> Batch:
        """Collect and parse a batch of log lines."""
        return Batch(entries=self._parse_log_lines(lines))

    def _process_batch(self, batch: Batch) -> tuple[int, int]:
        """Process a batch of SSH events and store them in the database."""
        if not batch.entries:
            self._last_inserted_events = []
            return 0, 0

        new_events = 0
        new_attackers = 0
        inserted_events: list[AttackEvent] = []
        now = datetime.now().isoformat()
        conn: sqlite3.Connection | None = None

        try:
            conn = sqlite3.connect(self.database_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")

            cursor = conn.cursor()
            for event in batch.entries:
                inserted = cursor.execute(
                    self._get_upsert_events_query(),
                    (
                        event.event_key,
                        event.detected_at,
                        event.sensor_host,
                        event.source_id or self._source_id,
                        event.source_type,
                        event.src_ip,
                        event.src_port,
                        event.dst_port,
                        event.protocol,
                        event.attack_type,
                        event.severity,
                        event.signature,
                        event.username,
                        event.raw_log,
                        event.created_at,
                    ),
                ).rowcount

                if inserted != 1:
                    continue

                new_events += 1
                inserted_events.append(event)

                attacker_exists = cursor.execute(
                    "SELECT 1 FROM attackers WHERE src_ip = ?",
                    (event.src_ip,),
                ).fetchone()

                cursor.execute(
                    self._get_upsert_attacker_query(),
                    (
                        event.src_ip,
                        event.detected_at,
                        event.detected_at,
                        1,
                        1,
                        event.severity,
                        event.severity,
                        event.attack_type,
                    ),
                )
                if attacker_exists is None:
                    new_attackers += 1

            if self._source_id is not None:
                cursor.execute(
                    """
                    UPDATE log_sources
                    SET events_today = events_today + ?,
                        last_event_at = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (new_events, now, self._source_id),
                )

            conn.commit()
        except sqlite3.Error:
            logger.exception("Database error while processing SSH batch")
            if conn is not None:
                conn.rollback()
            raise
        except Exception:
            logger.exception("Unexpected error while processing SSH batch")
            if conn is not None:
                conn.rollback()
            raise
        finally:
            if conn is not None:
                conn.close()

        self._last_inserted_events = inserted_events
        return new_events, new_attackers

    def _build_telegram_alert(
        self,
        events: list[AttackEvent],
        new_events: int,
        new_attackers: int,
    ) -> str:
        """Build the aggregated Telegram alert text."""
        if not events:
            return ""

        top_sources = Counter(event.src_ip for event in events)
        usernames = sorted(
            {event.username for event in events if event.username and event.username.strip()}
        )
        time_values = sorted(event.detected_at for event in events)
        detected_range = (
            time_values[0]
            if len(time_values) == 1
            else f"{time_values[0]} - {time_values[-1]}"
        )

        lines = [
            "🚨 SecMon SSH Attack Alert",
            "",
            f"Host: {self._hostname}",
            f"New events: {new_events}",
            f"New attackers: {new_attackers}",
            f"Detected: {detected_range}",
            "",
            "Top sources:",
        ]

        for index, (ip, count) in enumerate(top_sources.most_common(5), start=1):
            lines.append(f"{index}. {ip} — {count} attempts")

        lines.append("")
        lines.append("Users:")
        if usernames:
            lines.extend(usernames)
        else:
            lines.append("- none")

        lines.append("")
        lines.append("Database: healthy")

        return "\n".join(lines)

    def _send_telegram_alerts(
        self,
        events: list[AttackEvent],
        new_events: int,
        new_attackers: int,
    ) -> None:
        """Send a single aggregated Telegram alert for a collection run."""
        if self.notifier is None or new_events <= 0:
            return

        eligible_events = [
            event for event in events if event.severity >= self._telegram_min_severity
        ]
        if not eligible_events:
            return

        alert_new_events = len(eligible_events)
        alert_new_attackers = len({event.src_ip for event in eligible_events})
        message = self._build_telegram_alert(
            eligible_events,
            alert_new_events,
            alert_new_attackers,
        )
        if not message:
            return

        try:
            if not self.notifier.send_message(message):
                logger.warning("Telegram notification failed for %d SSH events", alert_new_events)
        except Exception:
            logger.exception("Telegram notification raised an unexpected error")

    def collect_from_file(
        self,
        log_file_path: str | Path | None = None,
        batch_size: int = 100,
        wal_enabled: bool = True,
        busy_timeout: int = 5000,
    ) -> tuple[int, int]:
        """Collect SSH events from a log file."""
        log_path = Path(log_file_path or self._ssh_log_path)
        batch_size = max(1, batch_size)
        self._last_inserted_events = []
        if not log_path.exists():
            logger.error("Log file not found: %s", log_path)
            raise FileNotFoundError(f"Log file not found: {log_path}")

        if wal_enabled:
            try:
                conn = sqlite3.connect(self.database_path)
                conn.execute(f"PRAGMA busy_timeout={busy_timeout}")
                conn.close()
            except sqlite3.Error as exc:
                logger.warning("Could not set database busy timeout: %s", exc)

        total_new_events = 0
        total_new_attackers = 0
        inserted_events: list[AttackEvent] = []

        with open(log_path, encoding="utf-8", errors="replace") as log_file:
            initial_position = self._get_last_cursor_position()
            if initial_position > log_path.stat().st_size:
                logger.warning("Cursor exceeds file size; treating file as truncated/rotated")
                initial_position = 0

            log_file.seek(initial_position)
            current_position = initial_position

            while True:
                lines: list[str] = []
                for _ in range(batch_size):
                    line = log_file.readline()
                    if not line:
                        break
                    lines.append(line)
                    current_position = log_file.tell()

                if not lines:
                    break

                logger.debug(
                    "Processing batch of %d lines at position %d",
                    len(lines),
                    current_position,
                )
                batch = self._collect_batch(lines)
                new_events, new_attackers = self._process_batch(batch)
                total_new_events += new_events
                total_new_attackers += new_attackers
                inserted_events.extend(self._last_inserted_events)

                self._save_cursor_position(current_position)
                logger.info(
                    "Processed batch: %d new events, %d new attackers",
                    new_events,
                    new_attackers,
                )

        logger.info(
            "Collection complete. Total: %d new events, %d new attackers",
            total_new_events,
            total_new_attackers,
        )

        self._send_telegram_alerts(inserted_events, total_new_events, total_new_attackers)
        return total_new_events, total_new_attackers

    def collect_all(self, batch_size: int = 100) -> tuple[int, int]:
        """Collect all available SSH events from the configured log file."""
        logger.info("Starting SSH log collection")
        return self.collect_from_file(batch_size=batch_size)

    def reset_cursor(self) -> None:
        """Reset cursor position to start from the beginning of the log file."""
        self.cursor_position_file.unlink(missing_ok=True)
        logger.info("Cursor position reset to beginning")

    def test_connection(self) -> bool:
        """Test SSH collector connection to log file and database."""
        try:
            log_path = self._ssh_log_path
            if not log_path.exists():
                logger.error("Log file does not exist: %s", log_path)
                return False

            with open(log_path, encoding="utf-8", errors="replace") as file_handle:
                first_line = file_handle.readline()
                entry = self.parser.parse_line(first_line)
                if entry:
                    logger.info(
                        "Test line parsed successfully: %s - %s",
                        entry.timestamp,
                        entry.source_ip,
                    )
                else:
                    logger.info("Log file exists but no SSH events found in the first line")

            conn = sqlite3.connect(self.database_path)
            conn.execute("SELECT 1")
            conn.close()
            logger.info("Database connection successful")
            return True
        except Exception:
            logger.exception("Connection test failed")
            return False
