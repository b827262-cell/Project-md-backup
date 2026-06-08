# SQLite Schema Provision Patch Report

Phase: 2B.1 - SQLite Drizzle Config + Fresh Schema Provision Patch  
Branch: `release/vps-lite`

## 1. Scope

Allowed files changed:

- `drizzle.config.sqlite.ts`
- `package.json`
- `drizzle/sqlite/*`
- `scripts/sqlite-provision.ts`
- `SQLITE_SCHEMA_PROVISION_PATCH_REPORT.md`

Forbidden areas were not modified:

- `server/db.ts`
- `server/db.sqlite.ts`
- `server/db.runtime.ts`
- routers
- business logic
- `drizzle/schema.ts`

## 2. SQLite Config

Created:

```text
drizzle.config.sqlite.ts
```

Configuration:

```text
schema: ./drizzle/schema.sqlite.mvp.ts
out: ./drizzle/sqlite
dialect: sqlite
dbCredentials.url: SQLITE_PATH or ./data/smartbook.db
```

Result:

```text
SQLITE_CONFIG_PASS
```

## 3. Package Scripts

Added:

```text
db:sqlite:generate
db:sqlite:migrate
db:sqlite:push:fresh
```

Existing MySQL scripts were preserved:

```text
db:push
db:sync
db:migrate
```

`db:sqlite:push:fresh` uses:

```text
tsx scripts/sqlite-provision.ts
```

Reason:

`drizzle-kit push` can create the schema, but fresh runtime boot then hits the existing `initializeDefaultPdfCategories()` path in `server/db.ts`. That path still uses canonical MySQL table metadata and can emit SQLite-incompatible `now()` during the startup seed insert. Because this phase forbids modifying `server/db.ts`, the fresh provision command pre-seeds the five required `pdf_categories` rows so runtime boot does not enter that MySQL-schema seed insert path.

## 4. Generated SQLite Artifacts

Command:

```text
pnpm db:sqlite:generate
```

Result:

```text
66 tables detected
SQL migration generated
```

Generated files:

```text
drizzle/sqlite/0000_gorgeous_marvex.sql
drizzle/sqlite/meta/0000_snapshot.json
drizzle/sqlite/meta/_journal.json
```

Artifact counts:

```text
total files = 3
SQL migrations = 1
meta JSON files = 2
```

Generated SQL inventory:

```text
CREATE TABLE count = 66
CREATE INDEX count = 16
pdf_categories CREATE TABLE = present
```

Snapshot dialect:

```text
sqlite
```

## 5. Fresh Provision Script

Created:

```text
scripts/sqlite-provision.ts
```

Behavior:

- Opens `SQLITE_PATH` or `./data/smartbook.db`.
- Applies:
  - `journal_mode = WAL`
  - `busy_timeout = 5000`
  - `foreign_keys = ON`
- Refuses to run if user tables already exist.
- Applies generated SQL migrations from `drizzle/sqlite/*.sql`.
- Inserts the five boot-required default `pdf_categories` rows.

Fresh-only guard:

```text
Refuses non-empty DB
```

## 6. Fresh DB Smoke

Disposable DB:

```text
/tmp/smartbook-lite-schema-smoke.db
```

Provision command:

```text
SQLITE_PATH=/tmp/smartbook-lite-schema-smoke.db pnpm db:sqlite:push:fresh
```

Result:

```text
SQLITE_SCHEMA_PROVISION_PASS path=/tmp/smartbook-lite-schema-smoke.db migrations=1 tables=66 pdfCategories=5
```

Runtime adapter verification:

```json
{"tableCount":66,"pdfTable":1,"pdfRows":5,"journalMode":"wal","foreignKeys":1}
```

Checklist:

```text
DB created: PASS
pdf_categories exists: PASS
sqlite_master user table count = 66: PASS
WAL enabled: PASS
foreign_keys enabled: PASS
```

## 7. Runtime Boot Retry

Command:

```text
DATABASE_PROVIDER=sqlite
SQLITE_PATH=/tmp/smartbook-lite-schema-smoke.db
PORT=5512
NODE_ENV=production
pnpm start
```

Result:

```text
Server running on http://localhost:5512/
```

The process was stopped by `timeout` after boot verification.

Runtime boot result:

```text
RUNTIME_BOOT_PASS
NO_MISSING_TABLE_ERROR
```

Notes:

- No `no such table: pdf_categories` error occurred.
- No `no such table` error occurred.
- The earlier `no such function: now` was avoided by fresh provision pre-seeding `pdf_categories`, without modifying runtime/business code.
- OAuth warning remains unrelated to SQLite schema provisioning:
  - `OAUTH_SERVER_URL is not configured`

## 8. Modified Files

Modified/created in this phase:

```text
drizzle.config.sqlite.ts
package.json
drizzle/sqlite/0000_gorgeous_marvex.sql
drizzle/sqlite/meta/0000_snapshot.json
drizzle/sqlite/meta/_journal.json
scripts/sqlite-provision.ts
SQLITE_SCHEMA_PROVISION_PATCH_REPORT.md
```

## 9. Compatibility Assessment

SQLite:

```text
Fresh schema provision path is now present.
Fresh DB contains all 66 MVP tables.
Runtime boot no longer fails on missing pdf_categories.
```

MySQL:

```text
Existing MySQL Drizzle config and scripts are preserved.
No MySQL runtime code was modified.
```

Operational:

```text
db:sqlite:push:fresh is intentionally fresh-only and refuses non-empty DBs.
```

## 10. Recommendation

Proceed to Phase 2B.2:

```text
SQLite Provisioned Runtime Validation
```

Recommended validation:

1. Run `db:sqlite:push:fresh` against a clean deployment DB path.
2. Verify 66 tables.
3. Verify `pdf_categories` has 5 default rows.
4. Boot with `DATABASE_PROVIDER=sqlite`.
5. Run router smoke for lessonPoints, smartBookLearning, smartBookRouter, and tutorRouter.

RC1 schema provision status:

```text
SQLITE_CONFIG_PASS
SQLITE_SCHEMA_PROVISION_PASS
TABLE_COUNT = 66
PDF_CATEGORIES_EXISTS
RUNTIME_BOOT_PASS
NO_MISSING_TABLE_ERROR
```
