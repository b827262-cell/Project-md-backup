# Node 22 / better-sqlite3 Validation Report

**Task:** BLOCKER_2_TARGET_VPS_VALIDATION  
**Project:** `/home/b827262/project/smartbook-lite-rc1`  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-05  
**Mode:** Read-only evidence capture. No code, schema, deploy, or commit.

---

## STEP 1 — Execution Environment Identification

Evidence captured this session (`hostname`, `/etc/os-release`, `uname -a`, `free -h`, `swapon --show`):

| Attribute | This Host (measured) | Target VPS (per `VPS_BETTER_SQLITE3_PROBE.md:11-17`) | Match? |
|-----------|----------------------|------------------------------------------------------|--------|
| Hostname | `b827262-E500-G9-WS760T` (workstation model) | VPS Lite | ❌ |
| OS | Zorin OS 18 (desktop distro, Ubuntu 24.04 base) | Ubuntu 24.04 LTS (server) | ❌ |
| Kernel | `6.17.0-22-generic` | (VPS kernel) | ❌ |
| RAM | **30 GiB** | **955 MB** | ❌ |
| Swap | **0 B** | **2 GB** | ❌ |
| Node | v22.22.2 | v22.22.2 | ✅ (coincidental) |
| Arch | x86_64 | x86_64 | ✅ |
| User / Home | `b827262` / `/home/b827262` | (VPS deploy user) | ❌ |

```
CURRENT_HOST    = b827262-E500-G9-WS760T (Zorin OS 18 desktop workstation, 30 GiB RAM, 0 swap)
IS_TARGET_VPS   = NO
```

**Determination:** This is a **local desktop workstation**, not the deployment VPS. Five independent axes (hostname, OS distro, RAM, swap, kernel) disprove target-VPS identity. The matching Node version (v22.22.2) is coincidental and, on its own, does **not** establish target identity — the native-module install path also depends on OS/libc and the install-time memory budget, both of which differ here.

---

## STEP 2 — Non-Target Environment Result

Because `IS_TARGET_VPS = NO`, this validation **does not close Blocker 2**. Local results are recorded for reference only:

```
LOCAL_NODE_VERSION          = v22.22.2
LOCAL_BETTER_SQLITE3_VERSION= 12.10.0
LOCAL_BETTER_SQLITE3_RESULT = PASS
  - node -e "require('better-sqlite3'); console.log('PASS')"  →  PASS
  - bundled sqlite_version (prior session)                    →  3.53.1
  - node abi                                                  →  127 (matches VPS ABI)

TARGET_VPS_VALIDATED        = NO
BLOCKER_2                   = PENDING
```

**Reference value of the local PASS:** it confirms the installed `better-sqlite3@12.10.0` binary is ABI-127 compatible (the VPS Node ABI), eliminating the `NODE_MODULE_VERSION` mismatch failure class. It does **not** confirm the on-VPS install path (prebuilt download vs. source compile) under Ubuntu 24.04 glibc 2.39 within the 955 MB RAM / 2 GB swap budget — that is the residual unknown that only the VPS run can resolve.

**Observation (non-blocking):** `npm ls better-sqlite3` shows a peer-dependency notice — `drizzle-kit@0.31.5` declares `better-sqlite3 "^11.9.1"` while `12.10.0` is installed (marked `invalid`). This is a dev-tooling peer-range warning only; the runtime `require()` succeeds. Not a deployment blocker; noted for awareness.

---

## STEP 3 — Target VPS Validation

**NOT EXECUTED.** Step 3 runs only when `IS_TARGET_VPS = YES`. This session is not on the target VPS, so the authoritative probe was intentionally not run here (running it locally would misrepresent local data as VPS data — explicitly prohibited by the task rules).

### To close Blocker 2, run ON THE TARGET VPS:

```bash
node -v
npm ls better-sqlite3        # (or: pnpm why better-sqlite3)
node -e "require('better-sqlite3'); console.log('PASS')"
```

Plus the fuller probe in `VPS_BETTER_SQLITE3_PROBE.md:25-56` (install timing, memory before/after, prebuilt-vs-compile detection, `select sqlite_version()`).

### PASS criteria (must all hold on the VPS):
- `pnpm install --frozen-lockfile` completes with no unresolved native-build error.
- `require('better-sqlite3')` loads — no `MODULE_NOT_FOUND` / `NODE_MODULE_VERSION` error.
- `select sqlite_version()` returns ≥ 3.45 (expected 3.53.x).
- Peak install RSS fits within 955 MB RAM + 2 GB swap.
- `pnpm db:sqlite:push:fresh` then app boot succeed.

---

## OUTPUT SUMMARY

```
LOCAL_OR_VPS              = LOCAL  (b827262-E500-G9-WS760T / Zorin OS 18 workstation)
NODE_VERSION             = v22.22.2
BETTER_SQLITE3_VERSION   = 12.10.0
RESULT                   = PASS (local reference only — NOT a VPS validation)
```

---

## FINAL STATUS

```
TARGET_VPS_VALIDATED = NO
BLOCKER_2            = PENDING
```

> Blocker 2 remains **PENDING**. It can be closed only by executing the probe on the actual target VPS and meeting the PASS criteria above. The local PASS is a positive analog (ABI-127 compatibility proven) but, per the no-inference rule, does **not** substitute for target-host validation. Per the STOP condition, execution halts here without continuing to the final remediation report.
