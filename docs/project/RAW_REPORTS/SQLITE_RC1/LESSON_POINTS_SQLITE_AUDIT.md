# lessonPointsRouter SQLite Readiness Audit

> **Phase 1-F.0 — Analysis Only / No Code Changed**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Target: `server/routers/lessonPointsRouter.ts` (1050 lines)
> **Nothing modified. Audit only.**

---

## Executive Summary

| Category | Count | Verdict |
|----------|-------|---------|
| **Hard blockers (P0 — runtime crash / data corruption under SQLite)** | **3 categories, 17 sites** | Must fix |
| **Correctness (P1 — type mismatch / convention)** | 2 categories, 15 sites | Should fix |
| **Cleanup (P2)** | 3 items | Optional |
| Structural blockers (raw SQL, insertId, onDuplicateKeyUpdate, mysql2) | **0** | ✅ none |

**lessonPointsRouter has ZERO structural mysql2 blockers** — no `insertId`, `onDuplicateKeyUpdate`, `RAND()`, `DATE_SUB()`, raw `sql\`\``, `.execute()`, or mysql2 typing. All issues are **value-convention mismatches** (timestamps, JSON, booleans) between the two storage models. This is the ideal pilot.

---

## Pattern Scan Results (13 checks)

| # | Pattern | Found | Sites |
|---|---------|-------|-------|
| 1 | `JSON.stringify()` on DB column | ⚠️ Yes | 4 DB-write sites (+1 read-path) |
| 2 | `JSON.parse()` on DB column | ⚠️ Yes | 4 DB-read sites (+5 LLM-response, not DB) |
| 3 | boolean `1/0` | ⚠️ Yes | 12 write + 3 compare |
| 4 | `Date.now()` | ✅ DB-safe | 1 (S3 key only, not DB) |
| 5 | `new Date()` | ⚠️ Yes | 9 (all datetime-string timestamps) |
| 6 | MySQL datetime string | ⚠️ Yes | 9 |
| 7 | `insertId` | ❌ None | 0 |
| 8 | `onDuplicateKeyUpdate` | ❌ None | 0 |
| 9 | `RAND()` | ❌ None | 0 |
| 10 | `DATE_SUB()` | ❌ None | 0 |
| 11 | raw SQL `` sql`` `` | ❌ None | 0 |
| 12 | `db.execute()` | ❌ None | 0 |
| 13 | mysql2-specific typing | ❌ None | 0 |

---

## P0 — Hard Blockers (must fix; break under SQLite)

### P0-A · Datetime-string timestamps → `integer({ mode: "timestamp" })` columns (9 sites)

Columns `publishedAt`, `completedAt`, `classroomQuizGeneratedAt` are `integer({ mode: "timestamp" })` in `schema.sqlite.mvp.ts`. Drizzle's timestamp encoder calls `.getTime()` on the value — a **string has no `.getTime()` → runtime TypeError / corrupt write**.

| Line | Snippet | SQLite compat | Fix | Risk |
|------|---------|---------------|-----|------|
| 254 | `publishedAt: new Date().toISOString().slice(0,19).replace('T',' ')` | ❌ crash | `publishedAt: new Date()` | **High** |
| 388 | `const nowUtc = new Date().toISOString().slice(0,19)...` (→ publishedAt) | ❌ | use `new Date()` / `null` | **High** |
| 409 | `const nowUtc2 = ...` (→ publishedAt) | ❌ | `new Date()` / `null` | **High** |
| 772 | `publishedAt: new Date().toISOString().slice(0,19)...` | ❌ | `new Date()` | **High** |
| 845 | `const nowUtc = ...` (→ classroomQuizGeneratedAt) | ❌ | `new Date()` | **High** |
| 901 | `const nowUtc = ...` (→ classroomQuizGeneratedAt) | ❌ | `new Date()` | **High** |
| 930 | `const nowUtc = ...` (→ classroomQuizGeneratedAt) | ❌ | `new Date()` | **High** |
| 1007 | `completedAt: ... ? new Date().toISOString()... : existing.completedAt` | ❌ | `new Date()` / keep existing | **High** |
| 1018 | `completedAt: input.correct ? new Date().toISOString()... : null` | ❌ | `new Date()` / `null` | **High** |

**Fix pattern:** replace the datetime-string expression with a plain `new Date()` (Drizzle `mode:"timestamp"` converts Date → Unix seconds automatically, as proven in the Phase 1-E.7 smoke test). For nullable cases keep `null`.

### P0-B · `JSON.stringify()` on the `options` json-mode column (4 write sites)

`options` is `text("options", { mode: "json" }).notNull()` — Drizzle auto-serializes. A manual `JSON.stringify` produces a **double-encoded** value in the DB.

| Line | Snippet | SQLite compat | Fix | Risk |
|------|---------|---------------|-----|------|
| 247 | `options: JSON.stringify(p.options)` | ❌ double-encode | `options: p.options` (pass array) | **High** |
| 297 | `options: JSON.stringify(input.options)` | ❌ | `options: input.options` | **High** |
| 336 | `updateData.options = JSON.stringify(input.options)` | ❌ | `updateData.options = input.options` | **High** |
| 765 | `options: JSON.stringify(p.options)` | ❌ | `options: p.options` | **High** |

### P0-C · `JSON.parse()` on the `options` json-mode column (4 read sites)

