# P1 SQLite SSH Detector Implementation Design

**Date:** 2026-07-10
**Phase:** P1 — SSH Detection Collector
**Status:** Design

## Overview

Implement a SSH journal-based intrusion detection system with:
- SQLite database with attack_events, attackers, log_sources tables
- SSH Journal Collector with cursor persistence
- SSH log parser for Failed/Invalid user events
- Event deduplication using event_key
- Attackers UPSERT logic
- CLI report for last 24h attack IPs

## Table Schemas

### log_sources (New)

```sql
CREATE TABLE log_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    source_path TEXT,
    config_json TEXT,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'unknown' CHECK (status IN ('unknown', 'healthy', 'warning', 'error', 'disabled')),
    last_event_at TEXT,
    last_error TEXT,
    events_today INTEGER NOT NULL DEFAULT 0,
    parse_errors_today INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Primary key, auto-increment
- `name`: Unique source name (e.g., 'ssh-journal')
- `source_type`: 'journal', 'file', 'socket', etc.
- `source_path`: Path to log source (journal unit, file path, etc.)
- `config_json`: JSON config (polling interval, filters, etc.)
- `enabled`: 1=enabled, 0=disabled
- `status`: unknown, healthy, warning, error, disabled
- `last_event_at`: ISO 8601 timestamp of last successful event
- `last_error`: Last error message (if any)
- `events_today`: Total events parsed today
- `parse_errors_today`: Parse errors today
- `created_at`, `updated_at`: Timestamps

**Indexes:**
- UNIQUE(name)
- INDEX(status, enabled)
- INDEX(last_event_at)

### attack_events (Existing)

```sql
CREATE TABLE attack_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_key TEXT NOT NULL UNIQUE,
    detected_at TEXT NOT NULL,
    sensor_host TEXT NOT NULL,
    source_id INTEGER REFERENCES log_sources(id) ON DELETE SET NULL,
    source_type TEXT NOT NULL,
    src_ip TEXT NOT NULL,
    src_port INTEGER CHECK (src_port IS NULL OR src_port BETWEEN 0 AND 65535),
    dst_ip TEXT,
    dst_port INTEGER CHECK (dst_port IS NULL OR dst_port BETWEEN 0 AND 65535),
    protocol TEXT,
    attack_type TEXT NOT NULL,
    severity INTEGER NOT NULL DEFAULT 3 CHECK (severity BETWEEN 1 AND 5),
    signature TEXT,
    http_method TEXT,
    request_path TEXT,
    username TEXT,
    blocked INTEGER NOT NULL DEFAULT 0 CHECK (blocked IN (0, 1)),
    raw_log TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `event_key`: UNIQUE identifier (e.g., "20260710-123456-ssh-failed-password-192.0.2.1-22-admin")
- `detected_at`: ISO 8601 timestamp when detected
- `sensor_host`: Hostname/IP of sensor collecting event
- `source_id`: FK to log_sources (NULL if no source)
- `source_type`: 'journal', 'file', 'socket'
- `src_ip`: Source IP (IPv4 or IPv6)
- `src_port`: Source port (NULL if unknown)
- `dst_ip`: Destination IP (NULL for SSH)
- `dst_port`: Destination port
- `protocol`: 'tcp', 'udp', etc.
- `attack_type`: 'ssh_failed_password', 'ssh_invalid_user', etc.
- `severity`: 1-5 (5=highest)
- `signature`: Detection signature
- `http_method`, `request_path`: HTTP-specific fields
- `username`: Login username
- `blocked`: 0=unblocked, 1=blocked
- `raw_log`: Original log entry (truncated)
- `metadata_json`: Additional structured data
- `created_at`: Record creation timestamp

**Indexes:**
- UNIQUE(event_key)
- INDEX(detected_at)
- INDEX(src_ip)
- INDEX(attack_type)
- INDEX(source_id, detected_at)
- INDEX(severity, detected_at)

### attackers (Existing)

```sql
CREATE TABLE attackers (
    src_ip TEXT PRIMARY KEY,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    total_events INTEGER NOT NULL DEFAULT 0,
    threat_score INTEGER NOT NULL DEFAULT 0,
    highest_severity INTEGER NOT NULL DEFAULT 1 CHECK (highest_severity BETWEEN 1 AND 5),
    last_attack_type TEXT,
    status TEXT NOT NULL DEFAULT 'observed' CHECK (status IN ('observed', 'high_risk', 'blocked', 'allowlisted')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `src_ip`: PRIMARY KEY (IPv4 or IPv6)
- `first_seen`: ISO 8601 first event timestamp
- `last_seen`: ISO 8601 last event timestamp
- `total_events`: Cumulative event count
- `threat_score`: 0-100 (aggregated from events)
- `highest_severity`: Maximum severity (1-5)
- `last_attack_type`: Most recent attack type
- `status`: observed, high_risk, blocked, allowlisted
- `updated_at`: Last update timestamp

**Indexes:**
- PRIMARY KEY(src_ip)
- INDEX(status, threat_score DESC)

## SSH Journal Collector

### Architecture

```
┌─────────────────┐
│   systemd-journ  │
│   (journalctl)   │
└────────┬────────┘
         │ journalctl --lines 0 --no-pager --quiet
         │ (or --follow + cursor tracking)
         ▼
┌─────────────────────────────────┐
│   SSH Journal Collector         │
│   ┌─────────────────────────┐  │
│   │  Cursor Persistence      │  │
│   │  - Save: cursor path     │  │
│   │  - Load: cursor path     │  │
│   │  - Auto-save on SIGTERM │  │
│   └─────────────────────────┘  │
│   ┌─────────────────────────┐  │
│   │  Event Batch Processing │  │
│   │  - Read batch            │  │
│   │  - Parse events          │  │
│   │  - Deduplicate          │  │
│   │  - UPSERT attackers      │  │
│   │  - INSERT events         │  │
│   └─────────────────────────┘  │
│   ┌─────────────────────────┐  │
│   │  Source Monitoring       │  │
│   │  - Update log_sources    │  │
│   │  - Count events/errors   │  │
│   └─────────────────────────┘  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│    SQLite Database              │
│  (WAL mode, foreign keys ON)    │
└─────────────────────────────────┘
```

### Cursor Persistence Strategy

**Cursor File Location:**
```
/var/secmon/cursors/ssh_journal_cursor.txt
```

**Cursor Format (JSON):**
```json
{
  "cursor": "9619d62770020f4d819687fb5f5946760000000000000004",
  "timestamp": "2026-07-10T14:23:45Z",
  "source_id": 1
}
```

**Implementation:**

```python
class SSHJournalCursor:
    def __init__(self, cursor_path: Path):
        self.cursor_path = cursor_path
        self.cursor_data = self._load()

    def _load(self) -> dict:
        if self.cursor_path.exists():
            with open(self.cursor_path) as f:
                return json.load(f)
        return {"cursor": "", "timestamp": "", "source_id": None}

    def save(self) -> None:
        self.cursor_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cursor_path, "w") as f:
            json.dump(self.cursor_data, f)

    def update(self, cursor: str, timestamp: str, source_id: int) -> None:
        self.cursor_data = {
            "cursor": cursor,
            "timestamp": timestamp,
            "source_id": source_id
        }
        self.save()

    def reset(self) -> None:
        self.cursor_data = {"cursor": "", "timestamp": "", "source_id": None}
        self.save()
