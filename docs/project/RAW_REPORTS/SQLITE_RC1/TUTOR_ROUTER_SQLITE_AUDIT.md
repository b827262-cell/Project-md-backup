# TutorRouter SQLite Audit

> **Phase 1-J.0 — Audit Only / No Code Changed**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Target: `server/routers/tutorRouter.ts` (4,948 lines)
> No SQLite DB created. No migration/build/patch executed.

---

## 1. Executive Summary

| Metric | Value |
|---|---:|
| Total lines | 4,948 |
| `getDb()` calls | 101 |
| P0 blocker sites | 22 |
| P1 blocker sites | 35 |
| P2 cleanup sites | 5 |
| MySQL-only blocker sites | 17 |
| Structural blocker types | 5 |
| Overall risk | **High** |

`tutorRouter.ts` is SQLite-patchable, but not in a single pass. The largest hard blockers are insert result handling (`insertId` + `$returningId()`), MySQL-only random ordering (`RAND()`), raw `db.execute()` with MySQL result shape / MySQL syntax, and `.onDuplicateKeyUpdate()`.

Compared with `smartBookRouter`, this router has fewer timestamp issues but more mixed ownership: it imports MySQL schema tables, dynamically imports many optional tables, and even defines `sqliteTable(...)` inside the router for `book_suggestion_cache`. That local schema definition is not an immediate runtime crash by itself, but it is a cleanup/ownership smell that should not be expanded.

---

## 2. Pattern Scan Results

| Pattern | Count | Notes |
|---|---:|---|
| file lines | 4,948 | `wc -l server/routers/tutorRouter.ts` |
| `getDb()` | 101 | all still MySQL runtime path |
| explicit `insertId` | 2 | lines 413, 484 |
| `$returningId()` | 4 | lines 1273, 1306, 2020, 2056 |
| `.onDuplicateKeyUpdate()` | 1 | line 1882 |
| `RAND()` | 4 | lines 739, 851, 866, 882 |
| `DATE()` | 0 | none |
| `NOW()` | 0 | none |
| `DATE_SUB()` | 0 | none |
| `JSON.stringify` | 5 | 3 DB json-mode risks, 2 keep-as-is/plain text |
| `JSON.parse` | 18 | mostly LLM/plain-string/guarded parses; no unconditional DB json-mode parse blocker found |
| boolean `? 1 : 0` | 4 | 3 DB boolean-mode writes + 1 numeric counter group |
| `eq(col, 1)` | 15 | boolean-mode comparisons |
| `eq(col, 0)` | 4 | boolean-mode comparisons |
| raw ``sql`...` `` | 54 | mostly portable predicates/counts; several P0/P2 sites |
| `db.execute()` | 6 | driver/result-shape blocker |
| `mysql2` import | 0 | none |
| `createConnection` | 0 | none |
| `createPool` | 0 | none |
| `transaction(` | 0 | none |
| datetime-string writes | 2 | saved-note `updatedAt`, lines 3582 and 3889 |
| local `sqliteTable(...)` in router | 4 definitions + 1 import | P2 cleanup |

---

## 3. P0 Blockers

### P0-A · Insert result handling (`insertId`) — 2 sites

| Line | Pattern | Issue |
|---:|---|---|
| 406-413 | `const [result] = await db.insert(...); (result as any).insertId` | SQLite insert result shape is not MySQL tuple/`insertId`. |
| 478-484 | same | Same issue for video-course subject links. |

Fix direction: import `normalizeInsertId` or switch to driver-safe `.returning({ id })` where supported by the active driver branch.

### P0-B · MySQL-only `$returningId()` insert return — 4 sites

| Line | Table | Issue |
|---:|---|---|
| 1273 | `tutorChatSessions` | `$returningId()` is MySQL-oriented Drizzle API and should not be assumed on SQLite path. |
| 1306 | `tutorChatSessions` | Same. |
| 2020 | `tutorChatFolders` | Same. |
| 2056 | `tutorChatLabels` | Same. |

Fix direction: use a dual-driver insert-id helper or mode-aware `.returning({ id })` for SQLite.

### P0-C · MySQL-only `.onDuplicateKeyUpdate()` — 1 site

| Line | Table | Issue |
|---:|---|---|
| 1882 | `pageAiResponseCache` | MySQL `ON DUPLICATE KEY UPDATE`; SQLite needs `onConflictDoUpdate` or mode-aware raw SQL. |

