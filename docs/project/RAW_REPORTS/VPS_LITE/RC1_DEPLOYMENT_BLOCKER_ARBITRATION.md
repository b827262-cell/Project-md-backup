# RC1 Deployment Blocker Arbitration

**Task:** RC1_DEPLOYMENT_BLOCKER_ARBITRATION  
**Role:** Independent Release Gate Arbitrator  
**Project:** `/home/b827262/project/smartbook-lite-rc1`  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-05  
**Mode:** Read-only arbitration. No patches, no file modifications, no deploy, no commit.

---

## ARBITRATION METHOD

Each confirmed finding was independently re-verified against source (not accepted on trust from the remediation report). Two prior ambiguities were resolved empirically by executing isolated probes in this session:

- **Blocker 1 failure mode** — tested `jose@6.1.0` (the installed version, `package.json:102`) signing with the exact empty key `getSessionSecret()` produces when `JWT_SECRET` is unset.
- **Blocker 2 ABI compatibility** — tested whether the installed `better-sqlite3@12.10.0` binary loads under Node v22.22.2 / ABI 127 (the VPS Node target).

Both probe results are reported inline below and change the precision of the severity findings.

---

## BLOCKER 1 — JWT_SECRET_MISMATCH

### Finding Validation: **VALID — CONFIRMED**

Independently re-verified:
- `server/_core/env.ts:20` → `cookieSecret: process.env.JWT_SECRET ?? ""` (sole source).
- Code-wide grep: `SESSION_SECRET` is **not referenced in any code file** — confirmed it is read nowhere in the runtime.
- `.env.production.sqlite.example:54` and `VPS_DEPLOYMENT_RUNBOOK.md:133,139` instruct setting `SESSION_SECRET` (the ignored name).

### Empirical Failure-Mode Resolution (new evidence)

The remediation report left the failure mode as "either login throws **or** tokens are forgeable." This was resolved by direct test:

```
jose 6.1.0, Node v22.22.2:
SIGN_RESULT = THROW: "Zero-length key is not supported"
=> FAILURE MODE: login throws; no user can authenticate
```

**Definitive failure mode: fail-closed.** With `JWT_SECRET` unset, `auth.loginLocal` → `signSession()` → `jose` `.sign(emptyKey)` throws before any token is issued. The system does **not** mint forgeable tokens (the prior "trivially forgeable" framing is **corrected** — it is not a silent security hole). Instead, authentication is **deterministically and completely broken**: no user, including the admin, can obtain a session on a fresh VPS that followed the runbook.

### Severity Arbitration: **CRITICAL — upheld**

The corrected failure mode does not reduce severity. A release bundle whose own runbook + env template guarantee that no one can log in is a hard release defect. It is also embedded *in the shipped artifacts* (runbook and env template are listed release deliverables), so the defect ships with the bundle.

### Decision

```
BLOCKER_1_DECISION = MUST_FIX_BEFORE_DEPLOY
REMEDIATION_EFFORT = LOW
```

- **Why MUST_FIX:** deterministic auth failure on any runbook-following deploy.
- **Effort LOW:** documentation-only — rename `SESSION_SECRET` → `JWT_SECRET` in 2 files (env template line 54, runbook lines 133/139), and make the env-template line active (uncommented). No code change required; the rest of the project already standardizes on `JWT_SECRET`.
- **Arbitrator caveat:** the doc fix is necessary but not *sufficient on its own*. The real gate is that the operator must **actually set a non-empty `JWT_SECRET`** in the VPS `.env`. The fixed docs make that the documented instruction; deployment sign-off must confirm the variable is present on the host.

---

## BLOCKER 2 — NODE22_BETTER_SQLITE3_VALIDATION

### Finding Validation: **VALID — but real risk is lower than stated**

Independently re-verified the validation gap is real: prior validation ran on Node v20 / ABI 115 / Arch (`BETTER_SQLITE3_INSTALL_PROBE.md:17`), and `VPS_BETTER_SQLITE3_PROBE.md:3-5` explicitly states it was **NOT YET RUN ON THE VPS** (Node v22 / ABI 127 / Ubuntu 24.04 / glibc 2.39).

### Empirical De-risking (new evidence)

The single highest-risk axis — the Node **ABI** — was tested directly in this session:

