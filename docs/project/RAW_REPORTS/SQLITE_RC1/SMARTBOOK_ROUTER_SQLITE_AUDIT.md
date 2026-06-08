# SmartBookRouter SQLite Audit

> **Phase 1-I.0 — Analysis Only / No Code Changed**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Target: `server/routers/smartBookRouter.ts` (5936 lines; `smartBookAdminRouter` + `smartBookStudentRouter`)
> **Nothing modified. Audit only.**

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total lines | **5936** |
| **P0 blockers** | **~54 sites** |
| **P1 blockers** | **25 sites** |
| **MySQL-only blockers** | **19 sites** (17 insertId + 1 DATE + 1 raw `INSERT IGNORE`) |
| Structural blocker | **1** — raw `db.execute()` with MySQL `INSERT IGNORE` (line 2843) |
| Drizzle ops | select 142 · insert 47 · update 75 · delete 32 (portable) |
| Overall risk | **HIGH** (largest router; structural raw SQL; complex chat/option-parsing) |

This is the **largest and highest-risk** router. Unlike lessonPoints (Low) and smartBookLearning (Medium), it adds a **structural blocker** (raw `db.execute()` + MySQL `INSERT IGNORE`) and a **large JSON double-encode surface** (15 `batchQaProgress` writes). No `mysql2` import, no `createConnection`, no `onDuplicateKeyUpdate`, no `transaction`, no `RAND()`.

---

## Blockers

### P0-A · Datetime string → `integer({mode:"timestamp"})` columns (13 sites)
`new Date().toISOString().slice(0,19).replace('T',' ')` written to timestamp columns. `.getTime()` on a string crashes under SQLite. Sample sites: 2791 (publishedAt), 3658 (scriptGeneratedAt), 4196/4200 (expiredAt), 4205 (passedAt), 4297 (suspendedUntil), + ~7 more in the verification region (~4196–4310).
**Fix:** pass `new Date()` (dual-safe). For computed expiries, pass the `Date` object.

### P0-B · `JSON.stringify` → json-mode column (16 sites)
- **`batchQaProgress: JSON.stringify({...})` ×15** (1791, 1809, 1835, 1894, 1905, 1913, 1930, 1936, 1943, 2520, 2548, 2913, 3605, 3667, 3671) — `batchQaProgress` is `text({mode:"json"})` → double-encodes.
- **`options: JSON.stringify(lp.options)` ×1** (2782).
**Fix:** pass the object/array directly (json mode auto-serializes).
**Keep (NOT DB):** hash inputs 2187, 2891; chat-content builders `optionsJsonStr` 4571/4764/4947; `console.log` 4875/4881/4915; fetch body 62.

### P0-C · `JSON.parse` → json-mode column (≈6 sites)
- `JSON.parse(lp.options as string)` + double-decode: 3617–3618, 4560–4562, 4755–4756, 4933–4937 (options reads; some lack a leading typeof guard → throw under json mode).
- `JSON.parse(book.batchQaProgress as string)`: 3682.
**Fix:** use the value directly (already an object under json mode).
**Keep:** LLM/child-process `JSON.parse` (271, 299, 1362, 1437, 1563, 2597–2599, 2768, 2830, 2888, …) — not DB columns.

### P0-D · MySQL-only `sql\`DATE(...) = DATE(...)\`` (1 site)
- 5040: `sql\`DATE(${userUsageStats.date}) = DATE(${todayStr})\``. SQLite reads the Unix-seconds integer as a Julian day → wrong rows.
**Fix:** mode-aware (`date(col,'unixepoch')` for SQLite) — same pattern as smartBookLearning P0-E.

### P0-E · Structural — raw `db.execute()` with MySQL `INSERT IGNORE` (1 site) ⚠️
- 2843: `await db2.execute(sql\`INSERT IGNORE INTO book_suggestion_cache (...) VALUES (...)\`)`.
  - `db.execute()` is mysql2-shaped; better-sqlite3 drizzle uses `.run()`.
  - `INSERT IGNORE` is MySQL syntax; SQLite is `INSERT OR IGNORE`.
**Fix:** rewrite to Drizzle `.insert(bookSuggestionCache).values({...})` with mode-aware conflict handling (`.onConflictDoNothing()` for SQLite / `.onDuplicateKeyUpdate` no-op for MySQL), or a mode-branched raw statement. Already wrapped in try/catch (non-critical path), which eases this. **Highest-difficulty single item.**

### P0-F · `insertId` (17 sites) — MySQL-only result shape
738, 883, 937, 1112, 1200, 2048, 2982, 3099, 3240, 3334, 3365, 3529, 3801, 4083, 4087, 4777, 4987. Pattern `(result as any).insertId`.
**Fix:** `normalizeInsertId(result)` (helper exists); change `const [result]` destructures to `const result` where present.

### P1-A · boolean `1/0` writes (9 sites)
`? 1 : 0` writes to boolean-mode columns (isLearned, isRecommended, has*, etc.).
**Fix:** `true/false/!!x`.

### P1-B · boolean comparisons (16 sites)
- `eq(col, 1)` ×12, `eq(col, 0)` ×4 (e.g. `eq(smartBookWrongAnswers.isLearned, 0)` at 2463, 5672, 5716, 5819).
**Fix:** `eq(col, true)` / `eq(col, false)`.

---

## Module Breakdown

