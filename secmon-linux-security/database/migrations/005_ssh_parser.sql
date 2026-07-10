-- Migration: 005_ssh_parser
-- Description: Create SSH log parser configuration and tracking table
-- Date: 2026-07-10

-- Create SSH parser configuration table
CREATE TABLE IF NOT EXISTS ssh_parser_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL UNIQUE REFERENCES log_sources(id) ON DELETE CASCADE,
    parser_name TEXT NOT NULL DEFAULT 'ssh_parser',
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    last_parsed_at TEXT,
    parse_errors_today INTEGER NOT NULL DEFAULT 0,
    success_count_today INTEGER NOT NULL DEFAULT 0,
    total_events_parsed INTEGER NOT NULL DEFAULT 0,
    average_parse_time_ms INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_error TEXT,
    config_json TEXT
);

-- Create SSH-specific indexes
-- Index on source_id for efficient lookups
CREATE INDEX IF NOT EXISTS idx_ssh_parser_config_source_id ON ssh_parser_config(source_id);

-- Index on enabled status for filtering
CREATE INDEX IF NOT EXISTS idx_ssh_parser_config_enabled ON ssh_parser_config(enabled);

-- Index on last_parsed_at for maintenance queries
CREATE INDEX IF NOT EXISTS idx_ssh_parser_config_last_parsed_at ON ssh_parser_config(last_parsed_at);

-- Index on last_error for troubleshooting
CREATE INDEX IF NOT EXISTS idx_ssh_parser_config_last_error ON ssh_parser_config(last_error);

-- Composite index for monitoring queries (enabled + last_parsed_at)
CREATE INDEX IF NOT EXISTS idx_ssh_parser_config_enabled_parsed ON ssh_parser_config(enabled, last_parsed_at);

-- Create SSH parser statistics table for detailed tracking
CREATE TABLE IF NOT EXISTS ssh_parser_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_lines INTEGER NOT NULL DEFAULT 0,
    successful_parses INTEGER NOT NULL DEFAULT 0,
    failed_parses INTEGER NOT NULL DEFAULT 0,
    total_events INTEGER NOT NULL DEFAULT 0,
    unique_ssh_users INTEGER NOT NULL DEFAULT 0,
    total_connections INTEGER NOT NULL DEFAULT 0,
    authentication_failures INTEGER NOT NULL DEFAULT 0,
    successful_authentications INTEGER NOT NULL DEFAULT 0,
    parsing_errors INTEGER NOT NULL DEFAULT 0,
    avg_parse_time_ms INTEGER NOT NULL DEFAULT 0,
    peak_concurrent INTEGER NOT NULL DEFAULT 0,
    total_lines_scanned INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index on date for time-series queries
CREATE INDEX IF NOT EXISTS idx_ssh_parser_stats_date ON ssh_parser_stats(date DESC);

-- Index on success/failure counts for analysis
CREATE INDEX IF NOT EXISTS idx_ssh_parser_stats_success_rate ON ssh_parser_stats(successful_parses, failed_parses);

-- Index on authentication metrics for threat detection
CREATE INDEX IF NOT EXISTS idx_ssh_parser_stats_auth ON ssh_parser_stats(authentication_failures, successful_authentications);

-- Index on events for volume tracking
CREATE INDEX IF NOT EXISTS idx_ssh_parser_stats_events ON ssh_parser_stats(total_events);

-- Create SSH parsing errors table for detailed error tracking
CREATE TABLE IF NOT EXISTS ssh_parsing_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES log_sources(id) ON DELETE CASCADE,
    error_code TEXT NOT NULL,
    error_message TEXT NOT NULL,
    log_line TEXT,
    occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER NOT NULL DEFAULT 0,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0 CHECK (resolved IN (0, 1)),
    resolved_at TEXT,
    resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Index on source_id for source-specific error tracking
CREATE INDEX IF NOT EXISTS idx_ssh_parsing_errors_source_id ON ssh_parsing_errors(source_id);

