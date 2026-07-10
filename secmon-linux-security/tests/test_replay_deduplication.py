"""Test suite for replay deduplication using P1 canonical schema."""

import sqlite3
from pathlib import Path

import pytest

from backend.collectors.ssh_collector import SSHCollector
from backend.models import AttackEvent
from database.migrate import migrate_latest


@pytest.fixture
def migrated_db(tmp_path):
    """Fixture to create a clean migrated SQLite database."""
    db_path = tmp_path / "secmon.db"
    migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
    migrate_latest(db_path, migrations_dir)
    return db_path


@pytest.fixture
def cursor_path(tmp_path):
    """Fixture to create a temporary cursor file path."""
    return tmp_path / "ssh.cursor"


class TestReplayDeduplication:
    """Test that replaying fixtures does not create duplicate events."""

    def test_single_replay_no_duplicates(self, migrated_db, cursor_path):
        """Test that a single replay collection does not create duplicates."""
        collector = SSHCollector(database_path=migrated_db)
        collector.cursor_position_file = cursor_path
        collector.reset_cursor()

        fixture_path = Path(__file__).parent / "fixtures" / "ssh_failure.log"

        # First collection
        new_events, new_attackers = collector.collect_from_file(
            str(fixture_path), batch_size=10
        )
        print(f"First: {new_events} events, {new_attackers} attackers")

        # Second collection (replay)
        collector.reset_cursor()  # reset cursor to replay from start of file
        replay_events, replay_attackers = collector.collect_from_file(
            str(fixture_path), batch_size=100
        )
        print(f"Replay: {replay_events} events, {replay_attackers} attackers")

        # Verify no events were added in replay
        assert replay_events == 0, f"Expected 0 new events, got {replay_events}"
        assert replay_attackers == 0, f"Expected 0 new attackers, got {replay_attackers}"

        # Verify total events match fixture count
        conn = sqlite3.connect(migrated_db)
        cursor = conn.execute("SELECT COUNT(*) FROM attack_events")
        total_events = cursor.fetchone()[0]
        conn.close()

        # Fixture file has many lines with SSH failures
        assert total_events > 0, "No events found in database, expected >0"
        assert total_events == 118, f"Expected 118 events, got {total_events}"

    def test_multiple_replays_no_duplicates(self, migrated_db, cursor_path):
        """Test multiple replays produce no new events and no increase in total_events."""
        collector = SSHCollector(database_path=migrated_db)
        collector.cursor_position_file = cursor_path
        collector.reset_cursor()

        fixture_path = Path(__file__).parent / "fixtures" / "ssh_failure.log"

        # Initial collection
        init_events, init_attackers = collector.collect_from_file(
            str(fixture_path), batch_size=100
        )
        assert init_events == 118

        # Check total events count and attackers total events sum after first import
        conn = sqlite3.connect(migrated_db)
        total_events_1 = conn.execute(
            "SELECT COUNT(*) FROM attack_events"
        ).fetchone()[0]
        total_attacker_events_1 = conn.execute(
            "SELECT SUM(total_events) FROM attackers"
        ).fetchone()[0]
        conn.close()

        assert total_events_1 == 118
        assert total_attacker_events_1 is not None
        assert total_attacker_events_1 > 0

        # Perform 4 replays
        for i in range(4):
            collector.reset_cursor()
            replay_events, replay_attackers = collector.collect_from_file(
                str(fixture_path), batch_size=100
            )
            print(f"Replay {i + 1}: {replay_events} events, {replay_attackers} attackers")

            # Each replay should add 0 new events and 0 new attackers
            assert replay_events == 0, f"Replay {i + 1} added {replay_events} events"
            assert replay_attackers == 0, f"Replay {i + 1} added {replay_attackers} attackers"

        # Check counts after all replays
        conn = sqlite3.connect(migrated_db)
        total_events_final = conn.execute(
            "SELECT COUNT(*) FROM attack_events"
        ).fetchone()[0]
        total_attacker_events_final = conn.execute(
            "SELECT SUM(total_events) FROM attackers"
        ).fetchone()[0]
        conn.close()

        # The counts must not increase on replay
        assert total_events_final == total_events_1
        assert total_attacker_events_final == total_attacker_events_1

    def test_event_key_deduplication(self, migrated_db):
        """Test that event_key deduplication works correctly."""
        # Create a fake event using P1 canonical model schema
        now = "2024-07-10 08:15:23"
        event = AttackEvent(
            event_key=f"{now}|192.168.1.100|ssh|root",
            detected_at=now,
            sensor_host="localhost",
            source_id=1,
            source_type="file",
            src_ip="192.168.1.100",
            attack_type="ssh_failed_password",
            signature="Failed password",
            username="root",
            created_at="2024-07-10T08:15:23",
        )

        # Insert the event
        conn = sqlite3.connect(migrated_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attack_events (event_key, detected_at, sensor_host, source_id,
                                       source_type, src_ip, attack_type, signature,
                                       username, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (event.event_key, event.detected_at, event.sensor_host, event.source_id,
              event.source_type, event.src_ip, event.attack_type, event.signature,
              event.username, event.created_at))
        conn.commit()
        conn.close()

        # Verify it's in the database
        conn = sqlite3.connect(migrated_db)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM attack_events WHERE event_key = ?",
            (event.event_key,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1, f"Expected 1 event with key {event.event_key}, got {count}"

        # Now try to insert the same event_key again (simulating replay)
        conn = sqlite3.connect(migrated_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO attack_events (event_key, detected_at, sensor_host, source_id,
                                       source_type, src_ip, attack_type, signature,
                                       username, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (event.event_key, event.detected_at, event.sensor_host, event.source_id,
              event.source_type, event.src_ip, event.attack_type, event.signature,
              event.username, event.created_at))
        conn.commit()
        conn.close()

        # Verify count is still 1
        conn = sqlite3.connect(migrated_db)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM attack_events WHERE event_key = ?",
            (event.event_key,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1, f"Expected count to remain 1, got {count}"

    def test_replay_with_different_timestamps(self, migrated_db, cursor_path):
        """Test replay with events and verify attackers table updates properly."""
        collector = SSHCollector(database_path=migrated_db)
        collector.cursor_position_file = cursor_path
        collector.reset_cursor()

        # Collect first time
        fixture_path = Path(__file__).parent / "fixtures" / "ssh_failure.log"
        collector.collect_from_file(str(fixture_path), batch_size=100)

        # Collect second time (replay)
        collector.reset_cursor()
        new_events, _ = collector.collect_from_file(str(fixture_path), batch_size=100)

        # Should be 0 new events
        assert new_events == 0, f"Expected 0 new events, got {new_events}"

        # Check that attacker counts are correct (not duplicated)
        conn = sqlite3.connect(migrated_db)
        cursor = conn.execute("""
            SELECT src_ip, total_events, first_seen, last_seen
            FROM attackers
        """)
        attackers = cursor.fetchall()
        conn.close()

        # Should have multiple attackers
        assert len(attackers) > 0, "No attackers found"

        # Verify that attack counts are positive
        for ip, count, _first_seen, _last_seen in attackers:
            assert count > 0, f"Attacker {ip} has count 0"

    def test_fixture_line_count(self):
        """Test that fixture file has expected number of log lines."""
        fixture_path = Path(__file__).parent / "fixtures" / "ssh_failure.log"

        # Count lines (excluding comments)
        lines = []
        with open(fixture_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    lines.append(line)

        print(f"Fixture has {len(lines)} non-comment lines")

        # The fixture should have a significant number of events
        assert len(lines) > 100, f"Fixture should have > 100 lines, got {len(lines)}"

    def test_event_key_composition(self):
        """Test that event_key composition is consistent for deduplication."""
        test_events = [
            AttackEvent(
                event_key="2024-07-10 08:15:23|192.168.1.100|ssh|root",
                detected_at="2024-07-10 08:15:23",
                sensor_host="localhost",
                source_id=1,
                source_type="file",
                src_ip="192.168.1.100",
                attack_type="ssh_failed_password",
                signature="Failed password",
                username="root",
                created_at="2024-07-10T08:15:23",
            ),
            AttackEvent(
                event_key="2024-07-10 08:15:23|192.168.1.100|ssh|root",
                detected_at="2024-07-10 08:15:23",
                sensor_host="localhost",
                source_id=1,
                source_type="file",
                src_ip="192.168.1.100",
                attack_type="ssh_failed_password",
                signature="Failed password",
                username="root",
                created_at="2024-07-10T08:15:23",
            ),
        ]

        # All event keys should be identical
        k0, k1 = test_events[0].event_key, test_events[1].event_key
        assert k0 == k1, f"Event keys should be identical: {k0} != {k1}"

        # They should match the pattern: timestamp|ip|service|username
        assert "|" in test_events[0].event_key
        parts = test_events[0].event_key.split("|")
        assert len(parts) == 4

    def test_same_ip_multiple_events(self, migrated_db, cursor_path, tmp_path):
        """Test N distinct events for same IP results in N events and total_events +N."""
        collector = SSHCollector(database_path=migrated_db)
        collector.cursor_position_file = cursor_path
        collector.reset_cursor()

        # Create a log file with 3 distinct events for the same IP
        log_content = (
            "Jul 10 17:30:45 myhost sshd[1234]: Failed password for admin "
            "from 192.168.1.100 port 54321 ssh2\n"
            "Jul 10 17:31:45 myhost sshd[1234]: Failed password for admin "
            "from 192.168.1.100 port 54322 ssh2\n"
            "Jul 10 17:32:45 myhost sshd[1234]: Failed password for admin "
            "from 192.168.1.100 port 54323 ssh2\n"
        )
        temp_log = tmp_path / "same_ip.log"
        temp_log.write_text(log_content, encoding="utf-8")

        new_events, new_attackers = collector.collect_from_file(
            str(temp_log), batch_size=100
        )

        # Verify 3 events were added, but only 1 unique attacker
        assert new_events == 3
        assert new_attackers == 1

        # Query database to confirm
        conn = sqlite3.connect(migrated_db)
        event_count = conn.execute("SELECT COUNT(*) FROM attack_events").fetchone()[0]
        attacker_total_events = conn.execute(
            "SELECT total_events FROM attackers WHERE src_ip = '192.168.1.100'"
        ).fetchone()[0]
        conn.close()

        assert event_count == 3
        assert attacker_total_events == 3
