# Phase 2D-C: SQLite Schema Active Runtime Gap Patch

## Scope
This phase focuses on patching the remaining highly critical runtime crash gaps in the MVP SQLite schema. Specifically, this patch addresses the missing tables related to global announcements, homepage banners, and wrong question tracking that would actively crash the `<StudentPortal />`, `<Chat />` interface, and wrong question review flows on mount. Changes are strictly isolated to `drizzle/schema.sqlite.mvp.ts`. 

## Why these 4 tables only
Based on the Phase 2D-B analysis, these 4 tables (`announcements`, `announcement_reads`, `banners`, `wrong_questions`) are responsible for UI layout mounts and standalone feature routing crashes. The remaining 6 HIGH missing tables form a highly complex Knowledge Base and AI Q&A cluster with deep interconnectivity. Migrating the simple UI-centric tables separately isolates the risk, secures the main entry points, and leaves the complex vector/knowledge base dependencies for a dedicated Phase 2D-D batch.

## Tables added
The following 4 tables have been added to the MVP SQLite schema:
1. `announcements`
2. `announcement_reads`
3. `banners`
4. `wrong_questions`

## Column mapping summary
- **MySQL `int` / `bigint`**: Mapped to SQLite `integer`.
- **MySQL `varchar` / `text`**: Mapped to SQLite `text`.
- **MySQL `timestamp`**: Mapped to SQLite `integer({ mode: "timestamp" })`.
- **MySQL `tinyint` boolean**: Mapped to SQLite `integer({ mode: "boolean" })`.
- **MySQL `json`**: Mapped to SQLite `text({ mode: "json" })`.
- **MySQL `enum`**: Mapped to SQLite `text`, delegating restrictive validation to Zod/application logic to maintain SQLite MVP simplicity.

## Source evidence
- `announcements`, `announcement_reads`, and `banners` were mapped directly from their respective structures in `drizzle/schema.ts`.
- **Usage-Driven Fallback for `wrong_questions`**:
  - The MySQL schema for `wrong_questions` inherently relied on joining the `question_bank` table to resolve properties like `questionType` and `subject`.
  - Since `question_bank` is excluded from this phase to prevent cascade migrations, direct reference to these fields in the `WrongQuestions.tsx` active routes would result in schema resolution crashes.
  - To fulfill the actual necessary client query demands on the MVP layer, `questionType` and `subject` were appended to the `wrong_questions` SQLite schema definition as usage-driven fallbacks.

## Index / FK decisions
- **Indexes**: Migrated all standard single-column and composite indexes from the MySQL definitions to SQLite `index()`.
- **Foreign Keys**: Retained the MVP convention of relying on application-level integrity instead of explicit `.references()` constraints at the SQLite DB level to prevent unforeseen cascade deletion blocks. 

## Validation commands
1. **TypeScript import smoke**:
   `pnpm exec tsx -e 'import "./drizzle/schema.sqlite.mvp.ts"; console.log("SQLITE_SCHEMA_IMPORT_OK")'`
2. **Schema Push**:
   `pnpm exec drizzle-kit push --config=drizzle.config.smoke.ts`
3. **Insert/Select Testing**:
   A specific `smoke-test.ts` utilizing `better-sqlite3` executed basic E2E inserts and selects for the 4 newly added tables.
4. **Project Build**:
   `pnpm build`

## Validation results
- **TypeScript Import Smoke**: `PASS`
- **Schema Push Smoke**: `PASS`
- **Insert/Select Smoke**: `PASS`
- **Build**: `PASS`

## SQLite leftovers check
All test artifacts (`./data/phase2d-c-smoke.db*`, `smoke-test.ts`, `drizzle.config.smoke.ts`) were actively deleted at the end of the validation step.

## pnpm build result
Build completed successfully without breaking any schema typings or missing any export references.

## Remaining HIGH missing tables after 2D-C
6 highly complex tables remain in the HIGH priority gap:
- `question_bank`
- `question_bank_history`
- `qa_cache`
- `knowledge_base_pdfs`
- `knowledge_base_pages`
- `knowledge_base_categories`

## Risks and next recommendation
**Risks:** The usage-driven denormalization of `questionType` and `subject` into the `wrong_questions` table will require specific router adjustments whenever `question_bank` is officially migrated.

**Next Recommendation (Phase 2D-D):**
Proceed with integrating the remaining heavy Knowledge Base / AI Q&A cluster. This will fully close the active HIGH runtime crash gap and enable the core PDF retrieval functionality within the Lite client.
