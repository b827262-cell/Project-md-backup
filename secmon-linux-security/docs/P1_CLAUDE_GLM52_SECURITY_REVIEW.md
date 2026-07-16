# SecMon P1 — Independent Security / Architecture / Deployment / Test Review

## 1. Identity

- **Reviewer:** Claude (model: `glm-5.2`), independent verify-only reviewer.
- **Phase / Issue:** P1 — Production SSH collector loop + Telegram notifier + integration / `#2`.
- **Repository:** `b827262-cell/Project-md-backup` (git top-level: `/home/b822726/project/get-rg`; subproject `secmon-linux-security`).
- **Branch:** `main`.
- **Required implementation HEAD:** `f4f48281947e8149648e0d32726c9cb29c3af3bd`.
- **Tested HEAD (this review):** `f4f48281947e8149648e0d32726c9cb29c3af3bd` — **CONFIRMED** (`git rev-parse HEAD`).
- **Luna report under review:** `docs/P1_CODEX_LUNA_IMPLEMENTATION_REPORT.md`.
- **Review mode:** Static, read-only. No code, config, tests, service unit, or prior doc was modified.

## 2. HEAD reconciliation

- `git show --stat f4f4828` shows the required HEAD is a **docs-only** commit that adds exactly one file: `docs/P1_CODEX_LUNA_IMPLEMENTATION_REPORT.md` (+29 lines).
- The Luna report records its “Tested implementation HEAD” as `b83c4ea4…` (the last *code* commit). Because `f4f4828` is docs-only on top of `b83c4ea`, **the code the Luna report validated is byte-for-byte the code at the required HEAD.** No drift.
- Prior regression evidence at ancestor `1158eee` (`docs/P1_AGY_SECOND_REGRESSION_VERIFICATION.md`) is consistent with the current code state; the older `docs/P1_AGY_FULL_CODE_AUDIT.md` blockers (schema drift, parser self-contradiction, CLI column mismatch) are **resolved** in the current tree (verified: `database/migrations/001_initial.sql` defines the exact columns the collector writes; parser tests are internally consistent).

## 3. Scope of this decision

P1 deliverables reviewed against `docs/P1_TELEGRAM_CODEX_EXECUTION_TASK.md`:

- `backend/collectors/main.py` (production loop), `backend/collectors/ssh_collector.py` (integration), `backend/notifiers/telegram.py` (notifier).
- `backend/config.py` (settings + production-path guard).
- Tests: `test_telegram_notifier.py`, `test_collector_telegram.py`, `test_collector_main.py`, `test_config.py`, plus the broader suite.
- `systemd/secmon-collector.service`, `systemd/secmon-api.service`, `.env.example`.
- Luna report accuracy.

## 4. What this approval is — and is not

- **NOT** a P1 Release Gate PASS. The acceptance document (`§15`) is explicit that the gate stays `NOT PASSED` until the real-host **30-second end-to-end ingestion** is verified by AGY.
- **NOT** evidence from live behavior. Per the review brief, **real Telegram delivery, real systemd deployment, and the 30-second production validation are explicitly NOT counted as evidence for code approval.** Those remain AGY’s to execute on a real host.
- **This is** a code/architecture/config/test approval that P1 is **APPROVE FOR AGY** — i.e., ready for AGY’s independent real-environment Telegram/systemd/30-second verification, with no Blocker or High code defect.

## 5. Static verification performed (code quality only)

