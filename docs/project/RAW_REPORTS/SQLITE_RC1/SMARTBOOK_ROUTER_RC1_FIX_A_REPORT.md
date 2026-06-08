# SmartBookRouter RC1 Fix-A Report

Phase: RC1-Fix-A SmartBookRouter NOW() Patch
Target: `server/routers/smartBookRouter.ts`

## 1. Scope

This patch only handled the remaining `NOW()` P0 blockers in `server/routers/smartBookRouter.ts`.

In scope:

- `lockedUntil > NOW()`
- `suspendedUntil > NOW()`

Out of scope and untouched:

- `DATE()`
- `DATE_SUB()`
- `RAND()`
- JSON convention
- boolean convention
- `insertId`
- upsert
- `db.ts`
- runtime files
- schema
- other routers

## 2. Original NOW() Sites

Original count:

```text
NOW() = 4
```

Original sites:

- `listVerifications`: `lockedUntil > NOW()`
- `listVerifications`: `suspendedUntil > NOW()`
- `getVerificationStats`: `lockedUntil > NOW()`
- `getVerificationStats`: `suspendedUntil > NOW()`

## 3. Migration Strategy

Selected strategy:

```ts
const now = new Date();
gt(column, now)
```

Reason:

- Avoids MySQL-only `NOW()`.
- Uses Drizzle comparison binding.
- Preserves existing business logic.
- Works for MySQL and SQLite timestamp-mode values.

## 4. Patched Sites

Patched count:

```text
4
```

Changes:

- `sql\`${smartBookVerifications.lockedUntil} > NOW()\`` -> `gt(smartBookVerifications.lockedUntil, now)`
- `sql\`${smartBookVerifications.suspendedUntil} > NOW()\`` -> `gt(smartBookVerifications.suspendedUntil, now)`

Import added:

```ts
gt
```

## 5. Grep Results

Post-patch grep:

```text
rg -n "NOW\(" server/routers/smartBookRouter.ts
```

Result:

```text
NOW() = 0
```

## 6. Smoke Test

MySQL import smoke:

```text
IMPORT_OK(mysql) SMARTBOOK_ROUTER_IMPORT_PASS
```

SQLite import smoke:

```text
IMPORT_OK(sqlite) SMARTBOOK_ROUTER_IMPORT_PASS
```

SQLite locked/suspended filter smoke:

```text
SMARTBOOK_ROUTER_NOW_SMOKE_PASS locked=1 suspended=1 leftovers=0
```

Verified:

- locked future timestamp filter returns 1 row
- suspended future timestamp filter returns 1 row
- past timestamps do not match
- MySQL import passes
- SQLite import passes
- no SQLite DB/WAL/SHM leftovers

Disposable SQLite paths:

```text
/tmp/smartbook-router-now-smoke.db
/tmp/smartbook-router-now-import-smoke.db
```

Leftovers:

```text
leftovers = 0
```

## 7. Compatibility Assessment

MySQL compatibility:

- MySQL path no longer uses `NOW()` for these predicates.
- Drizzle binds the JS `Date` value for comparison.
- Business semantics remain "future locked/suspended timestamp".

SQLite compatibility:

- SQLite path no longer sees unsupported MySQL `NOW()`.
- Predicate is a normal bound comparison.
- Smoke verified locked/suspended filter behavior.

## 8. Recommendation

Rerun RC1 Readiness Review.

Reason:

- The only P0 blocker from the previous RC1 review was `NOW() = 4`.
- `NOW() = 0` after this patch.
- Import and SQLite predicate smoke passed.