| # | Module | Approx. lines | Key blockers | Risk |
|---|--------|--------------:|--------------|------|
| 0 | Helpers (Tavily search, option-gen, utils) | 1–778 | option JSON building (keep) | **LOW** |
| 1 | **Admin** — SmartBook CRUD (create/update/delete book) | 779–1300 | insertId ×4, datetime | **MEDIUM** |
| 2 | Admin — Chapters / split | 1300–1780 | insertId, JSON.parse(LLM) | MEDIUM |
| 3 | **Admin — Batch QA generation** | 1780–2950 | **15 batchQaProgress stringify, raw INSERT IGNORE (2843), insertId, options parse** | **HIGH** |
| 4 | Admin — Categories CRUD | 2958–3580 | insertId ×3, datetime | MEDIUM |
| 5 | Admin — Pre-gen scripts | 3587–3730 | batchQaProgress, scriptGeneratedAt datetime (3658) | MEDIUM |
| 6 | Admin — Exam-source linking | 3731–3810 | insertId (3801) | LOW–MEDIUM |
| 7 | **Student — Reading + Verification** | 3812–4400 | **datetime ×many (4196–4310), insertId (4083/4087), status flow** | **HIGH** |
| 8 | **Student — Chat `sendMessage`** | 4400–5430 | **options JSON double-decode (4560/4755/4933), insertId message (4777/4987)** | **HIGH** |
| 9 | Student — Quiz/test module | 5434–5660 | insertId, booleans | MEDIUM |
| 10 | Student — Wrong answers | 5660–5936 | `eq(isLearned,0)` ×3, booleans | MEDIUM |

---

## Drizzle Compatibility

| Op | Count | SQLite-portable as-is? |
|----|------:|------------------------|
| `.select()` | 142 | ✅ yes (after eq(col,bool) fixes) |
| `.insert()` | 47 | ✅ yes (after insertId result handling) |
| `.update()` | 75 | ✅ yes (after datetime/json/bool value fixes) |
| `.delete()` | 32 | ✅ yes |
| raw `` sql`` `` | 18 | 17 portable (`${}` interpolation, `SUM`); **1 P0** (`DATE`, 5040) |
| `db.execute()` | 1 | ❌ **structural** (INSERT IGNORE, 2843) |

The Drizzle query-builder surface (296 ops) is portable; the risk is concentrated in **value conventions + 2 raw-SQL sites + 17 insertId**.

---

## Migration Estimate

| Item | Count |
|------|------:|
| P0 sites to change | ~54 |
| P1 sites to change | 25 |
| Structural rewrite (INSERT IGNORE) | 1 |
| **Estimated changed lines** | **~75–90** |
| Smoke tests needed | **~10–12** (book CRUD, chapter, batch-QA progress json, verification timestamps, chat options round-trip, wrong-answer boolean filter, insertId across ≥4 inserts, DATE filter, INSERT-IGNORE/onConflict, credits) |
| **Risk level** | **HIGH** |

Drivers of HIGH: 5936 lines, 17 insertId across both sub-routers, a structural raw-SQL rewrite, a large json double-encode surface (15 batchQaProgress), and the complex `sendMessage` option double-decode logic (4400–5430).

---

## Recommendation

**✅ Suitable for Phase 1-I.1 — but split the patch.** The blocker types are all known and tooled (`normalizeInsertId`, `sqliteNowSeconds`, `sqliteDateSubDays`, `isSqliteMode`, json/boolean conventions), and only **one** truly structural item (INSERT IGNORE) needs a Drizzle rewrite. Given the size, do **NOT** patch in one pass.

Suggested 1-I.1 sub-batches (each audit→patch→smoke):
1. **1-I.1a** — insertId ×17 → `normalizeInsertId` (mechanical, both sub-routers)
2. **1-I.1b** — datetime ×13 → `new Date()` (verification + scripts regions)
3. **1-I.1c** — JSON: batchQaProgress ×15 + options write/read (P0-B/C)
4. **1-I.1d** — DATE() mode-aware + INSERT IGNORE → Drizzle onConflict (the 2 raw-SQL items)
5. **1-I.1e** — booleans (P1-A 9 + P1-B 16)
Then one combined smoke covering admin CRUD + student read/chat/quiz.

---

## Final Report

1. **smartBookRouter 總行數** — **5936**
2. **P0 Blocker 數量** — **~54** (datetime 13, JSON.stringify 16, JSON.parse ~6, DATE 1, INSERT IGNORE 1, insertId 17)
3. **P1 Blocker 數量** — **25** (boolean writes 9, eq(,1) 12, eq(,0) 4)
4. **insertId 數量** — **17**
5. **raw SQL 數量** — **18** (`sql\`\``) + **1** `db.execute()`; of these **2 are MySQL-specific** (DATE 5040, INSERT IGNORE 2843), 17 portable
6. **NOW/DATE 數量** — NOW: **0**; DATE: **1** (5040)
7. **JSON 類數量** — `JSON.stringify` 25 (16 DB writes = P0, 9 keep) · `JSON.parse` 29 (~6 DB reads = P0, rest LLM/child-proc keep)
8. **boolean 類數量** — **25** (9 writes + 12 `eq(,1)` + 4 `eq(,0)`)
9. **預估修改行數** — **~75–90**
10. **是否建議進入 Phase 1-I.1** — ✅ **Yes, but patch in 5 sub-batches** (1-I.1a…1-I.1e) given HIGH risk + size; do not single-pass.

---

*Audit only. smartBookRouter / db.ts / schema / db.sqlite.ts unchanged. No DB, no migration, no build, no install.*
