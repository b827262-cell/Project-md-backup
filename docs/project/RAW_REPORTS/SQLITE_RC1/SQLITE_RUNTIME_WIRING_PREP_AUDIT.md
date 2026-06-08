# SQLite Runtime Wiring Preparation Audit

> **Phase 1-D.1 — Audit Only / Design Preparation**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **No files were modified. No packages were installed. No SQLite DB was created.**

---

## Summary

| Item | Value |
|------|-------|
| Current schema tables | **66** |
| Current timestamp defaults | **25** |
| Remaining TODO timestamp | **42** |
| Runtime changed | **No** |
| Package installed | **No** |
| SQLite DB created | **No** |

---

## Blocker 1 — server/db.ts

**File:** `server/db.ts` (9,776 lines)

### mysql2 Import

| Line | Import |
|------|--------|
| 2 | `import { drizzle } from "drizzle-orm/mysql2"` |

This is the sole database driver import. Switching to SQLite requires changing to `drizzle-orm/better-sqlite3`.

### insertId Usage (43 occurrences)

MySQL's `INSERT` returns `insertId` in the result set. SQLite's `better-sqlite3` driver returns `lastInsertRowid` instead.

| Category | Count | Example Lines |
|----------|-------|---------------|
| `result[0].insertId` | 30 | L284, L437, L495, L530, L581, L785, L810, L910, … |
| `result.insertId` | 13 | L1411, L1472, L1839, L2232, L2564, L2686, L2742, L2787, L2951, L3298, L3557, L3665, L3906, L4063, L4129, L5930 |

**SQLite equivalent:** `result.lastInsertRowid` (better-sqlite3) or use Drizzle's `.returning({ id: table.id })` pattern (works on both drivers).

### onDuplicateKeyUpdate (3 occurrences)

MySQL-only upsert syntax. SQLite uses `ON CONFLICT ... DO UPDATE`.

| Line | Table | Purpose |
|------|-------|---------|
| 236 | `users` | User upsert on openId |
| 9278 | (unknown) | Insert-or-ignore pattern |
| 9292 | (unknown) | Insert-or-update pattern |

**SQLite equivalent:** Drizzle's `.onConflictDoUpdate()` or `.onConflictDoNothing()`.

### RAND() Usage (5 occurrences)

MySQL `RAND()` → SQLite `RANDOM()`.

| Line | Context |
|------|---------|
| 1554 | `.orderBy(sql`RAND()`)` — random question selection |
| 1601 | `.orderBy(sql`RAND()`)` — random question selection |
| 1607 | `.orderBy(sql`RAND()`)` — random question selection |
| 2551 | `.orderBy(sql`RAND()`)` — random selection |
| 2671 | `.orderBy(sql`RAND()`)` — random selection |

**SQLite equivalent:** `sql`RANDOM()``.

### NOW() / DATE_SUB() Usage (4 occurrences)

MySQL date functions with no SQLite equivalent.

| Line | Expression | Purpose |
|------|-----------|---------|
| 8622 | `DATE_SUB(NOW(), INTERVAL ${days} DAY)` | Credit transaction recent history |
| 8651 | `DATE_SUB(NOW(), INTERVAL 7 DAY)` | Credit transaction weekly stats |

**SQLite equivalent:** `datetime('now', '-' || days || ' days')` or compare Unix timestamps directly: `strftime('%s','now') - (days * 86400)`.

### new Date() Writes (75 occurrences)

Columns where `new Date()` is written directly as a value. In MySQL + Drizzle, `new Date()` is serialized to MySQL datetime string. In SQLite + Drizzle with `mode: "timestamp"`, `new Date()` is automatically converted to Unix seconds. **This mostly works without changes** if the schema column has `{ mode: "timestamp" }`, which is already the case for Convention A columns.

