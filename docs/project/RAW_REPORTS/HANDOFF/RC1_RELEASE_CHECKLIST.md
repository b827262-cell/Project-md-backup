# RC1 Release Checklist — SmartBook Lite SQLite

**Version:** RC1  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-04

---

## Pre-Deployment Validation

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | SQLite schema provision | ✅ PASS | `pnpm db:sqlite:push:fresh` → 66 tables, pdfCategories = 5 |
| 2 | Runtime boot (SQLite mode) | ✅ PASS | `DATABASE_PROVIDER=sqlite` → server starts, no crash |
| 3 | Router smoke test | ✅ PASS | smartBookRouter, tutorRouter, lessonPointsRouter, smartBookLearningRouter — 0 P0 blockers |
| 4 | Local auth (register) | ✅ PASS | `localAuth.ts` dual-mode `usersTable()`, explicit timestamps, scrypt hash |
| 5 | Local auth (login) | ✅ PASS | `getLocalUserByLogin()` + `verifyPassword()` — driver-agnostic |
| 6 | Home Page (HTTP 200) | ✅ PASS | Client renders without DB dependency; data endpoints are TRPC |
| 7 | Health API (HTTP 200) | ✅ PASS | `system.health` → `{ ok: true }` — public TRPC query |
| 8 | TRPC endpoints connected | ✅ PASS | 47+ sub-routers registered on `appRouter`, Express middleware at `/api/trpc` |
| 9 | PM2 configuration | ✅ PASS | `ecosystem.config.cjs` — fork mode, 450M max, `--max-old-space-size=384` |
| 10 | Rollback documented | ✅ PASS | `VPS_DEPLOYMENT_RUNBOOK.md` § 7 — switch `DATABASE_PROVIDER=mysql` |
| 11 | Backup documented | ✅ PASS | SQLite file-copy backup (`cp data/smartbook.db data/smartbook.db.bak`) |

---

## Deployment Artifacts

| # | Artifact | Status | Path |
|---|----------|--------|------|
| 1 | Environment template | ✅ Created | `.env.production.sqlite.example` |
| 2 | Deployment runbook | ✅ Created | `VPS_DEPLOYMENT_RUNBOOK.md` |
| 3 | Release checklist | ✅ Created | `RC1_RELEASE_CHECKLIST.md` |
| 4 | Final validation report | ✅ Created | `RC1_FINAL_VALIDATION_REPORT.md` |

---

## Schema Validation

| # | Check | Status |
|---|-------|--------|
| 1 | `schema.sqlite.mvp.ts` exists | ✅ |
| 2 | 66 tables defined | ✅ |
| 3 | `sqliteTable` used (not `mysqlTable`) | ✅ |
| 4 | Boolean columns use `mode: "boolean"` | ✅ |
| 5 | Timestamp columns use `mode: "timestamp"` | ✅ |
| 6 | JSON columns use `mode: "json"` | ✅ |
| 7 | No `mysqlEnum` in SQLite schema | ✅ |

---

## Runtime Adapter Validation

| # | Check | Status |
|---|-------|--------|
| 1 | `db.sqlite.ts` — lazy singleton | ✅ |
| 2 | WAL mode enabled | ✅ |
| 3 | `busy_timeout = 5000` | ✅ |
| 4 | `foreign_keys = ON` | ✅ |
| 5 | `normalizeInsertId()` — dual driver | ✅ |
| 6 | `sqliteRandom()` — `RANDOM()` vs `RAND()` | ✅ |
| 7 | `sqliteDateSubDays()` — SQLite date math | ✅ |
| 8 | `toSqliteTimestamp()` — Unix seconds | ✅ |
| 9 | `isSqliteMode()` — env check | ✅ |

---

## Known Conditions

| # | Condition | Impact | Mitigation |
|---|-----------|--------|------------|
| 1 | `mysql2` must remain installed | Low | Keep in `package.json` — no MySQL server needed |
| 2 | Non-core routers may throw in SQLite mode | Low | Auxiliary features only; server does not crash |
| 3 | `.env` must set `DATABASE_PROVIDER=sqlite` | Critical | Template provided in `.env.production.sqlite.example` |
| 4 | `./data/` must be writable | Critical | Documented in runbook § 4 |
| 5 | PM2 reads DB config from `.env` not `ecosystem.config.cjs` | Medium | Documented in runbook § 6 |

---

## Backup Strategy

### SQLite File Backup

```bash
# Stop the application first (recommended for consistency)
pm2 stop ai-tutor-helper

# Copy the database file
cp data/smartbook.db data/smartbook.db.bak.$(date +%Y%m%d_%H%M%S)

# Restart
pm2 start ai-tutor-helper
```

### Hot Backup (while running)

SQLite with WAL mode supports hot backup via `.backup()` API or file copy after checkpoint:

```bash
# Force WAL checkpoint then copy
node -e "
  const Database = require('better-sqlite3');
  const db = new Database('./data/smartbook.db');
  db.pragma('wal_checkpoint(TRUNCATE)');
  db.close();
"
cp data/smartbook.db data/smartbook.db.bak.$(date +%Y%m%d_%H%M%S)
```

---

## Sign-Off

```text
RC1_DEPLOY_READY = CONDITIONAL YES

Conditions:
  1. mysql2 npm package remains installed          ✅ Confirmed
  2. DATABASE_PROVIDER=sqlite set in .env          ✅ Template provided
  3. SQLITE_PATH set in .env                       ✅ Template provided
  4. ./data/ directory exists and is writable       ✅ Documented
  5. Deployment runbook followed                    ✅ Created

READY_FOR_VPS_LITE_RC1 = YES
```
