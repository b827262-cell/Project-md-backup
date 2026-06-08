# SQLite Schema Provision Design

Phase: 2B.0 - SQLite Schema Provision Design  
Branch: `release/vps-lite`  
Scope: Audit/design only. No code patch, no table creation, no migration execution, no `drizzle push`.

## 1. Executive Summary

Runtime boot currently fails in SQLite mode because the SQLite DB file exists but has no schema:

```text
SqliteError: no such table: pdf_categories
```

The codebase already has a SQLite MVP schema source:

```text
drizzle/schema.sqlite.mvp.ts
```

The codebase also has a SQLite runtime adapter:

```text
server/db.sqlite.ts
```

But the current Drizzle config is MySQL-only:

```text
drizzle.config.ts
schema: ./drizzle/schema.ts
dialect: mysql
out: ./drizzle
```

Design conclusion:

Use **方案 A: SQLite Drizzle Config** as the RC1 production provisioning path, with an explicit operator-run provision/migration command. Do not create schema automatically from runtime boot.

## 2. Current Inputs

### 2.1 `drizzle/schema.sqlite.mvp.ts`

Observed:

- Defines 66 SQLite tables via `sqliteTable(...)`.
- Includes `pdf_categories` at `drizzle/schema.sqlite.mvp.ts:184`.
- Uses SQLite column modes for booleans, JSON, and timestamps.
- Contains production-readiness notes:
  - Indexes and unique constraints are partially omitted.
  - Enum validation is deferred to app/Zod or later CHECK constraints.
  - Some timestamp defaults are marked TODO.
  - Some FK relationships are comments rather than enforced references.

Assessment:

This is the correct SQLite schema source for the RC1 Lite runtime, but it should be treated as a deployable schema source only after a provisioning mechanism is added and validated.

### 2.2 `drizzle.config.ts`

Observed:

```ts
export default defineConfig({
  schema: "./drizzle/schema.ts",
  out: "./drizzle",
  dialect: "mysql",
  dbCredentials: {
    url: connectionString,
  },
});
```

Assessment:

- Current config is MySQL-only.
- Existing package scripts (`db:push`, `db:sync`, `db:migrate`) call Drizzle Kit through this default config.
- Running current Drizzle commands would target the MySQL schema/migration path, not the SQLite MVP schema.
- A separate SQLite config is needed to avoid damaging the existing MySQL migration history.

### 2.3 `server/db.sqlite.ts`

Observed:

- Uses `better-sqlite3`.
- Uses `drizzle-orm/better-sqlite3`.
- Imports `../drizzle/schema.sqlite.mvp`.
- Opens DB lazily via `getSqliteDb()`.
- Applies PRAGMAs:
  - `journal_mode = WAL`
  - `busy_timeout = 5000`
  - `foreign_keys = ON`
- Does not run DDL.
- Does not run Drizzle migrations.
- Does not inspect `sqlite_master`.

Assessment:

This file is correct as a runtime adapter. It should not become a schema provisioning engine for RC1.

## 3. Design Goals

The provisioning design should satisfy:

- Fresh SQLite DB can be created deterministically.
- RC1 deploy process is explicit and repeatable.
- Runtime boot does not silently mutate schema.
- MySQL runtime remains untouched.
- Future SQLite migrations can be generated and reviewed.
- 1GB VPS deployment remains simple and low-memory.

## 4. Option A - SQLite Drizzle Config

### Design

Add a dedicated SQLite Drizzle config that targets:

```text
schema: ./drizzle/schema.sqlite.mvp.ts
dialect: sqlite
driver/runtime: better-sqlite3-compatible Drizzle Kit settings
out: ./drizzle/sqlite
```

Then use explicit commands for SQLite schema generation/provisioning.

Possible implementation shape:

```text
drizzle.config.sqlite.ts
drizzle/sqlite/
drizzle/sqlite/meta/
```

Possible scripts:

```text
db:sqlite:generate
db:sqlite:migrate
db:sqlite:push
```

For RC1, prefer an explicit provision command against a disposable/fresh DB first, then production DB.

### Maintainability

