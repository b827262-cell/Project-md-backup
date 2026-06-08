# DB Runtime Patch 1K1 Report

Phase: 1-K.1 Runtime Provider Wiring
Target: `server/db.ts`

## 1. Scope

This patch only changed runtime provider selection and `getDb()` initialization behavior.

In scope:

- Runtime provider selection
- MySQL / SQLite dual runtime initialization
- `getDb()` singleton behavior

Out of scope and untouched:

- `insertId`
- `.onDuplicateKeyUpdate(...)`
- `RAND()`
- `DATE()`
- `NOW()`
- `DATE_SUB()`
- `.execute()` cleanup
- JSON convention
- schema
- routers
- `package.json`

## 2. Driver Wiring Changes

MySQL driver path:

- `drizzle-orm/mysql2`
- imported in `server/db.ts` as `drizzleMysql`
- initialized from `process.env.DATABASE_URL`

SQLite driver path:

- `server/db.sqlite.ts`
- internally uses `better-sqlite3`
- internally uses `drizzle-orm/better-sqlite3`
- initialized through existing lazy `getSqliteDb()`

`server/db.ts` now imports:

- `getSqliteDb`
- `isSqliteMode`

No schema imports were changed.

## 3. Provider Selection Logic

Provider selector:

- `DATABASE_PROVIDER=sqlite` activates SQLite mode.
- Any other value, including unset, keeps the MySQL path.

`getDb()` behavior:

- SQLite mode:
  - returns the existing `getSqliteDb()` singleton
  - does not require `DATABASE_URL`
  - returns immediately after SQLite initialization
- MySQL mode:
  - preserves existing lazy initialization from `DATABASE_URL`
  - preserves `null` return when `DATABASE_URL` is absent

Singleton behavior:

- `_db` remains a single cached runtime handle.
- MySQL mode returns the same MySQL Drizzle handle on repeated calls.
- SQLite mode returns the same SQLite Drizzle handle on repeated calls.

## 4. Smoke Test

MySQL smoke:

```text
IMPORT_OK(mysql) GETDB_MYSQL_SINGLETON_PASS
```

SQLite smoke:

```text
IMPORT_OK(sqlite) GETDB_SQLITE_SINGLETON_PASS leftovers=0
```

Disposable SQLite path:

```text
/tmp/smartbook-runtime-1k1-smoke.db
```

Leftovers check:

```text
/tmp/smartbook-runtime-1k1-smoke.db absent
/tmp/smartbook-runtime-1k1-smoke.db-wal absent
/tmp/smartbook-runtime-1k1-smoke.db-shm absent
```

No formal production database was created.

## 5. Modified Files

Modified:

- `server/db.ts`

Added:

- `DB_RUNTIME_PATCH_1K1_REPORT.md`

Diff summary for `server/db.ts`:

```text
22 lines changed
19 insertions
3 deletions
```

`getDb()` modified count:

```text
1 function
```

## 6. Compatibility Assessment

MySQL compatibility:

- Default remains MySQL unless `DATABASE_PROVIDER=sqlite`.
- MySQL still uses `drizzle-orm/mysql2`.
- Existing `DATABASE_URL` lazy initialization remains.
- Business logic was not changed.

SQLite compatibility:

- `DATABASE_PROVIDER=sqlite` now routes `getDb()` to the existing SQLite runtime adapter.
- The SQLite adapter remains lazy and only opens a file when `getDb()` is called in SQLite mode.
- This phase does not make all downstream `db.ts` business functions SQLite-safe yet; insert result shape, upsert, random, date, and execute result shape blockers remain for later batches.

Known remaining blockers:

- `insertId`
- `.onDuplicateKeyUpdate(...)`
- `RAND()`
- `DATE_SUB(NOW(), ...)`
- MySQL-specific `.execute()` result assumptions

## 7. Recommendation

Proceed to Phase 1-K.2 Insert Return Normalization.

Reason:

- Runtime provider selection is now dual-mode ready.
- Import and singleton smoke tests pass for both providers.
- The next highest-risk blocker is the 43 `insertId` result-shape assumptions identified in Phase 1-K.0.
