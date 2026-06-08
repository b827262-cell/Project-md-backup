# SQLite LessonPoints Pilot Plan

> **Phase 1-E.4 — Pilot Planning (Design Only)**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **No runtime code changed. No SQLite DB created. MySQL remains the live source.**

---

## Executive Summary

`lessonPointsRouter.ts` is an **excellent first pilot**: pure Drizzle ORM, **no raw SQL, no `insertId`, no `onDuplicateKeyUpdate`, no transactions, no mysql2**. It touches only **4 tables, all present** in `schema.sqlite.mvp.ts`. The migration work is entirely **cross-DB convention adaptation** (timestamps, booleans, JSON columns) — exactly what a pilot should surface before larger routers.

| Question | Answer |
|----------|--------|
| Tables used | **4** (lessonPoints, lessonProgress, smartBookChapters, smartBooks) |
| All in 66-table schema? | ✅ Yes |
| mysql2 dependency? | ❌ None |
| Raw SQL / `.execute()`? | ❌ None |
| `insertId` used? | ❌ None |
| `onDuplicateKeyUpdate`? | ❌ None |
| Transactions? | ❌ None |
| Suitable as first pilot? | ✅ **Yes — strongest candidate** |

---

## Router Assessment

### File: `server/routers/lessonPointsRouter.ts` (1050 lines)

Two sub-routers:
- `lessonPointsAdminRouter` — 16 procedures (CRUD + AI generation + publish + reorder + quiz)
- `lessonPointsStudentRouter` — 3 procedures (getPublished, getProgress, recordAnswer)

### Imports (line 1–8)

| Import | Source | SQLite impact |
|--------|--------|---------------|
| `eq, and, asc, inArray` | `drizzle-orm` | ✅ dialect-agnostic (`inArray` imported but **unused** — dead import) |
| `getDb` | `../db` (MySQL) | 🔶 must become driver-aware (dual mode) |
| `lessonPoints, lessonProgress, smartBookChapters, smartBooks` | `../../drizzle/schema` (MySQL schema) | 🔶 must import from `schema.sqlite.mvp` in SQLite mode |
| `invokeLLM`, `storagePut` | core | ✅ DB-agnostic |

### DB Access Pattern

All access is via `const db2 = await getDb()` then Drizzle query-builder calls:
`.select().from().where().orderBy().limit()`, `.insert().values()`, `.update().set().where()`, `.delete().where()`.

Insert pattern (SQLite-friendly): inserts do **not** read `insertId` — they re-`select()` by `chapterId` after insert. No autoincrement-return dependency.

Upsert pattern (`recordAnswer`, line 996–1020): explicit **select → update-or-insert**, not `onDuplicateKeyUpdate`. Portable as-is.

---

## Table Coverage

| Table | Used for | In `schema.sqlite.mvp.ts`? |
|-------|----------|----------------------------|
| `lessonPoints` | Primary CRUD target | ✅ (table 27) |
| `lessonProgress` | Student progress | ✅ (table 28) |
| `smartBookChapters` | Read chapter title/pages | ✅ (table 14) |
| `smartBooks` | Read book text/pageIndex | ✅ (table 13) |

**Coverage: 4/4 = 100%.** No missing tables. No stub tables required.

---

## MySQL Dependencies (Migration Risk Classification)