High.

Reasons:

- Keeps schema source in TypeScript.
- Uses Drizzle's migration model.
- Keeps SQLite migration history separate from MySQL migration history.
- Future SQLite schema deltas can be reviewed as migration files.

### Deployment Difficulty

Medium.

Reasons:

- Requires one-time config and script setup.
- Requires deploy instructions to run SQLite provisioning before runtime boot.
- Must ensure `SQLITE_PATH` is passed to Drizzle Kit or a provision command.

### VPS Lite Compatibility

High.

Reasons:

- Drizzle Kit/provision command is a one-time deploy step.
- No long-running migration process at app boot.
- Better for 1GB memory than runtime boot doing schema checks repeatedly.

### Future Migration Ability

High.

Reasons:

- Supports versioned migrations.
- Supports snapshots.
- Keeps RC1 deploy path compatible with future schema evolution.

### Production Risk

Medium-Low.

Risks:

- `schema.sqlite.mvp.ts` still has TODOs and omitted constraints.
- Generated SQLite DDL must be reviewed before RC1 deploy.
- Need a clear "fresh DB only" versus "migrate existing DB" operator rule.

Mitigation:

- Generate migrations into a separate SQLite directory.
- Smoke test fresh DB has all 66 tables.
- Verify `pdf_categories` exists before runtime boot.

## 5. Option B - `schema.sqlite.sql`

### Design

Commit a generated or hand-reviewed SQL file:

```text
drizzle/schema.sqlite.sql
```

or:

```text
sql/schema.sqlite.sql
```

Provision command runs this SQL against the target SQLite DB before boot.

### Maintainability

Medium.

Reasons:

- Simple artifact to inspect.
- Easy to run with `sqlite3` or `better-sqlite3`.
- But schema drift risk is higher because TypeScript schema and SQL file can diverge.

### Deployment Difficulty

Low.

Reasons:

- One file, one command.
- Simple for VPS Lite operators.
- No Drizzle Kit setup needed at deploy time if SQL is pre-generated.

### VPS Lite Compatibility

High.

Reasons:

- Very low runtime and memory overhead.
- SQLite CLI or a tiny Node script can apply it quickly.

### Future Migration Ability

Low-Medium.

Reasons:

- A monolithic schema file works for fresh DB creation.
- It is weaker for incremental migrations.
- Requires a separate migration story once RC1 evolves.

### Production Risk

Medium.

Risks:

- Manual SQL drift.
- Potential mismatch with Drizzle runtime schema.
- Harder to maintain across future changes.

Mitigation:

- Generate SQL from `schema.sqlite.mvp.ts`, not by hand.
- Add checksum/version comment.
- Keep as RC1 fresh-provision-only artifact.

## 6. Option C - Runtime Auto Provision

### Design

Modify `server/db.sqlite.ts` so `getSqliteDb()` checks whether tables exist and creates missing tables automatically at boot.

Possible checks:

```text
sqlite_master
PRAGMA user_version
```

### Maintainability

Low.

Reasons:

- Mixes runtime connection code with schema lifecycle.
- Makes boot behavior stateful and harder to reason about.
- Can hide deployment mistakes until production boot.

### Deployment Difficulty

Low initially, high operationally.

Reasons:

- Looks easy because app boot would create schema.
- But production failures become app-start failures.
- Schema changes become runtime concerns.

### VPS Lite Compatibility

Medium.

Reasons:

- Fresh boot may do DDL work.
- Repeated boot checks add complexity.
- Locking behavior during auto-provision is risky under PM2 restarts.

### Future Migration Ability

Low.

Reasons:

- Runtime auto-create does not naturally provide a reviewed migration history.
- DDL changes become code branches.
- Harder to roll forward or diagnose partial schema states.

### Production Risk

High.

Risks:

- App boot mutates database.
- Crash loops can repeatedly encounter partial schema states.
- Conflates "runtime is healthy" with "migration succeeded".
- Harder to keep MySQL and SQLite paths conceptually clean.

Recommendation:

Do not use runtime auto provision for RC1.

## 7. Option Comparison

