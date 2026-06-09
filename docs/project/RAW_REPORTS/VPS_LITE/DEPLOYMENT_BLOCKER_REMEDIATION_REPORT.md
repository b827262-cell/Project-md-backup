# Deployment Blocker Remediation Report

**Task:** DEPLOYMENT_BLOCKER_REMEDIATION_AUDIT  
**Project:** `/home/b827262/project/smartbook-lite-rc1`  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-05  
**Mode:** Read-only verification & remediation planning. No files modified, no patches, no deploy.

---

## BLOCKER 1 — JWT_SECRET_MISMATCH

### ROOT_CAUSE

The application signs and verifies all session JWTs with `ENV.cookieSecret`, which is sourced **only** from `JWT_SECRET`:

- `server/_core/env.ts:20` — `cookieSecret: process.env.JWT_SECRET ?? ""`
- `server/_core/sdk.ts:160-162` — `getSessionSecret()` returns `TextEncoder().encode(ENV.cookieSecret)`
- `server/_core/sdk.ts:191,199-200` — `signSession()` signs with that key via `SignJWT(...).setProtectedHeader({ alg: "HS256" }).sign(secretKey)`
- `server/_core/sdk.ts:212-213` — `verifySession()` verifies with the same key

The two operator-facing documents instruct setting the **wrong** variable name:

- `.env.production.sqlite.example:54` — `# SESSION_SECRET=<generate-a-random-64-char-hex-string>` (also commented out)
- `VPS_DEPLOYMENT_RUNBOOK.md:133` — `SESSION_SECRET=<generate-a-random-64-char-hex-string>`
- `VPS_DEPLOYMENT_RUNBOOK.md:139` — heading "Generate SESSION_SECRET"

`SESSION_SECRET` is **never read** anywhere in the codebase. A deploy that follows the runbook sets `SESSION_SECRET` (ignored) and leaves `JWT_SECRET` unset → `ENV.cookieSecret` resolves to `""`.

**No boot-time guard exists.** `grep` confirms the only consumers of `cookieSecret` are `env.ts:20` and `sdk.ts:161`; neither validates that the secret is non-empty.

**Corroborating evidence the correct name is `JWT_SECRET`:** the project's own hotfix run logs and ~10 governance/verification docs already use `JWT_SECRET`:
- `SQLITE_RC1_HOTFIX1_REPORT.md:58` and `SQLITE_RC1_HOTFIX2_STATS_REPORT.md:71` — both launch the app with `JWT_SECRET=...`
- `docs/stability/environment-freeze.md`, `docs/verification/release-readiness-checklist.md`, `docs/verification/env-audit-checklist.md`, `docs/deployment/deployment-baseline.md`, `docs/operations/startup-sequence.md`, etc. all list `JWT_SECRET` as the required variable.

This makes the runbook/env-template the **outlier** — the rest of the project already standardizes on `JWT_SECRET`. The fix is a documentation correction, not a code change.

### Failure Mode (precise)

With `JWT_SECRET` unset, `getSessionSecret()` encodes `""` into a zero-length `Uint8Array`. On `auth.loginLocal`, `signSession()` calls `jose` `SignJWT.sign()` with that empty key. Outcome is one of two, both deployment-blocking:
1. `jose` rejects the zero-length HMAC key → login throws → **no user can log in**; or
2. tokens are minted under an empty/trivially-known key → **session tokens are forgeable** (any actor can mint an admin `openId` token).

Either way, the deployment is non-functional and/or insecure.

### MINIMUM_FIX

Documentation-only (no code change required):

1. `.env.production.sqlite.example` — replace the commented `# SESSION_SECRET=...` with an **active** line:
   `JWT_SECRET=<64-char-hex>`
2. `VPS_DEPLOYMENT_RUNBOOK.md:133` — change `SESSION_SECRET=...` to `JWT_SECRET=...`
3. `VPS_DEPLOYMENT_RUNBOOK.md:139` — change heading "Generate SESSION_SECRET" to "Generate JWT_SECRET" (the `crypto.randomBytes(32).toString('hex')` generator command at line 142 is already correct).

Optional hardening (code, out of minimum scope): add a fail-fast guard in `env.ts`/boot that throws when `NODE_ENV=production` and `JWT_SECRET` is empty. Recommended as a follow-on, not required for this remediation.

### FILES_AFFECTED