Fix direction: Drizzle conflict handling with SQLite `onConflictDoUpdate`, MySQL `onDuplicateKeyUpdate`, or explicit read/update/insert fallback.

### P0-D · MySQL-only random ordering (`RAND()`) — 4 sites

| Line | Usage |
|---:|---|
| 739 | cached book suggestions |
| 851 | recommended chapter QA |
| 866 | non-recommended chapter QA |
| 882 | unit QA |

SQLite requires `RANDOM()`. Fix with an existing helper pattern such as `sqliteRandom()`.

### P0-E · `db.execute()` driver/result-shape blockers — 6 sites

| Line | Pattern | Issue |
|---:|---|---|
| 438 | raw SELECT via `db.execute()` | MySQL returns tuple-like rows; SQLite Drizzle does not share the same `.execute()` result shape. |
| 458 | raw SELECT via `db.execute()` | Same. |
| 971-973 | `INSERT IGNORE` via `db.execute()` | MySQL syntax + driver method mismatch. |
| 1011-1013 | `INSERT IGNORE` via `db.execute()` | MySQL syntax + driver method mismatch. |
| 4939 | raw DELETE via `db.execute()` | SQL likely portable, but method should be mode-aware (`run`) or Drizzle delete. |
| 4942-4944 | raw INSERT via `db.execute()` | SQL likely portable, but method should be mode-aware (`run`) or Drizzle insert. |

Fix direction: prefer Drizzle query builder. If raw SQL remains, use mode-aware `execute`/`run`, and replace MySQL `INSERT IGNORE` with `INSERT OR IGNORE`.

### P0-F · Raw `IN (${ids.join(",")})` SQL construction — 3 sites

| Line | Pattern | Issue |
|---:|---|---|
| 1583 | `examSetIds.join(",")` inside raw `IN (...)` | Unsafe string interpolation and fragile SQL generation. |
| 1983 | `input.sessionIds.join(",")` inside raw `IN (...)` | Same; should use `inArrayDrizzle`. |
| 2486 | `subjectIds.join(",")` inside raw `IN (...)` | Same. |

These are not strictly MySQL-only syntax, but they are structural query-construction blockers for a clean dual-driver migration.

### P0-G · SQLite schema/runtime table coverage risk — 2 table groups

The router dynamically imports tables that were not found in `drizzle/schema.sqlite.mvp.ts` during this audit:

- `tutorChatFolders`
- `tutorChatLabels`
- `tutorChatSessionLabels`
- `pageAiResponseCache`

This is a router-readiness blocker if 1-J intends to run these modules against the current SQLite MVP schema. It should be confirmed before patching runtime code; do not solve this inside the router patch without an explicit schema phase.

---

## 4. P1 Blockers

### P1-A · Boolean-mode writes — 15 sites

DB boolean-mode columns currently receive `1`/`0` instead of `true`/`false`.

| Lines | Column / Table |
|---|---|
| 67, 96, 138 | `tutorSubjects.isEnabled` |
| 972, 4943 | `bookCustomSuggestions.isActive` in raw insert SQL |
| 1968, 1981, 2001 | `tutorChatSessions.isHiddenByUser` |
| 2869, 2900, 2936 | `practiceWrongBook.isResolved` |
| 4292 | `aiClassroomRecords.isCompleted` |
| 4576, 4588, 4735, 4745 | `aiClassroomLessons.isEdited` |

Fix direction: `1 -> true`, `0 -> false`, `condition ? 1 : 0 -> !!condition`.

### P1-B · Boolean comparisons — 19 sites

| Lines | Column / Table |
|---|---|
| 508 | `tutorSubjects.isEnabled = 1` |
| 849, 864 | `smartBookChapterQA.isRecommended = 1/0` |
| 880, 1528, 2274 | `smartBookUnitQA.isActive = 1` |
| 914 | `bookCustomSuggestions.isActive = 1` |
| 1033 | `smartBooks.isPublic = 1` |
| 1444, 2118, 4498, 4645 | `smartBookChapters.isEnabled = 1` |
| 1920, 1997 | `tutorChatSessions.isHiddenByUser = 0` |
| 2779, 2826, 4028, 4194 | `lessonPoints.isPublished = 1` |
| 2918 | `practiceWrongBook.isResolved = 0` |

Fix direction: `eq(col, true)` / `eq(col, false)`.

