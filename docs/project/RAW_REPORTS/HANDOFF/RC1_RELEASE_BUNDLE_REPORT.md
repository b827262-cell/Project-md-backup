# RC1 Release Bundle Report

Project: `AI Tutor Helper / SmartBook Lite`  
Branch: `release/vps-lite`  
Date: `2026-06-05`

## RC1 Current Status

Current release evidence on this branch shows:

- `RC1_FINAL_VALIDATION_REPORT.md` -> `RC1_DEPLOY_READY = CONDITIONAL YES`
- `RC1_RELEASE_CHECKLIST.md` -> `READY_FOR_VPS_LITE_RC1 = YES`
- `RC1_RELEASE_READINESS.md` -> `READY_TO_TAG_RC1 = YES`

Working conclusion:

```text
RC1 status = READY
Deployment status = CONDITIONAL READY
```

The newer RC1 validation artifacts supersede earlier pre-launch analysis that marked SQLite as not yet ready before the final router and runtime fixes landed.

## SQLite Migration Status

SQLite migration status for the RC1 core path:

- SQLite MVP schema exists and is validated at `66` tables.
- `server/db.sqlite.ts` is functional and uses WAL mode, `busy_timeout=5000`, and `foreign_keys=ON`.
- `server/db.runtime.ts` provides dual-mode provider selection.
- Core RC1 router validation is marked PASS for:
  - `smartBookRouter`
  - `tutorRouter`
  - `lessonPointsRouter`
  - `smartBookLearningRouter`
- Local auth is dual-mode aware and explicitly timestamps inserts.
- Admin stats SQLite date binding fix is documented in `SQLITE_RC1_HOTFIX2_STATS_REPORT.md`.

Remaining SQLite conditions:

- `mysql2` must remain installed because `server/db.ts` still contains a static MySQL import.
- Non-core routers outside the Lite MVP may still fail when invoked under SQLite mode.
- Target SQLite DB must be provisioned before runtime boot.

## Runtime Bundle Status

Runtime bundle evidence from `DEPLOYMENT_MANIFEST.md`:

- Bundle name: `smartbook-lite-runtime.tar.gz`
- Bundle size: `6.4M`
- Bundle SHA256: `2ad4bfa1034c473db503af7db3dbb865f9c15a3405d37541c62084031e31fd22`
- DB backup name: `backup_ai_tutor_20260603.sql`
- DB backup size: `5.1M`
- DB backup SHA256: `64aa6c8b7aad413fcb71c8ec823d5f83907ff3006da128ec6a9811dec7964d16`
- Release branch: `release/vps-lite`
- Build time: `2026-06-03T13:34:32+08:00`

Runtime prerequisites from the runbook:

- `DATABASE_PROVIDER=sqlite`
- `SQLITE_PATH=./data/smartbook.db`
- writable `./data/`
- `better-sqlite3` loadable on the target host
- `pnpm db:sqlite:push:fresh` run before first boot

## Production Readiness Summary

Production readiness for the Lite RC1 scope is positive if deployment follows the documented sequence.

Release-ready core surface:

- auth
- SmartBook CRUD
- Tutor session CRUD
- Lesson points
- SmartBook learning
- TRPC routing
- health endpoint

Operational conditions still required before VPS cutover:

- provision the SQLite schema
- keep `mysql2` installed
- set `.env` correctly
- ensure PM2 reads the intended environment
- validate on the target VPS, not only the development machine

## Open Issues

Open issues are operational or scope-boundary issues, not current RC1 core blockers:

- `mysql2` dependency must remain installed even in SQLite mode.
- Non-core routers may throw under SQLite if those endpoints are invoked.
- SQLite runtime boot fails against an empty DB; schema push is mandatory before first start.
- Actual 1 GB VPS validation still depends on target-host execution, not only local validation.
- Existing duplicate-key build warnings remain in `smartBookRouter.ts`, but they are not build blockers.

## Rollback Strategy

Rollback path is documented and simple because the runtime is dual-mode:

1. stop the app
2. change `.env` from `DATABASE_PROVIDER=sqlite` to `DATABASE_PROVIDER=mysql`
3. restore the MySQL connection string if needed
4. restart PM2
5. verify `/api/trpc/system.health`

SQLite file rollback is also supported:

- copy-back SQLite DB backup if the SQLite file itself is the issue
- keep the runtime bundle unchanged
- restart PM2 after restore

## Deployment Recommendation

Recommended release posture:

```text
Proceed with RC1 release bundle preparation and VPS deployment only when:
  - SQLite schema is provisioned
  - .env is configured
  - data/ is writable
  - mysql2 remains installed
  - smoke checks pass on the target VPS
```

Final recommendation:

```text
RC1_READY = YES
VPS_DEPLOY_READY = YES
```

This is a conditional YES tied to deployment discipline, not a claim that a blank VPS can boot successfully without schema provision and environment setup.