| File | Change | Type |
|------|--------|------|
| `.env.production.sqlite.example` | `SESSION_SECRET` → active `JWT_SECRET` | docs/config template |
| `VPS_DEPLOYMENT_RUNBOOK.md` | lines 133, 139 rename | docs |
| `server/_core/env.ts` | (optional) empty-secret guard | code — out of minimum scope |

### RISK_LEVEL

**CRITICAL** — confirmed. Breaks authentication and/or session integrity on any fresh VPS that follows the runbook. Fix is low-effort and isolated to documentation.

---

## BLOCKER 2 — NODE22_BETTER_SQLITE3_VALIDATION

### VALIDATION_GAP

`better-sqlite3` is a native addon; its loadable binary is keyed on `{Node ABI, OS, libc}`. The validation matrix differs from the deployment target on **all three** axes:

| Axis | Validated (local) | Deployment Target (VPS) |
|------|-------------------|--------------------------|
| Node | v20.20.2 (ABI 115) | v22.22.2 (ABI 127) |
| OS | EndeavourOS (Arch rolling) | Ubuntu 24.04 LTS |
| libc | Arch glibc | glibc 2.39 |
| RAM/Swap | 14 GB / 0 swap | 955 MB / 2 GB swap |

Evidence:
- `BETTER_SQLITE3_INSTALL_PROBE.md:17,30` — local run on Node v20.20.2 / ABI 115; explicitly states (line 21) the result is a "strong positive analog… not guaranteed identical to the VPS."
- `VPS_BETTER_SQLITE3_PROBE.md:3-5` — header: **"NOT YET RUN ON THE VPS."** It is a ready-to-run procedure + results template, because the authoring session was the laptop with no VPS access.
- `package.json:82` — `"better-sqlite3": "^12.10.0"`; line 180 lists it under build-allowed native deps.

**Net:** the package is proven to build-from-source and run on Node 20 locally (compile ~50s, ~600 MB peak, bundled SQLite 3.53.1). It has **not** been executed on Node 22 / Ubuntu 24.04. The pre-assessed risk is **LOW** (Ubuntu 24.04 + Node 22 + glibc 2.39 is a standard, prebuilt-friendly target, and the VPS has 2 GB swap to cover a worst-case source compile), but the authoritative gate remains **unexecuted**.

### REQUIRED_TESTS

Run the procedure already documented in `VPS_BETTER_SQLITE3_PROBE.md:25-56` **on the VPS** (not the laptop):

1. Isolated probe install: `npm install better-sqlite3` in a throwaway dir, captured with `/usr/bin/time -v ... | tee install.log`.
2. Capture `free -h` / `swapon --show` before and after.
3. Detect prebuilt-vs-compile: `grep -Ei "prebuild-install|node-gyp|SOLINK|gyp info ok|Downloading" install.log` and check for `node_modules/better-sqlite3/build/Release/better_sqlite3.node`.
4. Runtime smoke: open `:memory:` DB and run `select sqlite_version()`.
5. **In the real project context** (beyond the isolated probe): on the VPS after `pnpm install --frozen-lockfile`, run the runbook's own check `node -e "require('better-sqlite3'); console.log('better-sqlite3 OK')"` (`VPS_DEPLOYMENT_RUNBOOK.md:80-82`), and if it fails, `pnpm rebuild better-sqlite3`.

### PASS_CRITERIA

- `pnpm install --frozen-lockfile` completes on the VPS without an unresolved native-build error.
- `require('better-sqlite3')` loads without `MODULE_NOT_FOUND` / `NODE_MODULE_VERSION` ABI-mismatch error under Node v22.
- `select sqlite_version()` returns a version ≥ 3.45 (expected 3.53.x bundled).
- Peak install RSS stays within `955 MB RAM + 2 GB swap` (compile path peaked ~600 MB locally — wide margin).
- `pnpm db:sqlite:push:fresh` then app boot succeed on the VPS (ties into Blocker 3 validation).

---

## BLOCKER 3 — DB_CONNECTIVITY_VALIDATION

### CURRENT_LIMITATION

`server/_core/systemRouter.ts` — the `health` procedure is a pure liveness probe with **no database access**:

```ts
health: publicProcedure
  .input(z.object({ timestamp: z.number().min(0, ...) }))
  .query(() => ({ ok: true })),
```

