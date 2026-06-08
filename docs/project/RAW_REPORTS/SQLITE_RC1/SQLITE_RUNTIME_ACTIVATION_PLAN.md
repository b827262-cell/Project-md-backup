# SQLite Runtime Activation Plan

> **Phase 1-E.0 — Planning Only / No Runtime Changes**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **No package install, no code change, no SQLite DB, no migration, no build.**

---

## Executive Summary

| Decision | Recommendation |
|----------|----------------|
| **Driver** | `better-sqlite3` (matches existing `server/db.sqlite.ts` design contract) |
| **VPS 1GB feasible?** | ✅ Yes — runtime footprint is small; only compile-time needs care |
| **First pilot router** | `lessonPointsRouter` (4 tables, fully covered, no raw mysql2) |
| **Biggest risk** | `better-sqlite3` native-build failure on 1GB VPS without a prebuilt binary |
| **Proceed to Phase 1-E.1?** | ✅ Yes — environment and schema are ready |

Current schema state (verified this phase): **66 tables · 25 `strftime` defaults · 16 indexes · 42 TODO markers remaining · `server/db.sqlite.ts` design draft present (15 KB, not wired)**.

---

## Environment Assessment

### A. Local Dev — ASUS TUF A16 (verified)

| Component | Value | Build-ready? |
|-----------|-------|--------------|
| OS | Arch Linux, kernel 7.0.9 | ✅ |
| Node.js | v20.20.2 | ✅ (better-sqlite3 supports 20.x) |
| pnpm | 10.4.1 | ✅ |
| npm | 10.8.2 | ✅ |
| gcc | 16.1.1 | ✅ |
| make | 4.4.1 | ✅ |
| python3 | 3.14.5 | ✅ (node-gyp needs python) |
| sqlite3 (CLI) | 3.53.1 | ✅ (supports `unixepoch()` + `strftime`) |
| node-gyp | 10.1.0 (present) | ✅ |
| RAM | 15.6 GB | ✅ ample |
| Swap | 0 | ⚠️ none, but RAM ample so irrelevant locally |

**Verdict:** Local machine can compile `better-sqlite3` from source with zero extra setup. All toolchain present.

### B. VPS Lite — Ubuntu 1GB (NOT inventoried — must verify on the VPS)

These values **cannot be read from the local machine** and must be confirmed by SSH-ing into the VPS before Phase 1-E.1:

| Component | Expected / To verify | Action |
|-----------|----------------------|--------|
| OS | Ubuntu (20.04 / 22.04 LTS likely) | `lsb_release -a` |
| Node.js | Must be ≥ 18 (ideally 20.x to match dev) | `node --version` |
| RAM | ~1 GB (Lite tier) | `free -m` |
| Swap | Often 0 on minimal VPS | `swapon --show` |
| sqlite3 (system) | 3.31 (20.04) / 3.37 (22.04) — **below 3.38** | `sqlite3 --version` |
| build-essential | Often absent on minimal image | `dpkg -l | grep build-essential` |
| python3 | Usually present | `python3 --version` |

**Critical note on system SQLite version:** Ubuntu 20.04 ships SQLite 3.31, Ubuntu 22.04 ships 3.37 — both **below** the 3.38 threshold for `unixepoch()`. This is already mitigated: the schema uses `strftime('%s','now')` (works on all versions). Additionally, `better-sqlite3` **bundles its own SQLite (≥ 3.45 in v11+)**, so the system `sqlite3` version is irrelevant to the running app — it only matters for the `sqlite3` CLI used in manual inspection.

---

## better-sqlite3 Build Risk Analysis

`better-sqlite3` is a **native C++ addon**. Installation path:

1. **Happy path (no compile):** `npm`/`pnpm` downloads a **prebuilt binary** via `prebuild-install` matching `{platform, arch, Node ABI}`. For linux-x64 + Node 20, prebuilts exist for recent versions → **no toolchain needed**.
2. **Fallback (compile from source):** if no matching prebuilt, it compiles via `node-gyp`, which requires the full toolchain.

### Toolchain Requirements When Compiling From Source

| Requirement | Arch Linux (local) | Ubuntu VPS |
|-------------|--------------------|-----------| 
| `node-gyp` | ✅ 10.1.0 present | ships with npm |
| python3 | ✅ 3.14.5 | `apt install python3` (usually present) |
| C++ compiler (gcc/g++) | ✅ gcc 16.1.1 | `apt install build-essential` (often ABSENT on minimal image) |
| make | ✅ 4.4.1 | included in build-essential |
| libc headers | ✅ | `apt install build-essential` |
| sqlite3-dev | ❌ NOT needed | ❌ NOT needed — better-sqlite3 bundles SQLite source |

