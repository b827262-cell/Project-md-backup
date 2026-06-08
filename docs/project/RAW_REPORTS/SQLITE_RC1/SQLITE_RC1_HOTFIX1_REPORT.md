# SmartBook Lite SQLite RC1 Hotfix 1 Report

## Date

2026-06-04

## Branch

release/vps-lite

## Commit Before

48b8f2f4

## Root Cause

SQLite runtime boot completed `seedDefaultAdminIfNeeded()`, then entered
`initializeDefaultPdfCategories()`.

That function used the canonical MySQL `pdfCategories` table metadata from
`drizzle/schema.ts` while running on the SQLite Drizzle handle. The MySQL schema
defines `createdAt` and `updatedAt` with `defaultNow()`, causing Drizzle to emit:

```sql
values (..., (now()), (now()))
```

SQLite has no `now()` function, so startup failed with:

```text
SqliteError: no such function: now
```

## Files Changed

- `server/db.ts`
- `SQLITE_RC1_HOTFIX1_REPORT.md`

## Patch Summary

- Added SQLite-only `pdfCategories` metadata import from `drizzle/schema.sqlite.mvp`.
- Added an `isSqliteMode()` branch at the start of `initializeDefaultPdfCategories()`.
- SQLite branch inserts default PDF categories through `sqlitePdfCategories`.
- SQLite branch explicitly writes `createdAt` and `updatedAt` using one shared `const now = new Date()`.
- Original MySQL production path remains unchanged.
- No changes to `drizzle/schema.ts`.
- No changes to `drizzle/schema.sqlite.mvp.ts`.
- No router changes.

## Validation Commands

```bash
git diff -- server/db.ts
git status --short
rm -f data/smartbook-lite.db data/smartbook-lite.db-wal data/smartbook-lite.db-shm
SQLITE_PATH=./data/smartbook-lite.db pnpm run db:sqlite:push:fresh
node -e "const Database=require('better-sqlite3'); const db=new Database('./data/smartbook-lite.db'); db.prepare('delete from pdf_categories').run(); console.log(JSON.stringify({pdfCategories: db.prepare('select count(*) as count from pdf_categories').get().count, users: db.prepare('select count(*) as count from users').get().count})); db.close();"
DATABASE_PROVIDER=sqlite SQLITE_PATH=./data/smartbook-lite.db SESSION_SECRET=smartbook-lite-session-secret-20260604-e500 JWT_SECRET=smartbook-lite-jwt-secret-20260604-e500 DEFAULT_ADMIN_USERNAME=admin DEFAULT_ADMIN_PASSWORD=admin123456 DEFAULT_ADMIN_NAME=Admin pnpm dev
curl -s -o /tmp/smartbook-login.html -w "%{http_code}\n" http://127.0.0.1:3001/login
curl -s -i -X POST http://127.0.0.1:3001/api/trpc/auth.loginLocal -H 'content-type: application/json' --data '{"json":{"username":"admin","password":"admin123456"}}'
pnpm build
```

## SQLite Provision Result

```text
SQLITE_SCHEMA_PROVISION_PASS path=./data/smartbook-lite.db migrations=1 tables=66 pdfCategories=5
```

For runtime validation, `pdf_categories` was then cleared so the patched startup
seed path executed directly.

## pnpm dev Result

```text
[Auth] Seeded development admin user: admin
[Database] Initialized default PDF categories
Port 3000 is busy, using port 3001 instead
Server running on http://localhost:3001/
```

No `SqliteError: no such function: now`.

No `Database not available`.

## loginLocal Result

`/login` returned HTTP 200.

`auth.loginLocal` returned HTTP 200 with:

```json
{
  "success": true,
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

SQLite row check after boot:

```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "loginMethod": "local"
    }
  ],
  "pdfCategories": 5
}
```

## pnpm build Result

`pnpm build` completed successfully:

```text
Done
```

## Remaining Warnings

Existing esbuild duplicate object key warnings remain and were not changed:

- `getCategoryExamSources`
- `searchExamSources`
- `addCategoryExamSource`
- `removeCategoryExamSource`
- `viewQA`

These warnings are outside the SQLite RC1 hotfix scope.

## Final Verdict

PASS. SQLite RC1 startup no longer emits MySQL `now()` from the default PDF
category seed path. Admin seed, default category seed, login page, local admin
login, and production build all pass.
