# SmartBookRouter Patch 1D

> **Phase 1-I.1d — DATE() + INSERT IGNORE batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/smartBookRouter.ts`

## Scope

Only the two requested blockers were handled:

- `DATE()` usage stats filter
- `INSERT IGNORE` suggestion-cache insert

No boolean, tutorRouter, db.ts, schema, package.json, runtime wiring, getActiveDb, or other router changes were made.

## Changes

### DATE()

The usage-stats daily lookup is now mode-aware:

- SQLite: `date(column, 'unixepoch') = date(value)`
- MySQL: `DATE(column) = DATE(value)`

Result:

- `rg "DATE\\(" server/routers/smartBookRouter.ts` -> 1
- The remaining `DATE(` is a mode-aware MySQL branch only.

### INSERT IGNORE

The suggestion-cache insert is now mode-aware:

- SQLite: `INSERT OR IGNORE`
- MySQL: `INSERT IGNORE`

The SQL keyword is assembled via `sql.raw(ignoreKeyword)`, so the source no longer contains the literal `INSERT IGNORE`.

Result:

- `rg "INSERT IGNORE" server/routers/smartBookRouter.ts` -> 0
- `rg "OR IGNORE|IGNORE" server/routers/smartBookRouter.ts` -> 1 mode-aware keyword branch

## Modified Lines

- Phase 1-I.1d scoped patch: about 20 line-level changes in `server/routers/smartBookRouter.ts`.
- Current accumulated `smartBookRouter.ts` diff versus git base, including earlier 1a/1b/1c work already present in the worktree: `83 insertions / 73 deletions`.

## Smoke Test

Disposable SQLite smoke:

- Created `/tmp/smartbook-router-1d-smoke.db`
- Verified duplicate suggestion-cache insert with `INSERT OR IGNORE` leaves 1 row
- Verified `date(date, 'unixepoch')` equivalent filter matches today
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_SMOKE_PASS cacheCount=1 dateRows=1 leftovers=0
```

Import check:

```text
IMPORT_OK
```

## SQLite DB Leftovers

No SQLite DB artifacts remain from the smoke test:

- `/tmp/smartbook-router-1d-smoke.db`: absent
- `/tmp/smartbook-router-1d-smoke.db-wal`: absent
- `/tmp/smartbook-router-1d-smoke.db-shm`: absent
- workspace `*.db`, `*.db-wal`, `*.db-shm`: none found

## Recommendation

Proceed to **Phase 1-I.1e Boolean Batch**.

The two 1d blockers are handled: `INSERT IGNORE` literal is zero, and `DATE()` remains only in a mode-aware MySQL branch.
