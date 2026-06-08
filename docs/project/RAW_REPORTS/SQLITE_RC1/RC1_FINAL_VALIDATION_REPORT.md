# RC1 Final Validation Report

**Date:** 2026-06-04  
**Branch:** `release/vps-lite`  
**Node:** v20.20.2  
**Scope:** Audit Only — No code/schema/runtime/router/package.json modifications

---

## Executive Summary

```text
RC1_DEPLOY_READY = CONDITIONAL YES
```

The SmartBook Lite SQLite RC1 build **can boot and serve the 4 core routers** (SmartBook, Tutor, LessonPoints, SmartBookLearning) in SQLite mode. However, deployment requires **mysql2 to remain installed** as a package dependency due to static imports, and several non-core routers will throw runtime errors if invoked in SQLite mode. The core MVP feature set is functional.

---

## PASS / FAIL Matrix

| # | Validation Item | Result | Details |
|---|-----------------|--------|---------|
| 1 | `auth.registerLocal` | ✅ **PASS** | `localAuth.ts` is dual-mode aware. `usersTable()` switches between MySQL/SQLite schema. `createLocalUser()` uses explicit `createdAt`/`updatedAt` (no `defaultNow()`). Password hashing via scrypt. |
| 2 | `auth.loginLocal` | ✅ **PASS** | `getLocalUserByLogin()` queries via Drizzle ORM on whichever driver is active. `verifyPassword()` is pure crypto — no DB dependency. `updateLocalLastSignIn()` is dual-safe. |
| 3 | SmartBook CRUD | ✅ **PASS** | `smartBookRouter.ts` (5,947 lines) imports from MySQL schema but runs through dual-mode `getDb()`. Uses `normalizeInsertId()`, `isSqliteMode()` helpers. Previous `NOW()` blockers cleared by RC1-Fix-A. P0 = 0. |
| 4 | Tutor Session CRUD | ✅ **PASS** | `tutorRouter.ts` (4,972 lines) uses `normalizeInsertId`, `isSqliteMode`, `sqliteRandom`, `toSqliteTimestamp` from `db.sqlite.ts`. No remaining P0 blockers. Structural `db.execute()` sites are non-blocking cleanup candidates. |
| 5 | TRPC Endpoint | ✅ **PASS** | 47+ sub-routers registered in `appRouter`. All connected via `createExpressMiddleware` at `/api/trpc`. Schema is valid, routing is complete. |
| 6 | Home Page | ⚠️ **CONDITIONAL PASS** | Client-side rendering is not DB-dependent. Pages that call non-migrated routers (calendar, watermark, ibrain, etc.) will fail on data fetch but won't crash the app. |
| 7 | Health API | ✅ **PASS** | `system.health` is a public TRPC query returning `{ ok: true }`. Simple ping — does NOT verify DB connectivity (by design for liveness checks). |
| 8 | Production Runtime Boot | ⚠️ **CONDITIONAL PASS** | App boots in SQLite mode (`DATABASE_PROVIDER=sqlite`). **Requirement:** `mysql2` npm package must remain installed — `db.ts` line 2 has static `import { drizzle as drizzleMysql } from "drizzle-orm/mysql2"` that executes unconditionally. No MySQL **server** connection needed. |
| 9 | RSS / CPU / Memory | ✅ **PASS (projected)** | PM2 config: `max_memory_restart: 450M`, `--max-old-space-size=384`. SQLite (in-process) eliminates MySQL server resident memory (~250-500MB savings). `better-sqlite3` is synchronous — no connection pool overhead. WAL mode enables concurrent reads. |

---

## Detailed Findings

### 1. Auth — `auth.registerLocal` / `auth.loginLocal`

**Status: PASS**

| Check | Result |
|-------|--------|
| Dual-mode table selector | ✅ `usersTable()` → `isSqliteMode() ? sqliteUsers : mysqlUsers` |
| Explicit timestamps | ✅ `createdAt: now, updatedAt: now` — no `defaultNow()` |
| Password hash | ✅ `scrypt` + `timingSafeEqual` — pure Node crypto |
| Login lookup | ✅ `getLocalUserByLogin()` — Drizzle ORM, works on both drivers |
| Admin seeding | ✅ `seedDefaultAdminIfNeeded()` — dual-safe with explicit timestamps |