| Category | Count | Examples |
|----------|-------|---------|
| `updatedAt: new Date()` | ~25 | L669, L1057, L1227, L3273, etc. |
| `lastMessageAt: new Date()` | 1 | L432 |
| `createdAt: new Date()` | ~5 | L4661, L4662 |
| `lastSignedIn: new Date()` | 2 | L229, L233 |
| `flaggedAt: new Date()` | 2 | L1332, L1361 |
| Date arithmetic (`new Date()` + offset) | ~15 | L4810, L4844, L4910, etc. |
| Other timestamps | ~25 | Various conditional timestamps |

**Impact:** Low — Drizzle handles `Date` → Unix seconds conversion when `mode: "timestamp"` is set. The `new Date()` writes are compatible.

### Full Blocker Summary

| Blocker | Count | Severity | Migration Effort |
|---------|-------|----------|-----------------|
| `drizzle-orm/mysql2` import | 1 | **Critical** | Change to `drizzle-orm/better-sqlite3` |
| `insertId` | 43 | **High** | Use `.returning()` or adapt to `lastInsertRowid` |
| `onDuplicateKeyUpdate` | 3 | **High** | Change to `.onConflictDoUpdate()` |
| `RAND()` | 5 | **Medium** | Change to `RANDOM()` |
| `DATE_SUB(NOW(), ...)` | 2 | **Medium** | Rewrite to SQLite datetime functions |
| `new Date()` writes | 75 | **Low** | Most auto-handled by Drizzle `mode: "timestamp"` |
| **Total unique blockers** | **6 types** | | |

---

## Blocker 2 — aiQuestionBankRouter.ts

**File:** `server/routers/aiQuestionBankRouter.ts` (5,167 lines)

### mysql2/promise Import

| Line | Import |
|------|--------|
| 9 | `import mysql from "mysql2/promise"` |

### createConnection Usage (5 occurrences)

Direct `mysql2` connection creation, bypassing Drizzle entirely:

| Line | Purpose |
|------|---------|
| 993 | Create goldensun sync job (INSERT raw SQL) |
| 1012 | Get sync job status (SELECT raw SQL) |
| 1023 | Get latest sync job (SELECT raw SQL) |
| 1041 | Cancel sync job (UPDATE raw SQL) |
| 1519 | Run goldensun sync worker (multiple raw SQL ops) |

### Raw SQL Usage

All 5 `createConnection` call sites + 1 `db.execute()` call issue raw SQL against the `goldensun_sync_jobs` table.

| Line | Operation | SQL |
|------|-----------|-----|
| 996-999 | INSERT | `INSERT INTO goldensun_sync_jobs (...)` |
| 1014 | SELECT | `SELECT * FROM goldensun_sync_jobs WHERE id=?` |
| 1025 | SELECT | `SELECT * FROM goldensun_sync_jobs ORDER BY created_at DESC LIMIT 1` |
| 1043 | UPDATE | `UPDATE goldensun_sync_jobs SET status='cancelled' WHERE ...` |
| 1419 | INSERT (db.execute) | Raw SQL via Drizzle execute |
| 1524 | UPDATE | `UPDATE goldensun_sync_jobs SET status=?, started_at=? ...` |
| 1544 | UPDATE | `UPDATE goldensun_sync_jobs SET total_pages=? ...` |
| 1549 | SELECT | `SELECT status FROM goldensun_sync_jobs WHERE id=?` |
| 1590 | INSERT | Raw SQL INSERT for batch import |
| 1596 | UPDATE | `UPDATE goldensun_sync_jobs SET current_page=? ...` |
| 1600 | UPDATE | `UPDATE goldensun_sync_jobs SET status=?, completed_at=? ...` |
| 1631 | UPDATE | `UPDATE goldensun_sync_jobs SET status=?, error_message=? ...` |

### goldensun_sync_jobs Table

- **NOT** in the 66-table SQLite schema (`schema.sqlite.mvp.ts`)
- **NOT** in the MySQL Drizzle schema (`schema.ts`) — only accessed via raw SQL
- This is an admin-only background job management table for crawling `goldensun.get.com.tw` exam archives