```

**Cursor Tracking in Collector:**

```python
class SSHJournalCollector:
    def __init__(
        self,
        database: Path,
        cursor_path: Path,
        journal_unit: str = "sshd",
        lines_per_batch: int = 1000,
        cursor_expires_hours: int = 24
    ):
        self.database = database
        self.cursor = SSHJournalCursor(cursor_path)
        self.journal_unit = journal_unit
        self.lines_per_batch = lines_per_batch
        self.cursor_expires_hours = cursor_expires_hours

    def collect(self) -> None:
        """Main collection loop."""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")

        try:
            # Reset if cursor expired
            if self.cursor.cursor_data["cursor"] and self._is_cursor_expired():
                logger.warning("Cursor expired, resetting")
                self.cursor.reset()

            # Get existing source_id
            source_id = self._get_or_create_source()

            # Read journal
            journal_output = self._read_journal()

            if not journal_output:
                return

            # Parse events
            events = self._parse_events(journal_output)

            if not events:
                return

            # Deduplicate and store
            conn.execute("BEGIN TRANSACTION")
            self._store_events(conn, events, source_id)
            conn.commit()

            # Update cursor
            latest_event = max(events, key=lambda e: e["detected_at"])
            self.cursor.update(
                cursor=latest_event["cursor"],
                timestamp=latest_event["detected_at"],
                source_id=source_id
            )

            logger.info(f"Processed {len(events)} SSH events")

        except Exception as e:
            conn.rollback()
            logger.error(f"Collection failed: {e}")
            raise
        finally:
            conn.close()

    def _is_cursor_expired(self) -> bool:
        """Check if cursor is older than cursor_expires_hours."""
        if not self.cursor.cursor_data["timestamp"]:
            return False

        cursor_time = datetime.fromisoformat(
            self.cursor.cursor_data["timestamp"].replace("Z", "+00:00")
        )
        age = datetime.now(cursor_time.tzinfo) - cursor_time
        return age.total_seconds() > (self.cursor_expires_hours * 3600)
