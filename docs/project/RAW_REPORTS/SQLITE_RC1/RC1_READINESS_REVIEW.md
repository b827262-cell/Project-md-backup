# RC1 Readiness Review

Branch: `release/vps-lite`
Scope: Audit only. No patch, migration, schema change, runtime change, or `package.json` change.

## 1. Executive Summary

RC1 is not ready yet.

Dual-mode runtime initialization is ready, and both provider import/singleton smoke tests passed. However, the final runtime scan found 4 remaining P0 SQLite blockers in `server/routers/smartBookRouter.ts`:

```text
NOW() = 4
```

These are real SQL predicates, not helper comments or mode-aware MySQL branches. They can crash or return wrong results in SQLite mode.

RC1 recommendation:

```text
RC1 Candidate Ready: No
Proceed to VPS Lite Deployment Validation: No
Required next step: focused P0 patch for SmartBookRouter NOW() predicates
```

## 2. Migration Completion Matrix

| Area | Status | Notes |
| --- | --- | --- |
| Schema | Complete for migration scope | No schema changes in this review |
| Runtime provider wiring | Complete | `getDb()` supports MySQL / SQLite |
| SQLite adapter | Complete for runtime selection | `getSqliteDb()` lazy singleton works |
| Active runtime selector | Complete | `getActiveDb()` selects by `DATABASE_PROVIDER` |
| lessonPointsRouter | RC1-compatible in scan | No P0 SQL blocker found |
| smartBookLearningRouter | RC1-compatible with known mode-aware branch | Remaining `DATE(...)` is MySQL branch under `isSqliteMode()` guard |
| smartBookRouter | Not RC1-ready | 4 real `NOW()` P0 blockers remain |
| tutorRouter | Functionally migrated | Remaining `db.execute()` sites are structural cleanup, not current P0 blockers |
| db.ts runtime migration | Complete for P0 batches | insert/upsert/random/date/execute blockers cleared |

## 3. Runtime Verification

Scanned files:

- `server/db.ts`
- `server/db.sqlite.ts`
- `server/db.runtime.ts`
- `server/routers/lessonPointsRouter.ts`
- `server/routers/smartBookLearningRouter.ts`
- `server/routers/smartBookRouter.ts`
- `server/routers/tutorRouter.ts`

Provider smoke:

```text
IMPORT_OK(mysql) DUAL_MODE_MYSQL_PASS
IMPORT_OK(sqlite) DUAL_MODE_SQLITE_PASS leftovers=0
```

Runtime readiness:

- `DATABASE_PROVIDER=mysql`: pass
- `DATABASE_PROVIDER=sqlite`: pass
- `getDb()`: dual-mode ready
- `getSqliteDb()`: lazy singleton ready
- `isSqliteMode()`: works
- `getActiveDb()`: routes to active provider
- Singleton behavior: pass in both modes

SQLite disposable smoke path:

```text
/tmp/smartbook-rc1-readiness-smoke.db
```

Leftovers:

```text
leftovers = 0
```

## 4. Router Verification

### lessonPointsRouter

Status: pass for RC1 blocker scan.

Findings:

- `insertId`: 0
- `.onDuplicateKeyUpdate(...)`: 0
- `RAND()`: 0
- `DATE_SUB()`: 0
- `NOW()`: 0
- MySQL-only execute blocker: 0
- result-shape blocker: 0

### smartBookLearningRouter

Status: pass with keep-as-is mode-aware branch.

Findings:

- `insertId`: 0
- `.onDuplicateKeyUpdate(...)`: 0
- `RAND()`: 0
- `DATE_SUB()`: 0
- `NOW()`: 0
- Real MySQL-only date blocker: 0

Keep-as-is:

- One `DATE(...)` literal remains in a MySQL-only branch guarded by `isSqliteMode()`.
- SQLite branch uses `date(column, 'unixepoch')`.

### smartBookRouter

Status: fail for RC1.

P0 findings:

```text
NOW() = 4
```

Locations:

- `listVerifications`: `lockedUntil > NOW()`
- `listVerifications`: `suspendedUntil > NOW()`
- `getVerificationStats`: `lockedUntil > NOW()`
- `getVerificationStats`: `suspendedUntil > NOW()`

Impact:

- SQLite does not support MySQL `NOW()` in this context.
- These predicates can crash under `DATABASE_PROVIDER=sqlite`.

