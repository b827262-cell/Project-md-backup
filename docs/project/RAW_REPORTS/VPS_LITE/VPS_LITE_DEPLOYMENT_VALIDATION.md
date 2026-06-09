# VPS Lite Deployment Validation

Branch: `release/vps-lite`
Scope: Validation only. No schema change, migration change, runtime refactor, router refactor, package upgrade, or feature work.

## 1. Environment

Environment commands:

```text
uname -a
Linux b822726-NB-TUFA16 7.0.9-arch1-1 #1 SMP PREEMPT_DYNAMIC Sun, 17 May 2026 17:23:07 +0000 x86_64 GNU/Linux

node -v
v20.20.2

npm -v
10.8.2

pnpm -v
10.4.1
```

Memory:

```text
Mem: 14Gi total, 8.9Gi used, 1.3Gi free, 6.0Gi available
Swap: 0B
```

Disk:

```text
/dev/sda2 467G total, 84G used, 359G available, 19% used
```

Assessment:

```text
ENVIRONMENT_PASS = PARTIAL
```

Notes:

- This host is not a 1GB VPS. It has 14GiB RAM and no swap.
- Node and package manager versions are valid for the runtime.
- Disk capacity is sufficient in this environment.
- True 1GB VPS resource validation still needs to be repeated on the target VPS.

## 2. SQLite Runtime

Command:

```bash
node -e "const Database=require('better-sqlite3'); const db=new Database(':memory:'); console.log(db.prepare('select sqlite_version() as v').get());"
```

Result:

```text
{ v: '3.53.1' }
SQLITE_RUNTIME_PASS
```

Assessment:

```text
SQLITE_PASS = YES
```

## 3. Build Result

Install:

```text
pnpm install
Done in 1.4s
real 0m1.718s
```

Build:

```text
pnpm build
PASS
real 0m21.053s
```

Build warnings:

```text
Duplicate key "getCategoryExamSources" in smartBookRouter.ts
Duplicate key "searchExamSources" in smartBookRouter.ts
Duplicate key "addCategoryExamSource" in smartBookRouter.ts
Duplicate key "removeCategoryExamSource" in smartBookRouter.ts
Duplicate key "viewQA" in smartBookRouter.ts
```

Assessment:

```text
BUILD_PASS = YES
```

Notes:

- Build succeeded.
- Warnings are existing duplicate object keys, not build blockers.
- Peak build memory was not captured because `/usr/bin/time` is not installed in this environment.

## 4. Runtime Boot

Runtime command:

```bash
DATABASE_PROVIDER=sqlite SQLITE_PATH=./data/smartbook.db PORT=5011 NODE_ENV=production ENABLE_TRPC_REQUEST_LOGS=false pnpm start
```

Result:

```text
FAIL
SqliteError: no such table: pdf_categories
```

Observed startup log:

```text
[OAuth] ERROR: OAUTH_SERVER_URL is not configured
[AI] Google Generative AI key exists: true
SqliteError: no such table: pdf_categories
```

Assessment:

```text
RUNTIME_PASS = NO
```

Root cause:

- `./data/smartbook.db` was created, but it contains no schema tables.
- Runtime boot touches `pdf_categories` early and crashes because the table is missing.

Important:

- This validation did not run migrations or create schema because the phase explicitly forbids migration/schema changes.
- No MySQL connection attempt was observed before the SQLite schema failure.

## 5. Router Smoke

Requested router smoke:

- lessonPointsRouter
- smartBookLearningRouter
- smartBookRouter
- tutorRouter
- Create / Read / Update

Result:

```text
ROUTER_SMOKE_PASS = NO
```

Reason:

- Production runtime did not boot due to missing SQLite schema table `pdf_categories`.
- Router CRUD smoke cannot be validly executed against an empty SQLite DB.

What was validated previously:

- RC1 final import smoke passed for all four target routers in both MySQL and SQLite modes.

