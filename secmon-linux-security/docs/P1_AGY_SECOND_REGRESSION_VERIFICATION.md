# P1 AGY Second Regression Verification

## Identity
- Repository: b827262-cell/Project-md-backup
- Branch: main
- Tested HEAD: 1158eee81934b23fc2e254a2469a70cdad609887
- First regression commit: b87c87296c633545fef478f9dae5c043aa672044
- Date: 2026-07-10
- Environment: Python 3.14.5; project .venv; SQLite 3.53.2

## Executive Decision
- Static Gate: PASS
- Parser Gate: PASS
- Migration Gate: PASS
- Unit Gate: PASS
- Collector Gate: PASS
- Dedup Gate: PASS
- Cursor Gate: PASS
- CLI Gate: PASS
- Documentation Gate: PASS
- 30-second Gate: NOT VERIFIED
- Final decision: **P1 Release Gate: NOT READY**

## Commit Scope Review
Commit history since the first AGY report was reviewed using `git log b87c87296c633545fef478f9dae5c043aa672044..HEAD`.
The following two commits were introduced in the second repair:
1. `d26f338d6ac95d571a9dfb700afe643e4683be26` (docs(p1): synchronize second repair handoff)
2. `1158eee81934b23fc2e254a2469a70cdad609887` (docs(p1): record second repair validation head)

The changes modify core python logic, tests, and documentation, ensuring no unwanted files (such as database files, active cursor position files, logs, or OpenClaw state files) are committed. Working tree modifications are clean, leaving only pre-existing untracked files outside the subproject.

## Commands and Exit Codes
- `.venv/bin/python -m compileall -q backend scripts tests` (Exit code: 0)
- `.venv/bin/ruff check backend tests scripts` (Exit code: 0)
- `.venv/bin/mypy backend` (Exit code: 0)
- `PATH="$PWD/.venv/bin:$PATH" make check` (Exit code: 0)
- `.venv/bin/python -m pytest -q` (Exit code: 0)

All static analysis and compilation gates completed successfully with exit code 0.

## Parser Matrix
Port Validation:
- Port 1, 22, 65535 are accepted.
- Port 0, -1, 65536, 99999, non-numeric, and missing port are correctly rejected (raising `ValueError` or failing regex matching).
- `src_port` is successfully extracted and saved to `SSHLogEntry` as an integer.
- The `event_key` logic generates unique hashes when only the port differs, enabling separate storage and preventing incorrect deduplication.

Time Validation:
- Historical and current timestamps are fully accepted.
- A future timestamp with 4 minutes skew is accepted.
- Future timestamps with 6 minutes skew and 2 hours skew are rejected.

Invalid User Validation:
- Log line `Failed password for invalid user baduser from 203.0.113.10 port 45678 ssh2` is parsed successfully:
  - username = baduser
  - src_ip = 203.0.113.10
  - src_port = 45678
  - failure_reason = Failed password for invalid user

## Clean Migration
A clean migration was executed on a fresh database at `/tmp/secmon-p1-agy-second.db`:
- Second idempotent migration runs returned exit code 0.
- `PRAGMA journal_mode;` returned `wal`.
- `PRAGMA quick_check;` returned `ok`.
- `PRAGMA foreign_key_check;` returned no rows.
- Schema verification confirmed all canonical fields are present in tables `log_sources`, `attack_events`, and `attackers`.

## Collector and Dedup
We copied the `tests/fixtures/ssh_failure.log` to `/tmp/ssh_failure.log` and executed a collection run:
- **First Import**:
  - `attack_events` count: 102
  - `attackers` count: 97
  - `SUM(total_events)`: 102
  (The other 16 events from the original 118-line fixture contain out-of-range port entries and were successfully skipped).
- **Idempotent Replay**:
  - `collect_from_file` returned `(0, 0)`.
  - Database counts did not increase.
- **Port Differentiation**:
  - Importing two entries with the same IP and timestamp but different ports successfully generated 2 events, 1 attacker, and increased `total_events` by 2.

## Cursor Verification
- Precedence checked: Constructor explicit path (`cursor_path`) > `SECMON_SSH_CURSOR_PATH` environment variable > default path (`./var/ssh_cursor.position`).
- Tested cursor behavior:
  - Env path resolves correctly.
  - Constructor path overrides env path.
  - Missing env path falls back to default.
  - Rotation/truncation is detected and resolved when cursor exceeds file size.
  - Non-numeric or invalid cursor content handles gracefully.
  - DB transaction errors abort the collection before saving, preventing cursor from advancing.

## CLI Verification
- CLI script executed against valid DB path: exit code 0. Reports correct numbers matching database, and `PRAGMA quick_check: ok`.
- CLI script executed against invalid DB path: exit code 1. Prints clear error and exits.
- No fallback behavior or incorrect reporting observed.

## Documentation Consistency
The following documents were inspected:
- `README.md`
- `docs/P1_SSH_DETECTOR_HANDOFF.md`
- `docs/P1_STATUS_REPORT.md`
- `docs/P1_SSH_DETECTOR_PROCESS_SUMMARY.md`
- `docs/DATABASE_DESIGN.md`
- `docs/P1_SSH_DETECTOR_DESIGN.md`

All obsolete declarations (including `AGY 100/100 PASS`, old schemas `ip_address`/`attack_count`, Trigger/Index count claims, and "repair in progress" notices) have been fully cleaned up. The handoff was simplified to 55 lines, containing the exact second repair tested HEAD hash (`d26f338d6ac95d571a9dfb700afe643e4683be26`), and status reports have been synchronized.

## 30-second Ingestion
**NOT VERIFIED — environment limitation**
There is no active production collector loop or journalctl hook running in the test environment to measure real latency. End-to-end timing remains unverified.

## Defects
No new defects were identified in this regression run. All AGY-P1-001 through AGY-P1-005 issues have been successfully resolved.

## Remaining Risks
- Latency and looping behaviors on real journalctl/auth.log streams under production loads.
- Host system configuration issues if system commands are invoked outside the virtual environment.

## Release Gate Decision
The code meets all functional correctness, data integrity, and documentation gates. However, because real ingestion latency remains unverified, the release gate is not yet fully ready.

- **Code Regression: PASS**
- **P1 Release Gate: NOT READY**
