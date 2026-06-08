# SQLite Runtime Scaffold Report

> **Phase 1-E.6 — Runtime Scaffold Only / No Router Migration**
> Generated: 2026-06-03 · Branch: `release/vps-lite`

---

## Summary

| Item | Status |
|------|--------|
| better-sqlite3 installed | ✅ `12.10.0` (compiled, loads, SQLite 3.53.1) |
| @types/better-sqlite3 installed | ✅ `7.6.13` (devDependency) |
| `server/db.sqlite.ts` activated | ✅ design draft → functional adapter |
| `server/db.runtime.ts` created | ✅ `getActiveDb()` selector |
| Runtime wired into routers | ❌ No |
| Routers modified | ❌ No |
| SQLite DB created | ❌ No (lazy singleton — not called) |
| `DATABASE_PROVIDER` default | **mysql** (SQLite is explicit opt-in only) |
| MySQL source of truth | ✅ unchanged |

---

## Files Changed

| File | Change |
|------|--------|
| `package.json` | Added `better-sqlite3@^12.10.0` (deps), `@types/better-sqlite3@^7.6.13` (devDeps), and `better-sqlite3` to `pnpm.onlyBuiltDependencies` (so future installs compile the native addon) |
| `pnpm-lock.yaml` | Updated by pnpm for the two new packages |
| `server/db.sqlite.ts` | Converted from design draft to **functional adapter**: real `better-sqlite3` + `drizzle-orm/better-sqlite3` imports, schema import, `getSqliteDb()` lazy singleton with PRAGMAs; helpers made functional |
| `server/db.runtime.ts` | **New** — `getActiveDb()` provider selector (mysql default) |
| `SQLITE_RUNTIME_SCAFFOLD_REPORT.md` | **New** — this report |

### NOT changed
- `server/db.ts` — untouched (still `getDb()` at line 172, `drizzle-orm/mysql2`)
- `server/routers/lessonPointsRouter.ts` — untouched (1050 lines)
- `smartBookRouter.ts`, `tutorRouter.ts`, all other routers — untouched
- `drizzle/schema.sqlite.mvp.ts` — untouched (66 tables)

---

## `server/db.sqlite.ts` — What It Now Provides

| Export | Role |
|--------|------|
| `getSqliteDb()` | **NEW** — lazy singleton; opens `SQLITE_PATH`, applies WAL + busy_timeout=5000 + foreign_keys=ON, returns Drizzle instance bound to `schema.sqlite.mvp` |
| `isSqliteMode()` | preserved — true only when `DATABASE_PROVIDER === "sqlite"` |
| `getSqlitePath()` | preserved — default `./data/smartbook.db` |
| `sqliteNowSeconds()` | functional — `(strftime('%s','now'))` / MySQL `UNIX_TIMESTAMP()` |
| `toSqliteTimestamp()` | functional — Date → Unix seconds (sqlite) / Date (mysql) |
| `sqliteRandom()` | functional — `RANDOM()` / `RAND()` |
| `normalizeInsertId()`, `sqliteDateSubDays()` | functional helpers |
| `schema`, `SqliteDb`, `SqliteEnvContract` | preserved/typed |

**PRAGMAs applied in `getSqliteDb()`:** `journal_mode = WAL`, `busy_timeout = 5000`, `foreign_keys = ON`.

**Safety:** `getSqliteDb()` is a lazy singleton. Importing the module has no side effects; the DB file is opened only when the function is first called — which nothing does yet.

---

## `server/db.runtime.ts` — Selector

```ts
export async function getActiveDb(): Promise<ActiveDb> {
  if (isSqliteMode()) return getSqliteDb();   // DATABASE_PROVIDER === "sqlite"
  return getDb();                              // default → MySQL (server/db.ts)
}
```

Default is MySQL. No router imports this file yet, so the runtime path is unchanged.

---

## Safety Verification

```
grep "better-sqlite3" package.json
  79:  "better-sqlite3": "^12.10.0",
  143: "@types/better-sqlite3": "^7.6.13",
  177: "better-sqlite3",   (onlyBuiltDependencies)

grep "better-sqlite3" server/db.sqlite.ts
  18: import Database from "better-sqlite3";
  19: import { drizzle, type BetterSQLite3Database } from "drizzle-orm/better-sqlite3";

grep "getActiveDb" server/db.runtime.ts
  38: export async function getActiveDb(): Promise<ActiveDb> {

grep "DATABASE_PROVIDER" server/db.runtime.ts
  → branch condition only; default path is getDb() (MySQL)

server/db.ts            → UNCHANGED (getDb @172, drizzle-orm/mysql2 @2)
routers importing scaffold → NONE
DATABASE_PROVIDER=sqlite set anywhere → NONE (MySQL remains default)
SQLite .db / .db-wal / .db-shm files → NONE
lessonPointsRouter.ts   → UNCHANGED (1050 lines)
schema.sqlite.mvp.ts    → UNCHANGED (66 tables)
```

**Native addon proof:** `node -e "require('better-sqlite3')"` → loads; `select sqlite_version()` → `3.53.1`.

---

## Not Executed (per constraints)

- ❌ `pnpm build` — not run
- ❌ migration / `drizzle-kit push` — not run
- ❌ runtime not started
- ❌ no production SQLite DB created
- ❌ `DATABASE_PROVIDER` default NOT changed (stays mysql)

---

## Remaining Work

| Phase | Task |
|-------|------|
| **1-E.7** | Disposable SQLite smoke test — call `getSqliteDb()` against a throwaway `./data/test.db` (NOT production), run `drizzle-kit push --dialect sqlite`, verify a round-trip insert/select, then delete the file |
| 1-E.8 | `lessonPointsRouter` pilot — switch its caller to `getActiveDb()`, adapt value conventions (timestamps/booleans/JSON), run the 5 Pilot Success Criteria with `DATABASE_PROVIDER=sqlite` |
| later | Data migration (MySQL → SQLite) — **not started** |
| invariant | **MySQL remains the source of truth** until full cut-over |

---

## Recommendation

✅ **Proceed to Phase 1-E.7 (Disposable SQLite Smoke Test).** The scaffold is in place: driver installed and proven to load, adapter functional, selector created, MySQL still default, zero router/DB changes.

*Scaffold only. No router migrated, no runtime switched, MySQL not removed.*
