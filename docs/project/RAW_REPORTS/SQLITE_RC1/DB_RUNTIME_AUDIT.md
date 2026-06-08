# DB Runtime Readiness Audit

Phase: 1-K.0 db.ts Runtime Readiness Audit
Target: `server/db.ts`
Scope: Audit only. No patch, build, migration, schema change, or runtime wiring change.

## 1. Executive Summary

`server/db.ts` is not SQLite-runtime ready yet. It is still bound to the MySQL Drizzle driver and contains many MySQL insert result shape assumptions.

Key findings:

- Total lines: 9,776
- Runtime driver import: `drizzle-orm/mysql2` x1
- `createPool`: 0
- `createConnection`: 0
- `PoolConnection`: 0
- `insertId`: 43 sites
- `.onDuplicateKeyUpdate(...)`: 3 sites
- `RAND()`: 5 sites
- `DATE(...)`: 3 sites
- `DATE_SUB(...)`: 2 sites
- `NOW()`: 2 sites
- raw `sql```: 47 sites
- `.execute(...)`: 8 sites
- `.query(...)`: 0 sites
- `.transaction(...)`: 4 sites
- `JSON.stringify`: 3 sites
- `JSON.parse`: 1 site

P0 runtime blockers remain and should be patched before RC1 SQLite runtime validation.

Recommended risk level: High.

## 2. Runtime Inventory

### Driver and Runtime Wiring

Current runtime binding:

- `import { drizzle } from "drizzle-orm/mysql2";`
- `_db: ReturnType<typeof drizzle> | null`
- `getDb()` lazily calls `drizzle(process.env.DATABASE_URL)`

Classification: P0

Reason: This file currently constructs a MySQL Drizzle runtime only. SQLite provider support requires provider-aware driver selection and typing.

### Helper Count Inventory

Runtime/helper functions identified: 6

- `getDb`
- `updateUserQuestionStats`
- `textOrEmpty`
- `sanitizeQuestionBankRow`
- `sanitizeExamQuestionRow`
- `getColorForCategory`

SQLite compatibility helpers currently present in `db.ts`: 0

Missing helper candidates:

- `normalizeInsertId(...)`
- `sqliteRandom(...)`
- `isSqliteMode(...)`
- `sqliteDate(...)` or date-range helper
- provider-aware execute/result normalizer

### Insert Return Inventory

`insertId`: 43 sites

Patterns:

- `result[0].insertId`
- `Number(result[0].insertId)`
- `result.insertId`
- `Number(result.insertId)`
- `newProgress.insertId`
- insert result used for immediate re-select by id

Classification: P0

Reason: MySQL insert result shape is not portable to SQLite Drizzle.

### Raw SQL Inventory

raw `sql```: 47 sites

Important groups:

- Counter increments and aggregates
- `RAND()` random ordering
- `DATE(...)`, `DATE_SUB(...)`, `NOW()`
- `sql.join(...)` for `IN (...)`
- `sql.raw(...)` dynamic SQL
- raw `database.execute(...)` calls
- MySQL foreign-key toggles

Classification:

- P0: MySQL-only syntax and provider result shape assumptions
- P1: timestamp/result-shape convention risks
- P2: portable predicates and aggregate cleanup

### Execute / Query / Transaction Inventory

`.execute(...)`: 8 sites

- 4 raw `database.execute(...)` SELECT sites in `getKnowledgeCategoriesWithDocuments`
- 1 Drizzle update `.execute()` in `resetDailyCreditsForAllUsers`
- 2 MySQL-only `SET FOREIGN_KEY_CHECKS` sites
- 1 raw DELETE via `sql.raw(...)`

`.query(...)`: 0 sites

`.transaction(...)`: 4 sites

- `deductUserCredits`
- `addUserCredits`
- `grantInitialCreditsIfNeeded`
- `grantDailyCreditsIfNeeded`

Classification:

- Raw `database.execute(...)` tuple result shape: P1/P0 depending runtime driver behavior
- `SET FOREIGN_KEY_CHECKS`: P0 MySQL-only
- Drizzle transactions: keep as-is unless runtime typing requires adjustment

## 3. P0 Blockers

