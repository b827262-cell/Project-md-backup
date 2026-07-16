"""Integration-style tests for SSH collector Telegram alerts."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.collectors.ssh_collector import SSHCollector
from database.migrate import migrate_latest


class _RecordingNotifier:
    def __init__(self, result: bool, raises: bool = False) -> None:
        self.result = result
        self.raises = raises
        self.messages: list[str] = []

    def send_message(self, text: str) -> bool:
        self.messages.append(text)
        if self.raises:
            raise RuntimeError("simulated notification failure")
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


def test_notification_exception_cannot_change_result_database_or_cursor(tmp_path) -> None:
    db_path = _migrated_db(tmp_path)
    cursor_path = tmp_path / "ssh.cursor"
    log_path = tmp_path / "auth.log"
    log_path.write_text(
        "Jul 10 17:30:45 host sshd[1234]: Failed password for admin "
        "from 2001:db8::9 port 54321 ssh2\n",
        encoding="utf-8",
    )
    notifier = _RecordingNotifier(result=False, raises=True)
    collector = SSHCollector(database_path=db_path, cursor_path=cursor_path, notifier=notifier)

    result = collector.collect_from_file(log_path)

    assert result == (1, 1)
    assert len(notifier.messages) == 1
    assert "2001:db8::9" in notifier.messages[0]
    assert cursor_path.exists()
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM attack_events").fetchone()[0] == 1
        assert connection.execute("SELECT total_events FROM attackers").fetchone()[0] == 1


def test_cursor_is_saved_before_single_aggregated_notification(tmp_path) -> None:
    db_path = _migrated_db(tmp_path)
    cursor_path = tmp_path / "ssh.cursor"
    log_path = tmp_path / "auth.log"
    log_path.write_text(
        "Jul 10 17:30:45 host sshd[1234]: Failed password for admin "
        "from 192.0.2.9 port 54321 ssh2\n"
        "Jul 10 17:31:45 host sshd[1234]: Failed password for admin "
        "from 192.0.2.10 port 54322 ssh2\n",
        encoding="utf-8",
    )
    order: list[str] = []
    notifier = _RecordingNotifier(result=True)
    collector = SSHCollector(database_path=db_path, cursor_path=cursor_path, notifier=notifier)
    save_cursor = collector._save_cursor_position

    def save_and_record(position: int) -> None:
        save_cursor(position)
        order.append("cursor")

    collector._save_cursor_position = save_and_record

    def send_and_record(text: str) -> bool:
        assert cursor_path.exists()
        with sqlite3.connect(db_path) as connection:
            assert connection.execute("SELECT COUNT(*) FROM attack_events").fetchone()[0] == 2
        order.append("telegram")
        notifier.messages.append(text)
        return True

    notifier.send_message = send_and_record
    assert collector.collect_from_file(log_path) == (2, 2)
    assert order == ["cursor", "telegram"]
    assert len(notifier.messages) == 1
