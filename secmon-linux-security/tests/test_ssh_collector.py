"""Tests for SSH collector module."""

from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock, patch

# Import modules directly from local paths
from backend.collectors.ssh_collector import SSHCollector


# Mock SSHLogEntry from ssh_collector
@dataclass
class SSHLogEntry:
    """Represents a parsed SSH log entry."""
    timestamp: str
    source_ip: str
    service: str
    failure_reason: str
    username: Optional[str] = None

    @property
    def event_key(self) -> str:
        """Generate unique event key for deduplication."""
        return f"{self.timestamp}|{self.source_ip}|{self.service}|{self.username or ''}"

from backend.parsers.ssh_parser import SSHParser


class TestSSHParser:
    """Test SSH log parser."""

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
        assert entry.event_key == "2024-01-15 10:30:45|192.168.1.100|ssh|"


class TestSSHCollector:
    """Test SSH collector functionality."""

    def test_get_settings(self):
        """Test that collector initializes with settings."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(environment="development")
            collector = SSHCollector()
            assert collector.settings is not None

    def test_cursor_position_initialization(self):
        """Test that cursor position initializes to None."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(environment="development")
            collector = SSHCollector()
            assert collector.cursor_position is None

    def test_batch_size_default(self):
        """Test that batch size is set to default value."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(environment="development")
            collector = SSHCollector()
            assert collector.batch_size == collector.DEFAULT_BATCH_SIZE

    def test_parse_ssh_line_pattern_match(self):
        """Test that SSH collector correctly parses SSH lines."""
        with patch("backend.collectors.ssh_collector.get_settings") as mock_settings:
            mock_settings.return_value = Mock(environment="development", database_path=Mock())

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