Under json mode, `p.options` is **already a parsed array** — `JSON.parse(array)` throws / mis-handles.

| Line | Snippet | SQLite compat | Fix | Risk |
|------|---------|---------------|-----|------|
| 24 | `options: JSON.parse(point.options as string)` | ❌ | `options: point.options` | **High** |
| 56 | `options: JSON.parse(p.options as string)` | ❌ | `options: p.options` | **High** |
| 958–962 | `getPublished` double-decode block (`JSON.parse` ×2 + re-`JSON.stringify` at 961) | ❌ | return `p.options` directly (already array); reconcile response shape | **High** |

> Note: `JSON.parse` at lines 224, 564, 748, 840, 900 parse **LLM response content**, not DB columns — ✅ keep unchanged.

---

## P1 — Correctness (should fix; type mismatch, mostly runtime-tolerant)

### P1-A · boolean `1/0` writes → `integer({ mode: "boolean" })` columns (12 sites)

`needsImage`, `isPublished`, `completed` are boolean-mode columns. Drizzle's boolean encoder does `value ? 1 : 0`, so passing `1` still stores `1` at **runtime** — but it is a **TypeScript type error** (number vs boolean) and poor practice.

| Lines | Column | Snippet | Fix |
|-------|--------|---------|-----|
| 252, 303, 341, 770 | needsImage | `needsImage: x ? 1 : 0` | `needsImage: !!x` |
| 253, 304, 342, 390, 411, 771 | isPublished | `isPublished: 1` / `x ? 1 : 0` | `isPublished: true` / `!!x` |
| 1006, 1016 | completed | `completed: x ? 1 : ...` | `completed: x` / `!!x` |

Risk: **Medium** (TS-compile + cleanliness; runtime tolerant).

### P1-B · `eq(col, 1)` boolean comparisons (3 sites)

| Line | Snippet | Fix | Risk |
|------|---------|-----|------|
| 950 | `eq(lessonPoints.isPublished, 1)` | `eq(lessonPoints.isPublished, true)` | Medium |
| 1031 | `eq(lessonPoints.isPublished, 1)` | `eq(..., true)` | Medium |
| 1041 | `eq(lessonProgress.completed, 1)` | `eq(..., true)` | Medium |

Generated SQL `= 1` matches stored `1` at runtime, but type-incorrect under boolean mode.

---

## P2 — Cleanup / Safe-to-keep

| Item | Lines | Note | Action |
|------|-------|------|--------|
| `classroomQuiz: ... as any` set | 847, 903, 932 | object → json-mode column is fine; the embedded `nowUtc` is the real issue (counted in P0-A). The `as any` masks types. | Drop `as any` after timestamp fix |
| `classroomQuiz` read | 57 | `p.classroomQuiz ?? null` — json mode returns object ✅ | keep |
| `Date.now()` + `Math.random()` | 426 | S3 object key only, DB-agnostic ✅ | keep |
| unused `inArray` import | 3 | dead import | remove (cleanup) |
| LLM-response `JSON.parse` | 224, 564, 748, 840, 900 | not DB columns ✅ | keep |

---

## Output Summary

### 1. Blocker count
**3 P0 categories = 17 hard-blocker sites** (9 datetime + 4 JSON-write + 4 JSON-read), all of which crash or corrupt under SQLite. **0 structural mysql2 blockers.**

### 2. Must-change items (必改)
- **P0-A** datetime strings → `new Date()` — **9 sites**
- **P0-B** remove `JSON.stringify(options)` on write — **4 sites**
- **P0-C** remove `JSON.parse(options)` on read — **4 sites** (incl. getPublished block)
- **P1-A** boolean `1/0` → `true/false` — **12 sites** (TS-correctness)
- **P1-B** `eq(col, 1)` → `eq(col, true)` — **3 sites**

### 3. Keep-as-is items (可保留)
- All structural patterns (none present)
- `Date.now()` / `Math.random()` S3 key (426)
- LLM-response `JSON.parse` (224, 564, 748, 840, 900)
- `classroomQuiz` object write/read under json mode (object part only)
- insert→re-select pattern (no insertId needed) ✅
- select→update/insert upsert in `recordAnswer` (no onDuplicateKeyUpdate) ✅

### 4. Estimated changed lines
**~32 lines mandatory** (P0: 17 + P1: 15), plus **~6 optional** (getPublished response-shape reconcile, `as any` removals, unused import). **Total ≈ 32–40 lines.** No new functions, no structural rewrites.

### 5. Ready for Phase 1-F.1 Router Pilot?
**✅ Yes.** All issues are localized value-convention edits with a known, mechanical fix pattern (already validated in the Phase 1-E.7 smoke test: `new Date()` timestamps, raw-array json, boolean values all round-trip correctly). No structural blockers, no raw SQL, no insertId/upsert rewrites. Low complexity, self-contained blast radius.

**Recommended pilot approach:** apply P0 (17 sites) + P1 (15 sites) under a dual-mode branch or a SQLite-adapted copy, switch the caller to `getActiveDb()`, then run the 5 Pilot Success Criteria with `DATABASE_PROVIDER=sqlite` against a throwaway DB. Keep MySQL default.

---

*Audit only. lessonPointsRouter / db.ts / db.runtime.ts / db.sqlite.ts unchanged. No DB, no migration, no build.*
