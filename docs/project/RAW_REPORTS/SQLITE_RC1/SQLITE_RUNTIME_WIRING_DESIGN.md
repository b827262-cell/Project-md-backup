# SQLite Runtime Wiring Design

> **Phase 1-D — Design Only / No Runtime Changes**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Basis: `SQLITE_SCHEMA_STUB_EXPANSION_REPORT.md` (66-table draft complete)
> **No db.ts / package / migration / SQLite DB / runtime changes were made.**

---

## Executive Summary

The 66-table schema stub is complete and compile-ready. The next phase (1-E) must resolve three layered blockers before SQLite can power the runtime:

1. **Layer 1 — Driver**: `server/db.ts` hardwires `drizzle-orm/mysql2`; the entire data-access layer must be rewired to `drizzle-orm/better-sqlite3`.
2. **Layer 2 — Raw SQL**: `aiQuestionBankRouter.ts` and `learningMaterials.ts` bypass Drizzle with direct `mysql2/promise` connections; these must be replaced with Drizzle ORM calls.
3. **Layer 3 — SQL dialect differences**: Several MySQL-specific operators inside `db.ts` (`RAND()`, `onDuplicateKeyUpdate`, `insertId`) must be replaced with SQLite equivalents.

The recommended path is **incremental dual-mode support**: create a new `server/db.sqlite.ts` (does not touch `server/db.ts`) and gradually migrate routers to use it, validating each one before cutting over.

---

## DB Layer Design

### Current vs. Future Comparison

| Layer | Current MySQL (`server/db.ts`) | Future SQLite (`server/db.sqlite.ts`) |
|-------|-------------------------------|---------------------------------------|
| **Driver** | `mysql2` (via `DATABASE_URL` MySQL DSN) | `better-sqlite3` (synchronous, file-based) |
| **ORM** | `drizzle-orm/mysql2` | `drizzle-orm/better-sqlite3` |
| **Connection** | Async, network TCP, pooled | Synchronous, local file, single connection |
| **Connection Init** | `drizzle(process.env.DATABASE_URL)` | `drizzle(new Database(process.env.SQLITE_PATH))` |
| **Async Pattern** | `async/await` throughout | Synchronous internally; Drizzle wraps in promise-compatible API |
| **Transaction** | `db.transaction(async (tx) => { ... })` | `db.transaction((tx) => { ... })` (sync callback) |
| **Auto-increment result** | `result[0].insertId` (number) | `result.lastInsertRowid` (BigInt — cast to Number) |
| **Upsert** | `.onDuplicateKeyUpdate({ set: {...} })` | `.onConflictDoUpdate({ target: col, set: {...} })` |
| **Random sort** | `sql\`RAND()\`` | `sql\`RANDOM()\`` |
| **Current timestamp SQL** | `sql\`NOW()\`` / `defaultNow()` | `sql\`(unixepoch())\`` |
| **Migration tool** | `drizzle-kit push` / migration files | `drizzle-kit push --dialect sqlite` |
| **Schema source** | `drizzle/schema.ts` (MySQL) | `drizzle/schema.sqlite.mvp.ts` (SQLite) |
| **Config file** | `drizzle.config.ts` (mysql2 dialect) | New `drizzle.config.sqlite.ts` (sqlite dialect) |

### Proposed `server/db.sqlite.ts` Structure (Design Only)

```typescript
// Design sketch — DO NOT implement yet
import Database from "better-sqlite3";
import { drizzle } from "drizzle-orm/better-sqlite3";
import * as schema from "../drizzle/schema.sqlite.mvp";

let _db: ReturnType<typeof drizzle> | null = null;

export function getSqliteDb() {
  if (!_db) {
    const path = process.env.SQLITE_PATH ?? "./data/smartbook.db";
    const sqlite = new Database(path);
    // WAL mode for concurrent readers
    sqlite.pragma("journal_mode = WAL");
    // Busy timeout prevents SQLITE_BUSY on concurrent writes
    sqlite.pragma("busy_timeout = 5000");
    // FK enforcement
    sqlite.pragma("foreign_keys = ON");
    _db = drizzle(sqlite, { schema });
  }
  return _db;
}
```

Key design decisions encoded in this sketch:
- **WAL mode**: required for VPS Lite (eliminates write-lock reader blocking)
- **busy_timeout 5000ms**: prevents crashes under burst writes
- **foreign_keys ON**: enforces referential integrity from day one
- Schema imported from `schema.sqlite.mvp.ts`, not `schema.ts`