```
Node v22.22.2, ABI 127:
better-sqlite3 OK, sqlite_version = 3.53.1
```

`better-sqlite3@12.10.0` loads and executes under **the exact Node major/ABI of the VPS target**. This eliminates the `NODE_MODULE_VERSION` ABI-mismatch failure class — the most likely and most damaging failure mode. The remaining unverified axes are narrower: Ubuntu **glibc 2.39** compatibility and the **install path on the VPS** (prebuilt download vs. source compile) under the 955 MB RAM / 2 GB swap budget.

### Severity Arbitration: **HIGH → MEDIUM (downgraded)**

With ABI compatibility empirically proven, the residual risk is install-environment-specific (glibc/prebuilt/memory), not a fundamental incompatibility. Ubuntu 24.04 + glibc 2.39 + x86_64 is a standard, prebuilt-friendly target, and the local source-compile fallback already succeeded at ~600 MB peak (well within 955 MB + 2 GB swap). Residual risk: **MEDIUM, unvalidated on the exact host.**

### Decision

```
BLOCKER_2_DECISION = MUST_VALIDATE_BEFORE_DEPLOY  (gating; executed as deploy step 1)
REMEDIATION_EFFORT = LOW
```

- **Why not CAN_DEFER:** the native module is the storage engine. If it fails to load on the VPS, the app cannot boot — this is non-deferrable. However, validation is **intrinsic to the deploy procedure itself** (`pnpm install` → `require('better-sqlite3')` check is runbook step §2). It is a go/no-go checkpoint *during* deployment, not separate pre-work.
- **Effort LOW:** run the existing probe (`VPS_BETTER_SQLITE3_PROBE.md:25-56`) plus the runbook's load check on the VPS; `pnpm rebuild better-sqlite3` is the documented fallback if a prebuilt is unavailable.
- **Pass criteria:** as enumerated in the remediation report (install completes, `require()` loads with no ABI error, `sqlite_version ≥ 3.45`, fits memory budget, `db:sqlite:push:fresh` + boot succeed).

---

## BLOCKER 3 — DB_CONNECTIVITY_VALIDATION

### Finding Validation: **VALID — CONFIRMED**

Independently re-verified `server/_core/systemRouter.ts`: `health` is `publicProcedure ... .query(() => ({ ok: true }))` — no DB access, no `getDb()`, no provider check. A `200 { ok: true }` is fully compatible with an unprovisioned/corrupt DB or a silent wrong-mode (MySQL) boot.

Mitigating context (also confirmed): a prose `sqlite validation` item exists at `RC1_DEPLOYMENT_CHECKLIST.md:27`, and concrete table-count/PRAGMA snippets exist at `VPS_DEPLOYMENT_RUNBOOK.md:181-209`. The building blocks exist; they are simply not wired into a mandatory gate.

### Severity Arbitration: **MEDIUM — upheld**

Does not break a correctly-followed deployment. It removes the safety net: a misprovisioned deploy passes the health gate and fails later on first real DB call. Because the verification commands already exist, closing the gap is low effort.

### Decision

```
BLOCKER_3_DECISION = SPLIT
  - Mandatory DB validation gate in checklist .......... MUST_FIX_BEFORE_DEPLOY  (effort LOW, docs)
  - system.dbHealth / readiness code procedure ......... CAN_DEFER (post-RC1)   (effort MEDIUM, code)
```

- **MUST_FIX (LOW):** promote the existing runbook DB checks (table count = 66, `journal_mode = wal`, `foreign_keys = 1`, `DATABASE_PROVIDER = sqlite`) into an explicit, mandatory post-provision checklist gate. Documentation/process only.
- **CAN_DEFER:** the code-level `system.dbHealth` readiness endpoint is a genuine improvement but not required for a controlled, checklist-driven first deploy. Defer to post-RC1.

---

## RELEASE GATE SUMMARY

| Blocker | Validated Severity | Decision | Effort |
|---------|--------------------|----------|--------|
| 1 — JWT_SECRET_MISMATCH | CRITICAL (upheld; fail-closed, not forgeable) | MUST_FIX_BEFORE_DEPLOY | LOW |
| 2 — NODE22_BETTER_SQLITE3 | HIGH → **MEDIUM** (ABI proven compatible) | MUST_VALIDATE_BEFORE_DEPLOY | LOW |
| 3 — DB_CONNECTIVITY | MEDIUM (upheld) | MUST_FIX (gate) + CAN_DEFER (code probe) | LOW / MEDIUM |

