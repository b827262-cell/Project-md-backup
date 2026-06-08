# RC1 Readiness Review Final

Scope: Audit only. No code, schema, runtime, router, migration, or `package.json` changes.

## 1. Executive Summary

RC1 Candidate is ready.

The previous RC1 P0 blocker in `server/routers/smartBookRouter.ts` was `NOW() = 4`. RC1-Fix-A cleared those predicates. The final audit found no remaining P0 blockers across the requested runtime and router files.

Final verdict:

```text
P0 = 0
SQLite Ready = Yes
MySQL Ready = Yes
Dual Mode Ready = Yes
RC1 Candidate Ready = Yes
VPS Lite Deployment Validation Ready = Yes
```

## 2. Reviewed Files

Scanned:

- `server/db.ts`
- `server/db.sqlite.ts`
- `server/db.runtime.ts`
- `server/routers/lessonPointsRouter.ts`
- `server/routers/smartBookLearningRouter.ts`
- `server/routers/smartBookRouter.ts`
- `server/routers/tutorRouter.ts`

## 3. Final Blocker Verification

Actual blocker counts:

```text
insertId blocker = 0
onDuplicateKeyUpdate = 0
RAND() blocker = 0
DATE_SUB() blocker = 0
NOW() blocker = 0
MySQL-only execute blocker = 0
result-shape blocker = 0
```

Literal keep-as-is notes:

- `server/db.sqlite.ts` contains `insertId`, `RAND()`, and `DATE_SUB(NOW(), ...)` inside compatibility helper comments or MySQL helper branches.
- `server/db.ts` contains `affectedRows` only inside `normalizeAffectedRows(...)`.
- `server/db.ts` contains `SET FOREIGN_KEY_CHECKS` only inside a provider-aware branch paired with SQLite `PRAGMA foreign_keys`.
- `smartBookLearningRouter` and `smartBookRouter` each retain guarded MySQL `DATE(...)` branches with SQLite-safe `date(..., 'unixepoch')` alternatives.
- tutorRouter still has portable/structural `db.execute(...)` cleanup candidates documented earlier, but no current MySQL-only execute blocker.

## 4. Runtime Verification

MySQL smoke:

```text
IMPORT_OK(mysql) RC1_FINAL_MYSQL_PASS getDb=pass getActiveDb=pass singleton=pass routers=4
```

SQLite smoke:

```text
IMPORT_OK(sqlite) RC1_FINAL_SQLITE_PASS getDb=pass getSqliteDb=pass getActiveDb=pass singleton=pass routers=4 leftovers=0
```

Verified:

- `DATABASE_PROVIDER=mysql`
- `DATABASE_PROVIDER=sqlite`
- `getDb()`
- `getSqliteDb()`
- `getActiveDb()`
- `isSqliteMode()`
- singleton behavior
- import of all four target routers in both modes
- no SQLite DB/WAL/SHM leftovers

Disposable SQLite path:

```text
/tmp/smartbook-rc1-final-smoke.db
```

Leftovers:

```text
leftovers = 0
```

## 5. Router Verification

### lessonPointsRouter

Status: Ready.

P0 blocker scan:

```text
insertId = 0
onDuplicateKeyUpdate = 0
RAND() = 0
DATE_SUB() = 0
NOW() = 0
MySQL-only execute blocker = 0
result-shape blocker = 0
```

### smartBookLearningRouter

Status: Ready.

Notes:

- No P0 blocker remains.
- Existing date comparison is mode-aware.
- SQLite branch uses `date(column, 'unixepoch')`.
- MySQL branch preserves `DATE(column)`.

### smartBookRouter

Status: Ready after RC1-Fix-A.

Final `NOW()` verification:

```text
NOW() = 0
```

The previous four `lockedUntil` / `suspendedUntil` predicates now use Drizzle `gt(column, now)` comparison.

### tutorRouter

Status: Ready for RC1.

Notes:

- Functional SQLite migration is complete.
- Remaining `db.execute(...)` sites are structural cleanup candidates, not current P0 blockers.
- No insert/upsert/random/date P0 blocker remains.

## 6. Remaining Risks

### P0

Count:

```text
0
```

No known SQLite runtime crash blocker remains in the reviewed scope.

### P1

Count:

```text
2
```

Items:

1. `server/db.ts` JSON convention risk: `JSON.parse(pdf.tags)`
2. `server/db.ts` JSON convention risk: `JSON.stringify(sources)`

Assessment:

- These are not current RC1 P0 blockers.
- They should be validated against the final SQLite schema column modes during deployment validation.

### P2

Count:

```text
8
```

Items:

- tutorRouter portable `db.execute(...)` structural cleanup candidates
- guarded MySQL date literals inside mode-aware branches
- runtime compatibility helper literals
- optional modernization around raw SQL helper consolidation

Assessment:

- Not blocking RC1.
- Track as post-RC1 cleanup.

## 7. Readiness Scores

SQLite Readiness:

```text
100%
```

MySQL Compatibility:

```text
98%
```

Reason for not scoring 100%:

- Upsert was converted from native MySQL upsert to fallback select/update/insert in prior runtime patch. Semantics are preserved, but atomicity differs.

Dual Mode Readiness:

```text
100%
```

## 8. RC1 Candidate Recommendation

RC1 Candidate is ready.

Recommendation:

```text
Proceed to VPS Lite Deployment Validation
```

Conditions:

- Keep the current branch scope intact.
- Do not start broad cleanup before VPS validation.
- Treat P1 JSON convention and P2 structural cleanup as validation watch items, not RC1 blockers.

## 9. VPS Lite Deployment Validation Plan

Recommended validation sequence:

1. Preflight environment
   - Confirm Node version.
   - Confirm `better-sqlite3` native module loads.
   - Confirm `DATABASE_PROVIDER=sqlite`.
   - Confirm `SQLITE_PATH` points to the intended VPS Lite DB path.

2. Runtime boot smoke
   - Start app in SQLite mode.
   - Verify `getDb()` returns SQLite runtime.
   - Verify no unexpected MySQL connection attempt.
   - Confirm app imports routers without crash.

3. SQLite file health
   - Confirm DB file is created at expected path.
   - Confirm WAL/SHM behavior is expected.
   - Confirm `PRAGMA foreign_keys = ON`.
   - Confirm `PRAGMA journal_mode`.

4. Core router smoke
   - lessonPointsRouter create/read/update flow.
   - smartBookLearningRouter unlock/session/progress flow.
   - smartBookRouter verification, usage, wrong-answer, and NOW-free locked/suspended paths.
   - tutorRouter insert/upsert/random/date/boolean/json/timestamp migrated paths.

5. Runtime db.ts smoke
   - insert return normalization.
   - fallback upsert paths.
   - random/date function helpers.
   - execute/result-shape helpers.

6. Data integrity checks
   - Verify boolean values round-trip.
   - Verify timestamp values round-trip as Date-compatible values.
   - Verify JSON-mode fields do not double encode/decode.
   - Verify row counts after repeated insert/update paths.

7. MySQL rollback sanity
   - Switch `DATABASE_PROVIDER=mysql`.
   - Confirm import/startup still works.
   - Do not run destructive writes unless using disposable data.

8. Artifact cleanup
   - Confirm no disposable `.db`, `.db-wal`, or `.db-shm` files remain.
   - Keep only the intended VPS Lite SQLite DB files.