- **No committed secrets.** Only `.env.example` is tracked (token/chat-id empty). No tracked `.env`, SQLite DB, cursor, or log files. Source scan for Telegram token signatures (`bot<digits>`, `<digits>:AA…`) in `backend tests scripts systemd .env.example`: **no matches**; tests use safe placeholders (`"token"`, `"super-secret-token"`). The chat id `8350114645` is not a secret.
- **Token hygiene.** `telegram_bot_token: SecretStr | None`; masked in `repr(Settings)` (asserted by `test_telegram_token_is_masked_in_settings_repr` and `test_secretstr_is_retrieved_only_by_notifier_constructor`); plaintext unwrapped only inside the notifier constructor; never interpolated into any logged string. `_describe_error` sanitizes network errors; `HTTPError` is consumed inside `_perform_request` so its `.url` (which carries the token) is never logged.
- **Transport security.** HTTPS-only (hardcoded `api.telegram.org` URL + explicit `https://` guard with a regression test that no network call is made for an insecure endpoint); `urlopen` performs default TLS certificate verification; **no SSRF** (no user-controllable URL; `chat_id` is sent as a JSON field, not reflected into the URL).
- **No injection surface.** All SQL uses `?` placeholders; the only f-string SQL is `PRAGMA busy_timeout={int}` / `PRAGMA journal_mode=WAL` (integer/constant — safe).
- **Collector↔Telegram ordering / atomicity.** Notifications are built only from events whose `INSERT … OR IGNORE` returned `rowcount == 1` (truly new); sent **after** `commit()` and `conn.close()` and **after** the cursor is advanced; a single aggregated alert per round; replay yields `new_events=0` → no re-notify; notifier failure (return False **or** raise) cannot alter persisted events, `attackers.total_events`, the cursor, or the return value. Verified by `test_cursor_is_saved_before_single_aggregated_notification` (order == `["cursor","telegram"]`), `test_failed_notification_keeps_committed_events_and_cursor`, and `test_notification_exception_cannot_change_result_database_or_cursor`.
- **Production loop.** Honors `SECMON_DATABASE_PATH/CURSOR/LOG_PATH/COLLECT_INTERVAL_SECONDS`; default 5 s, hard floor 0.5 s (`_MIN_SLEEP_SECONDS`) preventing busy-spin; SIGTERM/SIGINT set a `threading.Event` and the loop exits cleanly; recoverable per-round errors are logged and the loop continues; initialization/schema/config errors are logged and the process exits non-zero; each round logs start time, new events, new attackers, duration, next poll. `validate_production_storage_paths` rejects repository-local `./var` paths when `environment=production`.
- **`secmon-collector.service`** satisfies `§8`: `EnvironmentFile=/etc/secmon/secmon.env`, `ExecStart=/opt/secmon/.venv/bin/python -m backend.collectors.main`, `Restart=on-failure`, `RestartSec=5s`, `ReadWritePaths=/var/lib/secmon /var/log/secmon`, `NoNewPrivileges`/`PrivateTmp`/`ProtectSystem=strict`/`ProtectHome`, **no embedded token**, and **no unconditional `adm` group** (correctly deferred to the operator per `§8`).
- **`.env.example`** matches the required placeholders (`§9`), secrets blank, `SECMON_AUTO_BLOCK_ENABLED=false`, `SECMON_ENVIRONMENT=development`, Telegram disabled by default.
- **Executable gates NOT re-run here.** This sandbox required interactive approval to execute `pytest`/`ruff`/`mypy`/`compileall`, which was not granted; I therefore did **not** independently re-execute them and I am **not** citing their results as proof of production behavior. The Luna report records them PASS at `b83c4ea` (== current code), and the AGY second-regression records them PASS at ancestor `1158eee`. These are treated only as recorded static/test evidence, not as deployment validation.

## 6. Findings

### Blocker
None.

### High
None.

### Medium

- **M-1 — `systemd/secmon-api.service` references a non-existent module (out of P1 core scope).**
  `ExecStart=… uvicorn backend.app:app --host 127.0.0.1 --port 8080`, but there is **no** `backend/app.py`; `backend/api/__init__.py` is a one-line placeholder (“HTTP API package placeholder for P1/P2”). The API service would fail at start with `ModuleNotFoundError`. This is **outside P1’s stated scope** (P1 = collector + Telegram; the API is explicitly a P1/P2 placeholder) and is pre-existing, and the P1 deliverable `secmon-collector.service` is correct — so it does **not** block this P1 approval. *Required before any API deployment (P2):* create `backend/app.py` exposing the ASGI `app`, or remove/disable the unit so the tree ships no broken deploy artifact. Also note the port drift vs. `.env.example` (see L-2).

