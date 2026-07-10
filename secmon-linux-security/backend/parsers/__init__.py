"""Log parser package for SecMon backend."""

from .ssh_parser import SSHLogEntry, SSHParser

__all__ = ["SSHParser", "SSHLogEntry"]