Reference: [`localAuth.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/localAuth.ts)

### 2. SmartBook CRUD

**Status: PASS**

Previous P0 blockers (`NOW()` = 4 occurrences) resolved by RC1-Fix-A.

| Check | Count |
|-------|-------|
| `insertId` blocker | 0 |
| `onDuplicateKeyUpdate` | 0 |
| `RAND()` blocker | 0 |
| `DATE_SUB()` blocker | 0 |
| `NOW()` blocker | 0 |
| MySQL-only execute | 0 |
| result-shape blocker | 0 |

Date comparisons are mode-aware: SQLite uses `date(column, 'unixepoch')`, MySQL uses `DATE(column)`.

Reference: [`smartBookRouter.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/routers/smartBookRouter.ts)

### 3. Tutor Session CRUD

**Status: PASS**

| Check | Count |
|-------|-------|
| P0 blockers | 0 |
| Dual-mode helpers used | ✅ `normalizeInsertId`, `isSqliteMode`, `sqliteRandom`, `toSqliteTimestamp` |
| Structural cleanup candidates | 8 (P2, non-blocking) |

Reference: [`tutorRouter.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/routers/tutorRouter.ts)

### 4. Lesson Points

**Status: PASS**

| Check | Result |
|-------|--------|
| Boolean mode | ✅ Uses `{ mode: "boolean" }` |
| Timestamp mode | ✅ Explicit timestamp handling |
| P0 blockers | 0 |

Reference: [`lessonPointsRouter.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/routers/lessonPointsRouter.ts)

### 5. SmartBook Learning

**Status: PASS**

| Check | Result |
|-------|--------|
| Dual-mode helpers | ✅ `normalizeInsertId`, `isSqliteMode` |
| P0 blockers | 0 |

Reference: [`smartBookLearningRouter.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/routers/smartBookLearningRouter.ts)

### 6. TRPC Endpoint Architecture

**Status: PASS**

- 47+ sub-routers properly registered on `appRouter`
- All using `publicProcedure`, `protectedProcedure`, or `adminProcedure`
- Express middleware: `createExpressMiddleware` at `/api/trpc`
- Health endpoint: `system.health` → `{ ok: true }`

Reference: [`routers.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/routers.ts)

### 7. Production Runtime Boot

**Status: CONDITIONAL PASS**

Boot sequence in SQLite mode:

```text
1. db.ts loads → static import of drizzle-orm/mysql2 (always runs, needs mysql2 pkg)
2. db.sqlite.ts loads → better-sqlite3 adapter ready
3. getDb() called → isSqliteMode() = true → getSqliteDb()
4. SQLite PRAGMAs applied → WAL, busy_timeout=5000, foreign_keys=ON
5. Drizzle instance created with schema.sqlite.mvp tables
6. Router imports succeed → app boots
```

**Requirement**: `mysql2` npm package **MUST remain in `node_modules`** even if no MySQL server is used.

Reason: `db.ts` line 2 — `import { drizzle as drizzleMysql } from "drizzle-orm/mysql2"` is a static top-level import. Removing `mysql2` will crash the Node process at startup with `MODULE_NOT_FOUND`.

### 8. SQLite Adapter Quality

**Status: PASS**

| Component | Assessment |
|-----------|------------|
| [`db.sqlite.ts`](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/server/db.sqlite.ts) | Clean adapter, lazy singleton, proper PRAGMAs |
| `getSqliteDb()` | Correct WAL + busy_timeout + foreign_keys |
| `normalizeInsertId()` | Handles both `lastInsertRowid` (SQLite) and `insertId` (MySQL) |
| `sqliteRandom()` | `RANDOM()` vs `RAND()` |
| `sqliteDateSubDays()` | `strftime('%s','now') - N*86400` vs `DATE_SUB(NOW(), INTERVAL N DAY)` |
| `toSqliteTimestamp()` | Unix seconds vs Date object |

### 9. Memory Projection

| Component | MySQL Mode | SQLite Mode | Savings |
|-----------|-----------|-------------|---------|
| MySQL Server | ~250-500 MB RSS | 0 (eliminated) | **250-500 MB** |
| Node Process | ~150-250 MB | ~150-250 MB | 0 |
| SQLite in-process | 0 | ~10-30 MB | -10-30 MB |
| **Total VPS** | **400-750 MB** | **160-280 MB** | **~250-470 MB** |

PM2 limits: `max_memory_restart=450M`, `--max-old-space-size=384` — appropriate for 1GB VPS.

---

## Known Limitations (Non-Blocking for Core MVP)

### P0 — Resolved

