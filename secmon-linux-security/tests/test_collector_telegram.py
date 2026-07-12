"""Integration-style tests for SSH collector Telegram alerts."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.collectors.ssh_collector import SSHCollector
from database.migrate import migrate_latest


class _RecordingNotifier:
    def __init__(self, result: bool) -> None:
        self.result = result
        self.messages: list[str] = []

    def send_message(self, text: str) -> bool:
        self.messages.append(text)
        return self.result


def _migrated_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "secmon.db"
    migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
    migrate_latest(db_path, migrations_dir)
    return db_path


def test_failed_notification_keeps_committed_events_and_cursor(
    tmp_path,
) -> None:
    db_path = _migrated_db(tmp_path)
    cursor_path = tmp_path / "ssh.cursor"
    log_path = tmp_path / "auth.log"
    raw_line = (
        "Jul 10 17:30:45 host sshd[1234]: Failed password for admin "
        "from 192.0.2.9 port 54321 ssh2\n"
        "Jul 10 17:31:45 host sshd[1234]: Failed password for admin "
        "from 192.0.2.10 port 54322 ssh2\n"
    )
    log_path.write_text(raw_line, encoding="utf-8")

    notifier = _RecordingNotifier(result=False)
    collector = SSHCollector(
        database_path=db_path,
        cursor_path=cursor_path,
        notifier=notifier,
    )
    collector.reset_cursor()

    new_events, new_attackers = collector.collect_from_file(str(log_path))

    assert (new_events, new_attackers) == (2, 2)
    assert len(notifier.messages) == 1
    message = notifier.messages[0]
    assert "SecMon SSH Attack Alert" in message
    assert "New events: 2" in message
    assert "Top sources:" in message
    assert "sshd[1234]" not in message
    assert "port 54321 ssh2" not in message

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM attack_events").fetchone()[0] == 2
        assert conn.execute("SELECT COUNT(*) FROM attackers").fetchone()[0] == 2
    finally:
        conn.close()

    assert cursor_path.read_text(encoding="utf-8").strip() != ""