| # | Pattern | Count | Where | Risk | Class |
|---|---------|-------|-------|------|-------|
| 1 | **Datetime-string timestamps** `new Date().toISOString().slice(0,19).replace('T',' ')` → `"2026-06-03 12:00:00"` written to `publishedAt`, `classroomQuizGeneratedAt`, `completedAt` | 9 | lines 254, 388, 409, 772, 845, 901, 930, 1007, 1018 | **High** — SQLite schema columns are `integer({ mode: "timestamp" })` expecting a `Date`/Unix seconds, NOT a MySQL datetime string. Writing the string stores garbage / NaN. | **P0** |
| 2 | **tinyint 1/0 writes** `isPublished: 1`, `needsImage: x ? 1 : 0`, `completed: x ? 1 : 0` | 16 | throughout | **Medium** — SQLite schema columns are `integer({ mode: "boolean" })`; Drizzle boolean mode expects `true/false`. TS type mismatch; round-trip read may misbehave. | **P0/P1** |
| 3 | **Boolean compared to int** `eq(lessonPoints.isPublished, 1)`, `eq(lessonProgress.completed, 1)` | 3 | lines 950, 1031, 1041 | **Medium** — under boolean mode the comparison value should be `true`, not `1`. | **P1** |
| 4 | **Manual JSON stringify/parse on a json-mode column** `options: JSON.stringify(...)` write + `JSON.parse(p.options)` read; schema `options` is `text({ mode: "json" })` | many | create/generate/list/getPublished | **High** — json mode auto-serializes; manual `JSON.stringify` → double-encode; `JSON.parse(object)` on read → throws. | **P0** |
| 5 | `classroomQuiz` object via `.set({ classroomQuiz: quiz })` to json-mode column | 3 | 847, 903, 932 | **Low** — json mode auto-stringifies an object correctly; current `as any` cast hides type. Read `p.classroomQuiz ?? null` returns parsed object — OK. | **P2** |
| 6 | Unused `inArray` import | 1 | line 3 | None | **P2** (cleanup) |
| 7 | Raw SQL / `.execute()` / mysql2 | 0 | — | None | ✅ none |
| 8 | `insertId` / `onDuplicateKeyUpdate` / `transaction` | 0 | — | None | ✅ none |

### Risk Tiers
- **P0 (must fix before pilot works):** #1 timestamps, #4 JSON double-encode. These break read/write outright under SQLite.
- **P1 (should fix):** #2 tinyint writes, #3 boolean comparisons — correctness under boolean mode.
- **P2 (defer/cleanup):** #5 classroomQuiz cast, #6 unused import.

**Key finding:** All risks are **convention mismatches between two storage models**, not structural blockers. There is nothing mysql2-specific to rewrite — this is why lessonPoints is the ideal low-risk pilot.

---

## SQLite Mapping (MySQL → SQLite, design only)

| Concern | MySQL version (current) | SQLite version (target) |
|---------|-------------------------|--------------------------|
| **Timestamp write** | `publishedAt: new Date().toISOString().slice(0,19).replace('T',' ')` | `publishedAt: new Date()` (Drizzle timestamp mode converts to Unix seconds) — OR `Math.floor(Date.now()/1000)` |
| **Timestamp default** | DB `defaultNow()` | column has `.default(sql\`(strftime('%s','now'))\`)` for created_at; explicit `new Date()` for the rest |
| **Boolean write** | `isPublished: 1`, `needsImage: x ? 1 : 0` | `isPublished: true`, `needsImage: !!x` (boolean mode) |
| **Boolean read/compare** | `eq(lessonPoints.isPublished, 1)` | `eq(lessonPoints.isPublished, true)` |
| **JSON write** | `options: JSON.stringify(arr)` | `options: arr` (json mode auto-serializes) — drop manual stringify |
| **JSON read** | `JSON.parse(p.options as string)` | `p.options` is already parsed (json mode) — drop manual parse |
| **Schema import** | `from "../../drizzle/schema"` | `from "../../drizzle/schema.sqlite.mvp"` (mode-selected) |
| **db handle** | `getDb()` (mysql2 drizzle) | `getSqliteDb()` (better-sqlite3 drizzle) via dual-mode selector |
| **insert → id** | re-select (no insertId) | identical — no change needed ✅ |
| **upsert** | select → update/insert | identical — no change needed ✅ |

**Note:** A cleaner long-term option is to keep the router code DB-agnostic and push the timestamp/boolean/JSON conventions into the schema layer so both schemas behave identically. That decision belongs to Phase 1-E.5 (full migration); for the pilot, adapt at the call sites listed above.

---

## Dual Mode Design (diagram only — NOT implemented)

