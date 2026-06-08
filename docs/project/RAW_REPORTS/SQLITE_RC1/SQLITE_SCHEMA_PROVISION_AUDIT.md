# SQLite Schema Provision Audit

Phase: 2A - SQLite Schema Provision Audit  
Branch: `release/vps-lite`  
Scope: Audit only. No code patch, no migration, no table creation, no SQL execution.

## 1. Executive Summary

Runtime boot in SQLite mode fails because the SQLite database file has no tables:

```text
SqliteError: no such table: pdf_categories
```

The repository has a SQLite schema source file:

```text
drizzle/schema.sqlite.mvp.ts
```

That file defines the MVP SQLite schema and contains 66 `sqliteTable(...)` declarations, including `pdf_categories`.

However, the current repository does not include a complete SQLite schema provisioning path. `server/db.sqlite.ts` opens the SQLite database and binds the Drizzle schema, but it does not create tables. `drizzle.config.ts` is still MySQL-only and points to `drizzle/schema.ts`, not `drizzle/schema.sqlite.mvp.ts`.

Conclusion: SQLite runtime wiring is present, but empty-database schema provisioning is missing.

## 2. Scanned Targets

Scanned:

- `drizzle.config.ts`
- `drizzle/`
- `drizzle/migrations/`
- `migrations/`
- `schema/`
- `server/db.sqlite.ts`
- `server/db.ts`
- `scripts/`

No `schema/` directory was found in the repository scan.

## 3. SQLite Schema Source

SQLite schema source:

```text
drizzle/schema.sqlite.mvp.ts
```

Runtime binding:

```text
server/db.sqlite.ts
```

Evidence:

- `server/db.sqlite.ts` imports `better-sqlite3`.
- `server/db.sqlite.ts` imports `drizzle-orm/better-sqlite3`.
- `server/db.sqlite.ts` imports schema from `../drizzle/schema.sqlite.mvp`.
- The file comment identifies the schema as `../drizzle/schema.sqlite.mvp (66 tables)`.

Important limitation:

`getSqliteDb()` opens the SQLite file and applies PRAGMAs, but does not run DDL, migrations, or table creation.

## 4. Drizzle Config

Current Drizzle config:

```text
drizzle.config.ts
```

Current configuration:

```ts
schema: "./drizzle/schema.ts"
out: "./drizzle"
dialect: "mysql"
```

Assessment:

- This config is MySQL-oriented.
- It does not target `drizzle/schema.sqlite.mvp.ts`.
- It does not define a SQLite dialect/config.
- It cannot directly provision an empty SQLite database as currently configured.

## 5. pdf_categories Definition

SQLite definition:

```text
drizzle/schema.sqlite.mvp.ts:184
export const pdfCategories = sqliteTable("pdf_categories", {
```

Canonical MySQL schema definition:

```text
drizzle/schema.ts:980
export const pdfCategories = mysqlTable("pdf_categories", {
```

Migration/snapshot references:

- `drizzle/0013_fixed_songbird.sql` contains `CREATE TABLE \`pdf_categories\``.
- Many `drizzle/meta/*_snapshot.json` files include `pdf_categories`, but these snapshots are MySQL dialect snapshots.

## 6. SQLite Table Inventory

SQLite table source file:

```text
drizzle/schema.sqlite.mvp.ts
```

Table count:

```text
sqliteTable(...) = 66
```

Key SmartBook/Tutor-related tables present include:

- `pdf_categories`
- `smart_book_categories`
- `smart_books`
- `smart_book_chapters`
- `smart_book_progress`
- `smart_book_wrong_answers`
- `smart_book_category_exam_sources`
- `lesson_points`
- `lesson_progress`
- `tutor_subjects`
- `tutor_subject_books`
- `tutor_chat_sessions`
- `tutor_chat_messages`

The 66-table MVP schema appears broad enough to include the routers already migrated in Phase 1.

## 7. Migration File Locations

Existing SQL migration locations:

```text
drizzle/*.sql
drizzle/migrations/*.sql
migrations/*.sql
```

Counts observed:

```text
drizzle/*.sql = 138
drizzle/migrations/*.sql = 1
migrations/*.sql = 1
```

Assessment:

- Existing `drizzle/*.sql` migrations are MySQL-style migrations generated under the MySQL Drizzle config.
- They use MySQL quoting/backtick style and MySQL snapshot metadata.
- `drizzle/migrations/add_local_upload_fields.sql` exists.
- `migrations/add_gaodian_exams.sql` exists.
- No SQLite-specific migration directory was found.

No path such as the following was found:

```text
drizzle/sqlite/
drizzle/migrations/sqlite/
migrations/sqlite/
```

## 8. SQLite schema.sql

No SQLite schema SQL file was found.

Search result:

```text
./drizzle/essay_grading_schema.sql
```

Assessment:

- `drizzle/essay_grading_schema.sql` is a feature-specific SQL file, not a full SQLite schema provision file.
- No `schema.sql`, `sqlite.schema.sql`, or equivalent full SQLite DDL file was found.