---

## mysql2 Rewrite Design

### File Audit

| File | Current mysql2 Usage | Occurrences | Rewrite Strategy | Difficulty |
|------|---------------------|-------------|------------------|------------|
| `server/db.ts` | Core drizzle instance (`drizzle-orm/mysql2`); MySQL-specific operators throughout 9,777 lines | ~15 dialect-specific patterns | **New file**: Create `server/db.sqlite.ts` as parallel data layer. Migrate function by function. Do NOT delete `db.ts` until full cut-over. | **High** |
| `server/routers/aiQuestionBankRouter.ts` | 5 raw `mysql.createConnection()` calls for `goldensun_sync_jobs` CRUD (lines 993, 1012, 1023, 1041, 1519) | 5 | **Rewrite + stub**: `goldensun_sync_jobs` is a crawler-sync admin feature not needed for Lite. Replace each raw SQL call with either (a) a Drizzle query against a `goldensun_sync_jobs` stub table, or (b) a stub that returns `{ disabled: true }` for Lite. Option (b) is faster. | **Medium** |
| `server/learningMaterials.ts` | 1 dynamic `import('mysql2/promise')` for `auditory_playlists` UPDATE (line 2691) | 1 | **Rewrite**: Dynamic column list can be replaced with Drizzle's `.set()` accepting a partial object. Remove `setCols.push('updated_at = NOW()')` and handle `updatedAt` application-side. | **Low** |

### Detailed Rewrite Notes

#### `server/db.ts` — Dialect Incompatibilities

The following patterns in `db.ts` will fail or produce incorrect results under SQLite:

| Pattern (MySQL) | SQLite Equivalent | Location (sample) |
|----------------|-------------------|-------------------|
| `drizzle(process.env.DATABASE_URL)` | `drizzle(new Database(path))` | Line 175 |
| `import { drizzle } from "drizzle-orm/mysql2"` | `import { drizzle } from "drizzle-orm/better-sqlite3"` | Line 2 |
| `result[0].insertId` | `Number(result.lastInsertRowid)` | Lines 284, 437, 495, 529, etc. |
| `.onDuplicateKeyUpdate({ set })` | `.onConflictDoUpdate({ target: users.openId, set })` | Line 236 |
| `sql\`RAND()\`` | `sql\`RANDOM()\`` | Lines 1554, 1602 |
| `sql\`group_concat(distinct ...)\`` | `sql\`group_concat(distinct ...)\`` | ✅ Same in SQLite |
| `new Date()` in timestamp columns | `Math.floor(Date.now() / 1000)` (Unix seconds) | Lines 229, 668, 1057, etc. |
| `updatedAt: new Date()` | Application-level Unix timestamp | Throughout |
| `date` column compared via `eq(col, today)` where `today` is a `Date` | Use `Math.floor(today.getTime() / 1000)` | Line 627 |

**Estimated scope**: ~15 patterns, spread across all CRUD functions. The refactoring is mechanical (find/replace + type fixes) but large due to file size.

**Recommended approach for Phase 1-E**: Do NOT refactor `db.ts` in place. Instead:
1. Create `server/db.sqlite.ts` with SQLite-specific implementations.
2. Migrate routers one-by-one to import from `db.sqlite.ts`.
3. Keep `db.ts` intact (MySQL fallback) until all routers are migrated.

#### `aiQuestionBankRouter.ts` — Recommended Stub Approach

The 5 raw-SQL calls all target `goldensun_sync_jobs`, which is a crawler admin feature irrelevant to the SmartBook Lite runtime. The simplest Lite-safe rewrite:

```typescript
// Design sketch — replace each raw-mysql2 procedure with:
startSync: adminProcedure
  .mutation(async () => {
    // goldensun_sync not available in SQLite Lite mode
    throw new TRPCError({ code: 'NOT_IMPLEMENTED', message: 'Sync not available in Lite mode' });
  }),
```

If the goldensun sync feature is needed later, a proper `goldensun_sync_jobs` stub table can be added to `schema.sqlite.mvp.ts` and the Drizzle queries restored.

#### `learningMaterials.ts` — Rewrite Pattern

Current (mysql2 raw SQL):
```typescript
const rawSql = `UPDATE auditory_playlists SET ${setCols.join(', ')} WHERE id = ?`;
const conn = await mysql2.createConnection(process.env.DATABASE_URL!);
await conn.execute(rawSql, params);
```

