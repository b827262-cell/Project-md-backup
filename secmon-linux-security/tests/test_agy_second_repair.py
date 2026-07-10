"""Regression coverage for defects found by the first AGY review."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from backend.collectors.ssh_collector import SSHCollector
from backend.parsers.ssh_parser import SSHParser


def test_ports_and_invalid_user_are_structured():
    parser = SSHParser(reference_time=datetime(2026, 7, 10, 12, 0, 0))
    entry = parser.parse_line(
        "2026-07-10 11:00:00 sshd: Failed password for invalid user baduser "
        "from 203.0.113.10 port 45678 ssh2"
    )
    assert entry is not None
    assert entry.username == "baduser"
    assert entry.source_ip == "203.0.113.10"
    assert entry.src_port == 45678
    assert entry.failure_reason == "Failed password for invalid user"


def test_port_boundaries():
    parser = SSHParser()
    for port in (1, 22, 65535):
        assert parser.validate_port(str(port)) == port
    for port in (0, -1, 65536, 99999, "abc", ""):
        try:
            parser.validate_port(port)
        except ValueError:
            pass
        else:
            raise AssertionError(f"port {port!r} should be rejected")


def test_future_policy_uses_injected_reference_time():
    reference = datetime(2026, 7, 10, 12, 0, 0)
    parser = SSHParser(reference_time=reference)

    def line(timestamp: datetime) -> str:
        return (
            f"{timestamp:%Y-%m-%d %H:%M:%S} sshd: Failed password for root "
            "from 192.0.2.1 port 22 ssh2"
        )
    assert parser.parse_line(line(reference - timedelta(days=365))) is not None
    assert parser.parse_line(line(reference + timedelta(minutes=4))) is not None
    for timestamp in (reference + timedelta(minutes=6), reference + timedelta(hours=2)):
        try:
            parser.parse_line(line(timestamp))
        except ValueError:
            pass
        else:
            raise AssertionError("excessively future timestamp was accepted")


def test_event_key_differs_by_port():
    parser = SSHParser(reference_time=datetime(2026, 7, 10, 12, 0, 0))
    first = parser.parse_line(
        "2026-07-10 11:00:00 sshd: Failed password for root "
        "from 192.0.2.1 port 22 ssh2"
    )
    second = parser.parse_line(
        "2026-07-10 11:00:00 sshd: Failed password for root "
        "from 192.0.2.1 port 23 ssh2"
    )
    assert first is not None and second is not None
    assert first.event_key != second.event_key


def test_cursor_path_precedence(tmp_path, monkeypatch):
    monkeypatch.setenv("SECMON_SSH_CURSOR_PATH", str(tmp_path / "env.cursor"))
    from database.migrate import migrate
    db_path = tmp_path / "db.sqlite"
    migrate(db_path, Path(__file__).parent.parent / "database" / "migrations")
    collector = SSHCollector(database_path=db_path)
    assert collector.cursor_position_file == tmp_path / "env.cursor"
    explicit = SSHCollector(database_path=db_path, cursor_path=tmp_path / "explicit.cursor")
    assert explicit.cursor_position_file == tmp_path / "explicit.cursor"


def test_collector_persists_port_and_deduplicates_by_port(tmp_path):
    from database.migrate import migrate

    db_path = tmp_path / "db.sqlite"
    log_path = tmp_path / "auth.log"
    migrate(db_path, Path(__file__).parent.parent / "database" / "migrations")
    log_path.write_text(
        "2026-07-10 11:00:00 sshd: Failed password for root from 192.0.2.9 port 22 ssh2\n"
        "2026-07-10 11:00:00 sshd: Failed password for root from 192.0.2.9 port 23 ssh2\n"
    )
    collector = SSHCollector(database_path=db_path, cursor_path=tmp_path / "cursor")
    assert collector.collect_from_file(str(log_path)) == (2, 1)
    rows = sqlite3.connect(db_path).execute(
        "SELECT src_port FROM attack_events ORDER BY id"
    ).fetchall()
    assert rows == [(22,), (23,)]