P0 site count: 62

### P0-1: MySQL Drizzle Runtime Binding

Count: 2 structural sites

- `drizzle-orm/mysql2` import
- `getDb()` construction path using the MySQL driver

Impact: SQLite runtime cannot be selected from this file as currently written.

### P0-2: MySQL Insert Result Shape

Count: 43 sites

Impact: SQLite insert results will not expose MySQL `insertId` in the same shape. These sites need `normalizeInsertId(...)`, `.returning(...)`, or insert-then-reselect by unique key.

### P0-3: `.onDuplicateKeyUpdate(...)`

Count: 3 sites

Locations:

- `upsertUser`
- `initializeUserPoints`
- `chargePoints`

Impact: MySQL-only upsert API. Needs `onConflictDoUpdate(...)`, `onConflictDoNothing(...)`, or explicit select/update/insert fallback.

### P0-4: `RAND()`

Count: 5 sites

Impact: MySQL-only random ordering. Needs `sqliteRandom()` or provider-aware expression.

### P0-5: `DATE(...)`, `DATE_SUB(...)`, `NOW()`

Counts:

- `DATE(...)`: 3 sites
- `DATE_SUB(...)`: 2 sites
- `NOW()`: 2 sites

Impact: MySQL date functions either crash or produce wrong timestamp-mode results under SQLite. Needs provider-aware date expression or JS-computed date bounds.

### P0-6: MySQL Foreign Key Toggles

Count: 2 sites

Locations:

- `SET FOREIGN_KEY_CHECKS = 0`
- `SET FOREIGN_KEY_CHECKS = 1`

Impact: MySQL-only syntax. SQLite uses `PRAGMA foreign_keys`.

### P0-7: Raw MySQL-Oriented Delete Path

Count: 1 site

Location:

- `sql.raw(DELETE FROM users WHERE id IN (...))` inside `batchDeleteUsers`

Impact: Combined with MySQL foreign-key toggles and raw string interpolation. Needs provider-aware delete strategy.

### P0-8: Raw `database.execute(...)` Tuple Shape

Count: 4 sites

Impact: The code reads `rows[0] as any[]`, which assumes mysql2 tuple result shape. SQLite execution shape may differ. Prefer Drizzle select or a result normalizer.

## 4. P1 Blockers

P1 site count: 7

### P1-1: JSON Convention

DB JSON convention risk count: 2

- `JSON.parse(pdf.tags)` in `getAllKnowledgeBaseTags`
- `JSON.stringify(sources)` in `addKnowledgeLearningMessage`

Keep-as-is count: 2

- `JSON.stringify(...)` debug logging in `getPracticeExamQuestions`

Impact: If the schema column is JSON-mode under SQLite, DB values should be stored/read as raw objects or arrays, not double-encoded strings.

### P1-2: Execute Result Shape

Count: 5

- 4 raw `database.execute(...)` tuple row assumptions
- 1 update `.execute()` using `result[0]?.affectedRows`

Impact: Driver-specific result shape can break under SQLite even if SQL text is portable.

### P1-3: Timestamp Convention

Count: 0 confirmed timestamp-write blockers in this audit pass.

Notes:

- Date-only strings created with `toISOString().slice(0, 10)` appear to be date-key usage, not timestamp column writes.
- MySQL `DATE(...)` / `DATE_SUB(...)` / `NOW()` sites are counted as P0 because they are SQL runtime blockers.

## 5. P2 Cleanup

P2 items:

- Raw `sql`` aggregate expressions such as `COUNT(*)`, `SUM(...)`, and arithmetic increments
- Portable `LIKE` predicates that could use Drizzle helpers
- Dynamic imports of `drizzle-orm` helpers inside functions
- Repeated null-check boilerplate after `getDb()`
- Long mixed-domain storage module structure

These are not required for initial SQLite runtime enablement.

## 6. MySQL-only Components

MySQL-only blocker count: 14

Components:

- MySQL Drizzle runtime binding: 2 structural sites
- `.onDuplicateKeyUpdate(...)`: 3 sites
- `RAND()`: 5 sites
- `DATE_SUB(NOW(), ...)`: 2 sites
- `SET FOREIGN_KEY_CHECKS`: 2 sites

Not counted as MySQL-only blocker:

- `insertId` is a MySQL result-shape assumption, counted as P0 but not syntax-only.
- `DATE(...)` exists in SQLite but has timestamp-mode incompatibility, counted as P0 compatibility risk.
- Portable raw `sql`` predicates are P2 unless they depend on MySQL-only syntax or result shape.