Rewrite (Drizzle ORM, dialect-agnostic):
```typescript
const setPayload: Record<string, unknown> = {};
if (input.title !== undefined) setPayload['title'] = input.title;
// ... other fields ...
setPayload['updatedAt'] = Math.floor(Date.now() / 1000); // unix seconds
const db = getSqliteDb();
await db.update(auditoryPlaylists).set(setPayload).where(eq(auditoryPlaylists.id, input.id));
```

Note: `auditory_playlists` is a "Should Migrate 57" table not in the current 66-table schema. It would need to be added as a stub, or the router section can be stubbed out for Lite.

---

## Timestamp Strategy

All 66 tables in `schema.sqlite.mvp.ts` have `// TODO SQLite timestamp default strategy` markers. A unified strategy must be chosen before Phase 1-E wiring.

### Strategy Options

| Strategy | Mechanism | Pros | Cons | Recommendation |
|----------|-----------|------|------|----------------|
| **A — Application-level `Date.now()`** | All timestamps set in TypeScript before insert/update. No SQL default. | Full control, works identically across any DB. Easy to unit-test. | Every insert must set `createdAt` explicitly. Easy to miss in future code. Requires code changes across all `db.ts` inserts. | Acceptable but fragile |
| **B — `DEFAULT (unixepoch())`** | SQLite column default `DEFAULT (unixepoch())` added to schema. | Automatic for INSERT without explicit value. No app-level code needed. | `unixepoch()` returns Unix **seconds** (not ms). Some tables currently store ms bigints. Mixed precision causes bugs. Drizzle schema syntax: `integer("created_at").default(sql\`(unixepoch())\`)`. | Good for created_at only |
| **C — Hybrid (Recommended)** | `created_at`: `DEFAULT (unixepoch())` via SQL default. `updated_at`: Application-level, set explicitly on each update. ms-timestamp tables (video_*, tutor_*, exam_*): Store raw `Date.now()` as plain integer, no Drizzle timestamp mode. | Best of both: auto-created_at avoids missing inserts, explicit updated_at ensures accuracy, ms tables preserve precision. | Two conventions (seconds vs ms) must be documented. | ✅ **Recommended** |

### Hybrid Strategy Implementation Plan

**Two timestamp conventions (must be documented in `db.sqlite.ts` and enforced via code review):**

| Convention | Tables | Storage | Drizzle Column Mode |
|------------|--------|---------|---------------------|
| Unix seconds | `users`, `conversations`, `messages`, `credit_transactions`, `pdf_categories`, `system_settings`, and all tables originally using `timestamp({ mode: 'string' })` | Unix epoch seconds (`integer`) | `integer("col", { mode: "timestamp" })` |
| Unix milliseconds | `tutor_chat_sessions`, `tutor_chat_messages`, `exam_sets`, `video_*`, `smart_book_category_exam_sources`, and all tables originally using `bigint({ mode: "number" })` | `Date.now()` as plain integer | `integer("col")` (no mode) |

**Schema changes needed in `schema.sqlite.mvp.ts`** (Phase 1-C.8):
- Add `.default(sql\`(unixepoch())\`)` to all `created_at` columns that used `defaultNow()` in MySQL.
- No default for `updated_at` — must be set application-side.

---

## Enum Strategy

All 66 tables have enum columns converted from `mysqlEnum` to `text`. MySQL enforced values at the DB level; SQLite does not.

### Strategy Options

| Strategy | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **A — Zod Application Validation** | Already have tRPC + Zod at every API boundary. Zero schema migration work. Catches bad values at API entry point. | Does not catch values inserted by internal code or direct DB writes (admin scripts, migrations). | ✅ **Recommended for Phase 1-E** |
| **B — SQLite CHECK Constraints** | DB-level enforcement. Guards against all write paths including direct SQL. | Requires `ALTER TABLE` for each enum column (complex in SQLite). Drizzle doesn't generate CHECK constraints from `.default()`. Must be added manually in migration SQL. High migration complexity for ~80+ enum columns. | Defer to Phase 1-G (hardening) |
| **C — Hybrid** | Zod at API boundary (Phase 1-E), CHECK constraints on critical fields only (users.role, etc.) in Phase 1-G. | Adds complexity but is the most correct long-term. | Plan for Phase 1-G |

**Recommendation**: Phase 1-E uses **Option A (Zod only)**. The tRPC routers already validate inputs with Zod. Internal inserts (from `db.ts` helpers) are TypeScript-typed, which prevents most invalid values at compile time.

