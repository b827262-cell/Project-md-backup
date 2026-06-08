# TutorRouter Patch 1J1B

> **Phase 1-J.1b — Raw SQL MySQL-only batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/tutorRouter.ts`

## Scope

Only MySQL-only raw SQL blockers were changed:

- `RAND()`
- `INSERT IGNORE`
- `db.execute()` call sites containing MySQL-only `INSERT IGNORE`

No `onDuplicateKeyUpdate()`, JSON, boolean, timestamp, insert return handling, broad raw SQL cleanup, schema, db.ts, package.json, runtime wiring, or other router changes were made in this phase.

## Changes

Imported existing dual-driver helpers:

```ts
import { normalizeInsertId, isSqliteMode, sqliteRandom } from "../db.sqlite";
```

### RAND()

Fixed **4** sites:

- cached book suggestions random ordering
- recommended chapter QA random ordering
- non-recommended chapter QA random ordering
- unit QA random ordering

Pattern:

```ts
.orderBy(sql`RAND()`)
```

became:

```ts
.orderBy(sqliteRandom())
```

### INSERT IGNORE

Fixed **2** sites:

- `book_custom_suggestions` AI-generated insert
- `book_suggestion_cache` cache insert

Pattern:

```ts
INSERT IGNORE ...
```

became mode-aware raw SQL:

```ts
const ignoreKeyword = isSqliteMode() ? "OR IGNORE" : "IGNORE";
const insertSuggestionSql = sql`INSERT ${sql.raw(ignoreKeyword)} ...`;
```

SQLite uses `run(...)`; MySQL uses `execute(...)`.

### db.execute MySQL-only Fixes

Fixed **2** `db.execute()` MySQL-only sites, both tied to `INSERT IGNORE`.

Remaining `db.execute()` call sites were intentionally kept because this phase only targets MySQL-only syntax:

- lines 439 and 459: portable raw SELECTs, but still MySQL result-shape cleanup candidates from the audit
- lines 4947 and 4950: portable raw DELETE/INSERT, not MySQL-only syntax

## Grep Results

Exact blocker greps:

```text
rg -n 'RAND\(' server/routers/tutorRouter.ts
no matches

rg -n 'INSERT IGNORE' server/routers/tutorRouter.ts
no matches
```

Remaining relevant grep:

```text
740: .orderBy(sqliteRandom())
852: .orderBy(sqliteRandom())
867: .orderBy(sqliteRandom())
883: .orderBy(sqliteRandom())
972: const ignoreKeyword = isSqliteMode() ? "OR IGNORE" : "IGNORE";
975: await (db as any).run(insertSuggestionSql);
977: await (db as any).execute(insertSuggestionSql);
1016: const ignoreKeyword = isSqliteMode() ? "OR IGNORE" : "IGNORE";
1019: await (db as any).run(insertSuggestionSql);
1021: await (db as any).execute(insertSuggestionSql);
```

## Smoke Test

Disposable SQLite smoke:

- Created `/tmp/tutor-router-1j1b-smoke.db`
- Verified `sqliteRandom()` random query executes without crash
- Verified mode-equivalent `INSERT OR IGNORE` inserts once
- Verified duplicate insert does not crash
- Verified duplicate row count stays correct
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_RAW_SQL_SMOKE_PASS randomRows=1 duplicateCount=2 q1Rows=1 leftovers=0
```

Import check:

```text
IMPORT_OK
```

## SQLite DB Leftovers

No SQLite DB artifacts remain from the smoke test:

- `/tmp/tutor-router-1j1b-smoke.db`: absent
- `/tmp/tutor-router-1j1b-smoke.db-wal`: absent
- `/tmp/tutor-router-1j1b-smoke.db-shm`: absent
- workspace `*.db`, `*.db-wal`, `*.db-shm`: none found

## Modified Files

This phase modified only:

- `server/routers/tutorRouter.ts`
- `TUTOR_ROUTER_PATCH_1J1B_REPORT.md`

The wider working tree already contains prior migration artifacts and previous phase changes.

## Recommendation

Proceed to **Phase 1-J.1c Upsert Batch**.

The next batch should only handle the remaining `.onDuplicateKeyUpdate()` site and should not mix JSON, boolean, timestamp, or raw SQL cleanup.
