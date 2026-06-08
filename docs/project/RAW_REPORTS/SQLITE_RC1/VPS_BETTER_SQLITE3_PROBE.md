# VPS better-sqlite3 Native Probe

> **Phase 1-E.3 — VPS Probe**
> Status: **NOT YET RUN ON THE VPS.** This document is a ready-to-run procedure + results template.
> Reason: the agent session executing this is the **local laptop** (`b822726-NB-TUFA16`, EndeavourOS, Node v20.20.2), which has **no access to the VPS**. No VPS values may be filled in from the local machine — doing so would misrepresent local data as VPS data.

---

## Why this is a template, not a result

| | This agent session | The VPS you want probed |
|---|--------------------|--------------------------|
| Host | `b822726-NB-TUFA16` (laptop) | VPS Lite |
| OS | EndeavourOS (Arch rolling) | Ubuntu 24.04.4 |
| Node | v20.20.2 (ABI 115) | v22.22.2 (ABI 127) |
| RAM / Swap | 14 GB / 0 | 955 MB / 2 GB |
| SSH access from this session | — | **none provided** |

A prebuilt-vs-compile outcome is keyed on **{Node ABI, OS, libc}**, all of which differ. The only way to get the real VPS answer is to run the probe **on the VPS**.

There is already a **local analog** result from Phase 1-E.2 (`BETTER_SQLITE3_INSTALL_PROBE.md`): on the laptop, `better-sqlite3@12.10.0` compiled from source in 50 s, ~600 MB peak, runtime test passed (`sqlite_version 3.53.1`). That proves the package works even without a prebuilt — but it is not the VPS number.

---

## Procedure — run these ON THE VPS

```bash
# 1. Isolated probe dir (does NOT touch the SmartBook project)
mkdir -p ~/sqlite-vps-probe && cd ~/sqlite-vps-probe
npm init -y

# 2. Memory before
echo "=== free -h BEFORE ==="; free -h
echo "=== swap ==="; swapon --show

# 3. Install with timing + full log (no extra params first)
/usr/bin/time -v npm install better-sqlite3 2>&1 | tee install.log
# (if /usr/bin/time absent: `time npm install better-sqlite3 2>&1 | tee install.log`)

# 4. Memory after
echo "=== free -h AFTER ==="; free -h

# 5. Prebuilt vs compile detection
grep -Ei "prebuild-install|node-gyp|SOLINK|gyp info ok|Downloading" install.log || echo "(no build markers found)"
ls node_modules/better-sqlite3/build/Release/better_sqlite3.node 2>/dev/null \
  && echo "→ COMPILED FROM SOURCE" \
  || echo "→ used PREBUILT (no build/Release artifact)"

# 6. Runtime test
cat > test.js <<'EOF'
const Database = require('better-sqlite3');
const db = new Database(':memory:');
console.log(db.prepare('select sqlite_version() as v').get());
EOF
node test.js
```

---

## Results Template — fill from the VPS run

| Field | Value (fill on VPS) |
|-------|---------------------|
| 1. Install success? | `TBD (Yes/No)` |
| 2. Prebuilt or compile? | `TBD` |
| 3. node-gyp compile triggered? | `TBD` |
| 4. Install elapsed time | `TBD (s)` |
| 5. `free -h` before — available | `TBD` |
| 5. `free -h` after — available | `TBD` |
| 5. Max resident (from `/usr/bin/time -v` "Maximum resident set size") | `TBD (kB)` |
| 6. `swapon --show` | `TBD` (expect 2 GB) |
| 7. `sqlite_version()` | `TBD` (expect ≥ 3.45) |

---

## Pre-filled risk expectation (from local analog + known VPS specs)

- VPS = Ubuntu 24.04 LTS / Node 22 / glibc 2.39 / x86_64 → a **standard, prebuilt-friendly** target. Likely **prebuilt (no compile)**.
- Even if it compiles: VPS has **955 MB RAM + 2 GB swap ≈ 3 GB** addressable. Local compile peaked ~600 MB → **fits with wide margin**.
- Expected risk: **LOW**. Fallback `@libsql/client` not expected to be needed.

These are **expectations**, not measurements — confirm by filling the template above.

---

## Final note

- SmartBook project not touched; no `package.json` change; no SQLite DB created; no runtime wiring.
- To complete Phase 1-E.3: run the procedure on the VPS, paste the output back, and I will fill the template and give the Phase 1-E.4 go/no-go.