**Key facts:**
- `sqlite3-dev` / system SQLite is **NOT required** — better-sqlite3 compiles its own bundled amalgamation.
- On Arch (local): everything present → builds either way.
- On Ubuntu VPS (1GB): if prebuilt matches, zero risk. If it must compile, `build-essential` must be installed first **and** memory pressure becomes a concern (see Risk table).

### Recommended Pre-flight for VPS (Phase 1-E.1)

```
# Verify before installing the driver (run on VPS):
node --version                 # confirm ABI matches available prebuilds
free -m                        # confirm available memory + swap
dpkg -l | grep build-essential # confirm fallback toolchain present
```

---

## Driver Evaluation

| Driver | Sync | Async | Drizzle Support | VPS RAM Footprint | Native Build | Production-ready |
|--------|------|-------|-----------------|-------------------|--------------|------------------|
| **better-sqlite3** | ✅ Yes | ❌ (sync only) | ✅ First-class (`drizzle-orm/better-sqlite3`) | **Lowest** — single in-process lib | Native addon, but prebuilts available | ✅ Yes — widely used |
| **@libsql/client** | ⚠️ (async API) | ✅ Yes | ✅ Good (`drizzle-orm/libsql`) | Slightly higher | Native-ish, has prebuilds; supports embedded + remote replica | ✅ Yes (Turso ecosystem) |
| **node-sqlite3 (`sqlite3`)** | ❌ | ✅ (callback) | ⚠️ Legacy/limited | Moderate | Native addon | ⚠️ Older, less ideal for Drizzle |
| **bun:sqlite** | ✅ | ❌ | ✅ (Bun only) | Low | N/A (built into Bun) | ❌ N/A — project runs on **Node**, not Bun |

### Verdict

**`better-sqlite3`** is the recommended driver:
- The existing `server/db.sqlite.ts` design draft is already written against it (`import Database from "better-sqlite3"; import { drizzle } from "drizzle-orm/better-sqlite3"`).
- Synchronous API is ideal for a single-process 1GB VPS (no event-loop overhead, simplest transaction model).
- Lowest memory footprint — important for the Lite tier.
- First-class Drizzle support, identical schema semantics already validated in the draft.

**Trade-off acknowledged:** better-sqlite3 is synchronous, so existing `async` db functions become sync internally. Drizzle's better-sqlite3 driver still exposes a promise-compatible query surface, so most `await db.select()...` call sites work unchanged. This was already accounted for in the `SQLITE_RUNTIME_WIRING_DESIGN.md` DB-layer table.

**Contingency:** If the VPS cannot build better-sqlite3 and no prebuilt matches, `@libsql/client` is the fallback — it ships reliable prebuilds and supports a pure-embedded file mode, at a small async-refactor cost.

---

## Runtime Wiring Roadmap

| Phase | Name | Scope | Gate to next |
|-------|------|-------|--------------|
| **1-E.1** | Driver + db.sqlite.ts real impl | Install `better-sqlite3` + `@types/better-sqlite3`; replace stubs in `server/db.sqlite.ts` with real `getSqliteDb()` (WAL, busy_timeout, FK ON); create empty `data/smartbook.db`; smoke-test connection | Connection opens, `PRAGMA` applied, one read returns |
| **1-E.2** | Dual mode (MySQL + SQLite) | Add a `DB_DRIVER` env switch so the app can run on either MySQL (`db.ts`) or SQLite (`db.sqlite.ts`) without code edits; default stays MySQL | Both modes boot; SQLite mode passes typecheck |
| **1-E.3** | Router pilot | Migrate ONE low-risk router (`lessonPointsRouter`) to SQLite; validate CRUD against `data/smartbook.db` | Pilot router green end-to-end |
| **1-E.4** | Full runtime | Migrate remaining routers in priority order; rewrite the 3 mysql2 blockers (`db.ts`, `aiQuestionBankRouter.ts`, `learningMaterials.ts`) | All routers green on SQLite |
| **1-E.5** | MySQL removal | Remove mysql2 driver + `db.ts` MySQL path once SQLite is proven in production for a soak period | SQLite-only build passes; rollback window elapsed |

**Data migration (MySQL → SQLite)** is a separate track (Phase 1-F) and is NOT part of activation; activation can run against an empty SQLite DB for pilot validation.

---

## Router Migration Priority (by risk)