-- Index on error_code for pattern-based error tracking
CREATE INDEX IF NOT EXISTS idx_ssh_parsing_errors_error_code ON ssh_parsing_errors(error_code);

-- Index on resolved status for issue prioritization
CREATE INDEX IF NOT EXISTS idx_ssh_parsing_errors_resolved ON ssh_parsing_errors(resolved);

-- Index on occurred_at for temporal analysis
CREATE INDEX IF NOT EXISTS idx_ssh_parsing_errors_occurred_at ON ssh_parsing_errors(occurred_at DESC);

-- Index on first_seen for issue tracking
CREATE INDEX IF NOT EXISTS idx_ssh_parsing_errors_first_seen ON ssh_parsing_errors(first_seen DESC);

-- Index on retry_count for prioritizing unresolvable errors
CREATE INDEX IF NOT EXISTS idx_ssh_parsing_errors_retry_count ON ssh_parsing_errors(retry_count DESC);

-- Create SSH connection events table (parsed SSH logs)
CREATE TABLE IF NOT EXISTS ssh_connection_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES log_sources(id) ON DELETE CASCADE,
    event_uuid TEXT NOT NULL UNIQUE,
    parsed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_timestamp TEXT NOT NULL,
    ssh_version TEXT,
    protocol_version TEXT,
    protocol TEXT,
    auth_method TEXT NOT NULL,
    auth_result TEXT NOT NULL,
    user TEXT NOT NULL,
    src_ip TEXT NOT NULL,
    src_port INTEGER CHECK (src_port IS NULL OR src_port BETWEEN 0 AND 65535),
    dst_ip TEXT,
    dst_port INTEGER CHECK (dst_port IS NULL OR dst_port BETWEEN 0 AND 65535),
    session_id TEXT,
    ssh_msg_type TEXT,
    error_message TEXT,
    raw_log TEXT,
    severity INTEGER NOT NULL DEFAULT 3 CHECK (severity BETWEEN 1 AND 5),
    is_duplicate INTEGER NOT NULL DEFAULT 0 CHECK (is_duplicate IN (0, 1)),
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index on event_uuid for unique event lookups
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_uuid ON ssh_connection_events(event_uuid);

-- Index on parsed_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_parsed_at ON ssh_connection_events(parsed_at DESC);

-- Index on log_timestamp for log correlation
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_log_timestamp ON ssh_connection_events(log_timestamp DESC);

-- Index on source_id for source-specific queries
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_source_id ON ssh_connection_events(source_id);

-- Index on user for user-based analysis
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_user ON ssh_connection_events(user);

-- Index on src_ip for IP-based threat analysis
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_src_ip ON ssh_connection_events(src_ip);

-- Index on auth_method for authentication pattern analysis
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_auth_method ON ssh_connection_events(auth_method);

-- Index on auth_result for success/failure analysis
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_auth_result ON ssh_connection_events(auth_result);

-- Index on severity for priority-based alerts
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_severity ON ssh_connection_events(severity);

-- Index on protocol for protocol-based analysis
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_protocol ON ssh_connection_events(protocol);

-- Index on is_duplicate for deduplication queries
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_is_duplicate ON ssh_connection_events(is_duplicate);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_parsed_user ON ssh_connection_events(parsed_at DESC, user);
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_parsed_ip ON ssh_connection_events(parsed_at DESC, src_ip);
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_auth_result_severity ON ssh_connection_events(auth_result, severity);
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_user_src_ip ON ssh_connection_events(user, src_ip);
CREATE INDEX IF NOT EXISTS idx_ssh_connection_events_src_ip_parsed ON ssh_connection_events(src_ip, parsed_at DESC);

