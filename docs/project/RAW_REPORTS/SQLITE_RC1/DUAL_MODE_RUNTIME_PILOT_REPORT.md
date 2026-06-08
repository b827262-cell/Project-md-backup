# Dual Mode Runtime Pilot Report

> **Phase 1-F.2 — Dual Mode Runtime Pilot**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> `getActiveDb()` switching validated in mysql / sqlite / rollback. Disposable DB created + deleted. No forbidden files modified.

---

## Result: ✅ PASS (all modes)

`server/db.runtime.ts` `getActiveDb()` routes correctly by `DATABASE_PROVIDER`, the SQLite adapter performs full CRUD, and rollback to MySQL needs **zero code change** — env var only.

| Test | Result |
|------|--------|
| 1. mysql mode → MySQL adapter | ✅ PASS |
| 2. sqlite mode → SQLite adapter | ✅ PASS |
| 3. helpers (isSqliteMode/getSqlitePath/normalizeInsertId/sqliteNowSeconds/sqliteRandom/sqliteDateSubDays) | ✅ PASS |
| 4. CRUD via getActiveDb() | ✅ PASS |
| 5. rollback to mysql (no code change) | ✅ PASS |

---

## Test Method (constraint-honest)

`lessonPointsRouter` **could not be modified** this phase (forbidden), so it still calls `getDb()` directly. Test 4 therefore drives the **patched router's exact CRUD operations through `getActiveDb()`** in a temporary harness — proving the selector returns an adapter capable of the router's operations. The same code ran unchanged under three env settings to prove switching + rollback.

---

## 1. MySQL Mode (`DATABASE_PROVIDER=mysql`)
```
isSqliteMode()            = false        ✅
activeProvider()          = mysql        ✅
helpers build (RAND/UNIX_TIMESTAMP/DATE_SUB variants) ✅
getActiveDb() routed to MySQL path, NOT SQLite ✅
  → db = null  (no DATABASE_URL in test env → MySQL connect N/A;
     the routing is what's under test, and it correctly avoided SQLite)
no SQLite adapter returned in mysql mode ✅
MODE_PASS
```
**Note:** No `DATABASE_URL` is set in this sandbox, so `getDb()` returns `null` (cannot connect to a MySQL server that isn't here). This is expected and does not affect the test — the assertion is that `getActiveDb()` **routes to the MySQL path and never opens SQLite**, which it does.

## 2. SQLite Mode (`DATABASE_PROVIDER=sqlite`, `SQLITE_PATH=./data/runtime-pilot.db`)
```
isSqliteMode()            = true         ✅
activeProvider()          = sqlite       ✅
getSqlitePath()           = ./data/runtime-pilot.db ✅
getActiveDb() returned SQLite adapter (pragma journal_mode = wal) ✅
sqliteNowSeconds() executes as real SQLite SQL ✅
sqliteRandom() executes as real SQLite SQL ✅
MODE_PASS
```

## 3. Helpers
| Helper | mysql mode | sqlite mode |
|--------|-----------|-------------|
| `isSqliteMode()` | false ✅ | true ✅ |
| `getSqlitePath()` | n/a | `./data/runtime-pilot.db` ✅ |
| `normalizeInsertId()` | — | returned `1` from `lastInsertRowid` ✅ |
| `sqliteNowSeconds()` | builds (UNIX_TIMESTAMP) ✅ | executes `(strftime('%s','now'))` ✅ |
| `sqliteRandom()` | builds (RAND) ✅ | executes `RANDOM()` ✅ |
| `sqliteDateSubDays(7)` | builds (DATE_SUB) ✅ | builds `(strftime - 7*86400)` ✅ |

## 4. CRUD via `getActiveDb()` (SQLite mode)
```
CREATE  → normalizeInsertId = 1                       ✅
READ    → options=["A","B"] (array), isPublished=true, publishedAt=Date ✅
UPDATE  → question/ isPublished=false persisted        ✅
GETPUBLISHED → eq(isPublished,true) → 0 rows after unpublish ✅
DELETE  → row removed                                  ✅
```
Confirms the patched value conventions (json array / boolean / Date) work end-to-end through the dual-mode selector.

## 5. Rollback (`DATABASE_PROVIDER=mysql`, SAME code re-run)
```
isSqliteMode() = false, activeProvider() = mysql, routed to MySQL path ✅
MODE_PASS
```
**Rollback requires only flipping the env var** — no source edit. Identical script, identical result as Test 1.

---

## Safety

| File | Status |
|------|--------|
| `server/db.ts` | ✅ untouched (getDb intact) |
| `server/routers/lessonPointsRouter.ts` | ✅ untouched (1043 lines) |
| `smartBookRouter.ts` / `tutorRouter.ts` | ✅ untouched |
| `drizzle/schema.sqlite.mvp.ts` | ✅ untouched (66 tables) |
| `server/db.runtime.ts` / `db.sqlite.ts` | ✅ untouched (only invoked) |
| SQLite DB files | ✅ none remain (`runtime-pilot.db*` deleted) |
| Temp test script | ✅ deleted |
| `DATABASE_PROVIDER` default | ✅ mysql (sqlite only transient per-run) |

---

## Report Answers

1. **mysql mode** — ✅ PASS (routes to MySQL path, never opens SQLite)
2. **sqlite mode** — ✅ PASS (adapter + WAL + CRUD all work)
3. **Adapter switching** — ✅ Normal; `getActiveDb()` selects by `DATABASE_PROVIDER`
4. **CRUD** — ✅ PASS (Create/Read/Update/Delete via getActiveDb)
5. **Rollback** — ✅ PASS (env-var only, no code change)
6. **Proceed to Phase 1-G smartBookLearningRouter Pilot?** — ✅ **Yes**

---

## Recommendation

✅ **Proceed to Phase 1-G — smartBookLearningRouter Pilot.** The dual-mode runtime is proven: clean provider switching, working SQLite CRUD via `getActiveDb()`, instant env-only rollback, MySQL default and source of truth preserved.

**Carry-forward for the next pilot:** apply the same audit→patch→smoke flow to `smartBookLearningRouter` (~14 tables, larger surface), and — when a router is finally allowed to be edited — switch its `getDb()` calls to `getActiveDb()` to make the dual-mode path live in-process.

*Pilot only. No forbidden file modified, no production DB, MySQL default preserved.*