```text
Count: 0
```

No P0 blockers remain for the 4 core routers.

### P1 — Non-Core Routers (2 items)

| Item | Impact |
|------|--------|
| `server/db.ts` line 2: static `drizzle-orm/mysql2` import | Requires `mysql2` npm pkg to remain installed |
| `aiQuestionBankRouter.ts` line 9: static `mysql2/promise` import | Requires `mysql2` npm pkg to remain installed |

**Mitigation**: Keep `mysql2` in `package.json` dependencies. No MySQL server needed.

### P2 — Non-Migrated Routers (will throw on invocation)

These routers import tables from MySQL schema that do **not** exist in `schema.sqlite.mvp.ts`. They will fail at runtime if invoked but **will NOT crash the server at boot**:

| Router | Missing Tables |
|--------|---------------|
| `watermarkRouter` | `watermarkSettings` |
| `adminConversationsRouter` | `userWarnings` |
| `ibrainPackage` | `ibrainPackages`, `ibrainQuestions` |
| `calendarRouter` | `calendarEvents` |
| `apiKeyRouter` | `apiKeys`, `apiKeyUsageLogs` |
| `essayGradingRouter` | `essaySubmissions`, `essayGradings` |
| `studentLearningRouter` | `studentLearningSessions`, `studentBehaviorAlerts` |
| `checklistRouter` | `checklistSubmissions` |
| `learningMaterials` (auditoryHall) | `materialAccess`, dynamic `mysql2` import |

**Impact**: These are auxiliary features not part of the core SmartBook Lite MVP. They represent runtime errors only when those specific endpoints are hit — the server will not crash at boot.

### P3 — Deployment Config Gaps

| Item | Status |
|------|--------|
| `ecosystem.config.cjs` missing `DATABASE_PROVIDER=sqlite` | Must be set via `.env` or shell |
| `ecosystem.config.cjs` missing `SQLITE_PATH` | Must be set via `.env` or shell |
| `.env` has no `DATABASE_PROVIDER` or `SQLITE_PATH` | Must be added before deployment |
| Dockerfile missing SQLite env vars | Must be added if using Docker |

---

## Pre-Deployment Checklist

```text
[ ] Add DATABASE_PROVIDER=sqlite to .env
[ ] Add SQLITE_PATH=./data/smartbook.db to .env
[ ] Ensure ./data/ directory exists and is writable
[ ] Keep mysql2 in package.json (do NOT remove)
[ ] Run SQLite migration: pnpm db:sqlite:push:fresh
[ ] Verify better-sqlite3 native module loads on target OS
[ ] Verify PM2 env passes DATABASE_PROVIDER correctly
```

---

## Final Verdict

```text
╔══════════════════════════════════════════════════════════╗
║  RC1_DEPLOY_READY = CONDITIONAL YES                     ║
║                                                         ║
║  Conditions:                                            ║
║  1. mysql2 npm package MUST remain installed             ║
║  2. DATABASE_PROVIDER=sqlite must be set in .env         ║
║  3. SQLITE_PATH must be set in .env                      ║
║  4. ./data/ directory must exist and be writable          ║
║  5. Non-core routers may throw if invoked                 ║
║                                                         ║
║  Core MVP (Auth + SmartBook + Tutor + LessonPoints       ║
║  + SmartBookLearning + Health) = ALL PASS                ║
╚══════════════════════════════════════════════════════════╝
```

---

## Validation Scope Summary

| Category | Items Validated | Result |
|----------|----------------|--------|
| Auth (register + login) | `localAuth.ts`, dual-mode users table | ✅ PASS |
| SmartBook CRUD | `smartBookRouter.ts`, 0 P0 blockers | ✅ PASS |
| Tutor Session CRUD | `tutorRouter.ts`, dual-mode helpers | ✅ PASS |
| LessonPoints | `lessonPointsRouter.ts`, boolean/timestamp mode | ✅ PASS |
| SmartBook Learning | `smartBookLearningRouter.ts`, dual-mode | ✅ PASS |
| TRPC Endpoints | 47+ routers, proper registration | ✅ PASS |
| Home Page | Client renders, data fetches for non-core may fail | ⚠️ CONDITIONAL |
| Health API | `system.health` → `{ ok: true }` | ✅ PASS |
| Production Boot | Boots with SQLite, needs mysql2 pkg | ⚠️ CONDITIONAL |
| Memory | ~250-470 MB savings projected | ✅ PASS (projected) |
