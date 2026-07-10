"""Tests for log sources management service using P1 canonical schema."""

import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from backend.services.log_sources import LogSourcesService


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        # Run initial migration
        migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
        from database.migrate import migrate

        migrate(db_path, migrations_dir)
        yield db_path


def test_create_log_source(temp_db):
    """Test creating a new log source."""
    service = LogSourcesService(temp_db)

    log_source_id = service.create_log_source(
        name="Test SSH",
        device_path="/var/log/test.log",
        parser_type="ssh",
        status="active",
    )

    assert log_source_id > 0

    log_source = service.get_log_source(log_source_id)
    assert log_source is not None
    assert log_source.name == "Test SSH"
    assert log_source.source_path == "/var/log/test.log"
    assert log_source.source_type == "ssh"
    assert log_source.status == "healthy"


def test_get_log_source_by_name(temp_db):
    """Test getting a log source by name."""
    service = LogSourcesService(temp_db)

    service.create_log_source(
        name="Test Logs",
        device_path="/var/log/test.log",
        parser_type="syslog",
        status="active",
    )

    log_source = service.get_log_source_by_name("Test Logs")
    assert log_source is not None
    assert log_source.name == "Test Logs"


def test_get_nonexistent_log_source(temp_db):
    """Test getting a nonexistent log source."""
    service = LogSourcesService(temp_db)

    log_source = service.get_log_source(999)
    assert log_source is None

    log_source = service.get_log_source_by_name("Nonexistent")
    assert log_source is None


def test_get_all_log_sources(temp_db):
    """Test getting all log sources."""
    service = LogSourcesService(temp_db)

    # Empty the default log sources first
    with sqlite3.connect(temp_db) as conn:
        conn.execute("DELETE FROM log_sources")

    service.create_log_source("SSH", "/var/log/auth.log", "ssh", "active")
    service.create_log_source("Secure", "/var/log/secure", "syslog", "inactive")

    sources = service.get_all_log_sources()
    assert len(sources) >= 2

    names = {source.name for source in sources}
    assert "SSH" in names
    assert "Secure" in names


def test_update_log_source(temp_db):
    """Test updating a log source."""
    service = LogSourcesService(temp_db)

    log_source_id = service.create_log_source(
        name="Original",
        device_path="/var/log/old.log",
        parser_type="old_parser",
        status="inactive",
    )

    # Update the log source
    updated = service.update_log_source(
        log_source_id, name="Updated", status="active"
    )
    assert updated is True

    # Verify the changes
    log_source = service.get_log_source(log_source_id)
    assert log_source.name == "Updated"
    assert log_source.status == "healthy"
    assert log_source.source_path == "/var/log/old.log"  # Should not change


def test_update_log_source_with_partial_data(temp_db):
    """Test updating a log source with partial data."""
    service = LogSourcesService(temp_db)

    log_source_id = service.create_log_source(
        name="Original",
        device_path="/var/log/old.log",
        parser_type="old_parser",
        status="inactive",
    )

    # Only update the device_path
    service.update_log_source(log_source_id, device_path="/var/log/new.log")

    log_source = service.get_log_source(log_source_id)
    assert log_source.name == "Original"  # Should remain unchanged
    assert log_source.source_path == "/var/log/new.log"
    assert log_source.status == "disabled"  # mapped from inactive


def test_delete_log_source(temp_db):
    """Test deleting a log source."""
    service = LogSourcesService(temp_db)

    log_source_id = service.create_log_source(
        name="ToDelete",
        device_path="/var/log/test.log",
        parser_type="ssh",
        status="active",
    )

    deleted = service.delete_log_source(log_source_id)
    assert deleted is True

    # Verify deletion
    log_source = service.get_log_source(log_source_id)
    assert log_source is None

    sources = service.get_all_log_sources()
    names = {source.name for source in sources}
    assert "ToDelete" not in names


def test_set_last_scanned(temp_db):
    """Test updating the last scanned timestamp."""
    service = LogSourcesService(temp_db)

    log_source_id = service.create_log_source(
        name="Test",
        device_path="/var/log/test.log",
        parser_type="ssh",
        status="active",
    )

    test_time = datetime(2024, 1, 1, 12, 30, 45)
    updated = service.set_last_scanned(log_source_id, test_time)

    assert updated is True

    log_source = service.get_log_source(log_source_id)
    assert log_source.last_event_at is not None
    assert log_source.last_event_at == test_time.isoformat()


def test_duplicate_name_prevents_creation(temp_db):
    """Test that creating a log source with an existing name fails."""
    service = LogSourcesService(temp_db)

    service.create_log_source(
        name="UniqueName",
        device_path="/var/log/first.log",
        parser_type="ssh",
    )

    # Try to create another with the same name
    with pytest.raises(RuntimeError):
        service.create_log_source(
            name="UniqueName",
            device_path="/var/log/second.log",
            parser_type="syslog",
        )


def test_ensure_default_log_sources(temp_db):
    """Test ensuring default log sources exist."""
    service = LogSourcesService(temp_db)

    # Empty the default log sources first
    with sqlite3.connect(temp_db) as conn:
        conn.execute("DELETE FROM log_sources")

    # Initially, no default sources should exist
    sources = service.get_all_log_sources()
    assert len(sources) == 0

    # Ensure defaults are created
    service.ensure_default_log_sources_exist()

    # Now we should have the default sources
    sources = service.get_all_log_sources()
    assert len(sources) >= 3

    names = {source.name for source in sources}
    assert "SSH Journal" in names
    assert "Privileged Logs" in names
    assert "Secure Logs" in names


def test_default_log_sources_ids(temp_db):
    """Test that default log sources have the expected IDs."""
    service = LogSourcesService(temp_db)

    service.ensure_default_log_sources_exist()

    sources = service.get_all_log_sources()

    # Find the default sources by name and check their IDs
    ssh_journal = next((s for s in sources if s.name == "SSH Journal"), None)
    privileged = next((s for s in sources if s.name == "Privileged Logs"), None)
    secure = next((s for s in sources if s.name == "Secure Logs"), None)

    assert ssh_journal is not None
    assert privileged is not None
    assert secure is not None

    # Check that they have the expected properties
    assert ssh_journal.source_path == "/var/log/auth.log"
    assert ssh_journal.source_type == "file"
    assert privileged.source_path == "/var/log/authpriv.log"
    assert privileged.source_type == "file"
    assert secure.source_path == "/var/log/secure"
    assert secure.source_type == "file"


def test_get_default_log_sources(temp_db):
    """Test getting default log sources without creating them."""
    service = LogSourcesService(temp_db)

    defaults = service.get_default_log_sources()

    assert len(defaults) == 3

    names = {source.name for source in defaults}
    assert "SSH Journal" in names
    assert "Privileged Logs" in names
    assert "Secure Logs" in names

    # Verify device paths
    for source in defaults:
        assert source.source_path is not None
        assert len(source.source_path) > 0