```
                ┌──────────────────────────────────────┐
                │   env: DATABASE_PROVIDER               │
                │   "mysql" (default) | "sqlite"         │
                └──────────────────────────────────────┘
                                │
            ┌───────────────────┴────────────────────┐
            ▼                                         ▼
  DATABASE_PROVIDER === "mysql"           DATABASE_PROVIDER === "sqlite"
            │                                         │
   getDb()  (server/db.ts)                  getSqliteDb() (server/db.sqlite.ts)
   drizzle-orm/mysql2                        drizzle-orm/better-sqlite3
   schema: drizzle/schema.ts                 schema: drizzle/schema.sqlite.mvp.ts
            │                                         │
            └───────────────────┬─────────────────────┘
                                ▼
                  lessonPointsRouter procedures
                  (same Drizzle query-builder calls;
                   value conventions adapted per mapping table)
```

Conceptual selector (design sketch — do NOT implement this phase):
```ts
// db.runtime.ts (future)
export async function getActiveDb() {
  if (process.env.DATABASE_PROVIDER === "sqlite") return getSqliteDb();
  return getDb(); // mysql default
}
```

The router would call `getActiveDb()` instead of `getDb()`. MySQL stays the default until the pilot is validated. **No code is written in this phase.**

---

## Pilot Success Criteria

The pilot is "passed" when, running with `DATABASE_PROVIDER=sqlite` against a throwaway test SQLite DB (Phase 1-E.5+, not now), these flows succeed end-to-end and round-trip correctly:

| # | Operation | Procedure | Must verify |
|---|-----------|-----------|-------------|
| 1 | **Create** | `lessonPointsAdminRouter.create` | Row inserted; `options` stored as valid JSON (not double-encoded); `isPublished` reads back as true |
| 2 | **Read** | `lessonPointsAdminRouter.list` / `getByChapter` / student `getPublished` | `options` parses to an array; boolean filter `isPublished` returns published rows |
| 3 | **Update** | `lessonPointsAdminRouter.update` | Partial update persists; `publishedAt` (via publishChapter) stores a valid timestamp readable as a Date |
| 4 | **Delete** | `lessonPointsAdminRouter.delete` / `clearAllByBook` | Row(s) removed; filtered delete by book/chapter works |
| 5 | **Student progress upsert** | `lessonPointsStudentRouter.recordAnswer` | First answer inserts; repeat answer updates `attempts`/`completed`/`completedAt`; `allCompleted` computes correctly |

**Out of scope for pilot success:** AI-generation procedures (`generateByAI`, `batchGenerateByBook`, `generateClassroomQuiz`, `reformatQuestions`) depend on `invokeLLM` and only need the **DB write/read** portion to work — their LLM calls are DB-agnostic and can be smoke-tested with mocked content.

---

## Estimated Complexity

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Structural rewrite (raw SQL, txn, insertId) | **None** | Pure Drizzle, portable |
| Convention adaptation (P0/P1) | **Low–Medium** | ~25 call sites: 9 timestamps + 16 booleans + JSON pairs |
| Table/schema work | **None** | 4/4 covered, no stubs |
| Blast radius | **Low** | Self-contained router; admin + student only |
| Overall | **Low** | Best-in-class pilot candidate |

---

## Recommended Next Step

1. **Confirm VPS better-sqlite3 probe** (Phase 1-E.3) is genuinely PASSED on the VPS (currently a local analog only).
2. **Phase 1-E.5 (implementation, separate task):** build the dual-mode `getActiveDb()` selector and a SQLite-adapted copy of lessonPointsRouter (or call-site adaptations), against a **throwaway** test SQLite DB — not the production path. Keep MySQL default.
3. Run the 5 Pilot Success Criteria; only on green, proceed to P1 routers (`smartBookLearningRouter`, then `smartBookRouter`, `tutorRouter`).

---

## Verification (this phase changed nothing runtime)

```
server/db.ts            → unchanged ✅
server/db.sqlite.ts     → unchanged ✅ (no comment added; optional permission unused)
package.json            → unchanged ✅
schema.sqlite.mvp.ts    → unchanged ✅
SQLite DB               → not created ✅
lessonPointsRouter.ts   → unchanged ✅ (analysis only)
```

*Pilot Planning only. No SQLite switch, no runtime change, no DB created.*
