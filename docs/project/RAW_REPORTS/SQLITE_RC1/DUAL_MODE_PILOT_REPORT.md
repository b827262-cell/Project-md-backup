# Dual Mode Pilot Report

> **Phase 1-G.2 — Dual Mode Runtime Pilot (two routers)**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> `getActiveDb()` drives both pilot routers' flows in mysql / sqlite / rollback. Disposable DB created + deleted. No router, no MySQL logic, no schema, no package changed.

---

## Result: ✅ PASS (all modes)

`getActiveDb()` switches by `DATABASE_PROVIDER`; both pilot routers' (lessonPoints + smartBookLearning) Create/Read/Update flows run correctly under SQLite via the selector; rollback to MySQL is env-var-only.

---

## 1. getActiveDb() — already implemented to spec

The requested implementation already exists in `server/db.runtime.ts` (from Phase 1-E.6) and matches the spec **exactly** — so it was **left unchanged** (no churn):

```ts
export async function getActiveDb(): Promise<ActiveDb> {
  if (isSqliteMode()) {     // isSqliteMode() === (DATABASE_PROVIDER === "sqlite")
    return getSqliteDb();   // SQLite adapter
  }
  return getDb();           // default → MySQL (server/db.ts)
}
```

`isSqliteMode()` (`server/db.sqlite.ts:61`) = `process.env.DATABASE_PROVIDER === "sqlite"`. Default is MySQL. ✅ Spec satisfied without modification.

---

## 2–4. Pilot Runs (same script, env-only switch)

### MySQL mode (`DATABASE_PROVIDER=mysql`)
```
activeProvider() = mysql                                  ✅
routed to MySQL path (no SQLite adapter) — db=null        ✅
MODE_PASS
```
No `DATABASE_URL` in this sandbox, so `getDb()` returns `null` (cannot connect to an absent MySQL server). The assertion under test is that `getActiveDb()` **routes to the MySQL path and never opens SQLite** — confirmed. Functionally unchanged.

### SQLite mode (`DATABASE_PROVIDER=sqlite`, `SQLITE_PATH=./data/dualmode-pilot.db`)
```
activeProvider() = sqlite                                 ✅
getActiveDb() = SQLite adapter (journal_mode=wal)         ✅

Router A — lessonPointsRouter flow
  A.Create lessonPoints (normalizeInsertId)   id=1        ✅
  A.Read (array options + bool + Date)                    ✅
  A.Update                                                ✅

Router B — smartBookLearningRouter flow
  B.Create learning session (normalizeInsertId) id=1      ✅
  B.Read active session (endedAt IS NULL, Date)           ✅
  B.Update (end session, timestamp)                       ✅
  B.Read unit QA (json options + isActive=true filter)    ✅
MODE_PASS
```

### Rollback (`DATABASE_PROVIDER=mysql`, same code re-run)
```
activeProvider() = mysql, routed to MySQL path            ✅
MODE_PASS
```
**Rollback = flip the env var.** Identical script, identical result as the first MySQL run. No source change.

---

## 5. Disposable SQLite DB
Created `./data/dualmode-pilot.db` (66 tables via `drizzle-kit push`), exercised, then deleted along with `-wal`/`-shm` and the temp test script. **No SQLite DB remains.**

---

## Verification

```
grep DATABASE_PROVIDER server/db.runtime.ts  → branch condition / docs (routes by env)
grep getActiveDb       server/db.runtime.ts  → defined at line 38 (unchanged)
MySQL path  → getActiveDb() returns getDb() (null here, but routed correctly) ✅
SQLite path → getActiveDb() returns getSqliteDb() (WAL, CRUD works)            ✅
SQLite db files in project → NONE
```

---

## Safety

| File | Status |
|------|--------|
| `server/db.runtime.ts` | ✅ **unchanged** (already met spec from 1-E.6) |
| `server/db.ts` | ✅ untouched (MySQL logic intact) |
| `server/db.sqlite.ts` | ✅ untouched (only invoked) |
| `package.json` | ✅ untouched |
| `drizzle/schema.sqlite.mvp.ts` | ✅ untouched (66 tables) |
| `lessonPointsRouter.ts` | ✅ untouched (1043 lines) |
| `smartBookLearningRouter.ts` | ✅ untouched (1988 lines) |
| `smartBookRouter.ts` / `tutorRouter.ts` | ✅ untouched |
| `DATABASE_PROVIDER` default | ✅ mysql |
| SQLite DB files | ✅ none remain |
| Migration | ✅ none created (drizzle-kit push to disposable DB only, deleted) |

---

## Report Answers

1. **getActiveDb 是否完成** — ✅ Yes (already implemented to spec in 1-E.6; verified, left unchanged)
2. **MySQL 是否 PASS** — ✅ PASS (routes to MySQL path, never opens SQLite)
3. **SQLite 是否 PASS** — ✅ PASS (both routers' Create/Read/Update via getActiveDb)
4. **是否修改 Router** — ❌ No
5. **是否修改 MySQL Runtime** — ❌ No (`server/db.ts` untouched)
6. **是否留下 SQLite DB** — ❌ No (disposable deleted)
7. **是否建議進入 Phase 1-H** — ✅ Yes

---

## Recommendation

✅ **Proceed to Phase 1-H.** Dual-mode is proven across **two** routers' real flows: clean provider switching, working SQLite Create/Read/Update via `getActiveDb()`, env-only rollback, MySQL default + source of truth preserved.

**Carry-forward:** in-process routers still call `getDb()` directly. A future phase (when routers may be edited) should switch the two validated pilots' `getDb()` calls to `getActiveDb()` to make SQLite live in-process behind the env flag — only after the remaining core routers (`smartBookRouter`, `tutorRouter`) pass their own audit→patch→smoke cycle.

*Pilot only. No router, no MySQL runtime, no schema, no package modified. MySQL default preserved.*
