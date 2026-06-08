# RC1 Release Bundle Review

**Role:** Independent Release Reviewer  
**Branch:** `release/vps-lite`  
**Review Date:** 2026-06-05  
**Input Documents:** `RC1_RELEASE_BUNDLE_REPORT.md`, `RC1_DEPLOYMENT_CHECKLIST.md`, `RC1_RELEASE_ARTIFACT_INVENTORY.md`  
**Reviewer:** Independent — read-only, no code modifications

---

## EXECUTIVE_SUMMARY

The RC1 bundle is structurally sound. The 4 core routers (SmartBook, Tutor, LessonPoints, SmartBookLearning) are confirmed SQLite-capable, the adapter quality is good, and the runbook covers the main deployment sequence. However, this review identifies **one CRITICAL blocker** that would prevent successful authentication on a fresh VPS: the runbook and env template both reference `SESSION_SECRET`, while the actual application code reads `JWT_SECRET`. A deployment following the runbook exactly will have an empty JWT signing key, making session tokens trivially forgeable.

Two additional HIGH-severity findings are documented: a Node.js version mismatch between the test environment (v20) and the deployment target (v22), and an undocumented impact of the health endpoint that does not verify DB connectivity.

The bundle is **NOT SAFE to deploy as-is** until the CRITICAL finding is resolved in the runbook and env template.

---

## RISK_REGISTER

### CRITICAL

#### C-1 — JWT Signing Secret: `SESSION_SECRET` vs `JWT_SECRET` Mismatch

| Field | Detail |
|-------|--------|
| **Location** | `server/_core/env.ts:22`, `.env.production.sqlite.example:54`, `VPS_DEPLOYMENT_RUNBOOK.md:§3` |
| **Finding** | `ENV.cookieSecret` reads `process.env.JWT_SECRET ?? ""`. The env template and runbook both reference `SESSION_SECRET`. `JWT_SECRET` is nowhere in either document. |
| **Impact** | A deployment following the runbook sets `SESSION_SECRET` (which is ignored by the application). `JWT_SECRET` is left unset. `ENV.cookieSecret` resolves to `""`. All session JWTs are signed with an empty key — making them trivially forgeable. Any user can craft a valid admin session token. |
| **Fresh VPS Risk** | YES — an operator following the runbook exactly will deploy with a broken auth signing key. |
| **Mitigation Required** | Add `JWT_SECRET=<64-char-hex>` to `.env.production.sqlite.example` and update the runbook §3 table. `SESSION_SECRET` can remain as a comment clarification, but `JWT_SECRET` must be the documented variable. |

---

### HIGH

#### H-1 — Node.js Version: Validated on v20, Deployed on v22

| Field | Detail |
|-------|--------|
| **Location** | `RC1_FINAL_VALIDATION_REPORT.md:header`, `VPS_DEPLOYMENT_RUNBOOK.md:§1` |
| **Finding** | All RC1 validation (pass/fail matrix, adapter checks, boot sequence) was performed on Node.js v20.20.2. The runbook requires Node.js v22+. `better-sqlite3` is a native module compiled per Node ABI version — the compiled binary for v20 is not compatible with v22. |
| **Impact** | `pnpm install` on a fresh v22 VPS will compile `better-sqlite3` for v22 ABI. This compilation requires `build-essential` and `python3` (listed in runbook). If those build tools are absent or the compilation fails silently, the app will fail at startup with `MODULE_NOT_FOUND` or segfault. This has not been end-to-end tested on v22. |
| **Fresh VPS Risk** | YES — untested Node/native module combination. |
| **Mitigation** | Run `pnpm rebuild better-sqlite3` on the v22 target and confirm `node -e "require('better-sqlite3'); console.log('OK')"` passes before proceeding. Document this as an explicit validation step in the runbook. |

#### H-2 — Health Endpoint Does Not Verify DB Connectivity

| Field | Detail |
|-------|--------|
| **Location** | `RC1_FINAL_VALIDATION_REPORT.md:§7`, `VPS_DEPLOYMENT_RUNBOOK.md:§5` |
| **Finding** | `system.health` returns `{ ok: true }` regardless of database state. It is a pure liveness probe — it does NOT query the SQLite database. |
| **Impact** | An operator following the deployment checklist will see a passing health check (`200 {"result":{"data":{"ok":true}}}`) even if: (a) `data/smartbook.db` was never provisioned, (b) the DB file is corrupt, (c) `DATABASE_PROVIDER=sqlite` is not set and the app is silently running in MySQL mode. The checklist post-deployment health check provides a false confidence signal. |
| **Fresh VPS Risk** | YES — this is exactly the scenario where the DB state is uncertain. |
| **Mitigation** | Add an explicit SQLite validation step after health check: `node -e "const d=require('better-sqlite3')('./data/smartbook.db'); console.log('tables:', d.prepare(\"SELECT count(*) c FROM sqlite_master WHERE type='table'\").get().c); d.close()"`. Document expected output (`tables: 66`) in the deployment checklist. |