```

### Database Transaction Management

**Strategy:**
1. Start transaction with `BEGIN TRANSACTION`
2. Process batch of events
3. UPSERT attackers (PRIMARY KEY handling)
4. INSERT events (UNIQUE event_key constraint)
5. Update log_sources stats
6. If all successful: `COMMIT`
7. If any error: `ROLLBACK`

**Implementation:**

```python
def _store_events(self, conn, events: List[dict], source_id: int) -> None:
    """Store events and update attackers in single transaction."""
    for event in events:
        # UPSERT attacker
        attacker_sql = """
            INSERT INTO attackers (src_ip, first_seen, last_seen, total_events,
                                   threat_score, highest_severity, last_attack_type,
                                   status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'observed', CURRENT_TIMESTAMP)
            ON CONFLICT(src_ip) DO UPDATE SET
                last_seen = CURRENT_TIMESTAMP,
                total_events = total_events + 1,
                highest_severity = MAX(highest_severity, ?),
                threat_score = threat_score + ?,
                last_attack_type = ?,
                status = CASE
                    WHEN threat_score >= 80 THEN 'high_risk'
                    WHEN threat_score >= 50 THEN 'observed'
                    ELSE 'observed'
                END,
                updated_at = CURRENT_TIMESTAMP
        """
        conn.execute(
            attacker_sql,
            (
                event["src_ip"],
                event["detected_at"],
                event["detected_at"],
                1,
                event["severity"],
                event["severity"],
                event["attack_type"],
            )
        )

        # INSERT event (event_key is UNIQUE)
        event_sql = """
            INSERT INTO attack_events (
                event_key, detected_at, sensor_host, source_id, source_type,
                src_ip, src_port, dst_port, protocol, attack_type, severity,
                username, blocked, raw_log, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(
            event_sql,
            (
                event["event_key"],
                event["detected_at"],
                event["sensor_host"],
                source_id,
                "journal",
                event["src_ip"],
                event["src_port"],
                None,  # SSH dst_port
                "tcp",
                event["attack_type"],
                event["severity"],
                event.get("username"),
                0,  # Not blocked initially
                event["raw_log"],
                None,  # metadata_json
            )
        )

    # Update log_sources stats
    conn.execute(
        """
        UPDATE log_sources
        SET events_today = events_today + ?,
            last_event_at = CURRENT_TIMESTAMP,
            status = 'healthy'
        WHERE id = ?
        """,
        (len(events), source_id)
    )
```

## SSH Log Parser

### Supported Log Patterns

#### Pattern 1: Failed Password

```
Jul 10 14:23:45 sensor sshd[1234]: Failed password for invalid user admin from 192.0.2.100 port 45678 ssh2
Jul 10 14:23:46 sensor sshd[1234]: Failed password for root from 198.51.100.50 port 54321 ssh2
```

#### Pattern 2: Invalid User

```
Jul 10 14:23:45 sensor sshd[1234]: Invalid user testuser from 203.0.113.75 port 67890 ssh2
```

### Parser Logic

```python
import re
from datetime import datetime
from typing import Optional, Dict, Any

class SSHLogParser:
    """Parse SSH journal logs for intrusion detection."""

    # Pattern: Failed password for [username] from [IP] port [PORT]
    FAILED_PASSWORD_PATTERN = re.compile(
        r'^Failed password for (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) '
        r'port (\d+) ssh2$'
    )

    # Pattern: Invalid user [username] from [IP] port [PORT]
    INVALID_USER_PATTERN = re.compile(
        r'^Invalid user (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) '
        r'port (\d+) ssh2$'
    )

    # Pattern: Port [PORT] attempted [username]
    # Sometimes appears in older SSH logs
    ATTEMPTED_LOGIN_PATTERN = re.compile(
        r'^Port (\d+) attempted (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$'
    )

    def parse(self, journal_output: str, sensor_host: str) -> List[dict]:
        """Parse journalctl output and extract SSH events.

        Args:
            journal_output: Raw journalctl output (multiple lines)
            sensor_host: Hostname/IP of sensor

        Returns:
            List of parsed event dictionaries
        """
        events = []
        lines = journal_output.strip().split('\n')

        for line in lines:
            if not line.strip():
                continue

            # Extract timestamp and message
            timestamp, message = self._parse_line(line)
            if not timestamp or not message:
                continue

            # Try to match patterns
            event = self._match_patterns(timestamp, message, sensor_host)
            if event:
                events.append(event)

        return events

    def _parse_line(self, line: str) -> tuple[Optional[str], Optional[str]]:
        """Parse journal line into timestamp and message.

        Journal format:
        Jul 10 14:23:45 hostname sshd[1234]: message...

        Returns:
            (timestamp, message) or (None, None) if invalid
        """
        # Format: "Jul 10 14:23:45 hostname sshd[1234]: ..."
        parts = line.split(':', 4)
        if len(parts) < 3:
            return None, None

        # Extract timestamp (first field before first :)
        time_part = parts[0].strip()
        try:
            # Parse: "Jul 10 14:23:45"
            dt = datetime.strptime(time_part, "%b %d %H:%M:%S")
            # Add current year
            timestamp = dt.replace(year=datetime.now().year).isoformat() + "Z"
        except ValueError:
            return None, None

        # Extract message (everything after the first :)
        message = ':'.join(parts[1:]).strip()

        return timestamp, message

    def _match_patterns(
        self,
        timestamp: str,
        message: str,
        sensor_host: str
    ) -> Optional[dict]:
        """Try to match SSH log patterns and create event dict."""
        # Try Failed password pattern
        match = self.FAILED_PASSWORD_PATTERN.match(message)
        if match:
            username, ip, port = match.groups()
            return self._create_event(
                timestamp=timestamp,
                message=message,
                sensor_host=sensor_host,
                src_ip=ip,
                src_port=int(port),
                username=username,
                attack_type='ssh_failed_password',
                severity=4  # High severity
            )

        # Try Invalid user pattern
        match = self.INVALID_USER_PATTERN.match(message)
        if match:
            username, ip, port = match.groups()
            return self._create_event(
                timestamp=timestamp,
                message=message,
                sensor_host=sensor_host,
                src_ip=ip,
                src_port=int(port),
                username=username,
                attack_type='ssh_invalid_user',
                severity=3  # Medium severity
            )

        # Try attempted login pattern
        match = self.ATTEMPTED_LOGIN_PATTERN.match(message)
        if match:
            port, username, ip = match.groups()
            return self._create_event(
                timestamp=timestamp,
                message=message,
                sensor_host=sensor_host,
                src_ip=ip,
                src_port=int(port),
                username=username,
                attack_type='ssh_attempted_login',
                severity=3  # Medium severity
            )

        return None

    def _create_event(
        self,
        timestamp: str,
        message: str,
        sensor_host: str,
        src_ip: str,
        src_port: int,
        username: Optional[str],
        attack_type: str,
        severity: int
    ) -> dict:
        """Create normalized event dictionary.

        Args:
            timestamp: ISO 8601 timestamp
            message: Raw log message
            sensor_host: Sensor hostname/IP
            src_ip: Source IP address
            src_port: Source port
            username: Username from login attempt
            attack_type: Attack type classification
            severity: Severity level (1-5)

        Returns:
            Normalized event dict for database storage
        """
        # Generate event_key: YYYYMMDD-HHMMSS-type-ip-port-username
        # Truncate raw_log to max 1000 chars
        event_key = (
            f"{timestamp[:19].replace('-', '').replace(':', '')}-{attack_type}-"
            f"{src_ip}-{src_port}-{username or 'unknown'}"
        )[:200]  # Max length constraint

        # Determine protocol
        protocol = 'tcp'

        # Destination (SSH defaults to port 22)
        dst_port = 22
        dst_ip = None

        return {
            "event_key": event_key,
            "detected_at": timestamp,
            "sensor_host": sensor_host,
            "source_type": "journal",
            "src_ip": src_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": protocol,
            "attack_type": attack_type,
            "severity": severity,
            "username": username,
            "raw_log": message[:1000],  # Truncate
            "cursor": f"{timestamp[:19].replace(':', '')}-{src_ip}",  # Cursor marker
        }
```

### Input Validation

```python
def _validate_ip(self, ip: str) -> bool:
    """Validate IPv4 or IPv6 address."""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def _validate_port(self, port: Optional[int]) -> bool:
    """Validate port number (0-65535) or None."""
    if port is None:
        return True
    return 0 <= port <= 65535

def _validate_severity(self, severity: int) -> bool:
    """Validate severity level (1-5)."""
    return 1 <= severity <= 5
```

## CLI Report Tool

```python
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import json
from typing import List, Dict, Any

def report_last_24h(
    database: Path,
    hours: int = 24,
    min_severity: int = 1,
    status_filter: Optional[str] = None
) -> None:
    """Generate CLI report of attack IPs in last N hours.

    Args:
        database: Path to SQLite database
        hours: Number of hours to look back (default: 24)
        min_severity: Minimum severity level to include (default: 1)
        status_filter: Filter by attacker status ('observed', 'high_risk', etc.)
    """
    # Calculate time range
    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Connect to database
    conn = sqlite3.connect(database)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Build query
    query = """
        SELECT
            src_ip,
            first_seen,
            last_seen,
            total_events,
            threat_score,
            highest_severity,
            last_attack_type,
            status,
            json_group_array(
                json_object(
                    'timestamp', detected_at,
                    'attack_type', attack_type,
                    'severity', severity
                )
            ) as recent_events
        FROM attack_events
        WHERE detected_at >= ?
          AND severity >= ?
          AND source_type = 'journal'
          AND NOT blocked = 1
    """

    if status_filter:
        query += f" AND status = ?"

    query += """
        GROUP BY src_ip
        ORDER BY threat_score DESC, total_events DESC
        LIMIT 100
    """

    # Execute query
    cursor.execute(
        query,
        (cutoff_time.isoformat() + "Z", min_severity) +
        ([status_filter] if status_filter else [])
    )

    rows = cursor.fetchall()

    # Print report header
    print(f"\n{'='*80}")
    print(f"SecMon SSH Detector Report - Last {hours} Hours")
    print(f"{'='*80}")
    print(f"Generated: {datetime.now().isoformat()}Z")
    print(f"Time Range: {cutoff_time.isoformat()}Z - now")
    print(f"Minimum Severity: {min_severity}")
    if status_filter:
        print(f"Status Filter: {status_filter}")
    print(f"{'='*80}\n")

    if not rows:
        print("No attack events found in the specified time range.")
        conn.close()
        return

    # Print summary
    total_attacks = sum(row[3] for row in rows)
    total_high_risk = sum(1 for row in rows if row[7] == 'high_risk')
    avg_threat_score = sum(row[4] for row in rows) / len(rows)

    print(f"Summary:")
    print(f"  Total Attackers: {len(rows)}")
    print(f"  Total Attack Events: {total_attacks}")
    print(f"  High-Risk Attackers: {total_high_risk}")
    print(f"  Average Threat Score: {avg_threat_score:.1f}")
    print(f"\n")

    # Print attackers table
    print(f"{'IP Address':<20} {'Events':>6} {'Score':>5} {'Severity':>8} "
          f"{'Last Seen':>20} {'Type':<30} {'Status'}")
    print(f"{'-'*20} {'-'*6} {'-'*5} {'-'*8} {'-'*20} {'-'*30} {'-'*8}")

    for row in rows:
        ip, first_seen, last_seen, total_events, threat_score, severity, \
            last_attack_type, status, _ = row

        # Format severity badge
        severity_badge = self._severity_badge(severity)

        print(
            f"{ip:<20} {total_events:>6} {threat_score:>5} "
            f"{severity_badge:>8} {last_seen:>20} {last_attack_type:<30} {status}"
        )

    # Print detailed events for top 5 attackers
    print(f"\n{'='*80}")
    print("Top 5 Attackers - Detailed Events:")
    print(f"{'='*80}\n")

    for i, row in enumerate(rows[:5], 1):
        ip, first_seen, last_seen, total_events, threat_score, severity, \
            last_attack_type, status, recent_events_json = row

        recent_events = json.loads(recent_events_json) if recent_events_json else []

        print(f"{i}. {ip} (Total Events: {total_events}, Threat Score: {threat_score})")
        print(f"   Status: {status} | Severity: {severity}")
        print(f"   First Seen: {first_seen} | Last Seen: {last_seen}")
        print(f"   Attack Type: {last_attack_type}")
        print(f"   Recent Events:")
        for event in recent_events[:5]:  # Show max 5 recent events
            print(
                f"     - {event['timestamp']} [{event['attack_type']}] "
                f"Severity: {event['severity']}"
            )
        if len(recent_events) > 5:
            print(f"     ... and {len(recent_events) - 5} more events")
        print()

    conn.close()

def _severity_badge(self, severity: int) -> str:
    """Return severity level badge."""
    colors = {
        1: "\033[32m",  # Green
        2: "\033[32m",  # Green
        3: "\033[33m",  # Yellow
        4: "\033[91m",  # Red
        5: "\033[91m",  # Red
    }
    reset = "\033[0m"

    if severity <= 2:
        return f"{colors[severity]}L{severity}{reset}"
    elif severity <= 3:
        return f"{colors[severity]}M{severity}{reset}"
    else:
        return f"{colors[severity]}H{severity}{reset}"

def main() -> None:
    parser = argparse.ArgumentParser(
        description="SecMon SSH Detector Report Tool"
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("./var/secmon.db"),
        help="Path to SQLite database (default: ./var/secmon.db)"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)"
    )
    parser.add_argument(
        "--min-severity",
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help="Minimum severity level to include (default: 1)"
    )
    parser.add_argument(
        "--status",
        choices=['observed', 'high_risk', 'blocked', 'allowlisted'],
        help="Filter by attacker status"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.hours < 1 or args.hours > 168:
        parser.error("hours must be between 1 and 168 (7 days)")

    report_last_24h(
        database=args.database,
        hours=args.hours,
        min_severity=args.min_severity,
        status_filter=args.status
    )
```

## Unit Test Fixtures

### Fixtures File: `tests/fixtures/ssh_parser.py`

```python
from typing import Dict, Any

SSH_LOG_LINES = [
    "Jul 10 14:23:45 sensor sshd[1234]: Failed password for invalid user admin from 192.0.2.100 port 45678 ssh2",
    "Jul 10 14:23:46 sensor sshd[1234]: Failed password for root from 198.51.100.50 port 54321 ssh2",
    "Jul 10 14:23:47 sensor sshd[1234]: Invalid user testuser from 203.0.113.75 port 67890 ssh2",
    "Jul 10 14:23:48 sensor sshd[1234]: Port 54321 attempted root from 198.51.100.50",
]

SSH_LOG_OUTPUT = "\n".join(SSH_LOG_LINES)

PARSED_EVENTS = [
    {
        "event_key": "20260710-142345-ssh_failed_password-192.0.2.100-45678-admin",
        "detected_at": "2026-07-10T14:23:45Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "192.0.2.100",
        "src_port": 45678,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_failed_password",
        "severity": 4,
        "username": "admin",
        "raw_log": "Failed password for invalid user admin from 192.0.2.100 port 45678 ssh2",
        "cursor": "20260710-142345-192.0.2.100"
    },
    {
        "event_key": "20260710-142346-ssh_failed_password-198.51.100.50-54321-root",
        "detected_at": "2026-07-10T14:23:46Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "198.51.100.50",
        "src_port": 54321,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_failed_password",
        "severity": 4,
        "username": "root",
        "raw_log": "Failed password for root from 198.51.100.50 port 54321 ssh2",
        "cursor": "20260710-142346-198.51.100.50"
    },
    {
        "event_key": "20260710-142347-ssh_invalid_user-203.0.113.75-67890-testuser",
        "detected_at": "2026-07-10T14:23:47Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "203.0.113.75",
        "src_port": 67890,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_invalid_user",
        "severity": 3,
        "username": "testuser",
        "raw_log": "Invalid user testuser from 203.0.113.75 port 67890 ssh2",
        "cursor": "20260710-142347-203.0.113.75"
    },
    {
        "event_key": "20260710-142348-ssh_attempted_login-198.51.100.50-54321-root",
        "detected_at": "2026-07-10T14:23:48Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "198.51.100.50",
        "src_port": 54321,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_attempted_login",
        "severity": 3,
        "username": "root",
        "raw_log": "Port 54321 attempted root from 198.51.100.50",
        "cursor": "20260710-142348-198.51.100.50"
    },
]

INVALID_LOG_LINES = [
    "2026-07-10 14:23:45 invalid format",
    "Jul 10 14:23:45 hostname sshd[1234]:",
    "Jul 10 14:23:45 hostname sshd[1234]: message without port",
    "Jul 10 14:23:45 hostname sshd[1234]: Failed password from 192.0.2.100 ssh2",
]

NON_SSH_LINES = [
    "Jul 10 14:23:45 hostname sshd[1234]: Connection closed by authenticating user",
    "Jul 10 14:23:45 hostname sshd[1234]: Accepted password for user from 192.0.2.100",
]
```

### Unit Tests: `tests/test_ssh_detector.py`

```python
import pytest
from pathlib import Path
import tempfile
import sqlite3
from backend.parsers.ssh_parser import SSHLogParser
from backend.collectors.ssh_journal_collector import SSHJournalCollector
from database.migrate import migrate
from tests.fixtures.ssh_parser import (
    SSH_LOG_OUTPUT,
    PARSED_EVENTS,
    INVALID_LOG_LINES,
    NON_SSH_LINES,
)


class TestSSHLogParser:
    """Test SSH log parser."""

    def test_parse_valid_logs(self):
        """Test parsing of valid SSH journal logs."""
        parser = SSHLogParser()
        events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")

        assert len(events) == len(PARSED_EVENTS)

        # Verify first event
        expected = PARSED_EVENTS[0]
        actual = events[0]

        for key in ["event_key", "detected_at", "src_ip", "src_port",
                    "attack_type", "severity", "username"]:
            assert actual[key] == expected[key], f"Mismatch in {key}"

        assert actual["dst_port"] == 22
        assert actual["protocol"] == "tcp"

    def test_parse_invalid_logs(self):
        """Test handling of invalid log lines."""
        parser = SSHLogParser()
        output = "\n".join(INVALID_LOG_LINES)

        events = parser.parse(output, sensor_host="sensor")

        # Invalid lines should be ignored
        assert len(events) == 0

    def test_parse_non_ssh_lines(self):
        """Test filtering of non-SSH log lines."""
        parser = SSHLogParser()
        output = "\n".join(NON_SSH_LINES)

        events = parser.parse(output, sensor_host="sensor")

        # SSH-specific patterns should be filtered out
        assert len(events) == 0

    def test_create_event_key(self):
        """Test event key generation."""
        parser = SSHLogParser()

        event = parser._create_event(
            timestamp="2026-07-10T14:23:45Z",
            message="Test message",
            sensor_host="sensor",
            src_ip="192.0.2.100",
            src_port=45678,
            username="admin",
            attack_type="ssh_test",
            severity=4
        )

        # Event key should follow format: YYYYMMDD-HHMMSS-type-ip-port-username
        assert "20260710-142345-ssh_test-192.0.2.100-45678-admin" in event["event_key"]

    def test_event_key_truncation(self):
        """Test event key truncation to max 200 chars."""
        parser = SSHLogParser()

        # Create a very long event key
        long_key = "A" * 300 + "-test-ip-1-22-user"
        event = parser._create_event(
            timestamp="2026-07-10T14:23:45Z",
            message="Test message",
            sensor_host="sensor",
            src_ip="192.0.2.100",
            src_port=45678,
            username="user",
            attack_type="A" * 200,
            severity=4
        )

        assert len(event["event_key"]) <= 200

    def test_raw_log_truncation(self):
        """Test raw log truncation to max 1000 chars."""
        parser = SSHLogParser()

        long_message = "A" * 2000 + " test"
        event = parser._create_event(
            timestamp="2026-07-10T14:23:45Z",
            message=long_message,
            sensor_host="sensor",
            src_ip="192.0.2.100",
            src_port=45678,
            username="user",
            attack_type="ssh_test",
            severity=4
        )

        assert len(event["raw_log"]) <= 1000


class TestSSHJournalCursor:
    """Test SSH journal cursor persistence."""

    def test_cursor_load_save(self):
        """Test loading and saving cursor data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "cursor.txt"

            cursor = SSHJournalCursor(cursor_path)
            assert cursor.cursor_data == {"cursor": "", "timestamp": "", "source_id": None}

            # Update cursor
            cursor.update("test-cursor", "2026-07-10T14:23:45Z", 1)

            # Reload
            cursor2 = SSHJournalCursor(cursor_path)
            assert cursor2.cursor_data["cursor"] == "test-cursor"
            assert cursor2.cursor_data["timestamp"] == "2026-07-10T14:23:45Z"
            assert cursor2.cursor_data["source_id"] == 1

    def test_cursor_reset(self):
        """Test cursor reset functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "cursor.txt"

            cursor = SSHJournalCursor(cursor_path)
            cursor.update("test-cursor", "2026-07-10T14:23:45Z", 1)

            cursor.reset()
            assert cursor.cursor_data == {"cursor": "", "timestamp": "", "source_id": None}

    def test_cursor_file_persistence(self):
        """Test cursor is persisted to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "cursor.txt"

            # Create cursor, update, and close
            cursor = SSHJournalCursor(cursor_path)
            cursor.update("test-cursor", "2026-07-10T14:23:45Z", 1)

            # Recreate cursor from file
            cursor2 = SSHJournalCursor(cursor_path)
            assert cursor2.cursor_data["cursor"] == "test-cursor"
            assert cursor2.cursor_data["timestamp"] == "2026-07-10T14:23:45Z"
            assert cursor2.cursor_data["source_id"] == 1


