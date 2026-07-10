# P1 AGY Regression Verification

## 1. Identity

- Repository: `b827262-cell/Project-md-backup`
- Branch: `main`
- Tested HEAD: `1ad978687b277b4c1997a7355c5e8f6e75696cde`
- Audit baseline: `09721f7c0edc151475718a4f5d1ea3bd0432f384`
- Verification date: 2026-07-10
- Environment: Python 3.14.5; project `.venv`; SQLite 3.53.2
- `git fetch origin`: unable to update `.git/FETCH_HEAD` because the sandbox filesystem is read-only; local `origin/main` already matched Tested HEAD.

## 2. Executive Decision

| Gate | Result |
|---|---|
| Static Gate | PASS for direct venv commands; `make check` FAIL because it invokes system `ruff` absent from PATH |
| Migration Gate | PASS |
| Unit Gate | PASS: 78 collected, 78 passed |
| Parser Gate | FAIL: independent matrix found port and future-time defects |
| Collector Gate | PASS for clean DB fixture import |
| Dedup Gate | PASS for identical fixture replay |
| Cursor Gate | NOT VERIFIED as specified; implementation ignores `SECMON_SSH_CURSOR_PATH` |
| CLI Gate | PASS for normal and missing-DB paths |
| 30-second Gate | NOT VERIFIED |
| Documentation Gate | FAIL |
| Final decision | **P1 Release Gate: NOT PASSED** |

Current status: Implementation candidate verified at the expected HEAD; AGY regression was started and found unresolved defects. Issue #2 remains OPEN.

## 3. Commit Scope Review

The seven expected commits were present, in the requested order:

`0d170e2`, `c4fa327`, `865a171`, `0cc7d58`, `0f79176`, `e2eea5e`, `1ad9786`.

The range contained no SQLite DB, cursor, `.env`, log, OpenClaw state, backup artifact, or unrelated program file. Untracked workspace files outside this project were preserved and not included.

## 4. Commands and Exit Codes

| Command | Exit code | Result | Evidence |
|---|---:|---|---|
| `.venv/bin/python -m compileall -q backend scripts tests` | 0 | PASS | completed successfully |
| `.venv/bin/ruff check backend tests scripts` | 0 | PASS | All checks passed |
| `.venv/bin/mypy backend` | 0 | PASS | no issues in 11 source files |
| `make check` | 2 | FAIL | Makefile calls `ruff` outside project venv |
| `.venv/bin/python -m pytest -q` | 0 | PASS | 78 passed |

## 5. Clean Database Verification

Fresh `/tmp/secmon-p1-agy-regression.db` migration and an idempotent second migration both exited 0. `PRAGMA journal_mode` returned `wal`; `PRAGMA quick_check` returned `ok`; `PRAGMA foreign_key_check` returned no rows. Canonical columns were present in `log_sources`, `attack_events`, and `attackers`.

## 6. Test Results

The parser, log-source, collector, replay-deduplication groups and complete suite all passed. Collection count was 78 tests, all passed, with no skipped or xfailed tests observed.

## 7. Parser Matrix

Independent checks passed for normal IPv4/IPv6, historical timestamps, syslog timestamps, non-SSH filtering and malformed-line handling. Findings:

- **HIGH PARSER-001:** port `65536` was accepted; ports are not captured into the parsed entry and are not range-validated.
- **HIGH PARSER-002:** a timestamp two hours in the future was accepted because the implementation allows a two-hour skew; this exceeds the requested “small clock skew” boundary.
- **MEDIUM PARSER-003:** `Failed password for invalid user ...` was not parsed as an invalid-user event.

## 8. Collector and Dedup Results

Using a fresh DB and copied fixture: first import produced 118 events and 113 attacker rows; identical replay produced `new_events=0`, `new_attackers=0`, and counts remained 118 events / sum(total_events)=118. No partial transaction failure was induced in this regression run.

## 9. Cursor Tests

Existing isolated tests passed. The requested environment variable path was not honored: `SSHCollector` initializes `./var/ssh_cursor.position` directly. Manual tests therefore had to assign `cursor_position_file` after construction. Cursor failure, rotation and truncate behavior are not accepted as fully independently verified under the requested interface.

## 10. CLI Verification

Normal CLI execution returned 0, showed 118 attacks and `PRAGMA quick_check: ok`, and used canonical fields. A missing database returned exit code 1 with an explicit error.

## 11. 30-Second Ingestion Test

**NOT VERIFIED — environment limitation / no production collector loop or real journal timing test was executed.**

## 12. Documentation Consistency

**FAIL.** `P1_SSH_DETECTOR_HANDOFF.md` still contains obsolete “repair in progress” wording, the old 24-hour timestamp claim, stale fallback behavior, unearned `AGY Final Decision` / `100/100 PASS`, and P0 appendix fields including `ip_address`, `attack_count`, `timestamp`, and `source_ip`. These must be corrected by the implementation owner; AGY did not rewrite the handoff.

## 13. Defects

| ID | Severity | Area | Expected | Actual | Reproduction | Owner |
|---|---|---|---|---|---|---|
| AGY-P1-001 | High | Parser | Reject out-of-range ports and preserve valid `src_port` | 65536 accepted; port not persisted by parser model | Independent parser matrix | GPT-5.6 |
| AGY-P1-002 | High | Parser | Reject clearly future timestamps with only small skew | Two-hour future timestamp accepted | Independent parser matrix | GPT-5.6 |
| AGY-P1-003 | Medium | Parser | Explicit invalid-user form parsed | `Failed password for invalid user` returned no event | Independent parser matrix | GPT-5.6 |
| AGY-P1-004 | Medium | Cursor | Honor isolated `SECMON_SSH_CURSOR_PATH` | Collector hardcodes repository-relative cursor path | Collector initialization inspection | GPT-5.6 |
| AGY-P1-005 | High | Documentation | Handoff reflect tested AGY state and canonical schema | Stale PASS claims and P0 fields remain | Documentation Gate inspection | GPT-5.6 |
| AGY-P1-006 | High | Release Gate | Verify real 30-second ingestion | No production loop/timing evidence | 30-second Gate | GPT-5.6 / environment |

## 14. Remaining Risks

- Real journal/auth.log ingestion and end-to-end latency remain unverified.
- Transaction rollback under an induced write failure remains unverified in this run.
- The Makefile is not reproducible unless the project venv is activated or PATH is configured.

## 15. Release Gate Decision

Code tests and clean migration passed, but independent parser findings, cursor-interface mismatch, missing 30-second evidence and documentation defects prevent release approval.

**Final P1 decision: NOT PASSED / NOT READY FOR RELEASE GATE.**

Required follow-up: GPT-5.6 fixes AGY-P1-001 through AGY-P1-005 and updates the stale handoff; then AGY reruns the full regression. The 30-second gate must remain NOT VERIFIED until real timing evidence exists.

Working tree remaining changes: only pre-existing untracked files outside this project plus this regression document; no implementation files were modified by AGY.
