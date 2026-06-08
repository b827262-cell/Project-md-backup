# DB Runtime Patch 1K5 Report

Phase: 1-K.5 Execute / Result Shape Batch
Target: `server/db.ts`

## 1. Scope

This patch only handled raw `.execute(...)`, provider-specific execute result shape, and MySQL result assumptions.

In scope:

- `db.execute(...)`
- raw execute availability under SQLite
- MySQL tuple row shape
- MySQL `affectedRows` result shape
- MySQL-only foreign-key toggle execute statements

Out of scope and untouched:

- JSON convention
- schema
- routers
- `package.json`
- `insertId`
- upsert
- random
- date

## 2. Execute Inventory

Original `.execute(...)` count:

```text
8
```

Original sites:

1. Raw SELECT `pdf_categories`
2. Raw SELECT owner user by `openId`
3. Raw SELECT admin users
4. Raw SELECT `knowledge_chunks`
5. Drizzle update builder `.execute()` in `resetDailyCreditsForAllUsers`
6. Raw execute `SET FOREIGN_KEY_CHECKS = 0`
7. Raw execute `DELETE FROM users WHERE id IN (...)`
8. Raw execute `SET FOREIGN_KEY_CHECKS = 1`

Post-patch `.execute(...)` count:

```text
3
```

Remaining sites:

- `executeRows(...)` MySQL branch: `database.execute(statement)`
- `executeStatement(...)` MySQL branch: `database.execute(statement)`
- Drizzle update builder `.execute()` in `resetDailyCreditsForAllUsers`

These are not SQLite blockers:

- SQLite raw SELECT uses `database.all(...)`
- SQLite raw statement uses `database.run(...)`
- update builder result is normalized through `normalizeAffectedRows(...)`

## 3. Result Shape Inventory

Original result-shape blockers:

```text
5
```

Sites:

- 4 raw SELECT sites reading `rows[0] as any[]`
- 1 update builder site reading `result[0]?.affectedRows`

Patched result-shape blockers:

```text
5
```

Post-patch provider result-shape blockers:

```text
0
```

## 4. Migration Strategy

Added helpers:

```text
4
```

Helpers:

- `normalizeExecuteRows<T>(result)`
- `normalizeAffectedRows(result)`
- `executeRows<T>(database, statement)`
- `executeStatement(database, statement)`

Strategy:

- MySQL raw SELECT keeps `database.execute(...)`, then normalizes `[rows, fields]`.
- SQLite raw SELECT uses `database.all(...)`.
- MySQL raw statement keeps `database.execute(...)`.
- SQLite raw statement uses `database.run(...)`.
- MySQL update result reads `affectedRows`.
- SQLite update result reads `changes`.

## 5. Patched Sites

Patched raw SELECT sites:

```text
4
```

Patched affected rows sites:

```text
1
```

Patched MySQL-only execute statements:

```text
2
```

Details:

- `SET FOREIGN_KEY_CHECKS = 0` is now provider-aware:
  - MySQL: `SET FOREIGN_KEY_CHECKS = 0`
  - SQLite: `PRAGMA foreign_keys = OFF`
- `SET FOREIGN_KEY_CHECKS = 1` is now provider-aware:
  - MySQL: `SET FOREIGN_KEY_CHECKS = 1`
  - SQLite: `PRAGMA foreign_keys = ON`
- Raw delete is routed through `executeStatement(...)`, so SQLite uses `run(...)`.

## 6. Grep Results

Post-patch execute grep:

```text
.execute(...) = 3
```

Remaining `.execute(...)` sites are helper-contained MySQL branches or Drizzle builder execute.

Result-shape grep:

```text
affectedRows = helper only
changedRows = 0
warningStatus = 0
RowDataPacket = 0
OkPacket = 0
ResultSetHeader = 0
```

MySQL-only execute blocker:

```text
0
```

Provider result-shape blocker:

```text
0
```

## 7. Smoke Test

MySQL import/singleton smoke:

```text
IMPORT_OK(mysql) GETDB_MYSQL_SINGLETON_PASS
```

SQLite disposable execute/result-shape smoke:

```text
IMPORT_OK(sqlite) SQLITE_EXECUTE_SMOKE_PASS categories=1 affected=2 singleton=pass leftovers=0
```

Verified:

- SQLite import works
- raw SELECT execute path works through `executeRows(...)`
- affected rows path works through `normalizeAffectedRows(...)`
- `getDb()` singleton still works
- no crash
- leftovers = 0

Disposable SQLite path:

```text
/tmp/smartbook-runtime-1k5-smoke.db
```

Leftovers check:

```text
/tmp/smartbook-runtime-1k5-smoke.db absent
/tmp/smartbook-runtime-1k5-smoke.db-wal absent
/tmp/smartbook-runtime-1k5-smoke.db-shm absent
```

## 8. Compatibility Assessment

MySQL compatibility:

- MySQL raw execute remains available through helper branches.
- MySQL tuple row results are still supported.
- MySQL `affectedRows` is still supported.
- MySQL foreign-key toggle semantics are preserved.

SQLite compatibility:

- SQLite raw SELECT no longer calls missing `database.execute(...)`.
- SQLite raw statement no longer calls missing `database.execute(...)`.
- SQLite update result shape is normalized through `changes`.
- SQLite foreign-key toggles use `PRAGMA foreign_keys`.

Known residual risks:

- Raw delete still interpolates a comma-separated id list. It is numeric input and was not expanded in this scope.
- JSON convention risks remain for the next review stage.

## 9. Recommendation

Proceed to RC1 Readiness Review.

Reason:

- Runtime provider wiring is complete.
- `insertId` blockers are zero.
- upsert blockers are zero.
- random/date blockers are zero.
- execute/result-shape blockers are zero.
- Remaining known risk is JSON convention and broader RC1 validation, not a P0 runtime execute blocker.
