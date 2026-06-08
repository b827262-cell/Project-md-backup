# DB Runtime Patch 1K3 Report

Phase: 1-K.3 Upsert Runtime Batch
Target: `server/db.ts`

## 1. Scope

This patch only handled `.onDuplicateKeyUpdate(...)` sites in `server/db.ts`.

In scope:

- `.onDuplicateKeyUpdate(...)`
- equivalent dual-mode upsert behavior

Out of scope and untouched:

- `RAND()`
- `DATE()`
- `NOW()`
- `DATE_SUB()`
- `.execute()`
- JSON convention
- schema
- routers
- `package.json`
- `insertId`

## 2. Original Upsert Sites

Original `.onDuplicateKeyUpdate(...)` count:

```text
3
```

Sites:

1. `upsertUser(...)`
   - Table: `users`
   - Conflict key: `users.openId`
   - Original set fields: computed `updateSet`
   - Business logic: create user by `openId`, or update nullable profile/login/role/lastSignedIn fields.

2. `initializeUserPoints(...)`
   - Table: `user_points`
   - Conflict key: `userPoints.userId`
   - Original set fields: empty set / ignore
   - Business logic: create initial points row only if absent.

3. `chargePoints(...)`
   - Table: `user_points`
   - Conflict key: `userPoints.userId`
   - Original set fields: `points = points + amount`
   - Business logic: add points if row exists, otherwise create row with `amount`.

Schema notes:

- MySQL schema names indexes as unique, but current Drizzle definitions use `index(...)`, not `unique(...)`.
- SQLite MVP schema does not currently include `user_points`.
- Because the conflict target is not fully reliable across both schema definitions, this patch used select/update/insert fallback instead of direct `onConflictDoUpdate(...)`.

## 3. Migration Strategy

Selected strategy:

```text
SELECT
↓
exists?
↓
UPDATE
or
INSERT
```

Reason:

- Clears MySQL-only `.onDuplicateKeyUpdate(...)`.
- Works with both MySQL and SQLite Drizzle runtimes.
- Avoids requiring schema changes in this phase.
- Preserves existing business semantics.

## 4. Patched Sites

Patched count:

```text
3
```

Patched behavior:

1. `upsertUser(...)`
   - Select by `users.openId`
   - If found: update by `users.id`
   - If absent: insert `values`

2. `initializeUserPoints(...)`
   - Select by `userPoints.userId`
   - If absent: insert `{ userId, points: initialPoints }`
   - If found: do nothing

3. `chargePoints(...)`
   - Select by `userPoints.userId`
   - If found: update points with `points + amount`
   - If absent: insert `{ userId, points: amount }`

## 5. Grep Results

Post-patch API grep:

```text
onDuplicateKeyUpdate = 0
onConflictDoUpdate = 0
onConflictDoNothing = 0
```

Remaining textual matches from the broader audit grep:

- `upsertUser` function name and messages
- `deduplicated` local variable

These are not Drizzle upsert API usage.

## 6. Smoke Test

MySQL import/singleton smoke:

```text
IMPORT_OK(mysql) GETDB_MYSQL_SINGLETON_PASS
```

SQLite disposable upsert smoke:

```text
IMPORT_OK(sqlite) SQLITE_UPSERT_SMOKE_PASS firstId=1 updatedValue=25 leftovers=0
```

Verified:

- first insert
- duplicate insert path
- conflict update
- read back updated value
- id unchanged
- row count remains 1
- no crash
- leftovers = 0

Disposable SQLite path:

```text
/tmp/smartbook-runtime-1k3-smoke.db
```

Leftovers check:

```text
/tmp/smartbook-runtime-1k3-smoke.db absent
/tmp/smartbook-runtime-1k3-smoke.db-wal absent
/tmp/smartbook-runtime-1k3-smoke.db-shm absent
```

## 7. Modified Files

Modified:

- `server/db.ts`

Added:

- `DB_RUNTIME_PATCH_1K3_REPORT.md`

Diff summary for `server/db.ts`:

```text
154 lines changed
95 insertions
59 deletions
```

## 8. Compatibility Assessment

MySQL compatibility:

- Business semantics are preserved.
- MySQL-only `.onDuplicateKeyUpdate(...)` usage was removed.
- Existing tables and fields are unchanged.

SQLite compatibility:

- Upsert behavior no longer depends on MySQL-only syntax.
- Fallback select/update/insert works without schema-level conflict clauses.
- SQLite smoke verified the equivalent insert/update behavior.

Known residual risk:

- The fallback is not as atomic as native database upsert.
- `user_points` is not currently present in the SQLite MVP schema, so full production execution still depends on future schema/runtime completeness outside this phase.

## 9. Recommendation

Proceed to Phase 1-K.4 Random + Date Function Batch.

Reason:

- `.onDuplicateKeyUpdate(...)` blockers are now zero.
- The remaining high-priority runtime blockers are MySQL-only random/date SQL functions:
  - `RAND()`
  - `DATE()`
  - `NOW()`
  - `DATE_SUB()`