## 7. Dual Mode Compatibility Plan

Recommended patch batches:

### 1-K.1 Runtime Provider Wiring

Scope:

- Add provider-aware Drizzle initialization.
- Preserve MySQL path.
- Add SQLite path.
- Introduce runtime helper exports as needed.

Expected edits: 40-80 lines.

### 1-K.2 Insert Return Normalization

Scope:

- Patch 43 `insertId` sites.
- Introduce or import `normalizeInsertId(...)`.
- Use `.returning(...)` only where it is clearly dual-safe, otherwise normalize or reselect.

Expected edits: 120-220 lines.

### 1-K.3 Upsert Runtime Batch

Scope:

- Patch 3 `.onDuplicateKeyUpdate(...)` sites.
- Use `onConflictDoUpdate(...)` / `onConflictDoNothing(...)` where schema keys are available.
- Use select/update/insert fallback only if required.

Expected edits: 30-70 lines.

### 1-K.4 Random + Date Function Batch

Scope:

- Patch 5 `RAND()` sites.
- Patch 3 `DATE(...)` sites.
- Patch 2 `DATE_SUB(NOW(), ...)` sites.
- Prefer JS-computed date bounds for report filters where possible.

Expected edits: 50-100 lines.

### 1-K.5 Execute / Result Shape Batch

Scope:

- Patch 8 `.execute(...)` sites.
- Convert raw SELECTs to Drizzle selects where possible.
- Replace `affectedRows` result assumption.
- Make `batchDeleteUsers` provider-aware.

Expected edits: 80-160 lines.

### 1-K.6 JSON Convention Check

Scope:

- Confirm schema mode for `knowledgeBasePdfs.tags` and `knowledgeLearningMessages.sources`.
- Patch 2 DB JSON convention sites only if schema is JSON-mode.
- Keep debug logging stringifies.

Expected edits: 10-40 lines.

## 8. Migration Estimate

Estimated total modification range: 280-520 lines.

Risk drivers:

- `db.ts` is broad and mixed-domain.
- 43 insert-return sites are spread across unrelated features.
- Runtime provider wiring affects every module using `getDb()`.
- Some raw SQL paths include fallback logic and production data assumptions.

Suggested execution style:

- Patch in small batches.
- Run import smoke after each batch.
- Use disposable SQLite smoke tests for each affected pattern.
- Keep MySQL compatibility checks around insert/upsert paths.

## 9. Risk Assessment

Risk level: High

Reasons:

- Runtime is still MySQL-driver-only.
- Insert result assumptions are widespread.
- MySQL-only upsert and random/date functions remain.
- Raw `database.execute(...)` result shape assumptions remain.
- `batchDeleteUsers` uses MySQL-only foreign-key toggles and raw string SQL.

The risk is manageable if Phase 1-K is split into focused batches and avoids broad cleanup while enabling runtime dual mode.

## 10. Recommendation

Proceed to Phase 1-K patch work, but do not attempt a single large runtime patch.

Recommended first patch:

1. Phase 1-K.1 Runtime Provider Wiring
2. Phase 1-K.2 Insert Return Normalization
3. Phase 1-K.3 Upsert Runtime Batch
4. Phase 1-K.4 Random + Date Function Batch
5. Phase 1-K.5 Execute / Result Shape Batch
6. Phase 1-K.6 JSON Convention Check

RC1 should wait until:

- MySQL path still initializes and imports cleanly.
- SQLite path initializes and imports cleanly.
- `insertId` blockers are zero.
- `.onDuplicateKeyUpdate(...)` blockers are zero.
- `RAND()`, `DATE_SUB()`, and MySQL foreign-key toggle blockers are zero.
- No SQLite DB/WAL/SHM smoke artifacts remain after tests.