It returns `{ ok: true }` unconditionally. It does **not** open the SQLite DB, run a query, or check `DATABASE_PROVIDER`.

Consequently a passing health check (`200 {"result":{"data":{"ok":true}}}`) is fully compatible with a broken data layer:
- `data/smartbook.db` never provisioned (schema push skipped),
- DB file present but corrupt,
- `DATABASE_PROVIDER` unset → app silently running in MySQL mode against an absent `DATABASE_URL`.

The deployment docs lean on this endpoint as the primary signal:
- `RC1_DEPLOYMENT_CHECKLIST.md:19` (smoke test), `:23` (post-deploy health check), `:33` (rollback verify), `:49` (final gate "PM2 runtime is healthy").

A `sqlite validation` line **does** exist at `RC1_DEPLOYMENT_CHECKLIST.md:27` ("confirm DB file exists, WAL mode is active, and the schema is present"), but it is **prose, not an executable step**, and it is listed as a separate post-deploy item rather than being part of the health gate. The runbook provides concrete table-count and PRAGMA verification snippets (`VPS_DEPLOYMENT_RUNBOOK.md:181-209`), so the building blocks exist — they are simply not wired into a single authoritative health/connectivity gate.

### RECOMMENDED_VALIDATION_STEP

Documentation/process fix (no code change required to ship; optional code enhancement noted):

1. Promote the runbook's existing DB checks into an explicit, mandatory deployment-checklist gate, run **after** `pnpm db:sqlite:push:fresh` and app start:
   - Table count = 66:
     `node -e "const d=require('better-sqlite3')('./data/smartbook.db');console.log('tables:',d.prepare(\"SELECT count(*) c FROM sqlite_master WHERE type='table'\").get().c);d.close()"`
     (expect `tables: 66`)
   - PRAGMA check: `journal_mode = wal`, `foreign_keys = 1` (snippet at `VPS_DEPLOYMENT_RUNBOOK.md:195-209`).
   - Provider confirmation: `node -e "console.log('provider:', process.env.DATABASE_PROVIDER)"` (expect `sqlite`).
2. Treat the `system.health` `{ ok: true }` result as **liveness only**; document that it does not imply DB readiness.
3. Optional code enhancement (follow-on, not blocking): add a `system.dbHealth` (or `readiness`) procedure that executes a trivial query (e.g. `SELECT 1` / `select count(*) from pdf_categories`) against `getDb()` and returns `{ ok, provider, tables }`. This converts the manual step into an automatable readiness probe.

### DEPLOYMENT_RISK

**MEDIUM.** It does not by itself break a correctly-followed deployment, but it removes the safety net: a misprovisioned or wrong-mode deployment passes the health gate and appears healthy, surfacing only later as runtime errors on first real DB call. Because the verification commands already exist in the runbook, closing this is a low-effort documentation/process change; the code-level readiness probe is a recommended but optional hardening.

---

## FINAL SUMMARY

```
BLOCKER_1_READY_TO_FIX        = YES   (docs-only: rename SESSION_SECRET → JWT_SECRET in 2 files; root cause confirmed, fix isolated)
BLOCKER_2_READY_TO_VALIDATE   = YES   (VPS probe procedure already written in VPS_BETTER_SQLITE3_PROBE.md; needs execution ON the VPS)
BLOCKER_3_READY_TO_FIX        = YES   (docs/process: promote existing runbook DB checks into a mandatory checklist gate; optional readiness procedure)

RC1_DEPLOYMENT_READY_AFTER_REMEDIATION = CONDITIONAL YES
```

**Conditions for the final YES:**
1. Blocker 1 — apply the `JWT_SECRET` documentation correction (CRITICAL; required).
2. Blocker 2 — execute the VPS probe on the actual Node 22 / Ubuntu 24.04 target and meet PASS_CRITERIA (required; risk pre-assessed LOW but unverified).
3. Blocker 3 — add the explicit DB-connectivity gate to the deployment checklist (required for operational safety; building blocks already exist).

All three are confirmed, evidence-based, and ready to action. Blocker 1 is the only CRITICAL; Blockers 2 and 3 are validation/process gaps with low remediation effort. No code changes are strictly required for any of the three minimum fixes, though optional code hardening is noted for Blockers 1 and 3.

---

*Read-only audit. No files were modified, no patches applied, no deployment or commit performed. All findings cite specific file:line evidence verified during this session.*
