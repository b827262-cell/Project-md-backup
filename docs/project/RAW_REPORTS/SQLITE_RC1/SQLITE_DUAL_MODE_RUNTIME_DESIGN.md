# SQLite Dual Mode Runtime Design

> **Phase 1-E.5 — Design Draft Only**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **No runtime code changed. `server/db.ts`, `db.sqlite.ts`, routers untouched. No SQLite DB created.**

---

## Executive Summary

A `DATABASE_PROVIDER` environment switch selects the active Drizzle instance at runtime. MySQL stays the default; SQLite is opt-in. Rollback is instant (flip the env var). The pilot router (`lessonPointsRouter`) calls a new `getActiveDb()` selector instead of `getDb()` directly.

**Important scope note:** `server/db.ts` exposes **342 exported data-access functions** built on MySQL-specific patterns (`insertId`, `onDuplicateKeyUpdate`, `RAND()`, `NOW()`). The `getActiveDb()` selector does **not** migrate those — only routers that already call `getDb()` with portable Drizzle (like `lessonPointsRouter`) can switch cleanly. The 342-function legacy layer remains MySQL-only until a later phase.

---

## 1. Current Architecture (as-is)

```
                    DATABASE_URL (MySQL DSN)
                              │
                              ▼
                    ┌───────────────────┐
                    │   server/db.ts    │
                    │  getDb()          │
                    │  drizzle-orm/     │
                    │     mysql2        │
                    │  + 342 exported   │
                    │   data functions  │
                    └───────────────────┘
                              │  getDb()
            ┌─────────────────┼──────────────────┐
            ▼                 ▼                  ▼
   lessonPointsRouter   smartBookRouter     tutorRouter ...
   (portable Drizzle)   (portable Drizzle)  (portable Drizzle)
```

- Single source of truth: MySQL via `getDb()` (`server/db.ts:172`).
- `server/db.sqlite.ts` exists as a **design draft only** (`getSqliteDbDesignOnly()` throws; better-sqlite3 not installed).

---

## 2. Dual Mode Architecture (target)

```
                  env: DATABASE_PROVIDER   ("mysql" default | "sqlite")
                              │
                              ▼
                    ┌───────────────────┐
                    │  getActiveDb()    │   ← new thin selector
                    └───────────────────┘
                 mysql │                  │ sqlite
            ┌──────────┘                  └───────────┐
            ▼                                         ▼
   ┌───────────────────┐                   ┌────────────────────────┐
   │   server/db.ts    │                   │  server/db.sqlite.ts   │
   │  getDb()          │                   │  getSqliteDb()         │
   │  drizzle-orm/     │                   │  drizzle-orm/          │
   │     mysql2        │                   │     better-sqlite3     │
   │  schema.ts        │                   │  schema.sqlite.mvp.ts  │
   │  DATABASE_URL     │                   │  SQLITE_PATH (WAL,     │
   │                   │                   │  busy_timeout, FK=ON)  │
   └───────────────────┘                   └────────────────────────┘
            │                                         │
            └─────────────────┬───────────────────────┘
                              ▼
                    Pilot: lessonPointsRouter
                    (uses getActiveDb(); value conventions
                     adapted per SQLITE_LESSONPOINTS_PILOT_PLAN.md)
```

Selection rule (from existing `db.sqlite.ts:74` `isSqliteMode()`):

| `DATABASE_PROVIDER` | Active handle | Driver | Schema |
|---------------------|--------------|--------|--------|
| `mysql` (default / unset) | `getDb()` | `drizzle-orm/mysql2` | `drizzle/schema.ts` |
| `sqlite` | `getSqliteDb()` | `drizzle-orm/better-sqlite3` | `drizzle/schema.sqlite.mvp.ts` |

---

## 3. `getActiveDb()` Interface (design sketch — NOT implemented)

Interface only. No body, no wiring this phase.

```ts
// server/db.runtime.ts (FUTURE — not created in this phase)

import type { getDb } from "./db";              // mysql2 drizzle instance
// import type { getSqliteDb } from "./db.sqlite"; // better-sqlite3 drizzle (Phase 1-E.6)

/**
 * Returns the active Drizzle DB handle based on DATABASE_PROVIDER.
 * - "sqlite" → better-sqlite3 instance (server/db.sqlite.ts)
 * - anything else (default) → mysql2 instance (server/db.ts)
 *
 * DESIGN ONLY — implementation deferred to Phase 1-E.6.
 */
export declare function getActiveDb(): Promise<ActiveDb>;

/** Union of the two driver instance types (resolved in Phase 1-E.6). */
export type ActiveDb = Awaited<ReturnType<typeof getDb>>; // | Awaited<ReturnType<typeof getSqliteDb>>
```