### P1-C · JSON double-encode risk — 3 sites

`practiceWrongBook.options` is `text(..., { mode: "json" })` in SQLite. Current code stringifies options before writing:

| Line | Pattern |
|---:|---|
| 2872 | `options: input.options ? JSON.stringify(input.options) : existing.options` |
| 2882 | same |
| 2898 | `options: input.options ? JSON.stringify(input.options) : null` |

Fix direction: pass the array/object directly for json-mode columns. Preserve plain-string JSON storage where the schema is plain `text`, such as `smartBookSavedMessages.noteImages`.

### P1-D · Timestamp convention — 2 sites

| Line | Pattern | Column |
|---:|---|---|
| 3582 | `new Date().toISOString().replace('T', ' ').slice(0, 19)` | `smartBookSavedMessages.updatedAt` |
| 3889 | same | `smartBookSavedMessages.updatedAt` |

The SQLite MVP defines `updatedAt` as integer-ish storage (`integer("updated_at")`) while MySQL uses timestamp string. This should be mode-aware or normalized in a timestamp batch.

### P1-E · JSON parse review — mostly keep, but verify guarded DB reads

`JSON.parse` count is 18. Most are LLM/API/plain-text cases:

- LLM output: 823, 964, 1640, 1862, 3299, 3430, 3964, 4722, 4934
- Plain string storage: saved note images at 3885
- Guarded DB json-mode reads: 2244, 2297, 2375, 2544, 2599, 2630, 2739, 3025

The guarded DB reads use `typeof x === 'string' ? JSON.parse(x) : x`; this is dual-safe and can remain unless a later cleanup wants to simplify.

---

## 5. P2 Cleanup

1. **Local schema definitions in router** — lines 31 and 4777/4833/4854/4876 define `book_suggestion_cache` via `sqliteTable(...)` inside `tutorRouter.ts`. Prefer importing `bookSuggestionCache` from schema once SQLite schema coverage is confirmed.
2. **Raw SQL cleanup** — 54 raw ``sql`...` `` expressions exist; most are portable, but many could use Drizzle helpers (`inArrayDrizzle`, `isNull`, regular `like`, `count`).
3. **`db.execute()` raw SELECTs** — lines 438 and 458 can be converted to Drizzle select/join for consistent row shape.
4. **Dynamic schema imports** — many `await import("../../drizzle/schema")` calls make ownership and SQLite coverage harder to audit.
5. **Unused/odd imports** — router-level `sqliteTable`, `integer`, `text` imports belong in schema, not router code.

---

## 6. Keep-As-Is Items

- `DATE()`, `NOW()`, `DATE_SUB()` are not present.
- `mysql2`, `createConnection`, `createPool`, and explicit transactions are not present.
- Most `Date.now()` writes are bigint millisecond columns in both schemas and are compatible.
- `JSON.stringify(longOnes)` at line 804 is LLM prompt content, not a DB write.
- `JSON.stringify(updatedImages)` at line 3889 writes to plain `text` (`noteImages`), not json-mode; keep unless schema changes.
- Guarded DB `JSON.parse` patterns are dual-safe for MySQL legacy strings and SQLite json-mode objects.
- SQL subqueries such as `session_id IN (SELECT id FROM tutor_chat_sessions ...)` are generally portable.

---

## 7. Module Breakdown

| Module | Approx. lines | Key blockers | Risk |
|---|---:|---|---|
| Subject admin | 30-150 | boolean writes (`isEnabled`) | Low |
| Subject-book links | 150-260 | mostly bigint timestamps | Low |
| Subject exam/video links | 390-490 | `insertId` x2, raw `db.execute` SELECT x2 | High |
| Dynamic suggestions | 700-1020 | `RAND()` x4, `INSERT IGNORE` x2, boolean compares | High |
| Public books / page cache / chat | 1020-1890 | `isPublic`, `isEnabled`, `.onDuplicateKeyUpdate`, `$returningId()` | High |
| Sessions/folders/labels | 1900-2130 | boolean writes/compares, `$returningId()` x2, raw `IN join` | High |
| Practice source browsers | 2190-2760 | guarded JSON parse, boolean compares, raw `IN join` | Medium |
| Lesson points / wrong book | 2770-3035 | json stringify into `practiceWrongBook.options`, boolean writes/compares | Medium |
| Admin QA analytics | 3060-3448 | raw SQL predicates mostly portable, LLM JSON parse | Medium |
| Saved notes | 3450-3895 | datetime-string `updatedAt` x2; plain text JSON images | Medium |
| AI classroom | 4000-4750 | boolean writes (`isCompleted`, `isEdited`), lessonPoints boolean compares, LLM JSON parse | Medium |
| Suggestion cache admin | 4770-4948 | local `sqliteTable` definitions, raw `db.execute` delete/insert | High |

