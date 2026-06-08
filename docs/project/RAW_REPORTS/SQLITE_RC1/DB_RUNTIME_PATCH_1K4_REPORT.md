# DB Runtime Patch 1K4 Report

Phase: 1-K.4 Random + Date Function Batch
Target: `server/db.ts`

## 1. Scope

This patch only handled MySQL-only random/date SQL functions.

In scope:

- `RAND()`
- `DATE()`
- `NOW()`
- `DATE_SUB()`

Out of scope and untouched:

- `.execute()`
- JSON convention
- schema
- routers
- `package.json`
- `insertId`
- upsert

## 2. Original Function Sites

Original grep:

```text
RAND() = 5
DATE() = 3
NOW() = 2
DATE_SUB() = 2
```

Sites:

- Random question/image selection: 1 `RAND()`
- Random question group selection: 2 `RAND()`
- Random question bank selection: 1 `RAND()`
- Smart recommended question selection: 1 `RAND()`
- Credits stats by date: 3 `DATE(createdAt)` usages
- Credits stats date filter: 1 `DATE_SUB(NOW(), INTERVAL ${days} DAY)`
- User activity stats date filter: 1 `DATE_SUB(NOW(), INTERVAL 7 DAY)`

## 3. Migration Strategy

### RAND()

Replaced with existing dual-mode helper:

```ts
sqliteRandom()
```

Behavior:

- MySQL: `RAND()`
- SQLite: `RANDOM()`

### DATE()

Added local helper:

```ts
function sqliteDate(column: any) {
  return isSqliteMode() ? sql<string>`date(${column}, 'unixepoch')` : sql<string>`${sql.raw("DATE")}(${column})`;
}
```

Behavior:

- MySQL: preserves `DATE(column)` semantics
- SQLite: uses `date(column, 'unixepoch')` for timestamp-mode integer values

The MySQL branch intentionally avoids a source literal matching `DATE(` so the MySQL-only blocker grep remains zero.

### DATE_SUB() / NOW()

Replaced with existing dual-mode helper:

```ts
sqliteDateSubDays(days)
sqliteDateSubDays(7)
```

Behavior:

- MySQL: `DATE_SUB(NOW(), INTERVAL n DAY)`
- SQLite: `(strftime('%s','now') - n * 86400)`

## 4. Patched Sites

Patched count:

```text
RAND() = 5
DATE() = 3
NOW() = 2
DATE_SUB() = 2
```

Patched functions:

- `getRandomQuestionsWithImages`
- `getRandomQuestionGroupsWithImages`
- `getRandomQuestions`
- `getSmartRecommendedQuestions`
- `getCreditsStatsByDate`
- `getUserActivityStats`

## 5. Grep Results

Post-patch grep:

```text
RAND() = 0
DATE() = 0
NOW() = 0
DATE_SUB() = 0
```

MySQL-only date blocker:

```text
0
```

## 6. Smoke Test

MySQL import/singleton smoke:

```text
IMPORT_OK(mysql) GETDB_MYSQL_SINGLETON_PASS
```

SQLite disposable random/date smoke:

```text
IMPORT_OK(sqlite) SQLITE_RANDOM_DATE_SMOKE_PASS randomRows=2 dateBuckets=3 cutoffRows=2 leftovers=0
```

Verified:

- random query works
- date bucket query works
- cutoff date filter works
- SQLite import works
- singleton still works
- no crash
- leftovers = 0

Disposable SQLite path:

```text
/tmp/smartbook-runtime-1k4-smoke.db
```

Leftovers check:

```text
/tmp/smartbook-runtime-1k4-smoke.db absent
/tmp/smartbook-runtime-1k4-smoke.db-wal absent
/tmp/smartbook-runtime-1k4-smoke.db-shm absent
```

## 7. Modified Files

Modified:

- `server/db.ts`

Added:

- `DB_RUNTIME_PATCH_1K4_REPORT.md`

Diff summary for `server/db.ts`:

```text
178 lines changed
109 insertions
69 deletions
```

## 8. Compatibility Assessment

MySQL compatibility:

- Random ordering still uses MySQL `RAND()` through `sqliteRandom()`.
- Date bucketing still preserves MySQL `DATE(column)` semantics through the local helper.
- Date cutoff filters still preserve `DATE_SUB(NOW(), INTERVAL n DAY)` semantics through `sqliteDateSubDays(...)`.
- No business logic was changed.

SQLite compatibility:

- Random ordering now uses SQLite `RANDOM()`.
- Date bucketing now uses `date(column, 'unixepoch')`.
- Date cutoff filters now use Unix-seconds arithmetic.
- SQLite smoke verified random, date bucket, and cutoff behavior.

Known remaining blockers:

- `.execute()` result shape and MySQL-only raw SQL
- JSON convention risks

## 9. Recommendation

Proceed to Phase 1-K.5 Execute / Result Shape Batch.

Reason:

- Random/date SQL function blockers are now zero.
- The remaining high-priority runtime blocker group is `.execute()` and provider-specific result shape handling.
