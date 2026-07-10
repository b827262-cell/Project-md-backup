-- Add default log sources for common Linux log files.
-- This migration uses the P1 canonical source_type/source_path contract.

-- Insert default SSH log source (auth.log)
INSERT OR IGNORE INTO log_sources (name, source_type, source_path, status)
VALUES ('SSH Journal', 'file', '/var/log/auth.log', 'unknown');

-- Insert authpriv.log source
INSERT OR IGNORE INTO log_sources (name, source_type, source_path, status)
VALUES ('Privileged Logs', 'file', '/var/log/authpriv.log', 'unknown');

-- Insert secure source
INSERT OR IGNORE INTO log_sources (name, source_type, source_path, status)
VALUES ('Secure Logs', 'file', '/var/log/secure', 'unknown');

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_log_sources_status ON log_sources(status);
CREATE INDEX IF NOT EXISTS idx_log_sources_last_event_at ON log_sources(last_event_at);
CREATE INDEX IF NOT EXISTS idx_log_sources_source_type ON log_sources(source_type);

-- Add comment to schema_migrations
INSERT OR IGNORE INTO schema_migrations (version) VALUES ('006_log_sources_defaults');