### insertId Usage (10 occurrences)

| Line | Pattern | Table |
|------|---------|-------|
| 405, 662 | `(result[0] as any).insertId` | `aiQuestionSources` |
| 877, 934, 2032, 2163, 2563 | `(result[0] as any).insertId` | `aiGeneratedExams` |
| 1000 | `result.insertId` | `goldensun_sync_jobs` (raw SQL) |
| 2935, 3324 | `(attemptResult[0] as any).insertId` | `aiExamAttempts` |

### Is This Lite-Critical?

| Feature | Used by Lite Core? | Assessment |
|---------|---------------------|-----------|
| AI question source management | ❌ Admin-only | Not Lite core |
| AI exam generation | ❌ Admin-only | Not Lite core |
| Goldensun sync/scrape | ❌ Admin-only, external site | Not Lite core |
| Student exam attempts | ⚠️ Potentially used | Check if Lite students use AI exams |
| `aiExamAttempts` table | ❌ Not in 66-table schema | Not available in Lite |

### Recommendation

**Lite stub.** The goldensun sync feature is admin-only and depends on a raw-SQL table (`goldensun_sync_jobs`) that doesn't exist in the SQLite schema. The core Drizzle operations (aiQuestionSources, aiGeneratedExams, aiGeneratedQuestions) ARE in the 66-table schema but are admin-managed content — not student-facing Lite runtime.

**Action:** Keep this router on MySQL (`getDb()`). When Lite server starts with SQLite, this router either:
- (A) Remains pointing to MySQL (dual-mode), or
- (B) Gets stubbed out with `throw new TRPCError({ code: 'NOT_IMPLEMENTED' })` for all admin endpoints

---

## Blocker 3 — learningMaterials.ts

**File:** `server/learningMaterials.ts` (3,713 lines)

### mysql2 Dynamic Import

| Line | Import |
|------|--------|
| 2691 | `const { default: mysql2 } = await import('mysql2/promise')` |

This is a single dynamic import used for one specific operation (auditory playlists).

### Raw SQL Operations (via db.execute)

`db.execute(sql`...`)` is used extensively — these are Drizzle-wrapped raw SQL calls (not direct mysql2 calls), but they contain MySQL-specific syntax.

| Line | Operation | Table | MySQL-Specific? |
|------|-----------|-------|-----------------|
| 1577-1580 | INSERT ... ON DUPLICATE KEY UPDATE | `material_reading_progress` | ✅ `ON DUPLICATE KEY UPDATE` |
| 1593-1595 | SELECT | `material_reading_progress` | ❌ Standard SQL |
| 1610 | SELECT with backtick escaping | `learning_materials` | ⚠️ Backtick escaping |
| 1626 | UPDATE with backtick escaping | `learning_materials` | ⚠️ Backtick escaping |
| 1645-1647 | UPDATE with `NOW()` | `learning_materials` | ✅ `NOW()` |
| 1668-1672 | INSERT | `material_question_attempts` | ⚠️ Raw column names |
| 1713-1715 | UPDATE with `NOW()` | `learning_materials` | ✅ `NOW()` |
| 1765-1768 | SELECT | `material_question_attempts` | ❌ Standard SQL |
| 1943-1945 | SELECT | `qa_cache` | ❌ Standard SQL |
| 2059-2061 | SELECT | `qa_cache` | ❌ Standard SQL |
| 2123-2125 | SELECT | `qa_cache` | ❌ Standard SQL |
| 2144-2146 | SELECT | `qa_cache` | ❌ Standard SQL |
| 2173-2175 | SELECT with `sql.raw()` | `qa_cache` | ⚠️ `sql.raw()` for IN clause |
| 2215-2217 | SELECT with `sql.raw()` | `qa_cache` | ⚠️ `sql.raw()` for IN clause |
| 2244-2246 | SELECT with `sql.raw()` | `learning_materials` | ⚠️ `sql.raw()` for IN clause |
| 2272-2274 | SELECT with `sql.raw()` | `qa_cache` | ⚠️ `sql.raw()` for IN clause |
| 2534 | SELECT | (context-dependent) | ❌ |
| 2609-2611 | INSERT | `auditory_playlists` | ⚠️ Raw SQL INSERT |