- **M-2 — Notifier failure contract has an exception-coverage gap.**
  `send_message`/`_perform_request` catch `(HTTPError, URLError, TimeoutError, OSError, ValueError)`. `urllib.request.urlopen` can also raise `http.client.HTTPException` subclasses (`IncompleteRead`, `BadStatusLine`, `RemoteDisconnected`) on truncated/malformed HTTP, which are **not** subclasses of `OSError` and would propagate instead of returning `False`. Impact is bounded and safe: in the collector loop they are caught by `_send_telegram_alerts`’ broad `except Exception` (logged, loop continues, no rollback); such connection errors carry no token, so there is **no secret-leak path**. *Recommendation:* widen the handler to `except Exception` (or add `http.client.HTTPException`) and return `False`, so the documented “return False on failure” contract holds everywhere (notably for the unguarded call in the `--test` CLI path).

### Low

- **L-1 — systemd hardening could go further (defense in depth).** Consider adding `CapabilityBoundingSet=`, `SystemCallFilter=@system-service`, `ProtectClock`, `ProtectKernelTunables`, `RestrictRealtime`, `LockPersonality`, `MemoryDenyWriteExecute`. Current directives (NoNewPrivileges, PrivateTmp, ProtectSystem=strict, ProtectHome, ReadWritePaths) are already sound.
- **L-2 — Port/config drift (out of P1 scope).** `.env.example` sets `SECMON_API_PORT=8000` while `secmon-api.service` binds `--port 8080`. Align when the API lands.
- **L-3 — Naive timestamps / syslog year inference.** Times use `datetime.now()` (no tz); syslog-style timestamps infer the **current year**, so across a Dec→Jan boundary replayed older lines could be re-keyed and counted once. Pre-existing parser behavior; narrow edge case.
- **L-4 — No adaptive 429 backoff.** Telegram `429 Retry-After` is not honored; cooldown is purely time-based. Acceptable for P1.
- **L-5 — Cooldown is per-notifier and crosses rounds.** If `SECMON_TELEGRAM_COOLDOWN_SECONDS` exceeds the poll interval, rounds with genuinely new events can be silently suppressed. By design and configurable; worth a one-line doc note.
- **L-6 — Live validation intentionally not executed.** Real Telegram send, real systemd start, and the 30-second ingestion gate were not run (per Luna report and this brief). Excluded as code-approval evidence; AGY to perform on a real host. Process limitation, not a code defect.

## 7. Luna report assessment

- Accurate and appropriately scoped. It correctly records the last code HEAD (`b83c4ea`), lists the delivered hardening, and **honestly marks “Real Telegram smoke: NOT EXECUTED” and “30-second Gate: NOT VERIFIED.”** No overclaiming.
- Its static/test PASS claims are consistent with the AGY second-regression record at an ancestor HEAD; I did not re-execute them here (see §5).
- No defect found in the report itself.

## 8. Required fixes / recommendations

- **Before P1 hand-off to AGY real-environment verification:** none blocking. (M-2 is recommended but bounded; optional to address now.)
- **Before any API/P2 deployment (not P1):** fix M-1 (missing `backend/app.py` / broken `secmon-api.service`) and L-2 (port drift).
- **Hardening backlog (optional):** L-1, L-3, L-4, L-5.
- **AGY must still execute:** real Telegram `--test` send (token leak check on stdout/stderr), real `systemctl start` of the collector unit, and the 30-second end-to-end ingestion measurement. Until those pass, the P1 Release Gate remains `NOT PASSED`.

## 9. Decision

**APPROVE FOR AGY.**

No Blocker and no High-severity defect exist within P1 scope (production collector loop, Telegram notifier, collector↔Telegram integration, tests, `.env.example`, and `secmon-collector.service`). The two Medium findings are either out of P1’s stated scope (M-1, the placeholder API unit) or bounded with no security impact (M-2). Real Telegram/systemd/30-second production validation is **not** counted as evidence for this code approval and remains AGY’s responsibility; this decision does not constitute a P1 Release Gate PASS.