---

## 8. Drizzle Compatibility

| Surface | Status |
|---|---|
| `.select()` / `.insert()` / `.update()` / `.delete()` | Mostly portable after value convention fixes |
| Insert return IDs | Not portable: explicit `insertId` x2 + `$returningId()` x4 |
| `.onDuplicateKeyUpdate()` | MySQL-only; must be mode-aware |
| Raw SQL predicates | Mostly portable, but `RAND()`, `INSERT IGNORE`, `db.execute()` row shape, and raw `IN join` need patching |
| JSON mode | Mostly safe reads; `practiceWrongBook.options` writes need raw object/array |
| Boolean mode | Needs systematic conversion to `true/false` |
| Timestamp mode | Most tutor timestamps are bigint ms and safe; saved-note `updatedAt` string writes need normalization |

---

## 9. Migration Estimate

| Batch | Scope | Estimated changed lines |
|---|---|---:|
| 1-J.1a | Insert return handling: `insertId` + `$returningId()` | 12-20 |
| 1-J.1b | MySQL-only raw SQL: `RAND()`, `INSERT IGNORE`, `db.execute()` | 25-40 |
| 1-J.1c | `onDuplicateKeyUpdate` cache upsert | 8-16 |
| 1-J.1d | Boolean batch | 25-35 |
| 1-J.1e | JSON + timestamp conventions | 10-20 |
| 1-J.1f | Raw `IN join` / local `sqliteTable` cleanup | 15-30 |
| Combined estimate | All router-only compatibility work | 75-120 |

Schema coverage for `tutorChatFolders`, `tutorChatLabels`, `tutorChatSessionLabels`, and `pageAiResponseCache` may require a separate schema/runtime phase before full SQLite smoke.

---

## 10. Risk Assessment

**Risk level: High.**

Reasons:

- 4,948-line router with many modules and 101 `getDb()` calls.
- Multiple P0 classes: insert return IDs, MySQL upsert, random ordering, raw execute, and raw `IN` construction.
- Runtime schema coverage is not obviously complete for all dynamically imported tutor tables.
- Chat/session modules are user-facing and contain mixed DB writes, cache updates, and AI calls.

The risk is manageable if patched in small batches with disposable SQLite smoke tests per batch.

---

## 11. Recommendation

Proceed to **Phase 1-J.1 Patch**, but split the work.

Recommended patch batches:

1. **1-J.1a — Insert Return Batch**: explicit `insertId` x2 and `$returningId()` x4.
2. **1-J.1b — Raw SQL MySQL-only Batch**: `RAND()` x4, `INSERT IGNORE` x2, `db.execute()` x6.
3. **1-J.1c — Upsert Batch**: `.onDuplicateKeyUpdate()` x1 for `pageAiResponseCache`.
4. **1-J.1d — Boolean Batch**: writes x15 and comparisons x19.
5. **1-J.1e — JSON + Timestamp Batch**: `practiceWrongBook.options` stringify x3 and saved-note `updatedAt` x2.
6. **1-J.1f — Cleanup / Structural Batch**: raw `IN (${join})` x3 and local `sqliteTable` definitions x4, after schema coverage is confirmed.

Do not patch the whole router in one pass.

---

## Final Answers

| Question | Answer |
|---|---:|
| tutorRouter total lines | 4,948 |
| P0 count | 22 sites |
| P1 count | 35 sites |
| MySQL-only blocker count | 17 sites |
| structural blocker count | 5 types |
| insertId count | 2 explicit `insertId` + 4 `$returningId()` |
| RAND() count | 4 |
| DATE() count | 0 |
| NOW() count | 0 |
| DATE_SUB() count | 0 |
| raw sql count | 54 |
| estimated changed lines | 75-120 |
| risk level | High |
| recommend entering 1-J.1 Patch | Yes, split batches |

*Audit only. No code changed. No SQLite DB created. No migration/build executed.*
