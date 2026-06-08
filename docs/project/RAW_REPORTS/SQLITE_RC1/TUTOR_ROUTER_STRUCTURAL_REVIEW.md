# TutorRouter Structural Review

Phase: 1-J.1f Cleanup / Structural Review
Target: `server/routers/tutorRouter.ts`
Scope: Audit + minimal cleanup review only. No functional code changes.

## 1. Executive Summary

TutorRouter has completed the functional SQLite compatibility migration batches through 1-J.1e. The remaining work in this phase is structural review only.

Current structural compatibility inventory:

- `db.execute(...)`: 4 sites
- raw `sql```: 50 sites
- `isSqliteMode(...)`: 4 calls
- `sqliteRandom(...)`: 4 calls
- `normalizeInsertId(...)`: 6 calls
- local `sqliteTable(...)`: 4 definitions
- `.join(...)`: 15 total calls, including 3 raw SQL `IN (...)` string joins and 1 safe `sql.join(...)`

No functional blocker was patched in this phase. The remaining required compatibility code is intentional and should stay until the runtime migration is complete.

Recommendation: proceed to Phase 1-K `db.ts` Runtime Migration. Keep the structural cleanup items below as follow-up tickets after runtime dual mode is verified.

## 2. Required Compatibility Code

### Required: `normalizeInsertId(...)`

Count: 6

Locations:

- `414`
- `485`
- `1283`
- `1315`
- `2044`
- `2080`

Classification: A. Required

Reason: These calls normalize insert return shapes across MySQL and SQLite-compatible Drizzle paths. They are part of the 1-J.1a Insert Return migration and should remain.

### Required: `sqliteRandom(...)`

Count: 4

Classification: A. Required

Reason: These replace MySQL-only `RAND()` behavior with a dual-mode random expression. MySQL keeps `RAND()` semantics while SQLite uses `RANDOM()`.

### Required: `isSqliteMode(...)`

Count: 4

Classification: A. Required

Reason: These calls guard the remaining mode-aware insert-ignore raw SQL sites. They preserve:

- MySQL: `INSERT IGNORE`
- SQLite: `INSERT OR IGNORE`

The calls are currently required because the affected insert statements still use raw SQL and need provider-specific syntax.

### Required: mode-aware insert-ignore branches

Count: 2 branches, 4 `isSqliteMode(...)` calls

Locations:

- `book_custom_suggestions` raw insert
- `book_suggestion_cache` raw insert

Classification: A. Required

Reason: These branches are compatibility code introduced by 1-J.1b. They should remain until the statements are converted to Drizzle insert conflict handling or a shared insert-ignore helper is introduced.

## 3. Optional Cleanup Candidates

### Convert portable `db.execute(...)` sites to Drizzle

Count: 4

Classification: B. Optional Cleanup / C. Risk

Reason: The SQL itself is mostly portable after the previous batches, but `db.execute(...)` can still expose driver-specific result shapes. The two raw SELECT sites are the highest-value cleanup because they destructure returned rows directly.

Suggested future cleanup:

- Convert raw SELECT joins to Drizzle `select(...)` / `innerJoin(...)`
- Convert raw DELETE / INSERT cache maintenance to Drizzle `delete(...)` / `insert(...)`

### Replace raw SQL `IN (${array.join(",")})`

Count: 3 structural-risk joins

Locations:

- `examSetIds.join(",")`
- `input.sessionIds.join(",")`
- `subjectIds.join(",")`

Classification: C. Risk

Reason: These are raw string interpolations inside SQL fragments. They are likely numeric IDs, but they still bypass structured SQL binding and should be migrated to Drizzle `inArray(...)` or parameterized `sql.join(...)` in a cleanup phase.

### Consolidate local `sqliteTable(...)` definitions

Count: 4

Classification: B. Optional Cleanup / C. Risk

Reason: Local table shims avoid broader schema edits, which was appropriate for prior patch scope. They carry schema drift risk if `book_suggestion_cache` changes. Prefer importing the canonical schema once Phase 1-K confirms runtime behavior.

### Reduce raw SQL predicates where Drizzle helpers exist

Classification: B. Optional Cleanup

Examples:

- `IS NULL` / `IS NOT NULL`
- `LIKE`
- `COUNT(*)`
- date range predicates
- simple equality predicates

Reason: These are not immediate blockers, but replacing them with Drizzle helpers improves portability and type safety.

## 4. Raw SQL Inventory

Total raw `sql```: 50

High-value groups:

- Mode-aware insert-ignore raw SQL: 2 sites
- `db.execute(...)` raw SQL: 4 sites
- Raw SQL `IN (...)` string joins: 3 sites
- Safe `sql.join(...)`: 1 site
- Portable predicates / aggregates / ordering fragments: remaining sites

Classification:

- A. Required: mode-aware insert-ignore branches and `sqliteRandom(...)` expressions
- B. Optional Cleanup: portable predicates, aggregates, grouping, ordering
- C. Risk: raw SQL string joins and `db.execute(...)` row-shape dependencies

Notes:

- Raw SQL count remains high, but most sites are small Drizzle predicate fragments rather than MySQL-only blockers.
- No `RAND()`, `INSERT IGNORE`, or `.onDuplicateKeyUpdate(...)` blocker remains as a functional migration target from previous batches.

## 5. db.execute Inventory

Total `db.execute(...)`: 4

### Raw video-course SELECT join

Classification: C. Risk

Reason: Uses raw SQL SELECT with join and depends on returned row array shape. SQL syntax is portable, but runtime result shape may differ between providers.

Suggested future cleanup: Drizzle `select(...)` with explicit fields and join.

### Raw video-course SELECT with search predicate

Classification: C. Risk

Reason: Uses raw SQL SELECT with dynamic search predicate and depends on returned row array shape.

Suggested future cleanup: Drizzle `select(...)` with conditional `like(...)`.

### Raw `book_custom_suggestions` DELETE

Classification: B. Optional Cleanup

Reason: SQL is portable and not a current blocker, but can be expressed with Drizzle `delete(...)`.

### Raw `book_custom_suggestions` INSERT

Classification: B. Optional Cleanup

Reason: SQL is portable and not a current blocker, but can be expressed with Drizzle `insert(...)`.

## 6. sqliteTable Inventory

Total local `sqliteTable(...)`: 4

Table:

- `book_suggestion_cache`

Classification: B. Optional Cleanup / C. Risk

Reason: These local table definitions are compatibility shims. They are acceptable for scoped migration work, but keeping repeated local schema definitions in a router can drift from canonical schema.

Suggested future cleanup:

- Move `book_suggestion_cache` to canonical schema if missing.
- Import the canonical table definition in `tutorRouter.ts`.
- Remove repeated local `sqliteTable(...)` declarations after schema coverage is confirmed.

## 7. Risk Assessment

Risk level: Medium

Why not High:

- Functional SQLite blockers from prior TutorRouter batches have been addressed.
- MySQL-only syntax blockers targeted so far are cleared.
- Remaining mode-aware branches are intentional.

Why not Low:

- `db.execute(...)` still has provider result-shape risk.
- Raw SQL count remains high.
- Three raw SQL `IN (...)` joins still bypass structured binding.
- Four local `sqliteTable(...)` definitions carry schema drift risk.

Primary remaining structural risks:

1. Runtime result-shape differences from `db.execute(...)`.
2. Raw SQL array interpolation with `.join(...)`.
3. Local schema shim drift.
4. Compatibility branches duplicated in router instead of centralized runtime helpers.

## 8. Recommendation

Proceed directly to Phase 1-K `db.ts` Runtime Migration.

Rationale:

- TutorRouter functional SQLite migration is complete.
- Remaining items are structural cleanup risks, not current functional migration blockers.
- Phase 1-K will clarify the final provider abstraction and may make the best cleanup path clearer.

Recommended follow-up after Phase 1-K:

1. Convert the 4 `db.execute(...)` sites to Drizzle APIs.
2. Replace 3 raw SQL `IN (...)` string joins with structured `inArray(...)` or parameterized `sql.join(...)`.
3. Replace the 4 local `sqliteTable(...)` declarations with canonical schema imports.
4. Consider a shared dual-mode insert-ignore helper only if raw insert-ignore branches remain after cleanup.