| Tier | Router | Tables | mysql2 raw SQL? | Coverage | Rationale |
|------|--------|--------|-----------------|----------|-----------|
| **P0 (pilot)** | `lessonPointsRouter` | 4 (`lesson_points`, `lesson_progress`, `smart_book_chapters`, `smart_books`) | ❌ None | ✅ 100% | Smallest surface, clean Drizzle, read-heavy → safest first real wiring |
| **P1 (core)** | `smartBookLearningRouter` | ~14 | ❌ None | ✅ 100% | Core Lite flow; pure Drizzle |
| **P1 (core)** | `smartBookRouter` | ~31 | ❌ None | ✅ 100% | Largest core; migrate after learning router proves patterns |
| **P1 (core)** | `tutorRouter` | ~15 | ❌ None | ✅ 100% | Core; references exam/video/page_text_cache stubs |
| **P2 (peripheral)** | `videoCourseRouter` | 6 | ❌ None | ✅ 100% | Mounted but peripheral to Lite |
| **P2 (peripheral)** | `examSetRouter` | 8 | ❌ None | ✅ 100% | Peripheral; ms-timestamp tables |
| **P3 (blockers)** | `aiQuestionBankRouter` | goldensun_sync_jobs | ✅ 5 raw `mysql.createConnection()` | partial | Highest risk — needs rewrite/stub (goldensun sync is Lite-excludable) |
| **P3 (blockers)** | `learningMaterials` | `auditory_playlists` etc. | ✅ 1 dynamic `mysql2/promise` | partial | Needs Drizzle rewrite of raw UPDATE |

**Order of execution:** P0 → P1 → P2 → P3. The two P3 mysql2 blockers are deliberately last because they require code rewrites (not just an import swap) and would crash under SQLite until rewritten.

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **better-sqlite3 compile failure on VPS** | High — blocks activation entirely | Medium (low if prebuilt matches Node 20 / linux-x64) | Verify Node ABI has a prebuilt before install; pre-install `build-essential`; add ≥512 MB swap as compile headroom; fallback to `@libsql/client` |
| **1GB VPS memory pressure (compile-time)** | Medium — OOM-kill during `node-gyp` | Medium (only if compiling from source with 0 swap) | Add temporary swap during install; prefer prebuilt binary (no compile); install with `--build-from-source=false` default |
| **1GB VPS memory pressure (runtime)** | Low — SQLite + Node app | Low | SQLite is in-process and lightweight; WAL mode caps memory; far smaller than the current MySQL client + server |
| **mysql2 blockers crash under SQLite** | High — `aiQuestionBankRouter` / `learningMaterials` raw SQL fails | High (certain) if reached before rewrite | Schedule both as P3 (last); stub goldensun sync as `NOT_IMPLEMENTED` for Lite; rewrite auditory UPDATE as Drizzle `.set()` |
| **Schema drift (schema.ts vs schema.sqlite.mvp.ts)** | Medium — column name/type mismatch surfaces at query time | Medium | Dual-mode (1-E.2) keeps MySQL authoritative; compile-check SQLite path before each router cutover; column-name parity audit before Phase 1-F data move |
| **Migration rollback** | High — no path back if MySQL removed too early | Low (if sequenced) | Keep MySQL fully live through 1-E.4; only remove in 1-E.5 after a soak period; `data/smartbook.db` is a file → trivial to snapshot/restore |
| **Timestamp unit mismatch (sec vs ms)** | Medium — wrong dates | Medium | Two-convention rule already documented in schema header; assert at `getSqliteDb()` init in Phase 1-E.1 |
| **`unixepoch()` unsupported on old VPS SQLite** | Low — already avoided | Low | Schema uses `strftime('%s','now')`; better-sqlite3 bundles modern SQLite anyway |

---

## Recommended Driver

**`better-sqlite3`** — synchronous, lowest footprint, first-class Drizzle support, and already the target of the `server/db.sqlite.ts` design contract. Fallback: `@libsql/client` if native build proves unworkable on the VPS.

---

## Recommended First Runtime Pilot

**`lessonPointsRouter`** as the first migrated router (Phase 1-E.3), preceded by a bare connectivity smoke test in Phase 1-E.1:

1. **1-E.1 smoke:** open `data/smartbook.db`, apply PRAGMAs, run a single `SELECT` against an empty `users` table → confirms driver + schema import + connection.
2. **1-E.3 pilot:** `lessonPointsRouter` — only 4 tables, fully covered, no raw mysql2, read-dominant. Validates real Drizzle CRUD end-to-end with the least blast radius.

---

## Final Confirmation

- No package installed.
- No code modified (`db.ts`, `db.sqlite.ts`, routers, schema all untouched).
- No SQLite DB created.
- No migration / build executed.

---

*Planning Only. Phase 1-E.1 is the first phase that touches code/packages — not started.*