Critical enum fields that warrant future CHECK constraints (Phase 1-G priority):
- `users.role` — security-sensitive
- `users.subscriptionPlan` — business-critical
- `messages.role` — AI loop correctness
- `smart_book_verifications.status` — flow control

---

## Foreign Key Strategy

### MySQL vs SQLite Difference

| Aspect | MySQL (current) | SQLite (default) | SQLite (with PRAGMA) |
|--------|----------------|------------------|----------------------|
| FK enforcement | InnoDB: enforced by default | Disabled by default | Enforced when `PRAGMA foreign_keys = ON` set per-connection |
| Cascade on DELETE | Declarative in schema | Declarative in schema, only works if PRAGMA is ON | Works when PRAGMA is ON |
| Impact of missing FK | MySQL rejects the insert | SQLite silently accepts the insert | SQLite rejects the insert |

### Current Schema FK Status

The MySQL `schema.ts` has **no explicit `references()` FK declarations** in Drizzle syntax — all FK relationships are documented only as code comments. This means:
- MySQL was not enforcing FK constraints via Drizzle schema (they would need to be declared separately).
- SQLite behavior matches current MySQL behavior (FK not enforced by Drizzle schema).

### Recommendation

**Enable `PRAGMA foreign_keys = ON`** at connection init time in `server/db.sqlite.ts`.

Rationale:
- The 66-table schema has clear logical FK relationships (documented as comments).
- Enabling FK enforcement catches orphaned records early.
- No existing Drizzle `references()` declarations means no FK constraint migration complexity.
- However, initial data migration (Phase 1-F) must insert records in correct dependency order (parent before child) to avoid FK violations.

**Risk**: If Phase 1-F data migration inserts in wrong order, FK enforcement will block it. Mitigation: Temporarily disable `PRAGMA foreign_keys = OFF` during bulk import, then re-enable.

---

## Index Strategy

No indexes are currently defined in `schema.sqlite.mvp.ts`. The following table classifies the most critical indexes by query frequency and table size.

### Priority Index List

| Table | Index Column(s) | Priority | Reason |
|-------|-----------------|----------|--------|
| `conversations` | `userId` | **Must Add** | Every conversation list query filters by userId |
| `conversations` | `lastMessageAt` | **Must Add** | Timeline sort on homepage |
| `messages` | `conversationId` | **Must Add** | Every message load joins on this |
| `users` | `openId` | **Must Add** | Auth lookup on every request |
| `users` | `email` | High | Login by email |
| `smart_books` | `isPublic`, `processingStatus` | **Must Add** | Book list queries filter on both |
| `smart_book_chapters` | `bookId` | **Must Add** | Chapter load always filters by bookId |
| `smart_book_conversations` | `bookId, userId` | **Must Add** | Per-user per-book chat history |
| `smart_book_progress` | `bookId, userId` | **Must Add** | Progress lookup on every page load |
| `smart_book_review_questions` | `bookId, chapterId` | **Must Add** | Quiz question fetch |
| `smart_book_wrong_answers` | `userId, bookId` | **Must Add** | Error book lookup |
| `lesson_points` | `bookId, chapterId` | **Must Add** | Guided learning point fetch |
| `lesson_progress` | `userId, chapterId` | **Must Add** | Per-user lesson progress |
| `tutor_chat_sessions` | `userId`, `smartBookId` | **Must Add** | Session list per user/book |
| `tutor_chat_messages` | `sessionId` | **Must Add** | Message load for session |
| `credit_transactions` | `userId` | High | Transaction history |
| `smart_book_credits` | `bookId, userId` | High | Credit balance lookup |
| `user_usage_stats` | `userId, date` | High | Daily stats lookup |
| `book_suggestion_cache` | `bookId` | Medium | Suggestion fetch |
| `smart_book_question_shown` | `userId, chapterId` | Medium | Quiz dedup check |
| `smart_book_qa_viewed` | `userId, bookId` | Medium | QA view dedup |
| `smart_book_chapter_daily_verifications` | `bookId, userId, verifiedDate` | Medium | Daily verification check |
| `exam_sets` | `smartBookId`, `isPublished` | Medium | Exam set list |
| `exam_set_questions` | `examSetId` | Medium | Question list per set |
| `video_units` | `courseId` | Medium | Unit list per course |
| `video_progress` | `userId, unitId` | Medium | Progress per user/unit |
| `practice_wrong_book` | `userId, sourceType` | Medium | Wrong book list |
| `system_settings` | `key` | Medium | Settings lookup by key |
| `page_text_cache` | `bookId, page` | Low | Page cache lookup |
| `real_exam_questions` | `sourceId`, `year`, `subject` | Low | Exam question filter |

