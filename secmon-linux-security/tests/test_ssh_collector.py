"""Tests for SSH collector module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from backend.collectors.ssh_collector import SSHCollector
from backend.parsers.ssh_parser import SSHLogEntry, SSHParser


@pytest.fixture
def mock_db_path(tmp_path):
    """Create a temporary migrated database for testing."""
    db_path = tmp_path / "test.db"
    migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
    from database.migrate import migrate
    migrate(db_path, migrations_dir)
    return db_path


class TestSSHLogEntry:
    """Test SSH log entry dataclass."""

    def test_event_key_with_username(self):
        """Test event key generation with username."""
        entry = SSHLogEntry(
            timestamp="2024-01-15 10:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="testuser",
            failure_reason="Failed password"
        )
        assert "testuser" in entry.event_key

    def test_event_key_without_username(self):
        """Test event key generation without username."""
        entry = SSHLogEntry(
            timestamp="2024-01-15 10:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username=None,
            failure_reason="Failed password"
        )
        # Username should be empty string in event key
        assert entry.event_key == "2024-01-15 10:30:45|192.168.1.100|22|ssh||Failed password"


class TestSSHCollector:
    """Test SSH collector functionality."""

    def test_parse_failed_password(self):
        """Test parsing 'Failed password' log lines."""
        parser = SSHParser()
        line = "sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2"
        entry = parser.parse_line(line)

        assert entry is not None
        # Should use current timestamp due to fallback
        assert entry.timestamp == datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        assert entry.source_ip == "192.168.1.100"
        assert entry.service == "ssh"
        assert entry.username == "root"
        assert entry.failure_reason == "Failed password"

    def test_parse_invalid_user(self):
        """Test parsing 'Invalid user' log lines."""
        parser = SSHParser()
        line = "sshd[5678]: Invalid user admin from 10.0.0.1 port 33444 ssh2"
        entry = parser.parse_line(line)

        assert entry is not None
        # Should use current timestamp due to fallback
        assert entry.timestamp == datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        assert entry.source_ip == "10.0.0.1"
        assert entry.service == "ssh"
        assert entry.username == "admin"
        assert entry.failure_reason == "Invalid user"

    def test_parse_non_ssh_line(self):
        """Test that non-SSH lines return None."""
        parser = SSHParser()
        line = "Jan 15 10:30:45 example sshd[1234]: Connection closed by authenticating user"
        entry = parser.parse_line(line)

        assert entry is None

    def test_event_key_generation(self):
        """Test unique event key generation."""
        parser = SSHParser()
        line = "sshd[1234]: Failed password for testuser from 192.168.1.200 port 44322 ssh2"
        entry = parser.parse_line(line)

        assert entry is not None
        event_key = entry.event_key
        # The test should pass if it contains the correct fields
        assert "testuser" in event_key
        assert "192.168.1.200" in event_key
        assert "ssh" in event_key

    def test_get_settings(self, mock_db_path):
        """Test that collector initializes with settings."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                environment="development", database_path=str(mock_db_path)
            )
            collector = SSHCollector()
            assert collector.settings is not None

    def test_cursor_position_initialization(self, mock_db_path, tmp_path):
        """Test that cursor position initializes to None."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                environment="development", database_path=str(mock_db_path)
            )
            collector = SSHCollector()
            # Set cursor position file to tmp path to avoid polluting workspace
            collector.cursor_position_file = tmp_path / "ssh_cursor.position"
            # It loads cursor position dynamically
            assert collector._get_last_cursor_position() == 0

    def test_batch_size_default(self, mock_db_path):
        """Test that batch size is set to default value."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                environment="development", database_path=str(mock_db_path)
            )
            collector = SSHCollector()
            assert collector.batch_size == 100  # Default batch size

    def test_parse_ssh_line_pattern_match(self, mock_db_path):
        """Test that SSH collector correctly parses SSH lines."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                environment="development", database_path=str(mock_db_path)
            )

            collector = SSHCollector()
            line = "sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2"
            entry = collector.parse_ssh_line(line)

            assert entry is not None
            assert entry.timestamp is not None
            assert entry.source_ip == "192.168.1.100"
            assert entry.service == "ssh"
            assert entry.username == "root"
            custom_log_line = "sshd[5678]: Invalid user admin from 10.0.0.1 port 33444 ssh2"
            entry = collector.parse_ssh_line(custom_log_line)
            assert entry.username == "admin"