#### H-3 — Auth Credentials Not Configured in Env Template

| Field | Detail |
|-------|--------|
| **Location** | `.env.production.sqlite.example:54-58` |
| **Finding** | `SESSION_SECRET`, `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`, and `OWNER_OPEN_ID` are all commented out in the template. |
| **Impact** | An operator who runs `cp .env.production.sqlite.example .env` and starts the app will have: no working admin account (no `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` means the seed function may not create any admin), and no owner assignment (empty `OWNER_OPEN_ID` means no user is auto-promoted to admin on login). Combined with C-1, the app cannot authenticate anyone on a default-template deploy. |
| **Fresh VPS Risk** | YES — all auth configuration is absent from a default copy. |
| **Mitigation** | Uncomment and fill the auth block in `.env.production.sqlite.example`. Add a validation step confirming admin login succeeds before marking deployment complete. |

---

### MEDIUM

#### M-1 — `learningMaterials.ts` Contains a Direct MySQL2 Connection in SQLite Mode Path

| Field | Detail |
|-------|--------|
| **Location** | `server/learningMaterials.ts:2691-2692` |
| **Finding** | A code path inside `learningMaterials.ts` performs `await import('mysql2/promise')` followed by `mysql2.createConnection(process.env.DATABASE_URL!)`. If this endpoint is hit in SQLite mode, `DATABASE_URL` is unset, the connection string is `undefined`, and the mysql2 connection attempt will throw a runtime error. |
| **Impact** | Affects the `learningMaterials` (auditoryHall) router, which is listed as P2 non-migrated. However, the failure mode is a direct MySQL TCP connection attempt, not just a schema miss. It will emit a connection error stack trace rather than a clean TRPC error. |
| **Note** | This is not a new finding relative to the P2 list — `learningMaterials` is explicitly out-of-scope for the Lite MVP. The concern is logging noise and the specific failure mode (connection timeout vs schema error). |
| **Mitigation** | Acceptable for Lite MVP scope. No action required before deployment. Consider adding a guard in a follow-on patch: `if (isSqliteMode()) throw new TRPCError({ code: 'NOT_IMPLEMENTED' })`. |

#### M-2 — SQLite Data Is Abandoned on MySQL Rollback

| Field | Detail |
|-------|--------|
| **Location** | `VPS_DEPLOYMENT_RUNBOOK.md:§7`, `RC1_RELEASE_BUNDLE_REPORT.md:§Rollback Strategy` |
| **Finding** | The rollback procedure (switch `DATABASE_PROVIDER=mysql`, restore `DATABASE_URL`, restart PM2) leaves the SQLite database file intact but abandoned. Any data written to SQLite during the deployment period is not migrated back to MySQL. |
| **Impact** | Any user registrations, tutor sessions, SmartBook CRUD, or lesson points data created while SQLite was active are lost on rollback. No data export/import path is documented. |
| **Mitigation** | Acceptable for a green-field deployment where there is no prior user data in SQLite. Document the data loss window explicitly in the rollback section. For any deployment with real user data, a SQLite→MySQL export path must be created before cutover. |

#### M-3 — No Reverse Proxy or HTTPS Configuration Documented

| Field | Detail |
|-------|--------|
| **Location** | `VPS_DEPLOYMENT_RUNBOOK.md` |
| **Finding** | The runbook deploys the app directly on port 5000 with no nginx, caddy, or HTTPS termination instructions. |
| **Impact** | In production: (a) cookies are sent over plaintext HTTP — JWT session tokens are interceptable; (b) browsers block `sameSite: none` cookies over HTTP, which may cause login failures on some clients; (c) note in `cookies.ts` — `sameSite` is set to `"none"` only when `secure` (HTTPS) is detected. Over plain HTTP it falls back to `"lax"`, which may affect cross-origin flows. |
| **Mitigation** | Add a reverse proxy configuration section (nginx or caddy with HTTPS) to the runbook before public launch. This is a deployment infrastructure gap, not a code bug. |

#### M-4 — `pnpm db:sqlite:push:fresh` Safety Behavior Not Documented

