# SQLite DB Adapter Draft Report

> **Phase 1-D.2 — Design Draft Only / No Runtime Wiring**
> Generated: 2026-06-03 · Branch: `release/vps-lite`

---

## Summary

| Item | Value |
|------|-------|
| `server/db.sqlite.ts` created | **Yes** |
| Runtime wired | **No** |
| `better-sqlite3` installed | **No** |
| `package.json` modified | **No** |
| `server/db.ts` modified | **No** |
| `drizzle/schema.sqlite.mvp.ts` modified | **No** |
| `drizzle/schema.ts` modified | **No** |
| Any router modified | **No** |
| SQLite DB created | **No** |

---

## Design Contents

### Environment Variables

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `DATABASE_PROVIDER` | `"sqlite" \| "mysql"` | — | Selects active database driver |
| `SQLITE_PATH` | `string` | `./data/smartbook.db` | Path to SQLite database file |

### Stub Functions

| Function | Return Type | Status |
|----------|-------------|--------|
| `getSqlitePath()` | `string` | ✅ Implemented (reads env) |
| `isSqliteMode()` | `boolean` | ✅ Implemented (reads env) |
| `getSqliteDbDesignOnly()` | `never` | ✅ Stub — throws Error |
| `normalizeInsertId(result)` | `number` | ✅ Stub — throws Error |
| `sqliteRandom()` | `SQL` | ✅ Stub — throws Error |
| `sqliteNowSeconds()` | `SQL` | ✅ Stub — throws Error |
| `toSqliteTimestamp(date)` | `Date \| number` | ✅ Stub — throws Error |
| `sqliteDateSubDays(days)` | `SQL` | ✅ Stub — throws Error |

### Type Definitions

| Type | Purpose |
|------|---------|
| `SqliteDbMode` | `"disabled" \| "enabled"` flag |
| `SqliteEnvContract` | Interface for required env vars |
| `SqliteDb` | Placeholder for `BetterSQLite3Database<typeof schema>` |

### Future PRAGMA Plan

| PRAGMA | Value | Purpose |
|--------|-------|---------|
| `journal_mode` | `WAL` | Write-Ahead Logging for concurrent reads |
| `busy_timeout` | `5000` | 5s wait on DB lock before SQLITE_BUSY |
| `foreign_keys` | `ON` | Enable FK constraint enforcement |
| `synchronous` | `NORMAL` | (Phase 1-G) Balance safety/speed with WAL |
| `cache_size` | `-64000` | (Phase 1-G) 64MB page cache |

### Future Drizzle Driver Plan

```
Phase 1-E will use:
  import Database from "better-sqlite3";
  import { drizzle } from "drizzle-orm/better-sqlite3";

Schema source:
  import * as schema from "../drizzle/schema.sqlite.mvp";

Drizzle instance:
  drizzle(sqliteConnection, { schema })
```

### MySQL → SQLite Compatibility Helpers

| Helper | MySQL Pattern | SQLite Pattern |
|--------|--------------|----------------|
| `normalizeInsertId()` | `result[0].insertId` | `result.lastInsertRowid` or `.returning()` |
| `sqliteRandom()` | `sql\`RAND()\`` | `sql\`RANDOM()\`` |
| `sqliteNowSeconds()` | `sql\`UNIX_TIMESTAMP()\`` | `sql\`(strftime('%s','now'))\`` |
| `toSqliteTimestamp()` | `new Date()` → datetime string | `new Date()` → Unix seconds (auto by Drizzle) |
| `sqliteDateSubDays()` | `DATE_SUB(NOW(), INTERVAL n DAY)` | `strftime('%s','now') - n * 86400` |
| Upsert (pattern, not helper) | `.onDuplicateKeyUpdate()` | `.onConflictDoUpdate()` |

---

## Verification

```
grep -n "^import.*from.*better-sqlite3" server/db.sqlite.ts
→ (none) ✅ No real import of better-sqlite3

grep -n "^import.*from.*drizzle-orm/better-sqlite3" server/db.sqlite.ts
→ (none) ✅ No real import of drizzle-orm/better-sqlite3

grep -n "new Database" server/db.sqlite.ts
→ Only in comment (line 94) ✅

grep -n "getSqliteDbDesignOnly" server/db.sqlite.ts
→ line 106 ✅ Exists

git diff --name-only
→ (empty) ✅ No tracked files modified
```

---

## Blockers Remaining

| # | Blocker | Severity | Phase |
|---|---------|----------|-------|
| 1 | `better-sqlite3` package not installed | **Critical** | Phase 1-E.0 |
| 2 | `server/db.ts` still MySQL-only (9,776 lines, 43 insertId, 3 onDuplicateKeyUpdate, 5 RAND) | **Critical** | Phase 1-E |
| 3 | All 7 core Lite routers still import from `server/db.ts` | **Critical** | Phase 1-E |
| 4 | `aiQuestionBankRouter.ts` uses `mysql2/promise` directly (5 createConnection, 12 raw SQL) | **Medium** | Keep on MySQL or stub |
| 5 | `learningMaterials.ts` uses `mysql2/promise` dynamically + 18 raw SQL calls, 7/8 tables not in schema | **Medium** | Keep on MySQL or stub |
| 6 | Must-Add indexes not added yet (16 definitions on 13 tables) | **Medium** | Phase 1-D.3 or post-wiring |
| 7 | 42 remaining TODO timestamp markers (P1/P2/Defer — not blocking) | **Low** | Phase 1-F or deferred |

---

## Recommended Next Step

### Option A: Phase 1-D.3 — SQLite Index Patch

Add the 16 Must-Add index definitions to `schema.sqlite.mvp.ts`. This is a schema-only change (no runtime) and completes the pre-Phase-1-E schema hardening. Indexes are needed before production load testing but are not strictly required for initial wiring.

### Option B: Phase 1-E.0 — better-sqlite3 Installation Planning

Create an installation plan document that specifies:
- Package versions (`better-sqlite3@^11.x`, `@types/better-sqlite3@^7.x`)
- Node.js native binding requirements
- VPS build dependencies (`build-essential`, `python3`)
- Installation verification steps

### Recommendation

**Option B (Phase 1-E.0)** — The `db.sqlite.ts` design draft is complete. The next logical step is to plan the `better-sqlite3` installation so that Phase 1-E can begin immediately after approval. Indexes (Option A) can be added in parallel or after wiring, as they do not block the initial connection.

---

*Design Draft Only. No runtime files were modified. No packages were installed. No SQLite DB was created.*