-- Create trigger for updating updated_at timestamp on ssh_parser_config
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_config_updated_at
AFTER UPDATE ON ssh_parser_config
FOR EACH ROW
BEGIN
    UPDATE ssh_parser_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create trigger for updating ssh_parser_stats on daily aggregation
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_stats_update
AFTER INSERT ON ssh_connection_events
BEGIN
    INSERT OR REPLACE INTO ssh_parser_stats (
        date,
        total_lines,
        successful_parses,
        total_events,
        unique_ssh_users,
        total_connections
    )
    SELECT
        DATE(NEW.parsed_at),
        0,
        0,
        0,
        0,
        0
    WHERE NOT EXISTS (
        SELECT 1 FROM ssh_parser_stats WHERE date = DATE(NEW.parsed_at)
    );
END;

-- Create trigger for updating SSH parser configuration metrics
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_config_update_metrics
AFTER INSERT ON ssh_connection_events
BEGIN
    UPDATE ssh_parser_config
    SET
        total_events_parsed = total_events_parsed + 1,
        success_count_today = success_count_today + 1,
        last_parsed_at = NEW.parsed_at,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.source_id;
END;

-- Create trigger for updating SSH parser configuration on parse errors
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_config_error
AFTER INSERT ON ssh_parsing_errors
BEGIN
    UPDATE ssh_parser_config
    SET
        parse_errors_today = parse_errors_today + 1,
        last_error = NEW.error_message,
        updated_at = CURRENT_TIMESTAMP
    WHERE source_id = NEW.source_id;
END;

-- Create trigger for updating SSH parser stats on parse success
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_stats_success
AFTER INSERT ON ssh_connection_events
BEGIN
    UPDATE ssh_parser_stats
    SET
        successful_parses = successful_parses + 1,
        total_events = total_events + 1,
        unique_ssh_users = CASE
            WHEN NOT EXISTS (
                SELECT 1 FROM ssh_connection_events
                WHERE date = DATE(NEW.parsed_at) AND user = NEW.user
            ) THEN unique_ssh_users + 1
            ELSE unique_ssh_users
        END,
        total_connections = total_connections + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE date = DATE(NEW.parsed_at);
END;

-- Create trigger for updating SSH parser stats on parse failure
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_stats_failure
AFTER INSERT ON ssh_parsing_errors
BEGIN
    UPDATE ssh_parser_stats
    SET
        failed_parses = failed_parses + 1,
        parsing_errors = parsing_errors + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE date = DATE(NEW.occurred_at);
END;

-- Create trigger for handling duplicate SSH connection events
CREATE TRIGGER IF NOT EXISTS tr_ssh_connection_events_deduplicate
BEFORE INSERT ON ssh_connection_events
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM ssh_connection_events
            WHERE event_uuid = NEW.event_uuid
        ) THEN RAISE(ABORT, 'Duplicate event UUID')
        ELSE NULL
    END;
END;

-- Create trigger to update SSH parser stats total_lines
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_stats_lines
AFTER INSERT ON ssh_connection_events
BEGIN
    UPDATE ssh_parser_stats
    SET total_lines_scanned = total_lines_scanned + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE date = DATE(NEW.parsed_at);
END;

-- Create trigger to update last_seen in ssh_parsing_errors
CREATE TRIGGER IF NOT EXISTS tr_ssh_parsing_errors_update_last_seen
AFTER UPDATE ON ssh_parsing_errors
FOR EACH ROW
WHEN NEW.resolved = 0
BEGIN
    UPDATE ssh_parsing_errors
    SET last_seen = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Create trigger to update SSH parser stats on authentication results
CREATE TRIGGER IF NOT EXISTS tr_ssh_parser_stats_auth_results
AFTER INSERT ON ssh_connection_events
BEGIN
    UPDATE ssh_parser_stats
    SET
        authentication_failures = CASE
            WHEN NEW.auth_result = 'FAILED' THEN authentication_failures + 1
            ELSE authentication_failures
        END,
        successful_authentications = CASE
            WHEN NEW.auth_result = 'SUCCESS' THEN successful_authentications + 1
            ELSE successful_authentications
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE date = DATE(NEW.parsed_at);
END;

-- Record migration in schema_migrations table
INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES ('005_ssh_parser', CURRENT_TIMESTAMP);