| Field | Detail |
|-------|--------|
| **Location** | `scripts/sqlite-provision.ts:25-27`, `VPS_DEPLOYMENT_RUNBOOK.md:§4` |
| **Finding** | The provisioning script correctly guards against re-provisioning an existing database (throws `Refusing to provision non-empty SQLite DB`). However, this safety behavior is not documented in the runbook. Operators who run this command on an existing deployment will see an error and may attempt workarounds. |
| **Impact** | Low operational risk — the guard works correctly. Risk is operator confusion about the error message on non-fresh deployments. |
| **Mitigation** | Add a note to the runbook §4: "If the DB file already exists and has tables, this command will exit with an error — this is intentional and safe. Do not delete the DB file to force a re-run unless you intend to erase all data." |

---

### LOW

#### L-1 — Deployment Approach Inconsistency: Bundle vs. Clone+Build

| Field | Detail |
|-------|--------|
| **Location** | `DEPLOYMENT_MANIFEST.md`, `RC1_RELEASE_ARTIFACT_INVENTORY.md`, `VPS_DEPLOYMENT_RUNBOOK.md:§2` |
| **Finding** | The `DEPLOYMENT_MANIFEST.md` references `smartbook-lite-runtime.tar.gz` (6.4MB bundle with SHA256). The artifact inventory says `dist/` is "generated by build." The runbook's §2 deployment procedure is: `git clone` → `pnpm install` → `pnpm build`. These are two different deployment approaches (pre-built bundle vs. clone+build on server). It is not clear which one is the primary path. |
| **Impact** | A clone+build approach bypasses the SHA256 verification in the manifest. If the branch head has diverged from the tag `vps-lite-prod-20260601` (build date: 2026-06-03), the deployed build will not match the validated artifact. |
| **Mitigation** | Clarify in the runbook which approach is primary. If the bundle is authoritative, document how to extract it. If clone+build is primary, remove the SHA256 bundle reference from the manifest or explicitly state it is for reference only. |

#### L-2 — Git Tag and Branch Head May Diverge

| Field | Detail |
|-------|--------|
| **Location** | `DEPLOYMENT_MANIFEST.md:header` |
| **Finding** | The manifest records `Git Tag: vps-lite-prod-20260601` (build time 2026-06-03T13:34:32+08:00). The branch `release/vps-lite` has received commits after that date (e.g., `fix(sqlite): normalize stats date binds`, `fix(sqlite): use sqlite pdf category seed path` per recent commit history). |
| **Impact** | If the runbook's clone procedure checks out the branch tip rather than the tag, the deployment may include unreviewd post-bundle commits. |
| **Mitigation** | Confirm the tag is present and pinned on the release branch. Update the runbook to clone by tag: `git clone -b vps-lite-prod-20260601 ...` or `git checkout vps-lite-prod-20260601` after cloning, if the tag represents the validated artifact. |

#### L-3 — `group_concat(distinct ...)` in `db.ts` Is a Dual-Mode Risk on Older SQLite

| Field | Detail |
|-------|--------|
| **Location** | `server/db.ts:1443` |
| **Finding** | `sql<string>\`group_concat(distinct ${conversations.subject})\`` is used inside `getQuestionStats()`. While `GROUP_CONCAT(DISTINCT ...)` is supported in SQLite 3.39.0+, earlier versions silently treat it as `GROUP_CONCAT()` without deduplication. Ubuntu 24.04 ships SQLite 3.45.x — this is safe on the documented target OS. |
| **Impact** | Negligible on Ubuntu 24.04. Risk exists only if deployed on a system with SQLite < 3.39.0. |
| **Mitigation** | None required for the documented target (Ubuntu 24.04 LTS). |

---

## MISSING_ITEMS

The following items are absent from the bundle documentation and represent gaps for a fresh VPS deployment:

| # | Item | Severity | Location Gap |
|---|------|----------|-------------|
| 1 | `JWT_SECRET` is not in the env template or runbook | CRITICAL | `.env.production.sqlite.example`, runbook §3 |
| 2 | `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`, `OWNER_OPEN_ID` are commented out | HIGH | `.env.production.sqlite.example` |
| 3 | Explicit `better-sqlite3` verification step for Node v22 | HIGH | runbook §2 |
| 4 | Post-boot DB connectivity validation (table count check) | HIGH | `RC1_DEPLOYMENT_CHECKLIST.md` post-deployment section |
| 5 | HTTPS / reverse proxy setup | MEDIUM | runbook (entirely absent) |
| 6 | `db:sqlite:push:fresh` non-empty DB error behavior | MEDIUM | runbook §4 |
| 7 | Clarification of bundle vs. clone+build deployment path | LOW | runbook §2 |
| 8 | Tag-pinned clone instruction | LOW | runbook §2 |

---

## ROLLBACK_REVIEW

**Rollback mechanism assessment: ADEQUATE for fresh VPS, INCOMPLETE for data-bearing deployments.**

The dual-mode provider switch (`DATABASE_PROVIDER=mysql → restart PM2`) is a valid and fast rollback path. The procedure is documented clearly.

