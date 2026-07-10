"""P1 canonical database models."""

from pydantic import BaseModel


class AttackEvent(BaseModel):
    event_key: str
    detected_at: str
    sensor_host: str = "localhost"
    source_id: int | None = None
    source_type: str = "file"
    src_ip: str
    src_port: int | None = None
    dst_ip: str | None = None
    dst_port: int | None = 22
    protocol: str = "tcp"
    attack_type: str
    severity: int = 3
    signature: str | None = None
    username: str | None = None
    raw_log: str | None = None
    metadata_json: str | None = None
    created_at: str

    @property
    def timestamp(self) -> str:
        return self.detected_at

    @property
    def source_ip(self) -> str:
        return self.src_ip

    @property
    def service(self) -> str:
        return "ssh"


class Attacker(BaseModel):
    src_ip: str
    first_seen: str
    last_seen: str
    total_events: int
    ssh_failures: int
    threat_score: int
    highest_severity: int
    last_attack_type: str | None
    status: str
    updated_at: str


class LogSource(BaseModel):
    id: int
    name: str
    source_type: str
    source_path: str | None = None
    config_json: str | None = None
    enabled: int = 1
    status: str
    last_event_at: str | None = None
    last_error: str | None = None
    events_today: int = 0
    parse_errors_today: int = 0
    created_at: str
    updated_at: str

    @property
    def device_path(self) -> str | None:
        return self.source_path

    @property
    def parser_type(self) -> str:
        return self.source_type


class LogSourcesCreate(BaseModel):
    name: str
    device_path: str
    parser_type: str
    status: str = "unknown"


class LogSourcesUpdate(BaseModel):
    name: str | None = None
    device_path: str | None = None
    parser_type: str | None = None
    status: str | None = None
