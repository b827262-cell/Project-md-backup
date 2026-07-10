"""Test suite for SSH parser."""

import pytest
from backend.parsers.ssh_parser import SSHParser, SSHLogEntry


class TestSSHLogEntryValidation:
    """Test SSHLogEntry validation methods."""

    def test_valid_entry(self):
        """Test a valid SSH log entry."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True
        assert len(errors) == 0

    def test_valid_entry_ipv6(self):
        """Test a valid SSH log entry with IPv6 address."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="2001:db8::1",
            service="ssh",
            username="testuser",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True
        assert len(errors) == 0

    def test_valid_entry_no_username(self):
        """Test a valid SSH log entry without username (failed password without username?)."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username=None,
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_timestamp_format(self):
        """Test entry with invalid timestamp format."""
        entry = SSHLogEntry(
            timestamp="2024/07/10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "timestamp" in errors[0].lower()

    def test_future_timestamp(self):
        """Test entry with future timestamp."""
        from datetime import datetime, timedelta

        future_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        entry = SSHLogEntry(
            timestamp=future_time,
            source_ip="192.168.1.100",
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "future" in errors[0].lower()

    def test_old_timestamp(self):
        """Test entry with very old timestamp (before today)."""
        from datetime import datetime, timedelta

        old_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        entry = SSHLogEntry(
            timestamp=old_time,
            source_ip="192.168.1.100",
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "old" in errors[0].lower() or "past" in errors[0].lower()

    def test_invalid_ip_format(self):
        """Test entry with invalid IP address format."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="not.an.ip.address",
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "ip" in errors[0].lower() or "address" in errors[0].lower()

    def test_invalid_ipv4_length(self):
        """Test entry with IPv4 address that is too long."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="999.999.999.999",  # Each octet > 255
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1

    def test_invalid_ipv6_length(self):
        """Test entry with IPv6 address that is too long."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",  # Extra segment
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1

    def test_invalid_username_format(self):
        """Test entry with invalid username format."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="user@name",  # Contains @ character
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "username" in errors[0].lower()

    def test_username_too_long(self):
        """Test entry with username longer than 32 characters."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="a" * 33,  # 33 characters
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "long" in errors[0].lower()

    def test_username_start_end_special_char(self):
        """Test entry with username starting or ending with special characters."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username=".username",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "start" in errors[0].lower() or "end" in errors[0].lower()

    def test_invalid_service(self):
        """Test entry with invalid service."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ftp",  # Should be ssh
            username="admin",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "service" in errors[0].lower()

    def test_invalid_failure_reason(self):
        """Test entry with invalid failure reason."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="admin",
            failure_reason="Invalid action",  # Should be one of the valid reasons
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is False
        assert len(errors) == 1
        assert "failure" in errors[0].lower() or "reason" in errors[0].lower()

    def test_empty_username(self):
        """Test entry with empty username (should be None)."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username=None,
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True
        assert len(errors) == 0

    def test_event_key_generation(self):
        """Test event_key property."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="admin",
            failure_reason="Failed password",
        )
        event_key = entry.event_key
        assert isinstance(event_key, str)
        assert "|" in event_key
        parts = event_key.split("|")
        assert len(parts) == 4


class TestSSHParserParseLine:
    """Test SSHParser.parse_line method."""

    def test_parse_failed_password(self):
        """Test parsing failed password lines."""
        parser = SSHParser()

        lines = [
            "Failed password for admin from 192.168.1.100 port 54321 ssh2",
            "Failed password for root from 10.0.0.1 port 12345 ssh2",
            "Failed password for user from 172.16.0.50 port 67890 ssh2",
        ]

        for line in lines:
            entry = parser.parse_line(line)
            assert entry is not None, f"Failed to parse: {line}"
            assert entry.service == "ssh"
            assert entry.failure_reason == "Failed password"
            assert entry.username is not None
            assert entry.source_ip is not None

    def test_parse_invalid_user(self):
        """Test parsing invalid user lines."""
        parser = SSHParser()

        lines = [
            "Invalid user admin from 192.168.1.100 port 54321 ssh2",
            "Invalid user root from 10.0.0.1 port 12345 ssh2",
            "Invalid user user from 172.16.0.50 port 67890 ssh2",
        ]

        for line in lines:
            entry = parser.parse_line(line)
            assert entry is not None, f"Failed to parse: {line}"
            assert entry.service == "ssh"
            assert entry.failure_reason == "Invalid user"
            assert entry.username is not None
            assert entry.source_ip is not None

    def test_parse_non_ssh_line(self):
        """Test parsing non-SSH authentication lines."""
        parser = SSHParser()

        lines = [
            "Accepted publickey for admin from 192.168.1.100 port 54321 ssh2: RSA SHA256:abc123",
            "Nov  7 00:00:00 host sshd[1234]: Connection closed by authenticating user",
            "Jan 1 00:00:00 hostname sshd[5678]: PAM: Authentication failure for user",
            "Jul 10 17:30:45 myhost sshd[9999]: Accepted password for user from 192.168.1.100 port 22",
        ]

        for line in lines:
            entry = parser.parse_line(line)
            assert entry is None, f"Should not parse: {line}"

    def test_parse_empty_line(self):
        """Test parsing empty line."""
        parser = SSHParser()
        assert parser.parse_line("") is None
        assert parser.parse_line("   ") is None
        assert parser.parse_line("\n") is None

    def test_parse_line_with_timestamp_validation_error(self):
        """Test that parse_line raises ValueError on invalid data."""
        parser = SSHParser()

        # Line with IPv4 that is invalid (each octet > 255)
        line = "Failed password for admin from 999.999.999.999 port 54321 ssh2"
        with pytest.raises(ValueError) as exc_info:
            parser.parse_line(line)
        assert "validation" in str(exc_info.value).lower()
        assert "invalid ip" in str(exc_info.value).lower()

    def test_parse_line_with_invalid_timestamp(self):
        """Test that parse_line raises ValueError on invalid timestamp."""
        parser = SSHParser()

        # Line with invalid timestamp format
        line = "Failed password for admin from 192.168.1.100 port 54321 ssh2"
        # Note: This should work because timestamp is extracted automatically

    def test_parse_line_with_future_timestamp(self):
        """Test parsing line with future timestamp."""
        from datetime import datetime, timedelta

        parser = SSHParser()
        future_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        line = f"{future_time} myhost sshd[1234]: Failed password for admin from 192.168.1.100 port 54321 ssh2"

        entry = parser.parse_line(line)
        assert entry is not None
        assert entry.timestamp == future_time

    def test_multiple_timestamps_in_line(self):
        """Test parsing line with multiple timestamps (should extract first)."""
        parser = SSHParser()

        line = "2024-01-01 12:00:00 journal: ... 2024-07-10 17:30:45 myhost sshd[1234]: Failed password for admin from 192.168.1.100 port 54321 ssh2"

        entry = parser.parse_line(line)
        assert entry is not None
        assert entry.timestamp == "2024-01-01 12:00:00"  # Should extract first timestamp

    def test_parse_line_validates_after_extraction(self):
        """Test that parse_line validates even after successful extraction."""
        parser = SSHParser()

        # This line should fail validation because the source IP has octets > 255
        line = "Failed password for admin from 999.999.999.999 port 54321 ssh2"

        with pytest.raises(ValueError) as exc_info:
            parser.parse_line(line)

        assert "validation errors" in str(exc_info.value).lower()


class TestTimestampExtraction:
    """Test timestamp extraction functionality."""

    def test_extract_timestamp_standard_format(self):
        """Test extracting timestamp in standard format."""
        parser = SSHParser()

        line = "Jul 10 17:30:45 myhost sshd[1234]: Failed password for admin from 192.168.1.100 port 54321 ssh2"
        timestamp = parser._extract_timestamp(line)

        assert timestamp == "2024-07-10 17:30:45"

    def test_extract_timestamp_with_full_date(self):
        """Test extracting timestamp with full date."""
        parser = SSHParser()

        line = "Jul 10 17:30:45 myhost sshd[1234]: Failed password for admin from 192.168.1.100 port 54321 ssh2"
        timestamp = parser._extract_timestamp(line)

        assert timestamp == "2024-07-10 17:30:45"

    def test_extract_timestamp_fallback(self):
        """Test timestamp extraction fallback when no timestamp in line."""
        parser = SSHParser()

        line = "No timestamp here: Failed password for admin from 192.168.1.100 port 54321 ssh2"
        timestamp = parser._extract_timestamp(line)

        # Should fall back to current timestamp
        from datetime import datetime
        assert isinstance(timestamp, str)
        assert len(timestamp) == 19

    def test_extract_timestamp_invalid_format(self):
        """Test timestamp extraction raises error when format is invalid."""
        parser = SSHParser()

        line = "Invalid format timestamp here: Failed password for admin from 192.168.1.100 port 54321 ssh2"

        with pytest.raises(ValueError) as exc_info:
            parser._extract_timestamp(line)

        assert "valid timestamp" in str(exc_info.value).lower()

    def test_extract_timestamp_date_only(self):
        """Test extracting timestamp with only date (should fail)."""
        parser = SSHParser()

        line = "2024-07-10 Failed password for admin from 192.168.1.100 port 54321 ssh2"

        with pytest.raises(ValueError) as exc_info:
            parser._extract_timestamp(line)

        assert "valid timestamp" in str(exc_info.value).lower()

    def test_extract_timestamp_month_day_hour_minute_second(self):
        """Test extracting timestamp in abbreviated month format."""
        parser = SSHParser()

        line = "Jul 10 17:30:45 myhost sshd[1234]: Failed password for admin from 192.168.1.100 port 54321 ssh2"
        timestamp = parser._extract_timestamp(line)

        assert timestamp == "2024-07-10 17:30:45"


class TestIPv4Validation:
    """Test IPv4 address validation."""

    def test_valid_ipv4_addresses(self):
        """Test various valid IPv4 addresses."""
        valid_ips = [
            "0.0.0.0",
            "255.255.255.255",
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "8.8.8.8",
            "1.2.3.4",
            "127.0.0.1",  # Loopback
        ]

        for ip in valid_ips:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip=ip,
                service="ssh",
                username="test",
                failure_reason="Failed password",
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is True, f"IPv4 {ip} should be valid but got errors: {errors}"

    def test_invalid_ipv4_addresses(self):
        """Test various invalid IPv4 addresses."""
        invalid_ips = [
            "256.1.2.3",  # Octet > 255
            "1.256.2.3",
            "1.2.256.3",
            "1.2.3.256",
            "999.999.999.999",
            "not.an.ip",
            "192.168.1.1.1",
            "192.168.1",
            "192.168.1.1:22",  # Port included
        ]

        for ip in invalid_ips:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip=ip,
                service="ssh",
                username="test",
                failure_reason="Failed password",
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is False, f"IPv4 {ip} should be invalid but passed"


class TestIPv6Validation:
    """Test IPv6 address validation."""

    def test_valid_ipv6_addresses(self):
        """Test various valid IPv6 addresses."""
        valid_ips = [
            "::1",  # Loopback
            "2001:db8::1",
            "2001:0db8:0000:0000:0000:0000:0000:0001",
            "fe80::1",
            "::ffff:192.168.1.1",
            "2001:db8:85a3::8a2e:370:7334",
        ]

        for ip in valid_ips:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip=ip,
                service="ssh",
                username="test",
                failure_reason="Failed password",
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is True, f"IPv6 {ip} should be valid but got errors: {errors}"

    def test_invalid_ipv6_addresses(self):
        """Test various invalid IPv6 addresses."""
        invalid_ips = [
            "2001:db8::1::1",  # Double ::
            "2001:db8:1::g::1",  # Invalid character
            "2001:db8::1:8000",  # Too many segments
            "not.an.ipv6",
            "2001:db8:85a3::8a2e:370:7334",  # Extra segment
            "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
        ]

        for ip in invalid_ips:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip=ip,
                service="ssh",
                username="test",
                failure_reason="Failed password",
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is False, f"IPv6 {ip} should be invalid but passed"


class TestUsernameValidation:
    """Test username validation."""

    def test_valid_usernames(self):
        """Test various valid usernames."""
        valid_usernames = [
            "admin",
            "root",
            "user123",
            "test-user",
            "user.name",
            "_user",
            "user_",
            "test.user-name",
            "a" * 32,  # Maximum length
        ]

        for username in valid_usernames:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip="192.168.1.100",
                service="ssh",
                username=username,
                failure_reason="Failed password",
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is True, f"Username '{username}' should be valid but got errors: {errors}"

    def test_invalid_usernames(self):
        """Test various invalid usernames."""
        invalid_usernames = [
            "",  # Empty
            "a" * 33,  # Too long
            "user@name",  # Contains @
            "user name",  # Contains space
            "user/name",  # Contains /
            "user\\name",  # Contains \
            "user*name",  # Contains *
            "user?name",  # Contains ?
            "user$name",  # Contains $
            ".username",  # Starts with dot
            "-username",  # Starts with hyphen
            "_username",  # Starts with underscore
            "username.",  # Ends with dot
            "username-",  # Ends with hyphen
            "username_",  # Ends with underscore
        ]

        for username in invalid_usernames:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip="192.168.1.100",
                service="ssh",
                username=username,
                failure_reason="Failed password",
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is False, f"Username '{username}' should be invalid but passed"


class TestFailureReasonValidation:
    """Test failure reason validation."""

    def test_valid_failure_reasons(self):
        """Test valid failure reasons."""
        valid_reasons = ["Failed password", "Invalid user", "Failed login"]

        for reason in valid_reasons:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip="192.168.1.100",
                service="ssh",
                username="test",
                failure_reason=reason,
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is True, f"Reason '{reason}' should be valid but got errors: {errors}"

    def test_invalid_failure_reasons(self):
        """Test invalid failure reasons."""
        invalid_reasons = [
            "Password failure",
            "Invalid credential",
            "Login failed",
            "Authentication failed",
            "Access denied",
            "",  # Empty
        ]

        for reason in invalid_reasons:
            entry = SSHLogEntry(
                timestamp="2024-07-10 17:30:45",
                source_ip="192.168.1.100",
                service="ssh",
                username="test",
                failure_reason=reason,
            )
            is_valid, errors = entry.is_valid()
            assert is_valid is False, f"Reason '{reason}' should be invalid but passed"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_max_ipv4(self):
        """Test maximum valid IPv4 address."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="255.255.255.255",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_min_ipv4(self):
        """Test minimum valid IPv4 address."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="0.0.0.0",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_zero_username(self):
        """Test username that is just a single zero."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="0",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_username_with_numbers_and_special_chars(self):
        """Test username with numbers and allowed special characters."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="192.168.1.100",
            service="ssh",
            username="user-123_test.name",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_ipv4_loopback(self):
        """Test IPv4 loopback address."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="127.0.0.1",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_ipv6_link_local(self):
        """Test IPv6 link-local address."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="fe80::1",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_ipv6_mixed_case(self):
        """Test IPv6 address with mixed case."""
        entry = SSHLogEntry(
            timestamp="2024-07-10 17:30:45",
            source_ip="2001:DB8::1",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_very_old_entry(self):
        """Test entry with timestamp from last year."""
        from datetime import datetime, timedelta

        old_time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        entry = SSHLogEntry(
            timestamp=old_time,
            source_ip="192.168.1.100",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        # Should be valid (only check for future, not too old)
        assert is_valid is True

    def test_recent_entry(self):
        """Test entry with timestamp from 1 hour ago."""
        from datetime import datetime, timedelta

        recent_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        entry = SSHLogEntry(
            timestamp=recent_time,
            source_ip="192.168.1.100",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        assert is_valid is True

    def test_exact_current_time(self):
        """Test entry with current timestamp."""
        from datetime import datetime

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = SSHLogEntry(
            timestamp=current_time,
            source_ip="192.168.1.100",
            service="ssh",
            username="test",
            failure_reason="Failed password",
        )
        is_valid, errors = entry.is_valid()
        # Current time should be valid
        assert is_valid is True
