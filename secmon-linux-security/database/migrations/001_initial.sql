PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS log_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    source_path TEXT,
    config_json TEXT,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'unknown' CHECK (status IN ('unknown', 'healthy', 'warning', 'error', 'disabled')),
    last_event_at TEXT,
    last_error TEXT,
    events_today INTEGER NOT NULL DEFAULT 0,
    parse_errors_today INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attack_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_key TEXT NOT NULL UNIQUE,
    detected_at TEXT NOT NULL,
    sensor_host TEXT NOT NULL,
    source_id INTEGER REFERENCES log_sources(id) ON DELETE SET NULL,
    source_type TEXT NOT NULL,
    src_ip TEXT NOT NULL,
    src_port INTEGER CHECK (src_port IS NULL OR src_port BETWEEN 0 AND 65535),
    dst_ip TEXT,
    dst_port INTEGER CHECK (dst_port IS NULL OR dst_port BETWEEN 0 AND 65535),
    protocol TEXT,
    attack_type TEXT NOT NULL,
    severity INTEGER NOT NULL DEFAULT 3 CHECK (severity BETWEEN 1 AND 5),
    signature TEXT,
    username TEXT,
    raw_log TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attackers (
    src_ip TEXT PRIMARY KEY,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    total_events INTEGER NOT NULL DEFAULT 0,
    ssh_failures INTEGER NOT NULL DEFAULT 0,
    threat_score INTEGER NOT NULL DEFAULT 0,
    highest_severity INTEGER NOT NULL DEFAULT 5 CHECK (highest_severity BETWEEN 1 AND 5),
    last_attack_type TEXT,
    status TEXT NOT NULL DEFAULT 'observed' CHECK (status IN ('observed', 'high_risk', 'blocked', 'allowlisted')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'analyst', 'viewer')),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER REFERENCES attack_events(id) ON DELETE SET NULL,
    src_ip TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'acknowledged', 'investigating', 'resolved', 'ignored')),
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blocked_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_ip TEXT NOT NULL,
    reason TEXT NOT NULL,
    block_source TEXT NOT NULL DEFAULT 'manual' CHECK (block_source IN ('manual', 'auto', 'crowdsec', 'suricata')),
    blocked_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    blocked_at TEXT NOT NULL,
    expires_at TEXT,
    released_at TEXT,
    released_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    firewall_synced INTEGER NOT NULL DEFAULT 0 CHECK (firewall_synced IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_block ON blocked_ips(src_ip) WHERE active = 1;

CREATE TABLE IF NOT EXISTS ip_allowlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_or_cidr TEXT NOT NULL UNIQUE,
    description TEXT,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    target_type TEXT,
    target_value TEXT,
    old_value TEXT,
    new_value TEXT,
    client_ip TEXT,
    request_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_state (
    state_key TEXT PRIMARY KEY,
    state_value TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for attack_events
CREATE INDEX IF NOT EXISTS idx_attack_events_event_key ON attack_events(event_key);
CREATE INDEX IF NOT EXISTS idx_attack_events_detected_at ON attack_events(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_attack_events_src_ip ON attack_events(src_ip);
CREATE INDEX IF NOT EXISTS idx_attack_events_attack_type ON attack_events(attack_type);
CREATE INDEX IF NOT EXISTS idx_attack_events_username ON attack_events(username);
CREATE INDEX IF NOT EXISTS idx_attack_events_detected_src_ip ON attack_events(detected_at DESC, src_ip);
CREATE INDEX IF NOT EXISTS idx_attack_events_dedup ON attack_events(detected_at, src_ip, attack_type, username);

-- Indexes for attackers
CREATE INDEX IF NOT EXISTS idx_attackers_src_ip ON attackers(src_ip);
CREATE INDEX IF NOT EXISTS idx_attackers_total_events ON attackers(total_events DESC);
CREATE INDEX IF NOT EXISTS idx_attackers_first_seen ON attackers(first_seen ASC);
CREATE INDEX IF NOT EXISTS idx_attackers_last_seen ON attackers(last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_attackers_last_seen_count ON attackers(last_seen DESC, total_events DESC);

-- Other indexes
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('001_initial');
