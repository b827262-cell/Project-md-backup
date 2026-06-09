# RC1 Release Readiness Report

**Branch:** `release/vps-lite`  
**Date:** 2026-06-04  
**Status:** READY_TO_TAG_RC1 = YES

---

## 1. Branch State

| Property | Value |
|----------|-------|
| Branch | `release/vps-lite` |
| Modified files | 8 (code + deps from prior phases) |
| New files | 78 (docs, schemas, adapters, configs) |
| Excluded files | 4 (DB artifacts, tooling cache, backups) |
| Uncommitted code changes | schema, runtime, router, auth — all from prior audited phases |

---

## 2. Modified Files (Prior Phases)

These 8 files were modified during Phase 1-A through RC1 and represent the core SQLite migration:

| File | Changes | Purpose |
|------|---------|---------|
| `package.json` | +6 lines | Added `better-sqlite3`, `@types/better-sqlite3` |
| `pnpm-lock.yaml` | +202 lines | Lockfile for new dependencies |
| `server/db.ts` | +245 / -100 | Dual-mode `getDb()`, SQLite compat helpers |
| `server/localAuth.ts` | +47 / -30 | Dual-mode `usersTable()`, explicit timestamps |
| `server/routers/lessonPointsRouter.ts` | +71 / -50 | Boolean/timestamp mode, insert ID normalization |
| `server/routers/smartBookLearningRouter.ts` | +55 / -35 | Dual-mode insert ID, `isSqliteMode()` guards |
| `server/routers/smartBookRouter.ts` | +216 / -180 | NOW() removal, date mode-awareness |
| `server/routers/tutorRouter.ts` | +171 / -130 | Random/timestamp/insert ID normalization |

**Total:** +673 insertions, -340 deletions

---

## 3. New Files — SQLite Core

| File | Purpose |
|------|---------|
| `drizzle/schema.sqlite.mvp.ts` | SQLite schema (66 tables) |
| `drizzle.config.sqlite.ts` | Drizzle config for SQLite |
| `drizzle/sqlite/0000_gorgeous_marvex.sql` | Generated migration SQL |
| `drizzle/sqlite/meta/0000_snapshot.json` | Migration snapshot |
| `drizzle/sqlite/meta/_journal.json` | Migration journal |
| `server/db.sqlite.ts` | SQLite adapter (lazy singleton, PRAGMAs) |
| `server/db.runtime.ts` | Runtime mode detection |
| `scripts/sqlite-provision.ts` | Schema provision + seed script |
| `.npmrc` | pnpm build config |

---

## 4. New Files — Release Artifacts

| File | Purpose |
|------|---------|
| `.env.production.sqlite.example` | Production env template |
| `RC1_FINAL_VALIDATION_REPORT.md` | PASS/FAIL matrix for all 9 categories |
| `RC1_RELEASE_CHECKLIST.md` | Deployment checklist with sign-off |
| `RC1_READINESS_REVIEW.md` | Initial readiness review |
| `RC1_READINESS_REVIEW_FINAL.md` | Final readiness review (P0 = 0) |
| `VPS_DEPLOYMENT_RUNBOOK.md` | Step-by-step deployment guide |

---

## 5. New Files — Audit & Design Reports (58 files)

These document the entire migration journey from Phase 1-A through RC1:

| Category | Count | Examples |
|----------|-------|---------|
| Schema audit | 8 | `MYSQL_TO_SQLITE_SCHEMA_AUDIT.md`, `SQLITE_MVP_SCHEMA_DRAFT_REPORT.md` |
| Runtime audit | 7 | `SQLITE_RUNTIME_DEPENDENCY_AUDIT.md`, `DB_RUNTIME_AUDIT.md` |
| Router patch reports | 18 | `SMARTBOOK_ROUTER_PATCH_1A_REPORT.md` through `TUTOR_ROUTER_PATCH_1J1E_REPORT.md` |
| Design docs | 6 | `SQLITE_DUAL_MODE_RUNTIME_DESIGN.md`, `SQLITE_RUNTIME_WIRING_DESIGN.md` |
| Pilot reports | 5 | `DUAL_MODE_PILOT_REPORT.md`, `LESSON_POINTS_SQLITE_PILOT_REPORT.md` |
| Provision/validation | 8 | `SQLITE_SCHEMA_PROVISION_AUDIT.md`, `SQLITE_SMOKE_TEST_REPORT.md` |
| Deployment docs | 6 | `VPS_LITE_DEPLOYMENT_VALIDATION.md`, `docs/deployment/VPS_1GB_DEPLOYMENT_GUIDE.md` |

---

## 6. Excluded from Commit

| File/Directory | Reason |
|----------------|--------|
| `data/smartbook.db` | Already gitignored (`*.db`) |
| `data/smartbook.db-wal` | SQLite WAL — must be gitignored |
| `data/smartbook.db-shm` | SQLite SHM — must be gitignored |
| `deployment-backups/` | Local backup — must be gitignored |
| `.antigravitycli/` | Tooling cache — must be gitignored |

**Action Required:** Add `data/`, `deployment-backups/`, `.antigravitycli/` to `.gitignore` before committing.

---

## 7. Known Conditions

| # | Condition | Status |
|---|-----------|--------|
| 1 | `mysql2` npm package must remain installed | ✅ Present in `package.json` |
| 2 | `DATABASE_PROVIDER=sqlite` must be set in `.env` | ✅ Template provided |
| 3 | `SQLITE_PATH` must be set in `.env` | ✅ Template provided |
| 4 | `./data/` directory must exist and be writable | ✅ Documented in runbook |
| 5 | Non-core routers may throw in SQLite mode | ✅ Documented, non-blocking |
| 6 | Health endpoint does not check DB connectivity | ✅ By design (liveness only) |

---

## 8. Validation Summary

| Phase | Status |
|-------|--------|
| Phase 1-A: Schema Audit | ✅ PASS |
| Phase 1-B: Lite Scope Definition | ✅ PASS |
| Phase 1-C: SQLite MVP Schema Draft | ✅ PASS |
| Phase 1-C.5: Runtime Dependency Audit | ✅ PASS |
| Phase 1-D/E: SQLite Adapter & Wiring | ✅ PASS |
| Phase 2: Router Migration (4 routers) | ✅ PASS |
| Phase 3: Local Auth Migration | ✅ PASS |
| RC1 Final Validation | ✅ PASS |
| RC1.1 Deployment Packaging | ✅ PASS |

---

## 9. Release Recommendation

```text
READY_TO_TAG_RC1 = YES

Proposed tag:    v1.0.0-rc1-sqlite
Proposed commit: feat(sqlite): SQLite dual-mode runtime for VPS Lite deployment
```