**Gaps identified:**

1. **No SQLite data export path**: Any user data written during the SQLite deployment window cannot be recovered into MySQL. The rollback section should explicitly state: "Data written to SQLite during the deployment window will not be available after rollback to MySQL. Assess data loss window before executing."

2. **Rollback verification**: The runbook's rollback section correctly ends with a health check. However, given H-2 (health does not verify DB), a rollback verification should also confirm `DATABASE_PROVIDER` is set correctly: `node -e "console.log(process.env.DATABASE_PROVIDER)"` or by checking the application log confirms MySQL mode.

3. **PM2 environment source ambiguity**: `ecosystem.config.cjs` does not include `DATABASE_PROVIDER` or `SQLITE_PATH`. These come from `.env`. If the `.env` file is manually edited during rollback, PM2 must be restarted for changes to take effect — this is documented (`pm2 restart ai-tutor-helper`). No gaps here, but the operator must know that `.env` changes require a PM2 restart, not just a reload.

---

## DEPLOYMENT_REVIEW

**Does this bundle assume anything about the target VPS that may not be true?**

| Assumption | Status | Risk |
|-----------|--------|------|
| `JWT_SECRET` is configured | ❌ NOT in template | CRITICAL |
| `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` configured | ❌ Commented out | HIGH |
| `OWNER_OPEN_ID` configured | ❌ Commented out | HIGH |
| `DATABASE_PROVIDER=sqlite` set in `.env` | ✅ Set in template | OK |
| `SQLITE_PATH=./data/smartbook.db` set in `.env` | ✅ Set in template | OK |
| `data/` directory exists and is writable | Operator step | OK |
| `mysql2` package installed | ✅ pnpm install covers this | OK |
| `better-sqlite3` compiles on target OS | Partially verified (v20, not v22) | HIGH |
| PM2 installed | Operator step — documented | OK |
| 2 GB swap enabled | Operator step — documented | OK |
| SQLite schema provisioned before boot | Operator step — documented | OK |
| Build tools present (`build-essential`, `python3`) | Operator step — documented | OK |

**PM2 environment gap**: `ecosystem.config.cjs` does NOT pass `DATABASE_PROVIDER` or `SQLITE_PATH`. These must come from `.env`. If `.env` is absent, the app silently defaults to MySQL mode. This is documented in the validation report (P3) but is not surfaced in the deployment checklist as a pre-flight check.

**Runbook completeness**: The runbook is well-structured and covers the main deployment sequence. It includes a solid troubleshooting section. The primary gap is the CRITICAL `JWT_SECRET` naming error and the missing auth credential configuration.

---

## FINAL_RECOMMENDATION

This release bundle is **NEAR-READY** but requires resolution of the CRITICAL and HIGH findings before VPS deployment.

**Minimum required before deployment:**

1. **Fix `JWT_SECRET` in the env template and runbook** — this is the only CRITICAL blocker. Without it, authentication on a fresh deploy is broken and insecure.

2. **Uncomment and configure auth credentials** in `.env.production.sqlite.example` — `JWT_SECRET`, `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`, `OWNER_OPEN_ID` must all be present as active (non-commented) entries.

3. **Add DB connectivity validation step** after health check in the deployment checklist — the health check alone is insufficient to confirm the SQLite deployment is functional.

4. **Verify `better-sqlite3` on Node v22** on the actual target VPS and document it as an explicit validation gate in the runbook.

**Acceptable for deployment after the above are resolved:**

- mysql2 static import dependency (documented, managed)
- Non-core router P2 gaps (accepted for Lite MVP scope)
- No HTTPS (acceptable for initial deployment but should be addressed promptly)
- 1 GB memory constraint (PM2 limits are documented and appropriate)

---

## FINAL_VERDICT

```
REVIEW_PASS = NO

VPS_DEPLOY_READY = NO

ADDITIONAL_ACTIONS_REQUIRED = [
  "CRITICAL: Add JWT_SECRET to .env.production.sqlite.example and runbook §3",
  "HIGH: Uncomment DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, OWNER_OPEN_ID in env template",
  "HIGH: Add explicit better-sqlite3 v22 validation to runbook §2",
  "HIGH: Add DB table-count check to deployment checklist post-boot step",
  "MEDIUM: Add data loss warning to rollback section",
  "MEDIUM: Document db:sqlite:push:fresh non-empty DB guard behavior",
  "LOW: Clarify bundle vs. clone+build deployment path"
]
```

> The bundle becomes `VPS_DEPLOY_READY = YES` after CRITICAL item 1 and HIGH items 2–4 are addressed. The remaining MEDIUM and LOW findings are documentation improvements that do not block initial deployment on a controlled environment.
