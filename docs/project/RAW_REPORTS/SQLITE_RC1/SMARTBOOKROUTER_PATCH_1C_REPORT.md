# SmartBookRouter Patch 1C

> **Phase 1-I.1c — JSON batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Only `server/routers/smartBookRouter.ts` patched. Disposable DB created + deleted. MySQL untouched.

## Scope

**JSON only.** No insertId (1-I.1a), datetime (1-I.1b), boolean, DATE(), INSERT IGNORE, or getActiveDb touched.

## Changes

### TASK A — `JSON.stringify` → json-mode column writes (16 sites)
- **`batchQaProgress` ×15** → raw object: 9 single-line (1 init + 7 running `replace_all` + 1 done) + 3 script (running_script/done_script init/iter/done) + 3 multiline `JSON.stringify({...})` → `{...}`.
- **`options` ×1** (2784) → `options: lp.options`.

### TASK B — `JSON.parse` → json-mode column reads (3 unconditional fixes)
Only the **unconditional** DB-column parses were converted (they crash/lose data under json-mode where the value is already an object); the existing `typeof === 'string'` guards were **kept** as legacy-string (MySQL) defense:
| Line | Before | After |
|------|--------|-------|
| 3619 | `let parsed = JSON.parse(lp.options as string)` | `let parsed: any = lp.options` |
| 3684 | `const progress = JSON.parse(book.batchQaProgress as string)` | `let progress: any = book.batchQaProgress;` + `if (typeof progress === 'string') progress = JSON.parse(progress)` |
| 4562 | `let opts = JSON.parse(lp.options)` | `let opts: any = lp.options` |

**Total edited lines:** ~20.

## Verification (required greps)

```
1. grep -c "JSON.stringify("            → 9    (was 25; 16 DB writes removed)
2. grep -c "batchQaProgress: JSON.stringify" → 0  ✅
3. grep -c "JSON.parse("                → 26   (was 29; 3 unconditional DB parses removed)
   options: JSON.stringify (DB write)   → 0    ✅
   unconditional JSON.parse(lp.options/book.batchQaProgress) → 0  ✅
5. tsx import smartBookRouter.ts        → IMPORT_OK  ✅
```

### 4. Remaining JSON.parse (26) — why each remains

| Category | Lines | Why kept |
|----------|-------|----------|
| **Child-process stdout** | 273, 301 | parses Python helper output — not a DB column |
| **LLM / AI response content** | 490, 1362, 1364, 1437, 1439, 1563, 1565, 1743, 1903, 2092, 2185, 2599, 2601, 2770, 2832, 2890, 3653 | parses `response.choices[...].content` (and regex matches of it) — not DB columns |
| **typeof-string GUARDED, DB-derived** | 3620, 3685, 4565, 4758, 4759, 4938, 4940 | run **only** when the value is a `string` (`if (typeof x === 'string') JSON.parse(x)`). Under SQLite json-mode the value is already an object → skipped. They are **legacy/MySQL-string defense**, never an unconditional DB-column parse. Safe on both drivers. |

No **unconditional** `JSON.parse` on a DB column remains. The 9 remaining `JSON.stringify` are all non-DB: fetch body (62), content hashes (2185-area, 2884-area), chat-markdown `optionsJsonStr` (×3), `console.log` (×3).

## Smoke Test (disposable `./data/smartbook-json-test.db`, `DATABASE_PROVIDER=sqlite`)

| # | Test | Result |
|---|------|--------|
| 1 | batchQaProgress object round-trip (write raw object → read object) | ✅ |
| 2 | options array round-trip (lessonPoints.options raw array) | ✅ |
| 3 | chat option rendering path (lp.options already array) | ✅ `A. 選A  B. 選B  C. 選C` |
| 4 | pre-generated script path (`progress.key.startsWith`) | ✅ `lessonScript_42` |
| 5 | bookSuggestion cache path (insert/read) | ✅ |

`JSON_SMOKE_PASS` — 5/5. Objects/arrays write and read back without manual stringify/parse; no double-encode.

## Safety

| File | Status |
|------|--------|
| `server/db.ts` / `db.runtime.ts` / `db.sqlite.ts` | ✅ untouched |
| `package.json` / `schema.sqlite.mvp.ts` | ✅ untouched |
| other routers | ✅ untouched |
| `DATABASE_PROVIDER` default | ✅ mysql |
| SQLite DB files | ✅ none remain |
| 1-I.1a insertId | ✅ still 0 |
| 1-I.1b datetime DB writes | ✅ still 0 (the 2 `toISOString` matches are 1-I.1b's intentional return-value display strings) |

**MySQL forward-compat:** MySQL `json()` columns auto-(de)serialize; passing raw objects/arrays is correct on MySQL too, and the kept `typeof === 'string'` guards still handle any mysql2 string-returns. The router still calls `getDb()` — MySQL path not regressed.

## Success Criteria
1. All json-mode DB writes use raw object/array — ✅
2. No unconditional `JSON.parse` on DB columns — ✅ (guarded legacy defenses remain, explained)
3. LLM/API/child-process `JSON.parse` preserved — ✅
4. Smoke PASS — ✅ (5/5)
5. MySQL behavior unchanged — ✅
6. Only `smartBookRouter.ts` modified — ✅

## Report Answers
1. `grep -c "JSON.stringify("` → **9**
2. `grep -c "batchQaProgress: JSON.stringify"` → **0**
3. `grep -c "JSON.parse("` → **26**
4. Remaining JSON.parse explained above (child-proc / LLM / typeof-guarded legacy defense)
5. tsx import → **IMPORT_OK**
6. Smoke → **JSON_SMOKE_PASS**

*Patch 1C — JSON only. No insertId/datetime/boolean/DATE/INSERT-IGNORE, no other file, MySQL default preserved. Next: 1-I.1d (DATE + INSERT IGNORE).*
