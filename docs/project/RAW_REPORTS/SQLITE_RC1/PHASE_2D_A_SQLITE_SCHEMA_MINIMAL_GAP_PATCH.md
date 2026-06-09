# Phase 2D-A: SQLite Schema Minimal Gap Patch

## Scope
This patch closes the functional gaps in the MVP SQLite schema related to the core `practice` features and the `user_preferences` sidebar configurations, which were actively crashing the active pages without modifications. Changes were isolated to `drizzle/schema.sqlite.mvp.ts` only.

## Tables added
The following 6 tables were successfully ported from MySQL to the MVP SQLite schema:
1. `practice_exams`
2. `practice_exam_questions`
3. `practice_records`
4. `practice_answers`
5. `exam_purchases`
6. `user_preferences`

## Column mapping summary
- **MySQL `int` / `bigint`**: Mapped to SQLite `integer`. For timestamps like `updatedAt` in `user_preferences` that were using `bigint({mode: 'number'})`, they have been mapped identically.
- **MySQL `varchar` / `text` / `longtext`**: Mapped to SQLite `text`.
- **MySQL `timestamp` / `datetime`**: Mapped to SQLite `integer(..., { mode: "timestamp" })` or kept inline with existing schemas using Unix second strategies (`default(sql\`(strftime('%s','now'))\`)`).
- **MySQL `tinyint` boolean**: Mapped to SQLite `integer(..., { mode: "boolean" })`.
- **MySQL `json`**: Mapped to SQLite `text(..., { mode: "json" })` (e.g., `user_preferences.sidebarOrder` or implicit array stringification).
- **MySQL `enum`**: Mapped directly to SQLite `text`, adhering to the phase's minimal check-constraint approach.

## Index / FK decisions
- **Indexes**: Faithfully migrated index callbacks from the MySQL source to SQLite (e.g., indexes on category, subject, user/exam pairings, etc.). Added `uniqueIndex` for `user_preferences.userId`.
- **Foreign Keys**: Kept explicitly declared foreign keys out of the `.references()` structure, mirroring the existing consistent pattern in `schema.sqlite.mvp.ts`. Relationship keys (e.g. `userId`, `practiceExamId`, `questionId`) are preserved as simple columns but are implicitly understood as FKs by the application level. High risk cascade alterations were completely avoided.

## Why only these 6 tables
The goal of this phase was to deliver a minimal, high-impact patch. By targeting exactly the 6 tables associated with the active pages (the practice exam functionality cluster and sidebar preferences), we can stop immediate crashes during component rendering and routing, without bloating the schema footprint or migrating the entire remaining gap of 110 missing tables.

## Validation commands
1. **TypeScript import smoke**:
   `pnpm exec tsx -e 'import "./drizzle/schema.sqlite.mvp.ts"; console.log("SQLITE_SCHEMA_IMPORT_OK")'`
2. **Schema Push**:
   `pnpm exec drizzle-kit push --config=drizzle.config.smoke.ts`
3. **Insert/Select Testing**:
   A specific `smoke-test.ts` script utilizing `better-sqlite3` executing basic end-to-end inserts and selects for all 6 tables.
4. **Project Build**:
   `pnpm build` (plus cleanup scripts for test leftovers).

## Validation result
- **TypeScript Import Smoke**: `PASS`
- **Schema Push Smoke**: `PASS`
- **Insert/Select Smoke**: `PASS`
- **Build**: `PASS` (Built in ~28s, some existing duplicate key warnings in routers)

## SQLite DB leftovers check
All testing artifacts (`./data/phase2d-a-smoke.db*`, `smoke-test.ts`, `drizzle.config.smoke.ts`) were actively deleted during the final phase of the operation.

## Build result
`PASS`. Build completed successfully without errors caused by the new schema. 
(Note: Pre-existing TS duplicate key warnings exist in `smartBookRouter.ts`, which are technical debt unrelated to this database patch.)

## Remaining HIGH missing tables
10 remaining tables flagged as HIGH priority:
- `question_bank`
- `question_bank_history`
- `announcements`
- `announcement_reads`
- `qa_cache`
- `banners`
- `knowledge_base_pdfs`
- `knowledge_base_pages`
- `knowledge_base_categories`
- `wrong_questions`

## Risk notes
- The lack of explicit `.references()` for foreign keys in SQLite reduces absolute relational safety at the DB engine level; it relies on `drizzle` schemas / business logic.
- Text representation for ENUM values must be enforced precisely by application code (Zod, routers) as SQLite doesn't offer native restrictive ENUM types out of the box without `CHECK` constraints.

## Recommendation for Phase 2D-B
Proceed with the integration of the Question Bank and Knowledge Base clusters:
1. `question_bank` & `question_bank_history`
2. `knowledge_base_pdfs`, `knowledge_base_pages`, `knowledge_base_categories`
These groups contain higher structural complexity but will address the remaining major product gaps that heavily depend on AI/PDF document retrieval.