### Tables Involved

| Table | In 66-Table Schema? | In MySQL Schema? |
|-------|---------------------|------------------|
| `learning_materials` | ✅ Yes | ✅ Yes |
| `learning_conversations` | ❌ No | ✅ Yes |
| `qa_cache` | ❌ No | ✅ Yes |
| `material_access` | ❌ No | ✅ Yes |
| `class_verifications` | ❌ No | ✅ Yes |
| `material_reading_progress` | ❌ No | ✅ Yes |
| `material_question_attempts` | ❌ No | ✅ Yes |
| `auditory_playlists` | ❌ No | ✅ Yes |

**Only 1 of 8 tables** used by this router is in the 66-table SQLite schema.

### insertId Usage (1 occurrence)

| Line | Pattern | Table |
|------|---------|-------|
| 220 | `material.insertId` | `learning_materials` |

### Recommendation

**Lite stub for raw SQL features; Drizzle operations can be rewritten.**

The router has two layers:
1. **Drizzle layer** (CRUD for `learning_materials`) — compatible with SQLite after fixing `insertId`
2. **Raw SQL layer** (reading progress, question attempts, auditory playlists, qa cache) — depends on 7 tables NOT in the 66-table schema

**Action:** For Lite runtime:
- (A) The basic CRUD operations (list, getById, upload, update, delete) work if `learning_materials` table is pointed to SQLite
- (B) All raw SQL features (reading progress, question attempts, AI chat with cache, auditory playlists) should be **stubbed or kept on MySQL**
- (C) **Preferred approach:** Keep this router on MySQL for now. It depends on too many missing tables.

---

## Risk Table

| # | File | Blocker Type | Runtime Critical | Suggested Action | Risk |
|---|------|-------------|------------------|------------------|------|
| 1 | `server/db.ts` | `drizzle-orm/mysql2` driver import | ✅ **Critical** — all DB operations flow through this | Create `server/db.sqlite.ts` with `drizzle-orm/better-sqlite3` | **High** |
| 2 | `server/db.ts` | `insertId` (43 uses) | ✅ **Critical** — every INSERT returns this | Wrapper function or `.returning()` pattern | **High** |
| 3 | `server/db.ts` | `onDuplicateKeyUpdate` (3 uses) | ✅ **Critical** — user upsert is auth path | `.onConflictDoUpdate()` | **High** |
| 4 | `server/db.ts` | `RAND()` (5 uses) | ⚠️ Medium — random selection | `RANDOM()` | **Low** |
| 5 | `server/db.ts` | `DATE_SUB(NOW(), ...)` (2 uses) | ⚠️ Medium — credit history | SQLite datetime equivalent | **Low** |
| 6 | `server/db.ts` | `new Date()` writes (75 uses) | ✅ Critical — but auto-handled | Drizzle `mode: "timestamp"` handles conversion | **Low** |
| 7 | `aiQuestionBankRouter.ts` | `mysql2/promise` direct import | ❌ Not Lite core | Keep on MySQL or stub | **Low** |
| 8 | `aiQuestionBankRouter.ts` | `createConnection` (5 uses) | ❌ Not Lite core | Keep on MySQL | **Low** |
| 9 | `aiQuestionBankRouter.ts` | `goldensun_sync_jobs` (raw SQL, not in schema) | ❌ Not Lite core | Keep on MySQL | **Low** |
| 10 | `aiQuestionBankRouter.ts` | `insertId` (10 uses) | ❌ Not Lite core | Defer | **Low** |
| 11 | `learningMaterials.ts` | `mysql2/promise` dynamic import (1 use) | ❌ Not Lite core (auditory) | Stub | **Low** |
| 12 | `learningMaterials.ts` | `db.execute()` raw SQL (18 uses) | ⚠️ Partial — basic CRUD is Lite | CRUD: rewrite; raw SQL: keep on MySQL | **Medium** |
| 13 | `learningMaterials.ts` | 7 of 8 tables not in 66-table schema | ⚠️ Partial | Keep router on MySQL until tables added | **Medium** |

