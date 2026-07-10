"""SSH Journal Collector for SecMon backend.

This module collects SSH authentication events from /var/log/auth.log,
parses them, and stores them in the database with deduplication.
"""

import logging
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from backend.config import get_settings
from backend.models import AttackEvent
from backend.parsers.ssh_parser import SSHLogEntry, SSHParser

# Configure module-level logging
logger = logging.getLogger(__name__)


@dataclass
class Batch:
    """Represents a batch of parsed SSH log entries."""

    entries: list[AttackEvent] = field(default_factory=list)


class SSHCollector:
    """Collects SSH authentication events from journal logs."""

    def __init__(self, database_path: Path | None = None, cursor_path: Path | None = None):
        """Initialize SSH Journal Collector.

        Args:
            database_path: Database file path. If None, uses default from config.
        """
        self.settings = get_settings()
        self.database_path = database_path or self.settings.database_path
        self.parser = SSHParser()
        self.cursor_position_file = cursor_path or Path(
            os.environ.get("SECMON_SSH_CURSOR_PATH", "./var/ssh_cursor.position")
        )
        self.batch_size = 100
        self._source_id: int | None = None
        self._initialize_log_source()

    def parse_ssh_line(self, line: str) -> SSHLogEntry | None:
        """Parse SSH line using internal parser (compatibility method)."""
        return self.parser.parse_line(line)

    def _initialize_log_source(self) -> None:
        """Ensure SSH log source exists in database."""
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")

            cursor = conn.execute(
                "SELECT id FROM log_sources WHERE name = ?",
                ("SSH Journal",),
            )
            result = cursor.fetchone()

            if not result:
                cursor = conn.execute(
                    """INSERT INTO log_sources
                       (name, source_type, source_path, enabled, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    ("SSH Journal", "journal", "/var/log/auth.log", 1, "active"),
                )
                conn.commit()
                logger.info("Created SSH log source with ID: %d", cursor.lastrowid)
                if cursor.lastrowid is None:
                    raise RuntimeError("Failed to create SSH log source")
                self._source_id = cursor.lastrowid
            else:
                logger.debug("SSH log source already exists with ID: %d", result[0])
                self._source_id = int(result[0])

        except Exception as e:
            logger.error("Failed to initialize log source: %s", e)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def _get_last_cursor_position(self) -> int:
        """Get the last cursor position from persistent storage.

        Returns:
            Last cursor position, or 0 if not found.
        """
        try:
            if self.cursor_position_file.exists():
                position = int(self.cursor_position_file.read_text().strip())
                logger.debug("Loaded cursor position: %d", position)
                return position
            return 0
        except (OSError, ValueError) as e:
            logger.warning("Failed to read cursor position: %s, starting from beginning", e)
            return 0

    def _save_cursor_position(self, position: int) -> None:
        """Save cursor position to persistent storage.

        Args:
            position: Current cursor position in the log file.
        """
        try:
            self.cursor_position_file.parent.mkdir(parents=True, exist_ok=True)
            self.cursor_position_file.write_text(str(position))
            logger.debug("Saved cursor position: %d", position)
        except OSError as e:
            logger.error("Failed to save cursor position: %s", e)
            raise

    def _generate_event_key(self, entry: AttackEvent) -> str:
        """Generate unique event key for deduplication.

        Args:
            entry: Attack event.

        Returns:
            Unique event key string.
        """
        return (
            f"{entry.detected_at}|{entry.src_ip}|{entry.src_port}|{entry.username or ''}|"
            f"{entry.attack_type}|{entry.source_id or self._source_id}"
        )

    def _get_upsert_events_query(self) -> str:
        """Get SQL query for upserting attack events.

        Returns:
            SQL query string.
        """
        return """INSERT OR IGNORE INTO attack_events
            (event_key, detected_at, sensor_host, source_id, source_type, src_ip,
             src_port, dst_port, protocol, attack_type, severity, signature, username,
             raw_log, created_at)
            VALUES (?, ?, 'localhost', ?, 'file', ?, ?, 22, 'tcp', ?, 3, ?, ?, ?, ?)"""

    def _get_upsert_attacker_query(self) -> str:
        """Get SQL query for upserting attacker information.

        Returns:
            SQL query string.
        """
        return """INSERT INTO attackers
            (src_ip, first_seen, last_seen, total_events, ssh_failures,
             threat_score, highest_severity, last_attack_type, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'observed', CURRENT_TIMESTAMP)
            ON CONFLICT(src_ip) DO UPDATE SET
              last_seen=excluded.last_seen,
              total_events=attackers.total_events+excluded.total_events,
              ssh_failures=attackers.ssh_failures+excluded.ssh_failures,
              highest_severity=MIN(attackers.highest_severity, excluded.highest_severity),
              last_attack_type=excluded.last_attack_type, updated_at=CURRENT_TIMESTAMP"""

    def _parse_log_lines(self, lines: list[str]) -> list[AttackEvent]:
        """Parse multiple log lines into AttackEvent objects.

        Args:
            lines: List of raw log lines.

        Returns:
            List of AttackEvent objects.
        """
        events: list[AttackEvent] = []
        for line in lines:
            if not line.strip():
                continue

            try:
                entry = self.parser.parse_line(line)
            except ValueError as exc:
                logger.warning("Skipping malformed SSH line: %s", exc)
                continue
            if entry:
                events.append(AttackEvent(
                    event_key=entry.event_key, detected_at=entry.timestamp,
                    src_ip=entry.source_ip,
                    src_port=entry.src_port,
                    attack_type=("ssh_invalid_user" if entry.failure_reason == "Invalid user"
                                 else "ssh_failed_password"),
                    signature=entry.failure_reason, username=entry.username,
                    raw_log=line.rstrip("\n"), created_at=datetime.now().isoformat()))

        return events

    def _collect_batch(self, lines: list[str]) -> Batch:
        """Collect and parse a batch of log lines.

        Args:
            lines: List of raw log lines.

        Returns:
            Batch of parsed AttackEvent objects.
        """
        events = self._parse_log_lines(lines)
        return Batch(entries=events)

    def _process_batch(
        self,
        batch: Batch,
    ) -> tuple[int, int]:
        """Process a batch of SSH events and store in database.

        Args:
            batch: Batch of parsed events.

        Returns:
            Tuple of (new_events_count, new_attackers_count).
        """
        if not batch.entries:
            return 0, 0

        new_events = 0
        new_attackers = 0
        now = datetime.now().isoformat()

        try:
            conn = sqlite3.connect(self.database_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")

            cursor = conn.cursor()

            for event in batch.entries:
                inserted = cursor.execute(self._get_upsert_events_query(), (
                    event.event_key, event.detected_at, self._source_id,
                    event.src_ip, event.src_port, event.attack_type,
                    event.signature, event.username, event.raw_log, now,
                )).rowcount
                if inserted == 1:
                    new_events += 1
                    # Check if attacker already exists in DB
                    attacker_exists = cursor.execute(
                        "SELECT 1 FROM attackers WHERE src_ip = ?", (event.src_ip,)
                    ).fetchone()

                    cursor.execute(self._get_upsert_attacker_query(), (
                        event.src_ip, event.detected_at, event.detected_at,
                        1, 1, event.severity, event.severity, event.attack_type,
                    ))
                    if not attacker_exists:
                        new_attackers += 1

            # Update log source stats
            cursor.execute("""
                UPDATE log_sources
                SET events_today = events_today + ?,
                    last_event_at = ?
                WHERE name = ?
            """, (new_events, now, "SSH Journal"))

            conn.commit()

        except sqlite3.Error as e:
            logger.error("Database error while processing batch: %s", e)
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error("Unexpected error while processing batch: %s", e)
            raise
        finally:
            if conn:
                conn.close()

        return new_events, new_attackers

    def collect_from_file(
        self,
        log_file_path: str = "/var/log/auth.log",
        batch_size: int = 100,
        wal_enabled: bool = True,
        busy_timeout: int = 5000,
    ) -> tuple[int, int]:
        """
        Collect SSH events from the journal file.

        Args:
            log_file_path: Path to SSH log file.
            batch_size: Number of lines to read per batch.
            wal_enabled: Whether to enable WAL mode on database.
            busy_timeout: Database busy timeout in milliseconds.

        Returns:
            Tuple of (total_new_events, total_new_attackers).
        """
        log_path = Path(log_file_path)
        if not log_path.exists():
            logger.error("Log file not found: %s", log_file_path)
            raise FileNotFoundError(f"Log file not found: {log_file_path}")

        # Set database busy timeout if WAL enabled
        if wal_enabled:
            try:
                conn = sqlite3.connect(self.database_path)
                conn.execute(f"PRAGMA busy_timeout={busy_timeout}")
                conn.close()
            except sqlite3.Error as e:
                logger.warning("Could not set busy timeout: %s", e)

        total_new_events = 0
        total_new_attackers = 0

        try:
            with open(log_path, encoding='utf-8', errors='replace') as log_file:
                # Get initial cursor position
                initial_position = self._get_last_cursor_position()
                if initial_position > log_path.stat().st_size:
                    logger.warning("Cursor exceeds file size; treating file as truncated/rotated")
                    initial_position = 0
                log_file.seek(initial_position)
                current_position = initial_position

                # Read log in batches
                while True:
                    lines: list[str] = []
                    for _ in range(batch_size):
                        line = log_file.readline()
                        if not line:
                            # End of file reached
                            break
                        lines.append(line)
                        current_position = log_file.tell()

                    if not lines:
                        break

                    # Collect and process batch
                    logger.debug(
                        "Processing batch of %d lines at position %d",
                        len(lines),
                        current_position,
                    )
                    batch = self._collect_batch(lines)
                    new_events, new_attackers = self._process_batch(batch)
                    total_new_events += new_events
                    total_new_attackers += new_attackers

                    # Save cursor position after each batch
                    self._save_cursor_position(current_position)

                    logger.info(
                        "Processed batch: %d new events, %d new attackers",
                        new_events, new_attackers
                    )

                logger.info(
                    "Collection complete. Total: %d new events, %d new attackers",
                    total_new_events, total_new_attackers
                )

        except OSError as e:
            logger.error("Error reading log file: %s", e)
            raise
        except sqlite3.Error as e:
            logger.error("Database error during collection: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error during collection: %s", e)
            raise

        return total_new_events, total_new_attackers

    def collect_all(self, batch_size: int = 100) -> tuple[int, int]:
        """
        Collect all available SSH events from journal.

        Args:
            batch_size: Number of lines to read per batch.

        Returns:
            Tuple of (total_new_events, total_new_attackers).
        """
        logger.info("Starting SSH journal collection")
        return self.collect_from_file(batch_size=batch_size)

    def reset_cursor(self) -> None:
        """Reset cursor position to start from beginning of log file."""
        self.cursor_position_file.unlink(missing_ok=True)
        logger.info("Cursor position reset to beginning")

    def test_connection(self) -> bool:
        """Test SSH collector connection to log file and database.

        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            # Test log file readability
            log_path = Path("/var/log/auth.log")
            if not log_path.exists():
                logger.error("Log file does not exist: %s", log_path)
                return False

            with open(log_path, encoding='utf-8', errors='replace') as f:
                # Read and parse first line to test parsing
                first_line = f.readline()
                entry = self.parser.parse_line(first_line)
                if entry:
                    logger.info("Test line parsed successfully: %s - %s",
                              entry.timestamp, entry.source_ip)
                else:
                    logger.info("Log file exists but no SSH events found in first line")

            # Test database connection
            conn = sqlite3.connect(self.database_path)
            conn.execute("SELECT 1")
            conn.close()
            logger.info("Database connection successful")

            return True

        except Exception as e:
            logger.error("Connection test failed: %s", e)
            return False