Keep-as-is:

- One `DATE(...)` literal remains in a MySQL branch of a mode-aware date filter.
- SQLite branch uses `date(column, 'unixepoch')`.

### tutorRouter

Status: pass for functional RC1 blockers.

Findings:

- `insertId`: 0
- `.onDuplicateKeyUpdate(...)`: 0
- `RAND()`: 0
- `DATE_SUB()`: 0
- `NOW()`: 0
- MySQL-only execute blocker: 0

P2 cleanup remains:

- Several portable `db.execute(...)` sites remain as structural cleanup candidates.
- These were already documented in `TUTOR_ROUTER_STRUCTURAL_REVIEW.md`.

## 5. Remaining Risks

### P0

Count: 4

Items:

1. `smartBookRouter.ts` `lockedUntil > NOW()` in `listVerifications`
2. `smartBookRouter.ts` `suspendedUntil > NOW()` in `listVerifications`
3. `smartBookRouter.ts` `lockedUntil > NOW()` in `getVerificationStats`
4. `smartBookRouter.ts` `suspendedUntil > NOW()` in `getVerificationStats`

Required fix:

- Replace with JS `new Date()` comparison bound through Drizzle, or provider-aware SQL.

### P1

Count: 2

Items:

1. `server/db.ts` DB JSON convention risk: `JSON.parse(pdf.tags)`
2. `server/db.ts` DB JSON convention risk: `JSON.stringify(sources)`

Impact:

- These are not current RC1 P0 runtime blockers, but should be reviewed if the corresponding SQLite schema columns are JSON-mode rather than text-mode.

### P2

Count: 8

Items:

- tutorRouter portable `db.execute(...)` structural cleanup candidates
- smartBookRouter / smartBookLearningRouter mode-aware MySQL `DATE(...)` literals that are currently guarded
- helper-contained MySQL result handling literals in runtime compatibility helpers

Impact:

- Cleanup / modernization only.
- Not blocking RC1 after P0 `NOW()` is fixed.

## 6. SQLite Readiness

SQLite readiness:

```text
85%
```

Pass:

- SQLite provider initializes.
- SQLite singleton works.
- `getDb()` returns SQLite runtime in SQLite mode.
- `getActiveDb()` routes correctly.
- Runtime insert/upsert/random/date/execute batches passed their disposable smokes.

Fail:

- 4 `NOW()` P0 SQL blockers remain in `smartBookRouter.ts`.

Verdict:

```text
SQLite Ready: No
```

## 7. MySQL Readiness

MySQL compatibility:

```text
95%
```

Pass:

- MySQL provider still initializes through `drizzle-orm/mysql2`.
- MySQL import/singleton smoke passed.
- Runtime compatibility helpers preserve MySQL branches.
- Router MySQL paths were not intentionally removed.

Residual risk:

- The recent fallback upsert changes preserve semantics but are not native MySQL atomic upserts.

Verdict:

```text
MySQL Ready: Yes, with minor residual risk
```

## 8. Dual Mode Readiness

Dual mode readiness:

```text
100% for provider selection
```

Verified:

- `DATABASE_PROVIDER=mysql`
- `DATABASE_PROVIDER=sqlite`
- `getDb()`
- `getSqliteDb()`
- `isSqliteMode()`
- `getActiveDb()`
- singleton behavior
- SQLite no-leftovers smoke

Verdict:

```text
Dual Mode Runtime Ready: Yes
```

Important distinction:

- Provider selection is ready.
- Full SQLite application readiness is blocked by the 4 `NOW()` P0 router predicates.

## 9. RC1 Recommendation

RC1 is not ready.

Final counts:

```text
P0 = 4
P1 = 2
P2 = 8
```

Readiness:

```text
SQLite Readiness = 85%
MySQL Compatibility = 95%
Dual Mode Readiness = 100%
RC1 Candidate Ready = No
VPS Lite Deployment Validation = No
```

Recommended next step:

```text
RC1-Fix-A: SmartBookRouter NOW() P0 Patch
```

Patch scope should be narrow:

- Only `server/routers/smartBookRouter.ts`
- Only the 4 `NOW()` predicates
- Prefer `new Date()` bound comparisons or mode-aware helper
- Smoke SQLite locked/suspended filters
- Confirm `NOW() = 0`

After that patch passes:

```text
Repeat RC1 Readiness Review
```
