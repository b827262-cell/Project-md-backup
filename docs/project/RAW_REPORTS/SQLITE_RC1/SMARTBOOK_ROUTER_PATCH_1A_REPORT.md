# SmartBookRouter Patch 1A

> **Phase 1-I.1a — insertId batch only**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Only `server/routers/smartBookRouter.ts` patched. Disposable DB created + deleted. MySQL untouched.

## Scope

**insertId only.** No JSON, boolean, DATE, or INSERT IGNORE touched (those are batches 1-I.1b…1-I.1e).

## Changes

| Item | Count |
|------|------:|
| insertId usages converted → `normalizeInsertId(result)` | **17** |
| Insert captures un-destructured (`const [x]` → `const x`) | **16** |
| Import added (`normalizeInsertId` from `../db.sqlite`) | 1 |
| **Total edited lines** | **~34** (16 captures + 17 usages + 1 import) |
| File size | 5936 → 5938 lines (+2, the import comment) |

### Why un-destructure
The captures were `const [result] = await db2.insert(...)` (MySQL array shape). better-sqlite3 returns a non-iterable `{ changes, lastInsertRowid }`, so `const [result]` breaks under SQLite. Each was changed to `const result = await db2.insert(...)` and the id read via `normalizeInsertId(result)` (mysql: `result[0].insertId`; sqlite: `result.lastInsertRowid`). Verified no other `result.*` usage relied on the destructured shape.

### Sites (by table, all 17)
- `smartBooks` ×6 (883, 937, 3240, 3334, 3365, 3529)
- `smartBookChapters` ×3 (738, 1112, 1200)
- `smartBookChapterQA` ×1 (2048, via `newQA`)
- `smartBookCategories` ×1 (2982)
- `smartBookCategoryExamSources` ×2 (3099, 3801)
- `smartBookVerifications` ×2 (4083, 4087 — shared `result`)
- `smartBookConversations` ×2 (4777, 4987 — via `insertResult`, `|| null` fallback preserved)

## Verification

```
grep -c "insertId" smartBookRouter.ts                         → 0   ✅
grep -c "normalizeInsertId" smartBookRouter.ts                → 18  ✅ (17 usages + 1 import)
grep "const [result|newQA|insertResult] = await db2.insert"   → 0   ✅ (no destructures left)
tsx import smartBookRouter.ts                                 → IMPORT_OK ✅ (no syntax/load error)
```

## Smoke Test (disposable `./data/smartbook-insertid-test.db`, `DATABASE_PROVIDER=sqlite`)

Create → Read → Delete for each of the 7 table types touched by the 17 sites:

| Test | Result |
|------|--------|
| Book Create/Read/Delete (smartBooks) | ✅ id=1 |
| Chapter Create/Read/Delete | ✅ id=1 |
| ChapterQA Create/Read/Delete | ✅ id=1 |
| Category Create/Read/Delete | ✅ id=1 |
| CategoryExamSource Create/Read/Delete | ✅ id=1 |
| Verification Create/Read/Delete | ✅ id=1 |
| Message Create/Read/Delete (smartBookConversations) | ✅ id=1 |
| Message id `|| null` fallback yields number | ✅ mid=2 |

`INSERTID_SMOKE_PASS` — 8/8. `normalizeInsertId` returns valid rowids on better-sqlite3 across all table types.

## Safety

| File | Status |
|------|--------|
| `server/db.ts` | ✅ untouched |
| `server/db.runtime.ts` | ✅ untouched |
| `server/db.sqlite.ts` | ✅ untouched (only imported) |
| `package.json` | ✅ untouched |
| `drizzle/schema.sqlite.mvp.ts` | ✅ untouched (66 tables) |
| other routers | ✅ untouched |
| `DATABASE_PROVIDER` default | ✅ mysql |
| SQLite DB files | ✅ none remain |
| MySQL source of truth | ✅ unchanged |

**MySQL forward-compat:** `normalizeInsertId` reads `result[0].insertId` on MySQL (the un-destructured array), preserving production behavior; the router still calls `getDb()`.

## Result: PASS

## Report Answers
1. **insertId 是否歸零** — ✅ Yes (0)
2. **修改行數** — ~34 lines (16 captures + 17 usages + 1 import)
3. **Smoke 是否 PASS** — ✅ PASS (8/8)
4. **是否留下 SQLite DB** — ❌ No (disposable deleted)
5. **是否建議進入 1-I.1b datetime batch** — ✅ Yes

*Patch 1A — insertId only. No JSON/boolean/DATE/INSERT-IGNORE, no other file, MySQL default preserved.*
