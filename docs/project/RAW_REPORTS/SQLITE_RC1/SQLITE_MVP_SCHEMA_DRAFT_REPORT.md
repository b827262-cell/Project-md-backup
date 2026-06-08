# SQLite MVP Schema Draft Report

## Summary

| Item | Value |
|------|-------|
| Source schema | `drizzle/schema.ts` (MySQL, 3689 lines) |
| Draft schema | `drizzle/schema.sqlite.mvp.ts` |
| Tables included | 43 (Must Migrate only) |
| Tables excluded | 136 (Should Migrate 57 + Defer/Archive 79) |
| Runtime status | **Not connected** — draft only |
| Build status | **Not verified** — draft only, may require minor adjustments |

---

## Included Tables (43)

| # | Table Name | Notes |
|---|------------|-------|
| 1 | users | Core user account + credits |
| 2 | conversations | AI chat session |
| 3 | messages | Chat messages |
| 4 | conversation_files | Uploaded attachments |
| 5 | conversation_tags | Tag relations |
| 6 | tags | Tag master |
| 7 | system_settings | Global settings |
| 8 | credit_transactions | Credit ledger |
| 9 | credit_rules | Deduction rule config |
| 10 | user_usage_stats | Daily usage stats |
| 11 | pdf_categories | PDF subject categories |
| 12 | smart_book_categories | Book top-level categories |
| 13 | smart_books | Smart book master |
| 14 | smart_book_chapters | Book chapters |
| 15 | smart_book_conversations | Per-book learning chat |
| 16 | smart_book_progress | Chapter progress |
| 17 | smart_book_chapter_qa | AI-generated chapter Q&A |
| 18 | smart_book_credits | Per-book credit balance |
| 19 | smart_book_credit_transactions | Per-book credit ledger |
| 20 | smart_book_settings | Per-book credit/challenge config |
| 21 | smart_book_unit_qa | Admin-prepared interactive QA |
| 22 | smart_book_unit_qa_answers | Student interactive QA answers |
| 23 | smart_book_learning_sessions | Learning timer |
| 24 | smart_book_chapter_daily_verifications | Daily chapter switch verification |
| 25 | smart_book_chapter_completions | Chapter completion summary |
| 26 | smart_book_saved_messages | Saved AI replies |
| 27 | lesson_points | Guided learning knowledge points |
| 28 | lesson_progress | Student lesson point progress |
| 29 | smart_book_review_questions | Chapter review question bank |
| 30 | smart_book_wrong_answers | Wrong answer book |
| 31 | smart_book_quiz_sessions | Quiz session records |
| 32 | smart_book_question_shown | Question appearance count |
| 33 | smart_book_qa_viewed | QA view records (deduction tracking) |
| 34 | smart_book_verifications | Book purchase verification |
| 35 | tutor_subjects | AI tutor subject categories |
| 36 | tutor_subject_books | Subject × book relations |
| 37 | tutor_chat_sessions | AI tutor chat sessions |
| 38 | tutor_chat_messages | AI tutor chat messages |
| 39 | tutor_subject_exam_sources | Subject × exam source relations |
| 40 | tutor_subject_video_courses | Subject × video course relations |
| 41 | book_suggestion_cache | Auto-generated suggested questions |
| 42 | book_voucher_records | Book voucher redemption records |
| 43 | book_custom_suggestions | Admin-defined custom suggestions |

---

## Type Mapping Summary

| MySQL Type | SQLite Type | Note |
|------------|-------------|------|
| `mysqlTable(...)` | `sqliteTable(...)` | Direct rename |
| `int(...)` | `integer(...)` | Direct |
| `bigint({ mode: "number" })` | `integer(...)` | Ms timestamp: NOT using `{ mode: "timestamp" }` (which is seconds) |
| `tinyint()` (boolean field) | `integer("col", { mode: "boolean" })` | is_*, has_*, require_* fields |
| `tinyint()` (numeric field) | `integer(...)` | Counts, scores, indices |
| `varchar({ length: X })` | `text(...)` | Length ignored in SQLite |
| `mysqlEnum(...)` | `text(...)` | + comment: enforce by Zod/CHECK |
| `json(...)` | `text("col", { mode: "json" })` | Serialized JSON string |
| `timestamp({ mode: 'string' })` | `integer("col", { mode: "timestamp" })` | Unix seconds |
| `datetime(...)` | `integer("col", { mode: "timestamp" })` | Unix seconds |
| `text / mediumtext / longtext` | `text(...)` | All same in SQLite |
| `decimal / double / float` | `real(...)` | (not used in these 43 tables) |
| `binary / blob` | `blob(...)` | (not used in these 43 tables) |
| `autoincrement().primaryKey()` | `.primaryKey({ autoIncrement: true })` | |
| `defaultNow()` | removed | TODO marker added |
| `onUpdateNow()` | removed | TODO marker added |
| `sql\`CURRENT_TIMESTAMP\`` | removed | TODO marker added |