## 9. Migration Snapshot

Snapshot files exist:

```text
drizzle/meta/*_snapshot.json = 133
```

Snapshot dialect:

```text
"dialect": "mysql"
```

Assessment:

- MySQL migration snapshots exist.
- No SQLite migration snapshot was found.
- No SQLite Drizzle Kit journal/snapshot set was found for `drizzle/schema.sqlite.mvp.ts`.

## 10. SQLite Export / Provision Script

Searched scripts and server files for:

- MySQL to SQLite export
- SQLite import/export
- `better-sqlite3`
- `sqlite3`
- `schema.sqlite`
- `SQLITE_PATH`
- `DATABASE_PROVIDER`

Findings:

- `server/db.sqlite.ts` provides runtime adapter logic.
- `server/db.runtime.ts` provides active provider selection.
- `drizzle/schema.sqlite.mvp.ts` provides SQLite table definitions.
- Existing import/seed scripts are MySQL-oriented or unrelated utility scripts.

No complete MySQL -> SQLite export/provision workflow was found.

## 11. SQLite Schema Creation Method

Current state:

```text
No active SQLite schema creation method found.
```

What exists:

- SQLite schema definition source: `drizzle/schema.sqlite.mvp.ts`
- SQLite runtime adapter: `server/db.sqlite.ts`
- Provider selection: `server/db.runtime.ts`

What is missing:

- SQLite Drizzle config.
- SQLite migration output directory.
- SQLite migration snapshots.
- Full SQLite `schema.sql`.
- Runtime-independent schema provisioning command.
- MySQL -> SQLite data export/import process.

Current runtime behavior:

1. SQLite mode opens `SQLITE_PATH`.
2. PRAGMAs are applied.
3. Drizzle is bound to `schema.sqlite.mvp.ts`.
4. No DDL is executed.
5. First query against a missing table fails.

This explains the `pdf_categories` boot failure.

## 12. Can an Empty SQLite Schema Be Created Directly?

Current repository automation:

```text
No.
```

Reason:

- The repo has a SQLite schema source file, but no committed SQLite schema provisioning path.
- The current Drizzle config is MySQL-only.
- The runtime adapter intentionally does not create schema.

Technical feasibility:

```text
Yes, if a provisioning step is added.
```

Practical options:

1. Add a SQLite Drizzle config targeting `drizzle/schema.sqlite.mvp.ts`.
2. Generate and commit SQLite migrations/snapshots.
3. Add a controlled SQLite schema provision command for empty DB creation.
4. Add a separate MySQL -> SQLite export/import flow for existing production data.

These are implementation tasks and were not performed in this audit.

## 13. Risk Assessment

P0:

- Empty SQLite DB cannot boot because required tables are absent.
- `pdf_categories` is the first observed missing table, but all 66 SQLite MVP tables are expected to be absent in a fresh DB unless provisioned.

P1:

- SQLite schema source exists but is not connected to Drizzle Kit migration generation.
- Existing migration history is MySQL dialect and should not be applied directly to SQLite.
- Runtime adapter can create/open the DB file, which can make a zero-table DB look superficially present.

P2:

- `drizzle/schema.sqlite.mvp.ts` is marked as an MVP schema source and should be reviewed before making it the authoritative deployment schema.
- MySQL -> SQLite export process is not yet documented or implemented.

## 14. Recommendation

Proceed to Phase 2B: SQLite Schema Provision Plan / Patch.

Recommended batch split:

1. Phase 2B.0 - SQLite schema provision design
   - Decide whether the deployable artifact is SQLite migrations, a generated `schema.sql`, or a controlled provision script.

2. Phase 2B.1 - Empty SQLite schema creation
   - Add a SQLite-specific Drizzle config or provision script.
   - Target `drizzle/schema.sqlite.mvp.ts`.
   - Validate that a fresh SQLite DB contains all 66 tables.

3. Phase 2B.2 - Runtime boot retry
   - Start with `DATABASE_PROVIDER=sqlite`.
   - Confirm `pdf_categories` exists.
   - Confirm runtime no longer crashes at boot.

4. Phase 2B.3 - MySQL -> SQLite export/import plan
   - Define source MySQL extraction.
   - Define SQLite insert order.
   - Preserve foreign key constraints and identity values where required.

Deployment should not proceed until empty SQLite schema provisioning is implemented and validated.

## 15. Final Audit Result

```text
SQLite schema source: drizzle/schema.sqlite.mvp.ts
SQLite table count: 66
pdf_categories SQLite definition: drizzle/schema.sqlite.mvp.ts:184
pdf_categories MySQL definition: drizzle/schema.ts:980
SQLite schema.sql: not found
SQLite migration directory: not found
SQLite migration snapshot: not found
MySQL migration snapshots: found, 133 files, mysql dialect
MySQL -> SQLite export flow: not found
Can create empty SQLite schema with current repo automation: no
Recommended next phase: Phase 2B SQLite Schema Provision
```
