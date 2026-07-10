"""SSH log parser for parsing authentication events."""

import ipaddress
import re
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SSHLogEntry:
    """Represents a parsed SSH log entry."""

    timestamp: str
    source_ip: str
    service: str
    username: str | None
    failure_reason: str

    @property
    def event_key(self) -> str:
        """Generate unique event key for deduplication."""
        return f"{self.timestamp}|{self.source_ip}|{self.service}|{self.username or ''}"

    def is_valid(self) -> tuple[bool, list[str]]:
        """
        Validate the SSH log entry fields.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        # Validate timestamp format
        timestamp_error = self._validate_timestamp()
        if timestamp_error:
            errors.append(timestamp_error)

        # Validate source IP
        ip_error = self._validate_source_ip()
        if ip_error:
            errors.append(ip_error)

        # Validate service (if not SSH)
        if self.service and self.service.lower() != "ssh":
            errors.append(f"Service must be 'ssh', got '{self.service}'")

        # Validate username (if provided)
        if self.username is not None:
            username_error = self._validate_username()
            if username_error:
                errors.append(username_error)

        # Validate failure reason
        failure_error = self._validate_failure_reason()
        if failure_error:
            errors.append(failure_error)

        return (len(errors) == 0, errors)

    def _validate_timestamp(self) -> str | None:
        """Validate timestamp format is YYYY-MM-DD HH:MM:SS."""
        if not self.timestamp:
            return "Timestamp is empty"

        try:
            # Parse timestamp
            parsed = datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S")
            # Verify it can be converted back to the same format
            reconstructed = parsed.strftime("%Y-%m-%d %H:%M:%S")
            if reconstructed != self.timestamp:
                return f"Timestamp format mismatch: {self.timestamp}"
        except ValueError as e:
            return f"Invalid timestamp format '{self.timestamp}': {str(e)}"

        # Check maximum timestamp (future timestamps, allow up to 2 hours clock drift)
        max_time = datetime.now() + timedelta(hours=2)
        if parsed > max_time:
            return f"Timestamp is in the future: {self.timestamp}"

        return None

    def _validate_source_ip(self) -> str | None:
        """Validate source IP format (IPv4 or IPv6)."""
        if not self.source_ip:
            return "Source IP is empty"

        try:
            # Try parsing as IPv4
            ipaddress.IPv4Address(self.source_ip)
            if len(self.source_ip) > 15:  # Max IPv4 length: "255.255.255.255"
                return f"IPv4 address too long: {self.source_ip}"
            return None
        except ipaddress.AddressValueError:
            pass

        try:
            # Try parsing as IPv6
            ipaddress.IPv6Address(self.source_ip)
            # Max IPv6 length: "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
            if len(self.source_ip) > 45:
                return f"IPv6 address too long: {self.source_ip}"
            return None
        except ipaddress.AddressValueError:
            return f"Invalid IP address format: {self.source_ip}"

    def _validate_username(self) -> str | None:
        """Validate username format."""
        if self.username is None:
            return None

        # Username must be non-empty
        if len(self.username) == 0:
            return "Username is empty"

        # Username must be between 1-32 characters
        if len(self.username) > 32:
            return f"Username too long (max 32): {self.username}"

        # Username must match allowed characters (alphanumeric, dot, hyphen, underscore)
        # RFC 4342 and common SSH implementations
        if not re.match(r"^[a-zA-Z0-9._-]+$", self.username):
            return f"Username contains invalid characters: {self.username}"

        # Username must not start/end with dot or hyphen
        if self.username[0] in ['.', '-'] or self.username[-1] in ['.', '-']:
            return f"Username cannot start or end with dot or hyphen: {self.username}"

        return None

    def _validate_failure_reason(self) -> str | None:
        """Validate failure reason format."""
        if not self.failure_reason:
            return "Failure reason is empty"

        # Valid failure reasons
        valid_reasons = ["Failed password", "Invalid user", "Failed login"]
        if self.failure_reason not in valid_reasons:
            valid_list = ", ".join(valid_reasons)
            return f"Invalid failure reason '{self.failure_reason}'. Valid values: {valid_list}"

        return None


class SSHParser:
    """Parser for SSH authentication logs."""

    # Pattern for failed password attempts
    PATTERN_FAILED_PASSWORD = re.compile(
        r"Failed password for (\S+) from (\S+) port \d+ ssh2"
    )

    # Pattern for invalid user attempts
    PATTERN_INVALID_USER = re.compile(r"Invalid user (\S+) from (\S+) port \d+ ssh2")

    def parse_line(self, line: str) -> SSHLogEntry | None:
        """
        Parse a single SSH log line.

        Args:
            line: Raw log line from auth.log

        Returns:
            SSHLogEntry if line is an authentication failure, None otherwise.

        Raises:
            ValueError: If the line contains a valid SSH log entry but has invalid fields.
        """
        if not line or not line.strip():
            return None

        # Try failed password pattern
        match = self.PATTERN_FAILED_PASSWORD.search(line)
        if match:
            username = match.group(1)
            source_ip = match.group(2)
            entry = SSHLogEntry(
                timestamp=self._extract_timestamp(line),
                source_ip=source_ip,
                service="ssh",
                username=username,
                failure_reason="Failed password",
            )
            return self._validate_and_return(entry, line)

        # Try invalid user pattern
        match = self.PATTERN_INVALID_USER.search(line)
        if match:
            username = match.group(1)
            source_ip = match.group(2)
            entry = SSHLogEntry(
                timestamp=self._extract_timestamp(line),
                source_ip=source_ip,
                service="ssh",
                username=username,
                failure_reason="Invalid user",
            )
            return self._validate_and_return(entry, line)

        # Not an SSH authentication failure line
        return None

    def _validate_and_return(self, entry: SSHLogEntry, line: str) -> SSHLogEntry:
        """
        Validate an SSH log entry and return it or raise an error.

        Args:
            entry: Parsed SSH log entry
            line: Original log line for error messages

        Returns:
            Validated SSHLogEntry

        Raises:
            ValueError: If the entry contains invalid data.
        """
        is_valid, errors = entry.is_valid()

        if not is_valid:
            error_msg = f"SSH log line '{line.strip()}' has validation errors: {'; '.join(errors)}"
            raise ValueError(error_msg)

        return entry

    def _extract_timestamp(self, line: str) -> str:
        """
        Extract timestamp from log line.

        Expected format: YYYY-MM-DD HH:MM:SS

        Args:
            line: Raw log line

        Returns:
            Extracted timestamp in YYYY-MM-DD HH:MM:SS format.

        Raises:
            ValueError: If no valid timestamp can be extracted.
        """
        from datetime import datetime

        # 1. Try to extract first timestamp in the line (first group of digits)
        match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", line)
        if match:
            return match.group(1)

        # 2. Try to extract syslog style timestamp
        syslog_match = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})", line)
        if syslog_match:
            month = datetime.strptime(syslog_match.group(1), "%b").month
            timestamp = (
                f"{datetime.now().year}-{month:02d}-{int(syslog_match.group(2)):02d} "
                f"{syslog_match.group(3)}"
            )
            return timestamp

        # 3. If there is a date pattern but not a full timestamp, raise ValueError
        if (re.search(r"\d{4}-\d{2}-\d{2}", line) or
                re.search(r"[A-Z][a-z]{2}\s+\d{1,2}", line)):
            raise ValueError(
                "SSH log line has no supported timestamp; provide an ISO timestamp "
                "or normalize the journal timestamp before parsing"
            )

        # 4. Fallback to current time if the line starts with known SSH failure patterns
        clean_line = line.strip()
        if re.match(r"^(?:sshd\[\d+\]:\s+)?(?:Failed password|Invalid user)", clean_line):
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        raise ValueError(
            "SSH log line has no supported timestamp; provide an ISO timestamp "
            "or normalize the journal timestamp before parsing"
        )