---

## Known TODO

### 1. Enum Validation
- **Issue**: MySQL `mysqlEnum(...)` has DB-level enforcement. SQLite `text(...)` has none.
- **Action**: Add Zod schema validation in application layer for all enum fields, OR add SQLite CHECK constraints in migration.
- **Scope**: ~80+ enum columns across 43 tables.

### 2. Timestamp Default Strategy
- **Issue**: `defaultNow()`, `onUpdateNow()`, `sql\`CURRENT_TIMESTAMP\`` are MySQL-specific.
- **Options**:
  - Application-level: Set timestamp before insert/update in server code.
  - SQLite trigger: Use `DEFAULT (unixepoch())` for created_at.
  - Drizzle: Use `sql\`(unixepoch())\`` as default in SQLite schema.
- **Action required before Phase 1-D**: Decide strategy and apply to all timestamp columns.

### 3. Foreign Key Behavior
- **Issue**: SQLite foreign key enforcement is disabled by default (`PRAGMA foreign_keys = OFF`).
- **Action**: Enable at connection time: `PRAGMA foreign_keys = ON;` in `server/db.ts`.
- **Risk**: Without FK enforcement, orphaned records are possible during early migration phases.

### 4. mysql2 Dependency Refactor
- **Issue**: `server/db.ts` currently uses `mysql2` / `@planetscale/database` client.
- **Action**: Refactor `server/db.ts` to use `better-sqlite3` or `@libsql/client` for SQLite.
- **Blocked by**: `better-sqlite3` package not installed yet.
- **Note**: Do NOT modify until Phase 1-D begins.

### 5. better-sqlite3 Package Not Installed
- **Issue**: `better-sqlite3` (or `@libsql/client`) is not in `package.json`.
- **Action**: Install in Phase 1-D: `pnpm add better-sqlite3` and `pnpm add -D @types/better-sqlite3`.
- **Blocked by**: This is Phase 1-C draft only; no package install allowed in this phase.

### 6. Schema File Not Imported
- **Issue**: `drizzle/schema.sqlite.mvp.ts` is not imported anywhere in the runtime.
- **Action**: In Phase 1-D, update `server/db.ts` to import from this file instead of `drizzle/schema.ts`.
- **Note**: `drizzle/schema.ts` (MySQL version) must NOT be overwritten until full cut-over.

### 7. Index Definitions Omitted
- **Issue**: All SQLite indexes are omitted in this draft for readability.
- **Action**: Before Phase 1-D, add index definitions to all tables (especially userId, bookId, createdAt).

### 8. Column Name Consistency
- **Issue**: Some MySQL columns use camelCase property keys without explicit DB name strings (e.g., `openId: varchar(...)` → DB column is `openId`). Others have explicit snake_case names (e.g., `password_hash`). The SQLite draft maintains this pattern.
- **Action**: Verify column names match actual MySQL DB schema before data migration. Run `SHOW COLUMNS FROM users;` on MySQL to confirm.

---

## Risk Assessment

| Area | Risk | Level |
|------|------|-------|
| Schema completeness | All 43 Must Migrate tables included | Low |
| Type conversion correctness | Standard types mapped correctly | Low |
| Timestamp ms vs seconds confusion | bigint ms timestamps stored as plain integer (not timestamp mode) | Medium |
| Enum validation gap | No DB-level enforcement in SQLite | Medium |
| Foreign key enforcement disabled by default | Must enable manually | Medium |
| Column name drift | Some camelCase vs snake_case ambiguity | Medium |
| Build verification | Schema not verified against `tsc` / `drizzle-kit` | High (draft only) |
| Runtime data migration | Not started — zero data moved yet | N/A (deferred) |

**Overall Risk Level: Medium** (acceptable for draft phase)

---

## Recommendation

### Is Phase 1-D recommended?

**YES — conditionally.**

Before entering Phase 1-D (Runtime Wiring), the following must be completed:

- [ ] Decide and implement timestamp default strategy (TODO #2)
- [ ] Install `better-sqlite3` package
- [ ] Refactor `server/db.ts` to support SQLite connection alongside MySQL (dual-mode or swap)
- [ ] Add index definitions to schema.sqlite.mvp.ts
- [ ] Enable `PRAGMA foreign_keys = ON` in SQLite connection
- [ ] Verify column names against actual MySQL DB

### Phase 1-D Scope (suggested)

1. Install `better-sqlite3`
2. Create `server/db.sqlite.ts` (new file, do not overwrite `server/db.ts`)
3. Wire one simple readonly endpoint to SQLite for smoke test
4. Verify Drizzle ORM queries work with SQLite schema
5. Run `drizzle-kit push` on SQLite database (local only)

---

*Generated: 2026-06-03*
*Phase: 1-C SQLite Runtime MVP Schema Draft*
*Status: Draft Only / Not Connected to Runtime*
