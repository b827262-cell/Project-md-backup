# SQLite VPS Environment Verification

> **Phase 1-E.1 — Verification Only / No Runtime Changes**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **No package install, no code change, no SQLite DB, no migration, no build.**

---

## ⚠️ Important: Environment Mismatch

**This verification session ran on the LOCAL development laptop, NOT on the 1GB Ubuntu VPS.**

| Fact | Value |
|------|-------|
| Hostname of this session | `b822726-NB-TUFA16` (laptop) |
| OS of this session | **EndeavourOS** (Arch-based, rolling), kernel 7.0.9-arch1 |
| RAM of this session | **15.6 GB** (not 1 GB) |
| Chassis | laptop 💻 |

The commands in Steps 1–6 below therefore describe the **local dev machine**. They are recorded here as a **known-good build baseline** for reference. The actual 1GB Ubuntu VPS **cannot be inventoried from this machine** — its values must be collected by running the same commands over SSH on the VPS itself (see "VPS Verification Procedure" below). All VPS-specific values are marked **`TBD (run on VPS)`**.

I have not fabricated any VPS values.

---

## OS

| Field | Local Laptop (this session) | VPS Lite (target) |
|-------|----------------------------|-------------------|
| Distro | EndeavourOS (Arch-based, `ID_LIKE=arch`) | **TBD** — expect Ubuntu 20.04 / 22.04 LTS |
| Kernel | `7.0.9-arch1-1 x86_64` | **TBD** |
| Hostname | `b822726-NB-TUFA16` | **TBD** |

**VPS command:** `cat /etc/os-release && uname -a && hostnamectl`

---

## Node Environment

| Field | Local Laptop | VPS Lite |
|-------|-------------|----------|
| node | `v20.20.2` | **TBD** — must be ≥ 18, ideally 20.x to match dev (ABI for prebuilds) |
| npm | `10.8.2` | **TBD** |
| pnpm | `10.4.1` | **TBD** |
| node path | `~/.config/nvm/versions/node/v20.20.2/bin/node` (nvm) | **TBD** — check if nvm or system node |

**VPS command:** `node -v && npm -v && pnpm -v && which node && which pnpm`

**Note:** The local Node is managed by **nvm**. If the VPS uses nvm too, confirm the active version at boot (PM2/systemd may use a different PATH than the login shell).

---

## Native Toolchain

| Tool | Local Laptop | VPS Lite | Needed for source compile? |
|------|-------------|----------|----------------------------|
| gcc | `16.1.1` | **TBD** | ✅ |
| g++ | `16.1.1` | **TBD** | ✅ (C++ addon) |
| make | `4.4.1` | **TBD** | ✅ |
| python3 | `3.14.5` | **TBD** | ✅ (node-gyp) |
| node-gyp | `v12.3.0` | **TBD** | ✅ |
| sqlite3-dev | n/a | **not required** | ❌ better-sqlite3 bundles its own SQLite |

**VPS command:** `gcc --version; g++ --version; make --version; python3 --version; npx node-gyp --version; dpkg -l | grep build-essential`

**Note:** Minimal Ubuntu VPS images often **lack `build-essential`** (gcc/g++/make). If the prebuilt binary path is used, this is irrelevant. If source compile is needed, run `sudo apt-get install -y build-essential python3` first.

---

## SQLite Environment

| Field | Local Laptop | VPS Lite |
|-------|-------------|----------|
| `sqlite3` CLI | `3.53.1` | **TBD** — expect 3.31 (Ubuntu 20.04) / 3.37 (22.04) |
| CLI path | `/usr/bin/sqlite3` | **TBD** |

**VPS command:** `sqlite3 --version; which sqlite3`

**Critical clarification:** The system `sqlite3` CLI version does **NOT** affect the running app. `better-sqlite3` **bundles its own SQLite** (≥ 3.45 in v11+). The CLI matters only for manual `.db` inspection. The schema already uses `strftime('%s','now')` (all versions) rather than `unixepoch()` (needs ≥ 3.38), so even an old CLI can read the data correctly.

---

## Memory Assessment

| Field | Local Laptop | VPS Lite |
|-------|-------------|----------|
| MemTotal | 15.6 GB | **TBD** — expect ~1 GB |
| MemAvailable | 6.2 GB | **TBD** |
| SwapTotal | **0 B** | **TBD** — often 0 on minimal VPS |

**VPS command:** `free -h; swapon --show; grep -E "MemTotal|MemAvailable|SwapTotal|SwapFree" /proc/meminfo`

