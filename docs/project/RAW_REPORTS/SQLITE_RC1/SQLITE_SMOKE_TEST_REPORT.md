# SQLite Smoke Test Report

> **Phase 1-E.7 — Disposable SQLite Smoke Test**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Test DB `./data/test-smoke.db` created, exercised, then **deleted**. No production DB, no router/db.ts changes.

---

## Executive Summary

**✅ ALL CHECKS PASSED.** The SQLite runtime adapter (`server/db.sqlite.ts`) is fully functional: PRAGMAs apply correctly, `drizzle-kit push` builds the 66-table schema, full CRUD round-trips on `lesson_points`, and all helpers work. The disposable test DB was removed. MySQL remains untouched and default.

| Check | Result |
|-------|--------|
| 1. SQLite DB created | ✅ `./data/test-smoke.db` (67 objects = 66 tables + sqlite_sequence) |
| 2. Schema push | ✅ `drizzle-kit push --dialect=sqlite` → "Changes applied" |
| 3. CRUD round-trip | ✅ Insert / Select / Update / Delete all correct |
| 4. `normalizeInsertId()` | ✅ returned rowid `1` |
| 5. Helper functions | ✅ `sqliteRandom` / `sqliteNowSeconds` / `sqliteDateSubDays` build + execute |
| 6. Test DB deleted | ✅ no `.db` / `-wal` / `-shm` remain |
| 7. Routers unchanged | ✅ lessonPointsRouter 1050 lines, none import scaffold |
| 8. `server/db.ts` unchanged | ✅ `getDb()` intact |
| 9. `DATABASE_PROVIDER` default | ✅ mysql (sqlite set only transiently inside the test subprocess) |
| 10. This report | ✅ created |

---

## Execution Results

### Step B — PRAGMA verification (via `getSqliteDb()`)
```
isSqliteMode = true
sqlitePath   = ./data/test-smoke.db
PRAGMA journal_mode = wal      ✅ WAL enabled
PRAGMA foreign_keys = 1        ✅ FK ON
PRAGMA busy_timeout = 5000     ✅ 5000ms
```

### Step C — Schema push
```
drizzle-kit push --dialect=sqlite --schema=./drizzle/schema.sqlite.mvp.ts --url=./data/test-smoke.db --force
[✓] Changes applied
sqlite_master tables = 67   (66 schema tables + sqlite_sequence)
```

### Step D — CRUD round-trip (table: `lesson_points`)
```
INSERT  → lastInsertRowid = 1
SELECT  → rows=1  options=["A","B","C"]  isPublished=true  createdAt=Wed Jun 03 2026 ...
UPDATE  → question="smoke updated?"  correctIndex=2
DELETE  → rows=0 (row removed)
```
Convention correctness proven in one pass:
- **JSON mode** — `options` written as array `["A","B","C"]`, read back as array (no double-encode).
- **Boolean mode** — `isPublished: true` stored and read back as `true`.
- **Timestamp default** — `createdAt` (with `.default(sql\`(strftime('%s','now'))\`)`) auto-populated and read back as a JS `Date`.

### Step E — `normalizeInsertId()`
```
normalizeInsertId(insertRes) = 1   ✅ (better-sqlite3 lastInsertRowid path)
```

### Step F — Compatibility helpers
```
sqliteRandom()        → SQL object built: OK   (RANDOM())
sqliteNowSeconds()    → SQL object built: OK   ((strftime('%s','now')))
sqliteDateSubDays(7)  → SQL object built: OK   ((strftime('%s','now') - 7 * 86400))
ORDER BY sqliteRandom() executed: rows=0       ✅ runs as real SQL
```

### Step G — Cleanup
```
removed: ./data/test-smoke.db, -wal, -shm
removed: smoke-tmp.ts (temporary test script)
find project (excl. node_modules) for *.db/-wal/-shm → NONE
data/ contents: exam_structure_2024.json, exam_structure_2025.json (untouched)
```

---

## Test Table

| Table | Operation | Outcome |
|-------|-----------|---------|
| `lesson_points` | INSERT | ✅ rowid 1 |
| `lesson_points` | SELECT | ✅ JSON/boolean/timestamp correct |
| `lesson_points` | UPDATE | ✅ persisted |
| `lesson_points` | DELETE | ✅ removed |

(`lesson_points` chosen as the lowest-risk pilot table per `SQLITE_LESSONPOINTS_PILOT_PLAN.md`.)

---

## CRUD Success

| Operation | Success |
|-----------|---------|
| Create | ✅ |
| Read | ✅ |
| Update | ✅ |
| Delete | ✅ |
| Insert-id resolution | ✅ |

---

## Remaining Blockers

| # | Blocker | Note |
|---|---------|------|
| 1 | **Router value-convention adaptation not yet applied** | `lessonPointsRouter` still writes MySQL-style datetime strings (`toISOString().slice(0,19)`) and `1/0` for booleans, and manually `JSON.stringify`s `options`. These break under SQLite mode and must be adapted in the pilot (per pilot plan P0/P1). The adapter itself handles native values correctly — the router code is what needs the change. |
| 2 | **`getActiveDb()` not yet wired into any router** | Scaffold only. Pilot will switch lessonPoints' `getDb()` → `getActiveDb()`. |
| 3 | **No data migration** | MySQL → SQLite data move not started (Phase 1-F+). |
| 4 | **VPS-native better-sqlite3 confirmation** | Per probe phase, VPS install was reported PASS; runtime smoke on VPS still advisable before production switch. |

None of these block proceeding to the router pilot — they are the pilot's work items.

---

## Files Touched This Phase

| File | Change |
|------|--------|
| `./data/test-smoke.db` (+ -wal/-shm) | created then **deleted** |
| `smoke-tmp.ts` | created then **deleted** |
| `SQLITE_SMOKE_TEST_REPORT.md` | **new** (this report) |

**Unchanged:** `server/db.ts`, `server/db.sqlite.ts`, `server/db.runtime.ts`, all routers, `drizzle/schema.sqlite.mvp.ts`, `DATABASE_PROVIDER` default (mysql).

---

## Recommendation

✅ **Proceed to Phase 1-F Router Pilot.** The adapter is proven end-to-end against a real (disposable) SQLite DB: PRAGMAs, schema push, CRUD, insert-id, and helpers all work. The only remaining work is the router-side value-convention adaptation, which is exactly the pilot's scope. MySQL remains the source of truth.

*Disposable smoke test complete. No production SQLite DB, no router migration, MySQL default preserved.*
