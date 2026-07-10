# P1 SSH Detector Handoff

## Implementation status

- Phase / Issue: P1 / Issue #2
- Previous AGY regression: FAIL on `1ad978687b277b4c1997a7355c5e8f6e75696cde`
- Implementation owner: GPT-5.6
- Independent verifier: AGY
- Current state: second repair implementation under validation
- Release Gate: NOT PASSED

The previous AGY report is authoritative for its original results and is preserved in
`docs/P1_AGY_REGRESSION_VERIFICATION.md`. It must not be replaced by this implementation handoff.

## Canonical schema

The runtime contract follows the migration and database design documents:

- `log_sources`: `id`, `name`, `source_type`, `source_path`, `config_json`, `enabled`, `status`, `last_event_at`, `last_error`, `events_today`, `parse_errors_today`, `created_at`, `updated_at`
- `attack_events`: `event_key`, `detected_at`, `sensor_host`, `source_id`, `source_type`, `src_ip`, `src_port`, `dst_ip`, `dst_port`, `protocol`, `attack_type`, `severity`, `signature`, `username`, `raw_log`, `metadata_json`, `created_at`
- `attackers`: `src_ip`, `first_seen`, `last_seen`, `total_events`, `ssh_failures`, `threat_score`, `highest_severity`, `last_attack_type`, `status`, `updated_at`

The database column names above are the only runtime schema contract.

## Collector contract

The current collector reads auth.log using a byte offset. It is not a `journalctl` cursor collector. Cursor precedence is:

1. explicit constructor `cursor_path`;
2. `SECMON_SSH_CURSOR_PATH`;
3. `./var/ssh_cursor.position`.

The cursor advances only after the database transaction commits. Rotation/truncate handling resets an offset larger than the current file size.

## Parser contract

SSH source ports are parsed and validated as integers in the inclusive range 1–65535. Historical timestamps are accepted. A timestamp up to five minutes ahead of an injected/reference clock is accepted; timestamps beyond that are rejected. The specific OpenSSH form `Failed password for invalid user <name> ...` is parsed before the general failed-password form.

Missing timestamps are only tolerated for recognizable SSH failure lines through the current-time fallback; unrelated lines return `None`.

## Second repair handoff

GPT-5.6 second repair implementation complete.
Self-validation passed on tested HEAD `d26f338d6ac95d571a9dfb700afe643e4683be26`.
Ready for AGY second independent regression.
30-second ingestion and the P1 Release Gate remain pending AGY verification.

Required self-validation includes direct venv compileall, Ruff, mypy, grouped and complete pytest, clean migration, replay/deduplication, `src_port` persistence, cursor environment-path behavior, and CLI verification.

## Known limitations

- Real system journal/auth.log end-to-end latency has not been verified.
- AGY must independently confirm transaction rollback, cursor failure paths, and the 30-second requirement.
- This document makes no AGY final decision and contains no release-pass score.