Reuses helpers **already present** in `server/db.sqlite.ts`:
- `isSqliteMode()` (line 74) — the branch condition.
- `getSqlitePath()` (line 64) — DB file path.
- `getSqliteDb()` (documented stub at line 92; `getSqliteDbDesignOnly()` throws until Phase 1-E.6).

**Caller change (design intent):** `lessonPointsRouter` swaps `const db2 = await getDb()` → `const db2 = await getActiveDb()`. No other structural change; value-convention adaptation per the pilot plan. **Not done this phase.**

---

## 4. Router Migration Order

| Priority | Router | Tables | Why this order |
|----------|--------|--------|----------------|
| **P0** | `lessonPointsRouter` | 4 | Pilot — pure Drizzle, 0 raw SQL / insertId / txn; smallest blast radius |
| **P1** | `smartBookLearningRouter` | ~14 | Core Lite flow; pure Drizzle; validates credit/quiz/session writes |
| **P2** | `smartBookRouter` | ~31 | Largest core; migrate after patterns proven on P0/P1 |
| **P3** | `tutorRouter` | ~15 | Core chat; references exam/video/page_text_cache stubs |

Each step: switch caller to `getActiveDb()`, adapt conventions, validate, then proceed. mysql2-blocker routers (`aiQuestionBankRouter`, `learningMaterials`) are **not** in this dual-mode track — they need raw-SQL rewrites first (later phase).

---

## 5. Rollback Design

**Instant, zero-deploy rollback:**

```
DATABASE_PROVIDER=sqlite   →  problem detected  →  DATABASE_PROVIDER=mysql  →  restart
```

| Property | Detail |
|----------|--------|
| Trigger | Set `DATABASE_PROVIDER=mysql` (or unset — mysql is default) |
| Effect | `getActiveDb()` routes back to `getDb()` / MySQL immediately on next process start |
| Data risk | None to MySQL — it stays the live source throughout the pilot; SQLite writes go to a separate `SQLITE_PATH` file |
| Code risk | None — both paths remain compiled; no `db.ts` edits |
| Blast radius | Single env var; no schema/migration to undo |

Safety invariant: **MySQL remains authoritative and untouched** until a much later cut-over phase. SQLite runs in parallel against its own file; flipping the switch never mutates MySQL.

---

## 6. Pilot Success Criteria — `lessonPointsRouter`

Pilot passes when, with `DATABASE_PROVIDER=sqlite` against a **throwaway** test SQLite DB (Phase 1-E.6, not now), all five round-trip correctly:

| # | Operation | Procedure | Pass condition |
|---|-----------|-----------|----------------|
| 1 | **Create** | `admin.create` | Row inserted; `options` valid JSON (no double-encode); `isPublished` reads back `true` |
| 2 | **Read** | `admin.list` / `student.getPublished` | `options` parses to array; `isPublished` boolean filter returns published rows |
| 3 | **Update** | `admin.update` / `publishChapter` | Partial update persists; `publishedAt` stored as valid timestamp readable as Date |
| 4 | **Delete** | `admin.delete` / `clearAllByBook` | Row(s) removed; filtered delete by book/chapter works |
| 5 | **Progress Upsert** | `student.recordAnswer` | First answer inserts; repeat updates `attempts`/`completed`/`completedAt`; `allCompleted` correct |

All five green → proceed to P1 (`smartBookLearningRouter`).

---

## Verification (this phase changed nothing runtime)

```
server/db.ts             → unchanged ✅ (analyzed only: getDb at line 172, 342 exported fns)
server/db.sqlite.ts      → unchanged ✅ (analyzed only: isSqliteMode/getSqlitePath/getSqliteDbDesignOnly)
lessonPointsRouter.ts    → unchanged ✅
smartBookRouter.ts       → unchanged ✅
tutorRouter.ts           → unchanged ✅
package.json             → unchanged ✅
schema.sqlite.mvp.ts     → unchanged ✅
SQLite DB                → not created ✅
```

## Recommended Next Step (Phase 1-E.6)

Implement (against a throwaway test DB, MySQL still default):
1. Install `better-sqlite3` + types (only after VPS probe genuinely PASSES on the VPS).
2. Replace `getSqliteDbDesignOnly()` with the real `getSqliteDb()` (WAL / busy_timeout / FK=ON per the PRAGMA plan in `db.sqlite.ts`).
3. Create `server/db.runtime.ts` with the real `getActiveDb()`.
4. Adapt `lessonPointsRouter` call sites and run the 5 Pilot Success Criteria.

*Design Draft only. No dual-mode code implemented, no driver installed, no DB created.*