**Phase 1-E action**: Add **Must Add** indexes to `schema.sqlite.mvp.ts` before first runtime connection test. Add **High** priority before production launch. **Medium/Low** indexes can be deferred.

---

## Phase 1-E Wiring Plan

Phase 1-E installs the driver and wires the runtime. Do NOT begin until Phase 1-D design is reviewed.

### Work Breakdown

#### 1. Install SQLite Driver

```bash
pnpm add better-sqlite3
pnpm add -D @types/better-sqlite3
```

No other packages required. `drizzle-orm` already supports `better-sqlite3`.

#### 2. Create `server/db.sqlite.ts`

New file. Does **not** replace `server/db.ts` yet. Implements:
- `getSqliteDb()` function (synchronous connection, WAL mode, FK ON)
- Exports the same function signatures as `db.ts` but implemented for SQLite
- Start with the 5 most-used functions: `getUserByOpenId`, `upsertUser`, `getConversationsByUserId`, `createMessage`, `getMessagesByConversationId`

#### 3. Add Must-Add Indexes to `schema.sqlite.mvp.ts`

Add the ~15 Must Add indexes identified above before first compile test.

#### 4. Create `drizzle.config.sqlite.ts`

```typescript
// Design sketch
import type { Config } from "drizzle-kit";
export default {
  schema: "./drizzle/schema.sqlite.mvp.ts",
  out: "./drizzle/migrations/sqlite",
  dialect: "sqlite",
  dbCredentials: { url: process.env.SQLITE_PATH ?? "./data/smartbook.db" },
} satisfies Config;
```

#### 5. Rewrite mysql2 Blockers

In parallel with step 3:
- `aiQuestionBankRouter.ts`: Replace 5 raw mysql2 calls with `NOT_IMPLEMENTED` stubs (goldensun sync is Lite-excluded).
- `learningMaterials.ts`: Replace 1 raw mysql2 call with Drizzle `.update().set()` pattern.

#### 6. Compile Validation

```bash
pnpm tsc --noEmit
```

Expected result: zero errors related to SQLite schema imports. Remaining errors will be MySQL-specific type mismatches in `db.ts` (acceptable — `db.ts` is MySQL-only).

#### 7. First Smoke Test

```bash
# Create empty SQLite DB
mkdir -p data
SQLITE_PATH=./data/smartbook.test.db node -e "
  const db = require('./server/db.sqlite').getSqliteDb();
  console.log('SQLite connected:', !!db);
"
```

#### 8. Router-by-Router Migration

Migrate routers in order of Lite priority:
1. `auth` / user management
2. `smartBookStudent` / `smartBookAdmin`
3. `tutorChat` / `tutorPublic`
4. `conversations`
5. Remaining routers

Each router: update import from `../../server/db` → `../../server/db.sqlite`, run compile, run smoke test.

---

## Phase 1-F Data Migration Plan

Phase 1-F moves production data from MySQL to SQLite. Do NOT begin until Phase 1-E is complete and validated.

### Migration Architecture

```
MySQL Production DB
       ↓
  Export Script
  (Node.js, reads via mysql2 from MySQL, writes to SQLite)
       ↓
  Transform Layer
  (timestamp conversion, enum normalization, NULL cleanup)
       ↓
  SQLite Database
  (./data/smartbook.db)
       ↓
  Validation
  (row counts, spot checks)
```

### Table Migration Order (respects FK dependencies)

Tier 1 — No foreign keys:
`users`, `system_settings`, `tags`, `pdf_categories`, `smart_book_categories`, `tutor_subjects`, `exam_categories`

Tier 2 — Depend on Tier 1:
`conversations`, `credit_rules`, `smart_books`, `exam_subjects`, `ai_question_sources`, `tutor_subject_books`, `exam_sets`

Tier 3 — Depend on Tier 2:
`messages`, `conversation_files`, `conversation_tags`, `credit_transactions`, `user_usage_stats`, `smart_book_chapters`, `smart_book_settings`, `smart_book_verifications`, `smart_book_credits`, `smart_book_category_exam_sources`, `exam_questions`, `exam_set_questions`, `ai_generated_exams`, `tutor_chat_sessions`, `tutor_subject_exam_sources`, `tutor_subject_video_courses`, `video_courses`, `learning_materials`

Tier 4 — Depend on Tier 3:
All remaining tables.