**Note on RC1 code quality:** none of the three blockers is a defect in the RC1 *application code*. Blocker 1 and Blocker 3's mandatory part are documentation/process fixes; Blocker 2 is a validation gate. The RC1 runtime (4 core routers, SQLite adapter, dual-mode provider) is not implicated. The release defect is confined to the **bundled operator documentation** (runbook + env template), which is itself a shipped artifact.

---

## FINAL DECISION

```
RC1_RELEASE_APPROVED      = NO  (as-is)  →  YES after MINIMUM_ACTIONS 1–2
VPS_DEPLOYMENT_APPROVED   = NO  (as-is)  →  YES after ALL MINIMUM_ACTIONS verified on host
```

**Rationale for RC1_RELEASE_APPROVED = NO (as-is):** the release bundle includes the runbook and `.env.production.sqlite.example` as deliverables. Both carry the CRITICAL `SESSION_SECRET`/`JWT_SECRET` defect that deterministically breaks authentication. A bundle that ships with that defect cannot be approved as-is. The fix is LOW effort and docs-only — once applied, the release is approvable.

**Rationale for VPS_DEPLOYMENT_APPROVED = NO (as-is):** deployment additionally depends on the unexecuted on-host native-module validation (Blocker 2) and the missing DB-connectivity gate (Blocker 3). These must be satisfied on the actual VPS before cutover.

### MINIMUM_ACTIONS_REQUIRED

1. **(Blocker 1 — CRITICAL, docs)** Rename `SESSION_SECRET` → `JWT_SECRET` in `VPS_DEPLOYMENT_RUNBOOK.md` (lines 133, 139) and in `.env.production.sqlite.example` (line 54, made active/uncommented). *Flips RC1_RELEASE_APPROVED → YES.*
2. **(Blocker 1 — deploy-time verification)** Confirm a non-empty `JWT_SECRET` is actually present in the VPS `.env` before first boot (the doc fix alone does not set the value).
3. **(Blocker 2 — on-host validation)** Run the `better-sqlite3` probe + runbook load check on the actual Node 22 / Ubuntu 24.04 VPS; meet pass criteria. ABI compatibility is already proven; this confirms the glibc/install path on the real host.
4. **(Blocker 3 — docs/process)** Add the explicit DB-connectivity gate (table count, PRAGMAs, provider) as a mandatory step in `RC1_DEPLOYMENT_CHECKLIST.md`, run after `db:sqlite:push:fresh` and before sign-off.

*Actions 2–4 verified on host flip VPS_DEPLOYMENT_APPROVED → YES.*

### OPTIONAL_ACTIONS

- **(Blocker 1 hardening)** Add a fail-fast boot guard in `server/_core/env.ts` that throws when `NODE_ENV=production` and `JWT_SECRET` is empty — converts the silent-misconfig into an immediate, self-explanatory startup error. (Code; post-RC1.)
- **(Blocker 3 hardening)** Add a `system.dbHealth` / readiness TRPC procedure that runs a trivial query against `getDb()` and returns `{ ok, provider, tables }` — automates the manual DB gate. (Code; post-RC1.)
- **(Blocker 2 robustness)** Document `@libsql/client` as a contingency only if the VPS probe unexpectedly fails (not anticipated given ABI is proven). (Docs; post-RC1.)

---

## ARBITRATION VERDICT

All three findings are **VALID**. One correction to the prior analysis: Blocker 1's failure is **fail-closed (login throws)**, not forgeable tokens — severity remains CRITICAL. One downgrade: Blocker 2 is **MEDIUM**, not HIGH, because Node 22 / ABI 127 compatibility is now empirically proven; the residual risk is the on-host install path only.

The remediation path is **entirely LOW effort for the mandatory items** (two documentation fixes + one on-host validation that is already part of the deploy procedure). No RC1 application-code change is required to reach deployment approval. RC1 is a **strong conditional release**: approvable the moment the documentation defect is corrected, and deployable once the on-host validations pass.

---

*Read-only arbitration. No files modified, no patches, no deploy, no commit. Probe commands executed in isolated temp scripts that were removed after use; the SmartBook project sources were not altered.*
