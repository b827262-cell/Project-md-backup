"""Database models and types for SecMon backend."""

from datetime import datetime

from pydantic import BaseModel


class AttackEvent(BaseModel):
    """Attack event from SSH logs."""

    event_key: str  # Changed to str for compatibility with event_key generation
    timestamp: str
    source_ip: str
    service: str
    username: str | None = None
    failure_reason: str
    created_at: str


class Attacker(BaseModel):
    """Attacker information from SSH logs."""

    ip_address: str
    attack_count: int
    first_seen: str
    last_seen: str
    created_at: str
    updated_at: str


class LogSource(BaseModel):
    """Log source configuration."""

    id: int
    name: str
    source_type: str
    source_path: str | None = None
    config_json: str | None = None
    enabled: int
    status: str
    last_event_at: str | None = None
    last_error: str | None = None
    events_today: int
    parse_errors_today: int
    created_at: str
    updated_at: str


class LogSourcesCreate(BaseModel):
    """Log source creation request."""

    name: str
    device_path: str
    parser_type: str
    status: str = "active"


class LogSourcesUpdate(BaseModel):
    """Log source update request."""

    name: Optional[str] = None
    device_path: Optional[str] = None
    parser_type: Optional[str] = None
    status: Optional[str] = None
