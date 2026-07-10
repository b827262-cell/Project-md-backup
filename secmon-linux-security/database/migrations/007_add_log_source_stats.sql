-- P1 canonical log_sources already contains these columns in 001_initial.
-- Keep this version as a recorded, idempotent compatibility migration.
CREATE INDEX IF NOT EXISTS idx_log_sources_events_today ON log_sources(events_today);
CREATE INDEX IF NOT EXISTS idx_log_sources_parse_errors_today ON log_sources(parse_errors_today);

-- Update schema migration version
INSERT OR IGNORE INTO schema_migrations(version) VALUES ('007_add_log_source_stats');