| Criteria | A. SQLite Drizzle Config | B. schema.sqlite.sql | C. Runtime Auto Provision |
| --- | --- | --- | --- |
| Maintainability | High | Medium | Low |
| Deployment difficulty | Medium | Low | Low initially / high operationally |
| VPS Lite compatibility | High | High | Medium |
| Future migration ability | High | Low-Medium | Low |
| Production risk | Medium-Low | Medium | High |
| MySQL isolation | High | High | Medium |
| RC1 suitability | Best | Acceptable fallback | Not recommended |

## 8. Recommended Solution

Recommended:

```text
方案 A - SQLite Drizzle Config
```

Use a dedicated SQLite Drizzle config and separate SQLite migration output directory.

RC1 deploy should run schema provisioning explicitly before runtime boot.

Do not modify `server/db.sqlite.ts` to auto-create tables.

## 9. Proposed Implementation Steps

Step 1 - Add SQLite Drizzle config

```text
drizzle.config.sqlite.ts
```

Target:

```text
schema: ./drizzle/schema.sqlite.mvp.ts
out: ./drizzle/sqlite
dialect: sqlite
```

Step 2 - Add package scripts

Potential scripts:

```text
db:sqlite:generate
db:sqlite:migrate
db:sqlite:push:fresh
```

Exact script names should make the target provider explicit.

Step 3 - Generate SQLite migration artifacts

Expected output:

```text
drizzle/sqlite/*.sql
drizzle/sqlite/meta/*.json
```

Step 4 - Review generated DDL

Review specifically:

- `pdf_categories`
- All 66 tables
- primary keys
- indexes
- unique constraints
- JSON columns
- boolean columns
- timestamp columns

Step 5 - Fresh DB smoke

Use disposable DB only:

```text
SQLITE_PATH=/tmp/smartbook-lite-schema-smoke.db
```

Verify:

- DB file created
- `pdf_categories` exists
- all 66 tables exist
- WAL enabled
- foreign keys enabled
- no leftover DB/WAL/SHM after smoke

Step 6 - Runtime boot retry

Run:

```text
DATABASE_PROVIDER=sqlite
SQLITE_PATH=./data/smartbook.db
```

Expected:

```text
RUNTIME_PASS
no "no such table: pdf_categories"
```

## 10. Estimated Modified Files

Expected for Phase 2B.1 implementation:

Required:

```text
drizzle.config.sqlite.ts
package.json
```

Generated/provision artifacts:

```text
drizzle/sqlite/*.sql
drizzle/sqlite/meta/*.json
```

Optional:

```text
scripts/sqlite-provision.ts
SQLITE_SCHEMA_PROVISION_PATCH_REPORT.md
```

Not recommended for this batch:

```text
server/db.sqlite.ts
server/db.ts
routers
schema.ts
```

## 11. Estimated Risk

Overall risk:

```text
Medium
```

Risk reasons:

- `schema.sqlite.mvp.ts` is not yet backed by SQLite migration snapshots.
- The file still marks some production constraints/defaults as TODO.
- First generated DDL may surface type/default/index issues.

Risk reducers:

- Router/runtime compatibility blockers are already cleared.
- Schema source is already present and bound to runtime.
- Provisioning can be validated against disposable SQLite DB before touching deployment DB.
- MySQL path can stay isolated by using a separate config and output directory.

## 12. RC1 Deployment Suitability

方案 A is suitable as the SmartBook Lite RC1 formal deployment solution if implemented with:

- dedicated SQLite config
- explicit provision command
- generated SQLite migration artifacts
- disposable fresh DB smoke
- runtime boot retry

方案 B is acceptable only as a short-term fallback if Drizzle Kit SQLite generation is blocked.

方案 C is not suitable for RC1 production deployment.

## 13. Final Recommendation

Proceed to Phase 2B.1:

```text
SQLite Drizzle Config + Fresh Schema Provision Patch
```

Target success criteria:

```text
SQLite config present
SQLite migration/provision artifact present
fresh DB has 66 tables
pdf_categories exists
runtime boot no longer fails on missing table
no MySQL config regression
```
