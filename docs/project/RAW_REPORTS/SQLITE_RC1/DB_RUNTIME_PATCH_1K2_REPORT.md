# DB Runtime Patch 1K2 Report

Phase: 1-K.2 Insert Return Normalization
Target: `server/db.ts`

## 1. Scope

This patch only handled insert return result shape normalization.

In scope:

- `insertId`
- `result.insertId`
- `result[0].insertId`
- `Number(result.insertId)`
- `Number(result[0].insertId)`
- `newProgress.insertId`

Out of scope and untouched:

- `.onDuplicateKeyUpdate(...)`
- `RAND()`
- `DATE()`
- `NOW()`
- `DATE_SUB()`
- `.execute()`
- JSON convention
- schema
- routers
- `package.json`

## 2. InsertId Inventory

Original audit count:

```text
insertId = 43
```

Pre-patch grep confirmed 43 sites in `server/db.ts`.

Post-patch grep:

```text
insertId = 0
```

## 3. Patched Sites

Patched count:

```text
43
```

Patterns patched:

- `Number(result[0].insertId)` -> `normalizeInsertId(result)`
- `result[0].insertId` -> `normalizeInsertId(result)`
- `result.insertId` -> `normalizeInsertId(result)`
- `newProgress.insertId` -> `normalizeInsertId(newProgress)`

`normalizeInsertId(...)` call sites in `server/db.ts`:

```text
43
```

Import added:

```ts
import { getSqliteDb, isSqliteMode, normalizeInsertId } from "./db.sqlite";
```

## 4. Migration Strategy

The selected strategy was `normalizeInsertId(...)`.

Reason:

- It preserves existing business flow.
- It supports MySQL result shape: `result[0].insertId` or `result.insertId`.
- It supports SQLite better-sqlite3 result shape: `lastInsertRowid`.
- It avoids broader `.returning(...)` or post-insert re-select changes in this scope.

No business logic was changed.

## 5. Smoke Test

SQLite disposable insert-return smoke:

```text
IMPORT_OK SQLITE_INSERT_RETURN_SMOKE_PASS id=1 singleton=pass leftovers=0
```

Verified:

- insert succeeds
- returned id is valid
- id type is `number`
- row can be read back by the returned id
- row can be deleted
- `getDb()` singleton still works
- no SQLite db/wal/shm leftovers

MySQL import/singleton smoke:

```text
IMPORT_OK(mysql) GETDB_MYSQL_SINGLETON_PASS
```

SQLite leftovers check:

```text
/tmp/smartbook-runtime-1k2-smoke.db absent
/tmp/smartbook-runtime-1k2-smoke.db-wal absent
/tmp/smartbook-runtime-1k2-smoke.db-shm absent
```

## 6. Modified Files

Modified:

- `server/db.ts`

Added:

- `DB_RUNTIME_PATCH_1K2_REPORT.md`

This phase did not modify schema, routers, `package.json`, or runtime files outside `server/db.ts`.

## 7. Compatibility Assessment

MySQL compatibility:

- MySQL insert return paths still normalize from `result[0].insertId` / `result.insertId`.
- Existing business functions still return or use numeric ids.
- No MySQL-only upsert/random/date logic was changed.

SQLite compatibility:

- SQLite insert return paths now normalize from `lastInsertRowid`.
- The disposable smoke verified SQLite insert, id retrieval, readback, delete, and singleton behavior.

Known remaining blockers:

- `.onDuplicateKeyUpdate(...)`
- `RAND()`
- `DATE()`
- `NOW()`
- `DATE_SUB()`
- `.execute()` result shape and MySQL-only raw SQL
- JSON convention risks

## 8. Recommendation

Proceed to Phase 1-K.3 Upsert Runtime Batch.

Reason:

- `insertId` blockers are now zero.
- The next highest priority blocker in `server/db.ts` is `.onDuplicateKeyUpdate(...)` with 3 sites.
