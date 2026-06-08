# better-sqlite3 Install Probe

> **Phase 1-E.2 — Installation Probe Only**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Probe ran in isolated dir `~/sqlite-probe` — **SmartBook project untouched**.

---

## ⚠️ Important: Where This Probe Actually Ran

**This probe executed on the LOCAL development laptop, NOT on the VPS.**

| | This probe (LOCAL) | Target VPS (from task) |
|---|--------------------|------------------------|
| Host | `b822726-NB-TUFA16` (laptop) | VPS Lite |
| OS | EndeavourOS (Arch rolling) | Ubuntu 24.04.4 |
| Node | **v20.20.2** (ABI 115) | **v22.22.2** (ABI 127) |
| RAM | 14 GB | 955 MB |
| Swap | 0 | 2 GB |

Because the Node ABI and OS differ, the prebuilt-binary outcome here is **not** guaranteed identical to the VPS. The result below is a **strong positive analog** (it proves the package builds and runs end-to-end), but the authoritative VPS probe must be run on the VPS itself (procedure included at the end). No VPS values were fabricated.

---

## Environment

| Field | LOCAL probe value | VPS (to confirm) |
|-------|-------------------|------------------|
| OS | EndeavourOS (Arch rolling) | Ubuntu 24.04.4 |
| Node | v20.20.2 | v22.22.2 |
| npm | 10.8.2 | 10.9.7 |
| RAM | 14 GB (6.4 GB avail) | 955 MB |
| Swap | 0 | 2 GB |
| arch / libc | x86_64 / glibc (rolling) | x86_64 / glibc 2.39 |
| Toolchain | gcc/g++ 16.1.1, make 4.4.1, python 3.14.5, node-gyp 12.3.0 | TBD |

---

## Installation Result

**✅ SUCCESS** (LOCAL)

- Package: `better-sqlite3@12.10.0`
- 38 packages added, 0 vulnerabilities
- Elapsed: **50 seconds**

---

## Prebuilt Binary

**❌ No — prebuilt was NOT used on this machine.**

Evidence:
- Build log shows `node-gyp` running `g++`, `make`, `SOLINK_MODULE`, `gyp info ok`.
- `node_modules/better-sqlite3/build/Release/better_sqlite3.node` exists (freshly compiled).
- No `prebuilds/` directory present.

**Why:** On EndeavourOS (Arch rolling, very new glibc) with Node 20, `prebuild-install` found no matching prebuilt asset and fell back to a source compile. **The VPS (Ubuntu 24.04 LTS, glibc 2.39, Node 22) is a far more standard target and is more likely — though not guaranteed — to receive a prebuilt**, which would skip compilation entirely.

---

## Compile Required

**Yes (on LOCAL).** Full `node-gyp` source compile completed successfully using the local toolchain. This demonstrates that **even the worst case (no prebuilt → source compile) succeeds** when a C++ toolchain is present.

---

## Memory Usage

| Metric | Value (LOCAL, sampled every 0.5 s) |
|--------|-----------------------------------|
| MemAvailable before/peak | ~6532 MB |
| MemAvailable low (during compile) | ~5923 MB |
| Observed delta during build | **~608 MB** |

**Caveat:** This delta is `MemAvailable` movement on a busy 14 GB laptop (other processes contribute), so it over-estimates better-sqlite3's own footprint — the compiler's actual RSS is typically a few hundred MB. Treat ~600 MB as a conservative upper bound for the build's transient memory.

**VPS implication:** 955 MB RAM **+ 2 GB swap = ~3 GB addressable**. Even a conservative ~600 MB compile peak fits comfortably. The 2 GB swap fully neutralizes the "High risk / OOM" scenario from Phase 1-E.1.

---

## Runtime Test

`test.js`:
```js
const Database = require('better-sqlite3');
const db = new Database(':memory:');
console.log(db.prepare('select sqlite_version() as v').get());
```

Output (LOCAL):
```
{ v: '3.53.1' }
```

✅ Native addon loads, opens an in-memory DB, and executes a query. **Bundled SQLite version: 3.53.1** (better-sqlite3 ships its own SQLite — independent of any system `sqlite3`).

---

## Risk Re-assessment for VPS (Ubuntu 24.04 / Node 22 / 955 MB + 2 GB swap)

| Scenario | Applies to VPS? | Risk |
|----------|-----------------|------|
| A — Prebuilt available | Likely (standard Ubuntu/Node 22/glibc 2.39) | **Low** |
| B — Source compile, swap present | Possible fallback; 2 GB swap available | **Low–Medium** |
| C — Source compile, no swap | **Does NOT apply** — VPS has 2 GB swap | n/a |

**Net VPS risk: LOW.** The probe proves the package builds even without a prebuilt, the VPS has ample swap, and the VPS target is more prebuilt-friendly than the machine that just succeeded here.

---

## Recommendation

**✅ Safe for SmartBook — adopt `better-sqlite3`.**

- Install succeeded end-to-end (compile path), runtime query works, bundled SQLite 3.53.1 supports both `strftime` and `unixepoch`.
- VPS has 2 GB swap → even a source compile is safe within memory budget.
- No need for the `@libsql/client` fallback at this time.

**Before Phase 1-E.3**, run the authoritative probe **on the VPS** to confirm whether it gets a prebuilt (fast) or compiles (still safe), and to capture the real VPS install time/memory.

### VPS Probe Procedure (run on the VPS)
```bash
mkdir -p ~/sqlite-probe && cd ~/sqlite-probe && npm init -y
free -h; swapon --show
/usr/bin/time -v npm install better-sqlite3 2>&1 | tee install.log
# Inspect: did it download a prebuilt or run node-gyp/make?
grep -Ei "prebuild|node-gyp|SOLINK|gyp info ok" install.log
cat > test.js <<'EOF'
const Database = require('better-sqlite3');
const db = new Database(':memory:');
console.log(db.prepare('select sqlite_version() as v').get());
EOF
node test.js
```

---

## Cleanup

`~/sqlite-probe` retained per instructions (not deleted) for follow-up verification.
SmartBook project: **no files changed** (probe was fully isolated in the home directory).

---

## Final Confirmation

- SmartBook `package.json`, `db.ts`, `db.sqlite.ts`, `schema.sqlite.mvp.ts` — untouched.
- No SQLite DB created in the project.
- No migration / runtime wiring performed.
- better-sqlite3 installed **only** in throwaway `~/sqlite-probe`.

---

*Probe Only. The LOCAL result is a positive analog; the VPS probe (procedure above) is the authoritative gate for Phase 1-E.3.*
