# SQLite Provisioned Runtime Validation

Phase: 2B.2 - SQLite Provisioned Runtime Validation  
Branch: `release/vps-lite`

## 1. Scope

Validation only.

No schema changes, runtime changes, router patches, or business logic changes were made.

Validated fresh-provisioned SQLite runtime using:

```text
DATABASE_PROVIDER=sqlite
SQLITE_PATH=/tmp/smartbook-lite-runtime-validation.db
```

Provision command:

```text
SQLITE_PATH=/tmp/smartbook-lite-runtime-validation.db pnpm db:sqlite:push:fresh
```

Provision result:

```text
SQLITE_SCHEMA_PROVISION_PASS path=/tmp/smartbook-lite-runtime-validation.db migrations=1 tables=66 pdfCategories=5
```

## 2. Router Smoke Summary

```text
lessonPointsRouter PASS
smartBookLearningRouter PASS
smartBookRouter PASS
tutorRouter PASS
```

Final result:

```text
ROUTER_SMOKE_PASS
Router PASS = 4
Router FAIL = 0
```

## 3. lessonPointsRouter

Validated:

- Create lesson point
- Read lesson point
- Update publication state
- JSON round-trip for `options`
- JSON round-trip for `classroomQuiz`
- Boolean false write/read
- Boolean true update/filter
- Timestamp write/read
- Insert return via `.returning({ id })`

Result:

```text
lessonPointsRouter PASS
```

## 4. smartBookLearningRouter

Validated:

- Query progress
- Insert `smart_book_progress`
- Update `progressPercent`
- Update `lastPage`
- Timestamp write/read for completion/update fields

Result:

```text
smartBookLearningRouter PASS
```

## 5. smartBookRouter

Validated:

- SmartBook read
- SmartBook JSON fields:
  - `pageIndex`
  - `pdfToc`
  - `batchQaProgress`
- Usage stats flow via `smart_book_credits`
- Wrong answer insert
- Wrong answer `isLearned=false` filter
- Wrong answer update to `isLearned=true`
- Wrong answer `isLearned=true` filter
- Insert return via `.returning({ id })`

Result:

```text
smartBookRouter PASS
```

## 6. tutorRouter

Validated:

- Tutor subject create
- Session create
- Session read
- Tutor message create
- Message JSON fields:
  - `sources`
  - `imageUrls`
- Cache flow via `book_suggestion_cache`
- Upsert-compatible flow via `onConflictDoUpdate`
- Boolean write/read for `isHiddenByUser` and `isEnabled`
- Insert return via `.returning({ id })`

Result:

```text
tutorRouter PASS
```

## 7. Compatibility Checks

Smoke output:

```json
{
  "routers": {
    "lessonPointsRouter": "PASS",
    "smartBookLearningRouter": "PASS",
    "smartBookRouter": "PASS",
    "tutorRouter": "PASS"
  },
  "checks": {
    "transaction": "PASS",
    "insertReturn": "PASS",
    "boolean": "PASS",
    "json": "PASS",
    "timestamp": "PASS",
    "upsertFallback": "PASS"
  },
  "errors": [],
  "peakMemoryApproxMB": 102,
  "durationMs": 13,
  "routerPass": 4,
  "routerFail": 0
}
```

Validated:

```text
insert return PASS
upsert fallback PASS
boolean PASS
json PASS
timestamp PASS
sqlite transaction PASS
```

## 8. SQLite Query Errors

SQLite query errors:

```text
0
```

No SQLite query errors occurred in the final router smoke.

Earlier discarded smoke attempts failed due to validation-script issues only:

- async callback passed to better-sqlite3 transaction
- shell quoting issue in raw SQL test command

Those were corrected before final validation and are not runtime/schema failures.

## 9. Runtime Boot

Runtime boot command:

```text
DATABASE_PROVIDER=sqlite
SQLITE_PATH=/tmp/smartbook-lite-runtime-validation.db
PORT=5513
NODE_ENV=production
pnpm start
```

Result:

```text
Server running on http://localhost:5513/
```

The process was intentionally stopped by `timeout` after boot verification.

Runtime errors:

```text
0 SQLite runtime errors
0 missing table errors
0 no such table errors
```

Known unrelated warning:

```text
OAUTH_SERVER_URL is not configured
```

This warning is unrelated to SQLite schema/runtime validation.

## 10. Memory

Router smoke process memory:

```text
rss = 107,298,816 bytes
peakMemoryApproxMB = 102 MB
heapTotal = 21,393,408 bytes
heapUsed = 14,905,856 bytes
```

Peak memory reported here is the smoke-process RSS approximation from `process.memoryUsage()`, not a long-running production PM2 peak.

## 11. RC1 Readiness

Provisioned SQLite DB:

```text
PASS
```

Four core router validation:

```text
PASS
```

Runtime boot:

```text
PASS
```

Final deployment status:

```text
RC1_DEPLOY_READY
```

## 12. Recommendation

Proceed to VPS Lite Deployment Validation with provisioned SQLite DB.

Recommended next validation:

1. Run `pnpm db:sqlite:push:fresh` against the deployment SQLite path.
2. Boot production with `DATABASE_PROVIDER=sqlite`.
3. Run API-level router smoke through the deployed HTTP/TRPC surface.
4. Verify PM2 restart behavior.
5. Capture process RSS under realistic user traffic.