---

## Recommended Phase 1-D.2

### Assessment

| Option | Description | Blocks Phase 1-E? | Effort | Risk |
|--------|-------------|-------------------|--------|------|
| **A** | Create `server/db.sqlite.ts` design draft | ✅ **Yes — this IS the Phase 1-E entry point** | Medium (design + wrapper functions) | Low |
| **B** | Handle `aiQuestionBankRouter.ts` mysql2 blocker | ❌ No — admin-only, keep on MySQL | Low (stub only) | Low |
| **C** | Handle `learningMaterials.ts` mysql2 blocker | ❌ No — keep on MySQL for now | Low (stub only) | Low |
| **D** | Add Must-Add indexes to `schema.sqlite.mvp.ts` | ❌ No — indexes are not required for runtime wiring, only for performance | Medium (16 index definitions) | Low |

### Recommendation: **Option A First**

**Create `server/db.sqlite.ts` design draft** — this is the critical path.

**Reasoning:**
1. `server/db.ts` is the **sole database access layer** for all Lite core routers
2. Blockers B and C are **not on the critical path** — both routers can remain on MySQL in dual-mode or be stubbed
3. Indexes (D) improve performance but are not required for initial wiring — they can be added after SQLite is functional
4. The `db.sqlite.ts` file needs to solve the 3 critical patterns: driver import, `insertId` → `lastInsertRowid`, and `onDuplicateKeyUpdate` → `onConflictDoUpdate`

### Suggested `db.sqlite.ts` Design Scope

```
server/db.sqlite.ts
├── Import: drizzle-orm/better-sqlite3
├── Import: schema from drizzle/schema.sqlite.mvp
├── getSqliteDb() — lazy singleton pattern (mirrors getDb())
├── Wrapper: insert() → returning({ id }) pattern
├── Wrapper: upsertUser() → onConflictDoUpdate()
├── Re-export: all 66 table operations
└── RAND() → RANDOM() in sql templates
```

### Suggested Phase 1-D.2 Deliverables

1. **Design document**: `SQLITE_DB_WIRING_DESIGN.md` — the `db.sqlite.ts` interface contract
2. **Pattern catalog**: Each MySQL-specific pattern and its SQLite replacement
3. **Router migration order**: Which 7 core Lite routers switch first

---

## Appendix: Core Lite Router → db.ts Dependency Map

| Router | db.ts Functions Used | MySQL-Specific Patterns | Migration Complexity |
|--------|---------------------|------------------------|---------------------|
| `smartBookRouter.ts` | Many (SmartBook CRUD, progress, credits) | `insertId`, `new Date()` | High (largest router) |
| `smartBookLearningRouter.ts` | Learning sessions, QA, credits | `insertId`, `new Date()` | Medium |
| `lessonPointsRouter.ts` | Lesson points CRUD | `insertId` | Low |
| `tutorRouter.ts` | Tutor sessions, messages | `insertId` | Medium |
| `videoCourseRouter.ts` | Video progress, saved QA | `insertId` | Low |
| `examSetRouter.ts` | Exam sets CRUD | `insertId` | Medium |
| `userManagement.ts` | User CRUD, upsert | `insertId`, `onDuplicateKeyUpdate` | Low |

---

*Audit Only. No files were modified. No packages were installed. No SQLite DB was created.*