### Data Transformation Rules

| MySQL Type | SQLite Conversion |
|------------|------------------|
| `timestamp` string (`"2024-01-01 12:00:00"`) | `Math.floor(new Date(str).getTime() / 1000)` → Unix seconds |
| `bigint` ms timestamp | Pass through as-is (plain integer) |
| `tinyint` 0/1 | Pass through as-is (Drizzle boolean mode reads 0/1 correctly) |
| `json` string | Pass through as-is (already a JSON string in MySQL) |
| `NULL` | Pass through as-is |
| `varchar` / `text` | Pass through as-is |

### Migration Script Design (Phase 1-F)

```
scripts/migrate-mysql-to-sqlite.ts (Design Only)
  1. Connect to MySQL (read-only)
  2. Connect to SQLite (write)
  3. For each table in tier order:
     a. SELECT * FROM mysql_table
     b. Transform each row per rules above
     c. INSERT INTO sqlite_table (batch 1000 rows at a time)
     d. Log row counts
  4. Run validation queries
  5. Print summary report
```

---

## Risk Analysis

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| `db.ts` refactor introduces regressions in MySQL mode | High | Medium | Keep `db.ts` unchanged; run parallel dual-mode. MySQL `db.ts` remains live. |
| Timestamp unit mismatch (seconds vs ms) causes display bugs | High | High | Document two-convention rule clearly; add runtime assertion in `getSqliteDb()`. |
| `onDuplicateKeyUpdate` → `onConflictDoUpdate` migration missed | Medium | Medium | Grep all usages in `db.ts` before each function migration. |
| WAL mode SQLite file not writable on VPS | Medium | Low | Ensure `data/` directory has write permissions before deploy. |
| `RAND()` → `RANDOM()` missed in a query | Medium | Low | Grep audit before Phase 1-E. |
| FK violations during Phase 1-F bulk import | Medium | High | Disable FK PRAGMA during import, re-enable after. |
| `result[0].insertId` not replaced → returns undefined | Medium | High | TypeScript will flag this since better-sqlite3 returns different result shape. Compile validation will catch it. |
| `better-sqlite3` native binding fails on VPS Node version | Medium | Low | Verify Node version compatibility (requires Node ≥ 14, needs `node-gyp`). |
| `group_concat` dialect difference | Low | Low | `group_concat` works in both MySQL and SQLite. No change needed. |
| SQLite single-writer bottleneck under load | Low | Low | VPS Lite is single-user or low-concurrency. WAL mode handles concurrent reads. |

**Overall Risk Level: Medium** — manageable with the incremental dual-mode approach.

---

## Recommendation

### Summary Recommendations

| Decision | Recommendation | Rationale |
|----------|----------------|-----------|
| **SQLite Driver** | `better-sqlite3` | Native performance, synchronous API, Drizzle official support |
| **Timestamp Strategy** | Hybrid (Option C) — `DEFAULT (unixepoch())` for `created_at`, application-level for `updated_at` | Avoids missing timestamp bugs on insert; preserves ms precision for existing ms-timestamp tables |
| **Enum Strategy** | Zod-only (Option A) for Phase 1-E; CHECK constraints in Phase 1-G hardening | tRPC Zod already covers API boundary; incremental approach avoids schema migration complexity |
| **Foreign Key Enforcement** | Enable `PRAGMA foreign_keys = ON` at connection init | No existing Drizzle `references()` declarations so no schema complexity; catches referential integrity bugs early |
| **Index strategy** | Add ~15 Must-Add indexes to schema before Phase 1-E | Critical for query performance at SmartBook Lite scale |
| **mysql2 Blockers** | Parallel new file (`db.sqlite.ts`) + stubs for goldensun sync | Zero risk to existing MySQL runtime during transition |

### Is Phase 1-E Wiring Ready to Begin?

**YES — conditional on completing these pre-flight steps:**

- [ ] Add Must-Add indexes to `schema.sqlite.mvp.ts` (Phase 1-C.8)
- [ ] Add timestamp SQL defaults (`DEFAULT (unixepoch())`) to Phase 1-C.8
- [ ] Install `better-sqlite3` package (`pnpm add better-sqlite3`)
- [ ] Create empty `data/` directory on VPS for SQLite file
- [ ] Confirm VPS Node.js version ≥ 14 (for `better-sqlite3` native bindings)

---

*Design Only. No db.ts / schema.ts / package / migration / SQLite DB / runtime changes were made in this phase.*