What remains:

- Router CRUD smoke must be rerun after the target SQLite DB has the expected schema.

## 6. SQLite Verification

DB file:

```text
data/smartbook.db exists
size: 4.0K
```

Tables:

```text
sqlite3 data/smartbook.db ".tables"
<empty>
```

CLI PRAGMA:

```text
journal_mode = wal
foreign_keys = 0
```

App connection PRAGMA through `getSqliteDb()`:

```text
journal_mode { journal_mode: 'wal' }
foreign_keys { foreign_keys: 1 }
```

Assessment:

```text
SQLite file exists: YES
WAL mode: YES
Foreign keys enabled in app connection: YES
Schema tables present: NO
```

## 7. Resource Usage

Current memory snapshot after validation:

```text
Mem: 14Gi total, 8.3Gi used, 2.8Gi free, 6.6Gi available
Swap: 0B
```

Process snapshot:

```text
No running node dist/index.js / pnpm start / ai-tutor-helper process after runtime crash.
```

Peak memory:

```text
Not captured
```

Reason:

- `/usr/bin/time` is not installed on this host.
- Runtime exited early before a steady-state memory profile could be captured.

Assessment:

```text
RESOURCE_PASS = PARTIAL
```

Notes:

- This is not a 1GB VPS, so resource numbers are not representative of target deployment.

## 8. PM2 Verification

PM2 command results:

```text
pm2 status
/bin/bash: pm2: command not found

pm2 logs --lines 50
/bin/bash: pm2: command not found
```

Project PM2 config:

```text
ecosystem.config.cjs exists
app name: ai-tutor-helper
script: dist/index.js
max_memory_restart: 450M
NODE_OPTIONS: --max-old-space-size=384
```

Assessment:

```text
PM2_PASS = NO
```

Reason:

- PM2 is not installed in this validation environment.
- No PM2 process could be started or inspected.

## 9. Issues Found

### Blocker 1: SQLite schema is absent

Severity:

```text
Deployment blocker
```

Evidence:

```text
SqliteError: no such table: pdf_categories
sqlite3 data/smartbook.db ".tables" => empty
```

Impact:

- Runtime boot fails.
- Router CRUD smoke cannot run.
- RC1 cannot be deployed on VPS Lite until the SQLite DB has the expected schema.

### Blocker 2: PM2 not installed in validation environment

Severity:

```text
Deployment validation blocker for PM2 step
```

Impact:

- Cannot verify PM2 status, logs, auto restart, or crash-loop behavior.

### Blocker 3: Environment is not the target 1GB VPS

Severity:

```text
Validation caveat
```

Impact:

- Resource validation is not representative.
- Must rerun memory and PM2 checks on the actual VPS.

### Non-blocking build warnings

Build produced duplicate key warnings in `smartBookRouter.ts`.

Impact:

- Not a build blocker.
- Should be tracked separately if route override behavior matters.

## 10. Deployment Recommendation

Current deployment recommendation:

```text
RC1_DEPLOY_READY = NO
```

Reason:

- Build passes.
- SQLite driver works.
- Dual-mode import readiness was previously confirmed.
- But production runtime boot fails against `./data/smartbook.db` because the SQLite schema is missing.
- PM2 validation cannot run because PM2 is not installed in this environment.

Required next validation actions:

1. Provide or create the intended SQLite schema/database through the approved deployment process.
2. Rerun runtime boot with `DATABASE_PROVIDER=sqlite` and `SQLITE_PATH=./data/smartbook.db`.
3. Rerun router CRUD smoke after schema exists.
4. Install/enable PM2 on the target VPS, then run `pm2 start ecosystem.config.cjs`.
5. Rerun PM2 status/logs and resource checks on the actual 1GB VPS.

Do not proceed to production deployment until:

```text
RUNTIME_PASS
ROUTER_SMOKE_PASS
PM2_PASS
```
