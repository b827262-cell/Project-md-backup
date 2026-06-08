# SmartBook Lite SQLite RC1 Hotfix 2 Stats Report

## Date

2026-06-04

## Branch

release/vps-lite

## Commit Before

487d99e2

## Root Cause

Admin Dashboard stats queries converted request date strings into JavaScript
`Date` objects, then bound those values directly into better-sqlite3 queries.

better-sqlite3 accepts only numbers, strings, bigints, buffers, and null bind
values. Under `DATABASE_PROVIDER=sqlite`, direct `Date` binding caused:

```text
SQLite3 can only bind numbers, strings, bigints, buffers, and null
```

Affected API paths:

- `stats.getAdminStats`
- `stats.getAllQuestions`

## File Changed

- `server/stats.ts`

## Patch Summary

- Added `adminStatsTimestamp(date)`.
- In SQLite mode, date values are converted to Unix seconds:

```ts
Math.floor(date.getTime() / 1000)
```

- In MySQL mode, date values remain JavaScript `Date` objects.
- Applied the conversion to date filters in:
  - `getAdminStats()`
  - `getAllQuestions()`
- Did not modify:
  - `getCommonKeywords`
  - routers
  - schema files
  - runtime files
  - `server/db.ts`

## APIs Validated

- `/login`
- `auth.loginLocal`
- `/admin`
- `stats.getAdminStats`
- `stats.getAllQuestions`
- `stats.getCommonKeywords`

## Validation Commands

```bash
DATABASE_PROVIDER=sqlite \
SQLITE_PATH=./data/smartbook-lite.db \
SESSION_SECRET=smartbook-lite-session-secret-20260604-e500 \
JWT_SECRET=smartbook-lite-jwt-secret-20260604-e500 \
DEFAULT_ADMIN_USERNAME=admin \
DEFAULT_ADMIN_PASSWORD=admin123456 \
DEFAULT_ADMIN_NAME=Admin \
pnpm dev

curl -s -i -c /tmp/smartbook-cookies-phase2b.txt -b /tmp/smartbook-cookies-phase2b.txt \
  -X POST http://127.0.0.1:3001/api/trpc/auth.loginLocal \
  -H 'content-type: application/json' \
  --data '{"json":{"username":"admin","password":"admin123456"}}'

curl -s -o /tmp/smartbook-admin-phase2b.html -w "%{http_code}\n" \
  http://127.0.0.1:3001/admin

curl -s -i -G -b /tmp/smartbook-cookies-phase2b.txt \
  --data-urlencode 'input={"json":{"startDate":"2026-05-05T00:00:00.000Z","endDate":"2026-06-04T00:00:00.000Z"}}' \
  http://127.0.0.1:3001/api/trpc/stats.getAdminStats

curl -s -i -G -b /tmp/smartbook-cookies-phase2b.txt \
  --data-urlencode 'input={"json":{"limit":20,"offset":0,"startDate":"2026-05-05T00:00:00.000Z","endDate":"2026-06-04T00:00:00.000Z"}}' \
  http://127.0.0.1:3001/api/trpc/stats.getAllQuestions

curl -s -i -G -b /tmp/smartbook-cookies-phase2b.txt \
  --data-urlencode 'input={"json":{"limit":20}}' \
  http://127.0.0.1:3001/api/trpc/stats.getCommonKeywords

pnpm build
```

## Results

- `/login`: HTTP 200
- `auth.loginLocal`: HTTP 200, `success: true`, `user.username: admin`, `role: admin`
- `/admin`: HTTP 200
- `stats.getAdminStats`: HTTP 200
- `stats.getAllQuestions`: HTTP 200
- `stats.getCommonKeywords`: HTTP 200
- `pnpm build`: PASS
- Server log: no new runtime blocker after Admin Dashboard stats validation

## Remaining Known Issues

Not fixed in this hotfix:

- `user_preferences` missing table
- `practice_exams` missing table
- better-sqlite3 transaction incompatibility candidates:
  - `server/db.ts:8527`
  - `server/db.ts:8599`
  - `server/db.ts:9791`
  - `server/db.ts:9848`

Existing build warnings remain and were not addressed:

- duplicate key `getCategoryExamSources`
- duplicate key `searchExamSources`
- duplicate key `addCategoryExamSource`
- duplicate key `removeCategoryExamSource`
- duplicate key `viewQA`

## Final Verdict

PASS. Admin Dashboard stats date filters no longer bind JavaScript `Date` values
into SQLite. The validated Admin Dashboard stats APIs return HTTP 200 under
SQLite runtime, and the production build passes.
