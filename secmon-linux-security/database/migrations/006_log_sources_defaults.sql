-- Add default log sources for common Linux log files
-- Run this AFTER schema migration ensures log_sources table exists

-- Insert default SSH log source (auth.log)
INSERT INTO log_sources (name, device_path, parser_type, status, last_scanned)
VALUES ('SSH Journal', '/var/log/auth.log', 'ssh', 'active', NULL);

-- Insert authpriv.log source
INSERT INTO log_sources (name, device_path, parser_type, status, last_scanned)
VALUES ('Privileged Logs', '/var/log/authpriv.log', 'syslog', 'active', NULL);

-- Insert secure source
INSERT INTO log_sources (name, device_path, parser_type, status, last_scanned)
VALUES ('Secure Logs', '/var/log/secure', 'syslog', 'active', NULL);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_log_sources_status ON log_sources(status);
CREATE INDEX IF NOT EXISTS idx_log_sources_last_scanned ON log_sources(last_scanned);
CREATE INDEX IF NOT EXISTS idx_log_sources_parser_type ON log_sources(parser_type);

-- Add comment to schema_migrations
INSERT OR IGNORE INTO schema_migrations (version) VALUES ('006_log_sources_defaults');