**Assessment:** The local laptop has ample RAM and 0 swap — irrelevant locally because RAM is huge. On a **1 GB VPS with 0 swap**, a from-source `node-gyp` compile of better-sqlite3 can approach memory limits and risk OOM-kill. This is the single most important VPS value to confirm.

---

## Disk Assessment

| Mount | Local Laptop | VPS Lite |
|-------|-------------|----------|
| `/` | 467 G total, 359 G free (19% used) | **TBD** |
| `/tmp` | 7.5 G tmpfs | **TBD** — note: tmpfs `/tmp` consumes RAM |
| `/home` | same as `/` | **TBD** |

**VPS command:** `df -h /; df -h /tmp; df -h /home`

**Assessment:** SQLite DB file + WAL is tiny (MBs to low GBs). Disk is not a constraint. **Watch:** if the VPS `/tmp` is tmpfs, `node-gyp` build artifacts there consume RAM — set `TMPDIR=/var/tmp` during install on a low-RAM VPS.

---

## better-sqlite3 Installation Risk

Per the task's risk model:

| Scenario | Condition | Risk |
|----------|-----------|------|
| **A — Prebuilt binary available** | VPS Node ABI (e.g. Node 20 / linux-x64 / glibc) matches a published `better-sqlite3` prebuild → downloaded, no compile | **Low** |
| **B — Native compile required** | No matching prebuilt; `build-essential` present; **swap present** | **Medium** |
| **C — Native compile, no swap** | No prebuilt; compiling on 1 GB RAM with **0 swap** | **High** (OOM-kill risk) |

**Current determination: CANNOT be finalized — depends on unverified VPS values.**

Conditional verdict once VPS is inventoried:
- If VPS = Node 20.x, linux-x64, glibc (standard Ubuntu) → **Scenario A, Low risk** (prebuilt almost certainly available).
- If VPS Node is an odd/old version or musl libc, or build-essential missing + no swap → escalates toward **B/C**.

---

## Recommended Swap Size

For a 1 GB VPS that may need a source compile:

| VPS RAM | Recommended swap | Purpose |
|---------|------------------|---------|
| 1 GB | **+1 GB to +2 GB swap** | Headroom for `node-gyp` compile and Node runtime peaks |

**Setup (only if needed, run on VPS):**
```
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# persist: echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Swap can be removed after install if RAM proves sufficient at runtime (SQLite runtime footprint is small).

---

## Recommended Installation Strategy

### Strategy A — Prebuilt Binary (preferred)
```
# On VPS, after confirming Node 20.x / linux-x64:
pnpm add better-sqlite3            # downloads prebuilt via prebuild-install
pnpm add -D @types/better-sqlite3
```
- No toolchain needed. Fastest, lowest risk. Try this **first**.

### Strategy B — Native Compile (fallback)
```
# Only if Strategy A reports "no prebuilt found":
sudo apt-get install -y build-essential python3
# add swap first (see above) if RAM ≤ 1 GB and swap = 0
pnpm add better-sqlite3 --config.build-from-source=true
```
- Requires toolchain + swap headroom.

### Strategy C — Fallback to `@libsql/client`
```
# If better-sqlite3 cannot build/run on the VPS at all:
pnpm add @libsql/client
# schema stays identical; switch driver import to drizzle-orm/libsql
```
- Ships reliable prebuilds, embedded file mode supported. Small async-refactor cost vs better-sqlite3's sync API. Documented in `SQLITE_RUNTIME_ACTIVATION_PLAN.md` as the contingency driver.

---

## VPS Verification Procedure (run these ON the VPS to complete this report)

```bash
# 1. OS
cat /etc/os-release && uname -a && hostnamectl
# 2. Node
node -v && npm -v && pnpm -v && which node && which pnpm
# 3. Toolchain
gcc --version; g++ --version; make --version; python3 --version
npx node-gyp --version; dpkg -l | grep build-essential
# 4. SQLite
sqlite3 --version; which sqlite3
# 5. Memory
free -h; swapon --show; grep -E "MemTotal|MemAvailable|SwapTotal|SwapFree" /proc/meminfo
# 6. Disk
df -h /; df -h /tmp; df -h /home
# 7. Prebuilt probe (dry-run, no install) — checks if a prebuilt exists:
npm view better-sqlite3 version   # latest version; cross-check its prebuild matrix
```

---

## Final Confirmation

- No package installed.
- No code modified.
- No SQLite DB created.
- No migration / build executed.
- VPS values are **unverified** (this session is the local laptop) and marked TBD — to be filled by running the procedure above on the VPS.

---

*Verification Only. Phase 1-E.2 (Dual Mode wiring) should NOT begin until the VPS columns above are filled and the better-sqlite3 risk is confirmed Low (Strategy A) or mitigated (swap added).*