class TestSSHJournalCollector:
    """Test SSH journal collector."""

    def test_collection_pipeline(self):
        """Test complete collection pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            cursor_path = Path(tmpdir) / "cursors" / "ssh_journal_cursor.txt"

            # Run initial migration
            migrate(db_path, Path("database/migrations"))

            # Create parser and collector
            parser = SSHLogParser()
            collector = SSHJournalCollector(
                database=db_path,
                cursor_path=cursor_path,
                journal_unit="sshd"
            )

            # Collect events
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("BEGIN TRANSACTION")

            # Mock journalctl output
            import subprocess
            import io

            # Mock subprocess.run to return test SSH logs
            original_run = subprocess.run

            def mock_run(*args, **kwargs):
                if "journalctl" in args[0]:
                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=0,
                        stdout=SSH_LOG_OUTPUT,
                        stderr=""
                    )
                return original_run(*args, **kwargs)

            subprocess.run = mock_run

            try:
                # Parse and store events
                events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                collector._store_events(conn, events, source_id=1)

                # Commit and verify
                conn.commit()

                # Check attackers table
                attacker_rows = conn.execute(
                    "SELECT src_ip, total_events, threat_score FROM attackers"
                ).fetchall()

                assert len(attacker_rows) == 3
                assert attacker_rows[0][1] == 2  # 198.51.100.50 has 2 events
                assert attacker_rows[1][2] == 4  # 192.0.2.100 has threat score 4

                # Check attack_events table
                event_rows = conn.execute(
                    "SELECT COUNT(*), SUM(severity) FROM attack_events"
                ).fetchall()

                assert event_rows[0][0] == 4
                assert event_rows[0][1] == 14  # 4 + 4 + 3 + 3

            finally:
                subprocess.run = original_run
                conn.close()

    def test_deduplication(self):
        """Test event deduplication using event_key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            migrate(db_path, Path("database/migrations"))

            parser = SSHLogParser()
            collector = SSHJournalCollector(
                database=db_path,
                cursor_path=Path(tmpdir) / "cursor.txt"
            )

            # Mock subprocess to return same events multiple times
            import subprocess

            def mock_run(*args, **kwargs):
                if "journalctl" in args[0]:
                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=0,
                        stdout=SSH_LOG_OUTPUT,
                        stderr=""
                    )
                return subprocess.run(*args, **kwargs)

            subprocess.run = mock_run

            try:
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA foreign_keys = ON")

                # First collection
                events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                collector._store_events(conn, events, source_id=1)

                # Second collection (same logs, should be deduplicated)
                events2 = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                collector._store_events(conn, events2, source_id=1)

                # Count unique events
                unique_count = conn.execute(
                    "SELECT COUNT(*) FROM attack_events"
                ).fetchone()[0]

                assert unique_count == 4  # Should be 4 unique events

                # Total attackers should be 3 (not 6)
                attacker_count = conn.execute(
                    "SELECT COUNT(*) FROM attackers"
                ).fetchone()[0]

                assert attacker_count == 3

            finally:
                subprocess.run = subprocess.run
                conn.close()

    def test_cursor_expiration(self):
        """Test cursor expiration detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            cursor_path = Path(tmpdir) / "cursors" / "ssh_journal_cursor.txt"

            migrate(db_path, Path("database/migrations"))

            parser = SSHLogParser()
            collector = SSHJournalCollector(
                database=db_path,
                cursor_path=cursor_path,
                cursor_expires_hours=24
            )

            # Mock journalctl with recent output
            import subprocess

            def mock_run(*args, **kwargs):
                if "journalctl" in args[0]:
                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=0,
                        stdout=SSH_LOG_OUTPUT,
                        stderr=""
                    )
                return subprocess.run(*args, **kwargs)

            subprocess.run = mock_run

            try:
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA foreign_keys = ON")

                # Create cursor that is NOT expired (same time)
                collector.cursor.update(
                    "test-cursor",
                    "2026-07-10T14:23:45Z",
                    1
                )

                # Mock very old time (before cutoff)
                def mock_run_old(*args, **kwargs):
                    if "journalctl" in args[0]:
                        # Force parse to fail or return empty
                        return subprocess.CompletedProcess(
                            args=args[0],
                            returncode=0,
                            stdout="",
                            stderr=""
                        )
                    return subprocess.run(*args, **kwargs)

                subprocess.run = mock_run_old

                # Try to collect - cursor should be reset
                events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                assert len(events) == 0  # Should return empty because cursor expired

                # Cursor should be reset
                assert collector.cursor.cursor_data["cursor"] == ""

            finally:
                subprocess.run = subprocess.run
                conn.close()


class TestCLIReport:
    """Test CLI report generation."""

    def test_report_generation(self):
        """Test generating attack IP report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            migrate(db_path, Path("database/migrations"))

            # Populate test data
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")

            # Insert test attackers and events
            now = datetime.now()

            # Insert attackers
            conn.execute("""
                INSERT INTO attackers (src_ip, first_seen, last_seen, total_events,
                                       threat_score, highest_severity, last_attack_type,
                                       status)
                VALUES
                    ('192.0.2.1', '2026-07-10T10:00:00Z', '2026-07-10T14:00:00Z',
                     10, 85, 5, 'ssh_failed_password', 'high_risk'),
                    ('192.0.2.2', '2026-07-10T11:00:00Z', '2026-07-10T14:00:00Z',
                     5, 45, 4, 'ssh_invalid_user', 'observed'),
                    ('198.51.100.1', '2026-07-10T12:00:00Z', '2026-07-10T14:00:00Z',
                     2, 10, 3, 'ssh_attempted_login', 'observed')
            """)

            # Insert events
            conn.execute("""
                INSERT INTO attack_events (event_key, detected_at, sensor_host,
                                           source_type, src_ip, attack_type,
                                           severity)
                VALUES
                    ('20260710-100000-ssh_failed_password-192.0.2.1-22-admin', '2026-07-10T10:00:00Z',
                     'sensor', 'journal', '192.0.2.1', 'ssh_failed_password', 5),
                    ('20260710-140000-ssh_invalid_user-192.0.2.1-22-test', '2026-07-10T14:00:00Z',
                     'sensor', 'journal', '192.0.2.1', 'ssh_invalid_user', 4),
                    ('20260710-110000-ssh_failed_password-192.0.2.2-22-user', '2026-07-10T11:00:00Z',
                     'sensor', 'journal', '192.0.2.2', 'ssh_failed_password', 4)
            """)

            conn.commit()
            conn.close()

            # Generate report
            from backend.cli import report_last_24h

            # Capture output
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                report_last_24h(
                    database=db_path,
                    hours=24,
                    min_severity=1
                )

            output = f.getvalue()

            # Verify output contains expected content
            assert "SecMon SSH Detector Report" in output
            assert "Total Attackers: 3" in output
            assert "Total Attack Events: 17" in output
            assert "192.0.2.1" in output
            assert "High-Risk" in output
            assert "H5" in output  # Severity badge

    def test_report_filters(self):
        """Test report filtering by severity and status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            migrate(db_path, Path("database/migrations"))

            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")

            # Insert filtered and unfiltered data
            conn.execute("""
                INSERT INTO attackers (src_ip, first_seen, last_seen, total_events,
                                       threat_score, highest_severity, last_attack_type,
                                       status)
                VALUES
                    ('192.0.2.1', '2026-07-10T10:00:00Z', '2026-07-10T14:00:00Z',
                     10, 85, 5, 'ssh_failed_password', 'high_risk'),
                    ('192.0.2.2', '2026-07-10T11:00:00Z', '2026-07-10T14:00:00Z',
                     5, 45, 4, 'ssh_invalid_user', 'observed')
            """)

            conn.commit()
            conn.close()

            # Generate report with min_severity filter
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                report_last_24h(
                    database=db_path,
                    hours=24,
                    min_severity=3
                )

            output = f.getvalue()

            assert "192.0.2.1" in output  # Has severity 5
            assert "192.0.2.2" in output  # Has severity 4

            # Generate report with higher min_severity
            f = io.StringIO()
            with redirect_stdout(f):
                report_last_24h(
                    database=db_path,
                    hours=24,
                    min_severity=5
                )

            output = f.getvalue()

            # Only 192.0.2.1 should appear
            assert "192.0.2.1" in output
            assert "192.0.2.2" not in output
```

## Implementation File Paths

### Database Migration (New Table)

**File:** `database/migrations/002_add_ssh_support.sql`

```sql
-- Add SSH support fields to log_sources
ALTER TABLE log_sources ADD COLUMN source_type TEXT NOT NULL DEFAULT 'journal';

-- Add SSH-specific constraints and indexes
CREATE INDEX IF NOT EXISTS idx_log_sources_status_enabled
    ON log_sources(status, enabled);

CREATE INDEX IF NOT EXISTS idx_log_sources_last_event
    ON log_sources(last_event_at);
```

### Parser Implementation

**File:** `backend/parsers/ssh_parser.py`

```python
"""SSH log parser for journal-based intrusion detection."""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any

class SSHLogParser:
    """Parse SSH journal logs for intrusion detection."""
    # ... (full implementation from design)
```

### Collector Implementation

**File:** `backend/collectors/ssh_journal_collector.py`

```python
"""SSH journal collector with cursor persistence."""

import json
import subprocess
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from backend.parsers.ssh_parser import SSHLogParser

logger = logging.getLogger(__name__)


class SSHJournalCursor:
    """Cursor persistence for SSH journal collection."""

    def __init__(self, cursor_path: Path):
        self.cursor_path = cursor_path
        self.cursor_data = self._load()

    def _load(self) -> dict:
        """Load cursor data from file."""
        if self.cursor_path.exists():
            with open(self.cursor_path) as f:
                return json.load(f)
        return {"cursor": "", "timestamp": "", "source_id": None}

    def save(self) -> None:
        """Save cursor data to file."""
        self.cursor_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cursor_path, "w") as f:
            json.dump(self.cursor_data, f)

    def update(self, cursor: str, timestamp: str, source_id: int) -> None:
        """Update cursor data."""
        self.cursor_data = {
            "cursor": cursor,
            "timestamp": timestamp,
            "source_id": source_id
        }
        self.save()

    def reset(self) -> None:
        """Reset cursor."""
        self.cursor_data = {"cursor": "", "timestamp": "", "source_id": None}
        self.save()


class SSHJournalCollector:
    """SSH journal collector with cursor tracking."""

    def __init__(
        self,
        database: Path,
        cursor_path: Path,
        journal_unit: str = "sshd",
        lines_per_batch: int = 1000,
        cursor_expires_hours: int = 24
    ):
        self.database = database
        self.cursor = SSHJournalCursor(cursor_path)
        self.journal_unit = journal_unit
        self.lines_per_batch = lines_per_batch
        self.cursor_expires_hours = cursor_expires_hours

    def collect(self) -> None:
        """Main collection loop."""
        conn = sqlite3.connect(self.database)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")

        try:
            # Reset if cursor expired
            if self.cursor.cursor_data["cursor"] and self._is_cursor_expired():
                logger.warning("Cursor expired, resetting")
                self.cursor.reset()

            # Get or create source
            source_id = self._get_or_create_source()

            # Read journal
            journal_output = self._read_journal()

            if not journal_output:
                return

            # Parse events
            parser = SSHLogParser()
            events = parser.parse(journal_output, sensor_host="sensor")

            if not events:
                return

            # Store events in transaction
            conn.execute("BEGIN TRANSACTION")
            self._store_events(conn, events, source_id)
            conn.commit()

            # Update cursor
            latest_event = max(events, key=lambda e: e["detected_at"])
            self.cursor.update(
                cursor=latest_event["cursor"],
                timestamp=latest_event["detected_at"],
                source_id=source_id
            )

            logger.info(f"Processed {len(events)} SSH events")

        except Exception as e:
            conn.rollback()
            logger.error(f"Collection failed: {e}")
            raise
        finally:
            conn.close()

    def _is_cursor_expired(self) -> bool:
        """Check if cursor is expired."""
        if not self.cursor.cursor_data["timestamp"]:
            return False

        cursor_time = datetime.fromisoformat(
            self.cursor.cursor_data["timestamp"].replace("Z", "+00:00")
        )
        age = datetime.now(cursor_time.tzinfo) - cursor_time
        return age.total_seconds() > (self.cursor_expires_hours * 3600)

    def _get_or_create_source(self) -> int:
        """Get or create log source in database."""
        cursor = sqlite3.connect(self.database).cursor()
        cursor.execute(
            """
            INSERT INTO log_sources (name, source_type, source_path, enabled)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(name) DO UPDATE SET
                status = 'healthy',
                last_event_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
            """,
            (self.journal_unit, "journal", f"journal://{self.journal_unit}")
        )
        source_id = cursor.fetchone()[0]
        cursor.close()
        return source_id

    def _read_journal(self) -> str:
        """Read SSH journal using journalctl."""
        try:
            cmd = [
                "journalctl",
                f"--unit={self.journal_unit}",
                "--lines=0",  # 0 = no limit, use cursor instead
                "--no-pager",
                "--quiet"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"journalctl failed: {result.stderr}")
                return ""

            return result.stdout

        except subprocess.TimeoutExpired:
            logger.error("journalctl command timed out")
            return ""
        except Exception as e:
            logger.error(f"Failed to read journal: {e}")
            return ""

    def _store_events(self, conn: sqlite3.Connection, events: List[dict], source_id: int) -> None:
        """Store events and update attackers in transaction."""
        for event in events:
            # UPSERT attacker
            conn.execute("""
                INSERT INTO attackers (src_ip, first_seen, last_seen, total_events,
                                       threat_score, highest_severity, last_attack_type,
                                       status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'observed', CURRENT_TIMESTAMP)
                ON CONFLICT(src_ip) DO UPDATE SET
                    last_seen = CURRENT_TIMESTAMP,
                    total_events = total_events + 1,
                    highest_severity = MAX(highest_severity, ?),
                    threat_score = threat_score + ?,
                    last_attack_type = ?,
                    status = CASE
                        WHEN threat_score >= 80 THEN 'high_risk'
                        WHEN threat_score >= 50 THEN 'observed'
                        ELSE 'observed'
                    END,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                event["src_ip"],
                event["detected_at"],
                event["detected_at"],
                1,
                event["severity"],
                event["severity"],
                event["attack_type"],
            ))

            # INSERT event (event_key is UNIQUE)
            conn.execute("""
                INSERT INTO attack_events (
                    event_key, detected_at, sensor_host, source_id, source_type,
                    src_ip, src_port, dst_port, protocol, attack_type, severity,
                    username, blocked, raw_log, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event["event_key"],
                event["detected_at"],
                event["sensor_host"],
                source_id,
                "journal",
                event["src_ip"],
                event["src_port"],
                22,  # SSH defaults
                "tcp",
                event["attack_type"],
                event["severity"],
                event.get("username"),
                0,  # Not blocked initially
                event["raw_log"],
                None,
            ))

        # Update log_sources stats
        conn.execute("""
            UPDATE log_sources
            SET events_today = events_today + ?,
                last_event_at = CURRENT_TIMESTAMP,
                status = 'healthy'
            WHERE id = ?
        """, (len(events), source_id))
```

### CLI Tool Implementation

**File:** `backend/cli.py`

```python
"""CLI tools for SSH detector."""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import json
import logging
from typing import List, Dict, Any

from backend.parsers.ssh_parser import SSHLogParser

logger = logging.getLogger(__name__)


def report_last_24h(
    database: Path,
    hours: int = 24,
    min_severity: int = 1,
    status_filter: Optional[str] = None
) -> None:
    """Generate CLI report of attack IPs in last N hours."""
    # Calculate time range
    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Connect to database
    conn = sqlite3.connect(database)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Build query
    query = """
        SELECT
            src_ip,
            first_seen,
            last_seen,
            total_events,
            threat_score,
            highest_severity,
            last_attack_type,
            status,
            json_group_array(
                json_object(
                    'timestamp', detected_at,
                    'attack_type', attack_type,
                    'severity', severity
                )
            ) as recent_events
        FROM attack_events
        WHERE detected_at >= ?
          AND severity >= ?
          AND source_type = 'journal'
          AND NOT blocked = 1
    """

    if status_filter:
        query += f" AND status = ?"

    query += """
        GROUP BY src_ip
        ORDER BY threat_score DESC, total_events DESC
        LIMIT 100
    """

    # Execute query
    cursor.execute(
        query,
        (cutoff_time.isoformat() + "Z", min_severity) +
        ([status_filter] if status_filter else [])
    )

    rows = cursor.fetchall()

    # Print report header
    print(f"\n{'='*80}")
    print(f"SecMon SSH Detector Report - Last {hours} Hours")
    print(f"{'='*80}")
    print(f"Generated: {datetime.now().isoformat()}Z")
    print(f"Time Range: {cutoff_time.isoformat()}Z - now")
    print(f"Minimum Severity: {min_severity}")
    if status_filter:
        print(f"Status Filter: {status_filter}")
    print(f"{'='*80}\n")

    if not rows:
        print("No attack events found in the specified time range.")
        conn.close()
        return

    # Print summary
    total_attacks = sum(row[3] for row in rows)
    total_high_risk = sum(1 for row in rows if row[7] == 'high_risk')
    avg_threat_score = sum(row[4] for row in rows) / len(rows)

    print(f"Summary:")
    print(f"  Total Attackers: {len(rows)}")
    print(f"  Total Attack Events: {total_attacks}")
    print(f"  High-Risk Attackers: {total_high_risk}")
    print(f"  Average Threat Score: {avg_threat_score:.1f}")
    print(f"\n")

    # Print attackers table
    print(f"{'IP Address':<20} {'Events':>6} {'Score':>5} {'Severity':>8} "
          f"{'Last Seen':>20} {'Type':<30} {'Status'}")
    print(f"{'-'*20} {'-'*6} {'-'*5} {'-'*8} {'-'*20} {'-'*30} {'-'*8}")

    for row in rows:
        ip, first_seen, last_seen, total_events, threat_score, severity, \
            last_attack_type, status, _ = row

        severity_badge = _severity_badge(severity)

        print(
            f"{ip:<20} {total_events:>6} {threat_score:>5} "
            f"{severity_badge:>8} {last_seen:>20} {last_attack_type:<30} {status}"
        )

    # Print detailed events for top 5 attackers
    print(f"\n{'='*80}")
    print("Top 5 Attackers - Detailed Events:")
    print(f"{'='*80}\n")

    for i, row in enumerate(rows[:5], 1):
        ip, first_seen, last_seen, total_events, threat_score, severity, \
            last_attack_type, status, recent_events_json = row

        recent_events = json.loads(recent_events_json) if recent_events_json else []

        print(f"{i}. {ip} (Total Events: {total_events}, Threat Score: {threat_score})")
        print(f"   Status: {status} | Severity: {severity}")
        print(f"   First Seen: {first_seen} | Last Seen: {last_seen}")
        print(f"   Attack Type: {last_attack_type}")
        print(f"   Recent Events:")
        for event in recent_events[:5]:  # Show max 5 recent events
            print(
                f"     - {event['timestamp']} [{event['attack_type']}] "
                f"Severity: {event['severity']}"
            )
        if len(recent_events) > 5:
            print(f"     ... and {len(recent_events) - 5} more events")
        print()

    conn.close()


def _severity_badge(severity: int) -> str:
    """Return severity level badge with color codes."""
    colors = {
        1: "\033[32m",  # Green
        2: "\033[32m",  # Green
        3: "\033[33m",  # Yellow
        4: "\033[91m",  # Red
        5: "\033[91m",  # Red
    }
    reset = "\033[0m"

    if severity <= 2:
        return f"{colors[severity]}L{severity}{reset}"
    elif severity <= 3:
        return f"{colors[severity]}M{severity}{reset}"
    else:
        return f"{colors[severity]}H{severity}{reset}"


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SecMon SSH Detector CLI Tools"
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("./var/secmon.db"),
        help="Path to SQLite database"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to look back"
    )
    parser.add_argument(
        "--min-severity",
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help="Minimum severity"
    )
    parser.add_argument(
        "--status",
        choices=['observed', 'high_risk', 'blocked', 'allowlisted'],
        help="Filter by status"
    )
    parser.add_argument(
        "--parse",
        type=Path,
        help="Parse and validate SSH log file"
    )

    args = parser.parse_args()

    if args.parse:
        # File parsing mode
        parser = SSHLogParser()
        with open(args.parse) as f:
            content = f.read()
        events = parser.parse(content, sensor_host="sensor")
        print(f"Parsed {len(events)} SSH events")
        for event in events:
            print(f"  - {event['detected_at']}: {event['attack_type']} - {event['src_ip']}")
    else:
        # Report mode
        if args.hours < 1 or args.hours > 168:
            parser.error("hours must be between 1 and 168")

        report_last_24h(
            database=args.database,
            hours=args.hours,
            min_severity=args.min_severity,
            status_filter=args.status
        )
```

### Test Suite

**File:** `tests/test_ssh_detector.py`

```python
"""Unit tests for SSH detector implementation."""

import pytest
from pathlib import Path
import tempfile
import sqlite3
from datetime import datetime

from backend.parsers.ssh_parser import SSHLogParser
from backend.collectors.ssh_journal_collector import SSHJournalCollector
from backend.cli import report_last_24h, _severity_badge
from database.migrate import migrate
from tests.fixtures.ssh_parser import (
    SSH_LOG_OUTPUT,
    PARSED_EVENTS,
    INVALID_LOG_LINES,
    NON_SSH_LINES,
)


class TestSSHLogParser:
    """Test SSH log parser."""

    def test_parse_valid_logs(self):
        """Test parsing of valid SSH journal logs."""
        parser = SSHLogParser()
        events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")

        assert len(events) == len(PARSED_EVENTS)

        expected = PARSED_EVENTS[0]
        actual = events[0]

        for key in ["event_key", "detected_at", "src_ip", "src_port",
                    "attack_type", "severity", "username"]:
            assert actual[key] == expected[key]

        assert actual["dst_port"] == 22
        assert actual["protocol"] == "tcp"

    def test_parse_invalid_logs(self):
        """Test handling of invalid log lines."""
        parser = SSHLogParser()
        output = "\n".join(INVALID_LOG_LINES)
        events = parser.parse(output, sensor_host="sensor")
        assert len(events) == 0

    def test_parse_non_ssh_lines(self):
        """Test filtering of non-SSH log lines."""
        parser = SSHLogParser()
        output = "\n".join(NON_SSH_LINES)
        events = parser.parse(output, sensor_host="sensor")
        assert len(events) == 0

    def test_create_event_key(self):
        """Test event key generation."""
        parser = SSHLogParser()
        event = parser._create_event(
            timestamp="2026-07-10T14:23:45Z",
            message="Test message",
            sensor_host="sensor",
            src_ip="192.0.2.100",
            src_port=45678,
            username="admin",
            attack_type="ssh_test",
            severity=4
        )
        assert "20260710-142345-ssh_test-192.0.2.100-45678-admin" in event["event_key"]

    def test_event_key_truncation(self):
        """Test event key truncation to max 200 chars."""
        parser = SSHLogParser()
        long_key = "A" * 300 + "-test-ip-1-22-user"
        event = parser._create_event(
            timestamp="2026-07-10T14:23:45Z",
            message="Test message",
            sensor_host="sensor",
            src_ip="192.0.2.100",
            src_port=45678,
            username="user",
            attack_type="A" * 200,
            severity=4
        )
        assert len(event["event_key"]) <= 200

    def test_raw_log_truncation(self):
        """Test raw log truncation to max 1000 chars."""
        parser = SSHLogParser()
        long_message = "A" * 2000 + " test"
        event = parser._create_event(
            timestamp="2026-07-10T14:23:45Z",
            message=long_message,
            sensor_host="sensor",
            src_ip="192.0.2.100",
            src_port=45678,
            username="user",
            attack_type="ssh_test",
            severity=4
        )
        assert len(event["raw_log"]) <= 1000


class TestSSHJournalCursor:
    """Test SSH journal cursor persistence."""

    def test_cursor_load_save(self):
        """Test loading and saving cursor data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "cursor.txt"
            cursor = SSHJournalCursor(cursor_path)
            assert cursor.cursor_data == {"cursor": "", "timestamp": "", "source_id": None}

            cursor.update("test-cursor", "2026-07-10T14:23:45Z", 1)

            cursor2 = SSHJournalCursor(cursor_path)
            assert cursor2.cursor_data["cursor"] == "test-cursor"
            assert cursor2.cursor_data["timestamp"] == "2026-07-10T14:23:45Z"
            assert cursor2.cursor_data["source_id"] == 1

    def test_cursor_reset(self):
        """Test cursor reset functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cursor_path = Path(tmpdir) / "cursor.txt"
            cursor = SSHJournalCursor(cursor_path)
            cursor.update("test-cursor", "2026-07-10T14:23:45Z", 1)
            cursor.reset()
            assert cursor.cursor_data == {"cursor": "", "timestamp": "", "source_id": None}


class TestSSHJournalCollector:
    """Test SSH journal collector."""

    def test_collection_pipeline(self):
        """Test complete collection pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            cursor_path = Path(tmpdir) / "cursors" / "ssh_journal_cursor.txt"
            migrate(db_path, Path("database/migrations"))

            parser = SSHLogParser()
            collector = SSHJournalCollector(
                database=db_path,
                cursor_path=cursor_path,
                journal_unit="sshd"
            )

            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("BEGIN TRANSACTION")

            # Mock journalctl output
            import subprocess
            original_run = subprocess.run

            def mock_run(*args, **kwargs):
                if "journalctl" in args[0]:
                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=0,
                        stdout=SSH_LOG_OUTPUT,
                        stderr=""
                    )
                return original_run(*args, **kwargs)

            subprocess.run = mock_run

            try:
                events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                collector._store_events(conn, events, source_id=1)
                conn.commit()

                # Verify attackers
                attacker_rows = conn.execute(
                    "SELECT src_ip, total_events, threat_score FROM attackers"
                ).fetchall()

                assert len(attacker_rows) == 3
                assert attacker_rows[0][1] == 2  # 198.51.100.50 has 2 events
                assert attacker_rows[1][2] == 4  # 192.0.2.100 has threat score 4

                # Verify events
                event_rows = conn.execute(
                    "SELECT COUNT(*), SUM(severity) FROM attack_events"
                ).fetchall()
                assert event_rows[0][0] == 4
                assert event_rows[0][1] == 14

            finally:
                subprocess.run = original_run
                conn.close()

    def test_deduplication(self):
        """Test event deduplication using event_key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            migrate(db_path, Path("database/migrations"))

            parser = SSHLogParser()
            collector = SSHJournalCollector(
                database=db_path,
                cursor_path=Path(tmpdir) / "cursor.txt"
            )

            import subprocess
            original_run = subprocess.run

            def mock_run(*args, **kwargs):
                if "journalctl" in args[0]:
                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=0,
                        stdout=SSH_LOG_OUTPUT,
                        stderr=""
                    )
                return original_run(*args, **kwargs)

            subprocess.run = mock_run

            try:
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA foreign_keys = ON")

                events = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                collector._store_events(conn, events, source_id=1)

                events2 = parser.parse(SSH_LOG_OUTPUT, sensor_host="sensor")
                collector._store_events(conn, events2, source_id=1)

                unique_count = conn.execute(
                    "SELECT COUNT(*) FROM attack_events"
                ).fetchone()[0]
                assert unique_count == 4

                attacker_count = conn.execute(
                    "SELECT COUNT(*) FROM attackers"
                ).fetchone()[0]
                assert attacker_count == 3

            finally:
                subprocess.run = subprocess.run
                conn.close()


class TestCLIReport:
    """Test CLI report generation."""

    def test_report_generation(self):
        """Test generating attack IP report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            migrate(db_path, Path("database/migrations"))

            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")

            now = datetime.now()
            conn.execute("""
                INSERT INTO attackers (src_ip, first_seen, last_seen, total_events,
                                       threat_score, highest_severity, last_attack_type,
                                       status)
                VALUES
                    ('192.0.2.1', '2026-07-10T10:00:00Z', '2026-07-10T14:00:00Z',
                     10, 85, 5, 'ssh_failed_password', 'high_risk'),
                    ('192.0.2.2', '2026-07-10T11:00:00Z', '2026-07-10T14:00:00Z',
                     5, 45, 4, 'ssh_invalid_user', 'observed')
            """)

            conn.execute("""
                INSERT INTO attack_events (event_key, detected_at, sensor_host,
                                           source_type, src_ip, attack_type,
                                           severity)
                VALUES
                    ('20260710-100000-ssh_failed_password-192.0.2.1-22-admin', '2026-07-10T10:00:00Z',
                     'sensor', 'journal', '192.0.2.1', 'ssh_failed_password', 5),
                    ('20260710-140000-ssh_invalid_user-192.0.2.1-22-test', '2026-07-10T14:00:00Z',
                     'sensor', 'journal', '192.0.2.1', 'ssh_invalid_user', 4)
            """)

            conn.commit()
            conn.close()

            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                report_last_24h(database=db_path, hours=24, min_severity=1)

            output = f.getvalue()
            assert "SecMon SSH Detector Report" in output
            assert "Total Attackers: 2" in output
            assert "192.0.2.1" in output
            assert "High-Risk" in output

    def test_report_filters(self):
        """Test report filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "secmon.db"
            migrate(db_path, Path("database/migrations"))

            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")

            conn.execute("""
                INSERT INTO attackers (src_ip, first_seen, last_seen, total_events,
                                       threat_score, highest_severity, last_attack_type,
                                       status)
                VALUES
                    ('192.0.2.1', '2026-07-10T10:00:00Z', '2026-07-10T14:00:00Z',
                     10, 85, 5, 'ssh_failed_password', 'high_risk')
            """)

            conn.commit()
            conn.close()

            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                report_last_24h(database=db_path, hours=24, min_severity=5)

            output = f.getvalue()
            assert "192.0.2.1" in output
            assert "Total Attackers: 1" in output

            f = io.StringIO()
            with redirect_stdout(f):
                report_last_24h(database=db_path, hours=24, min_severity=1)

            output = f.getvalue()
            assert "192.0.2.1" in output
            assert "Total Attackers: 1" in output


class TestSeverityBadge:
    """Test severity badge formatting."""

    def test_low_severity(self):
        """Test low severity badges."""
        assert _severity_badge(1) == "\033[32mL1\033[0m"
        assert _severity_badge(2) == "\033[32mL2\033[0m"

    def test_medium_severity(self):
        """Test medium severity badges."""
        assert _severity_badge(3) == "\033[33mM3\033[0m"

    def test_high_severity(self):
        """Test high severity badges."""
        assert _severity_badge(4) == "\033[91mH4\033[0m"
        assert _severity_badge(5) == "\033[91mH5\033[0m"
```

## Test Fixtures

**File:** `tests/fixtures/ssh_parser.py`

```python
"""SSH parser test fixtures."""

from typing import Dict, Any

SSH_LOG_LINES = [
    "Jul 10 14:23:45 sensor sshd[1234]: Failed password for invalid user admin from 192.0.2.100 port 45678 ssh2",
    "Jul 10 14:23:46 sensor sshd[1234]: Failed password for root from 198.51.100.50 port 54321 ssh2",
    "Jul 10 14:23:47 sensor sshd[1234]: Invalid user testuser from 203.0.113.75 port 67890 ssh2",
    "Jul 10 14:23:48 sensor sshd[1234]: Port 54321 attempted root from 198.51.100.50",
]

SSH_LOG_OUTPUT = "\n".join(SSH_LOG_LINES)

PARSED_EVENTS = [
    {
        "event_key": "20260710-142345-ssh_failed_password-192.0.2.100-45678-admin",
        "detected_at": "2026-07-10T14:23:45Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "192.0.2.100",
        "src_port": 45678,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_failed_password",
        "severity": 4,
        "username": "admin",
        "raw_log": "Failed password for invalid user admin from 192.0.2.100 port 45678 ssh2",
        "cursor": "20260710-142345-192.0.2.100"
    },
    {
        "event_key": "20260710-142346-ssh_failed_password-198.51.100.50-54321-root",
        "detected_at": "2026-07-10T14:23:46Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "198.51.100.50",
        "src_port": 54321,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_failed_password",
        "severity": 4,
        "username": "root",
        "raw_log": "Failed password for root from 198.51.100.50 port 54321 ssh2",
        "cursor": "20260710-142346-198.51.100.50"
    },
    {
        "event_key": "20260710-142347-ssh_invalid_user-203.0.113.75-67890-testuser",
        "detected_at": "2026-07-10T14:23:47Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "203.0.113.75",
        "src_port": 67890,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_invalid_user",
        "severity": 3,
        "username": "testuser",
        "raw_log": "Invalid user testuser from 203.0.113.75 port 67890 ssh2",
        "cursor": "20260710-142347-203.0.113.75"
    },
    {
        "event_key": "20260710-142348-ssh_attempted_login-198.51.100.50-54321-root",
        "detected_at": "2026-07-10T14:23:48Z",
        "sensor_host": "sensor",
        "source_type": "journal",
        "src_ip": "198.51.100.50",
        "src_port": 54321,
        "dst_port": 22,
        "protocol": "tcp",
        "attack_type": "ssh_attempted_login",
        "severity": 3,
        "username": "root",
        "raw_log": "Port 54321 attempted root from 198.51.100.50",
        "cursor": "20260710-142348-198.51.100.50"
    },
]

INVALID_LOG_LINES = [
    "2026-07-10 14:23:45 invalid format",
    "Jul 10 14:23:45 hostname sshd[1234]:",
    "Jul 10 14:23:45 hostname sshd[1234]: message without port",
    "Jul 10 14:23:45 hostname sshd[1234]: Failed password from 192.0.2.100 ssh2",
]

NON_SSH_LINES = [
    "Jul 10 14:23:45 hostname sshd[1234]: Connection closed by authenticating user",
    "Jul 10 14:23:45 hostname sshd[1234]: Accepted password for user from 192.0.2.100",
]
```

## Summary

This design provides:

1. **Complete table schemas** for log_sources, attack_events, and attackers
2. **SSH log parser** with regex patterns for Failed password, Invalid user, and Attempted login
3. **Collector with cursor persistence** to avoid reprocessing old events
4. **Event deduplication** using UNIQUE event_key constraint
5. **Attackers UPSERT logic** with threat score aggregation
6. **CLI report tool** showing last 24h attack IPs with filtering options
7. **Comprehensive test suite** with fixtures and test cases

All components follow the existing SecMon architecture and are ready for implementation.
