# SmartBookRouter Patch 1B

> **Phase 1-I.1b — datetime batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Only `server/routers/smartBookRouter.ts` patched. Disposable DB created + deleted. MySQL untouched.

## Scope

**Datetime only.** No JSON, boolean, DATE(), INSERT IGNORE, or other raw SQL touched (those are 1-I.1c…1-I.1e).

## Changes

| Item | Count |
|------|------:|
| Datetime-string DB writes → `new Date()` / Date var | **13** |
| `let expiredAt: string \| null` → `Date \| null` (type fixes) | 2 |
| **Total edited lines** | **~15** |
| File size | 5938 (unchanged net) |

### Sites changed (13 datetime DB writes)
| Field | Lines | Fix |
|-------|-------|-----|
| `publishedAt` | 2793 | `new Date()` |
| `scriptGeneratedAt` | 3660 | `new Date()` |
| `expiredAt` (assign) | 4198, 4202, 5260, 5264 | `= now` / `= expDate` (Date) |
| `passedAt` | 4207, 5270, 5278 | `now` (Date) |
| `suspendedUntil` (`.set`) | 4299 | Date var |
| `lockedUntil` (`.set`) | 4318 | Date var |
| `learnedAt` | 5732 | `new Date()` (isLearned:1 left for 1-I.1e) |
| type decls | 4196, 5258 | `Date \| null` |

All are `integer({mode:"timestamp"})` columns. `new Date()` / Date vars are dual-safe (mysql2 accepts Date; SQLite timestamp mode → Unix seconds).

## Verification

```
grep -c "toISOString" smartBookRouter.ts → 6  (intentional keeps, see below)
datetime-string → timestamp DB writes remaining → 0  ✅
tsx import smartBookRouter.ts → IMPORT_OK ✅
```

### Why `toISOString` is 6, not 0 (correctness over vanity grep)
The 6 remaining `toISOString()` are **deliberately kept** — converting them would break correctness or overstep this batch:
| Line | Usage | Why kept |
|------|-------|----------|
| 3997, 4216, 4236 | `.slice(0,10)` → `today`/`today2` local vars | YYYY-MM-DD strings written to **text** columns (`verifiedDate`, `dailyResetAt`) — valid in SQLite; `new Date()` would break them |
| 4305, 4328 | `suspendedUntil`/`lockedUntil` inside `return {...}` | **API response** display strings (not DB writes) — changing alters frontend contract |
| 5036 | `todayStr` for `sql\`DATE(...) = DATE(${todayStr})\`` | Entangled with the **DATE() blocker** — deferred to batch **1-I.1d**, per scope (“不碰 DATE()”) |

Zero datetime-string writes to timestamp columns remain.

## Smoke Test (disposable `./data/smartbook-datetime-test.db`, `DATABASE_PROVIDER=sqlite`)

| Test | Result |
|------|--------|
| Book Create — createdAt is Date | ✅ |
| Verification — passedAt is Date | ✅ |
| Verification — expiredAt is Date | ✅ |
| Verification — suspendedUntil is Date | ✅ |
| Verification — lockedUntil is Date | ✅ |
| no getTime() crash (`passedAt.getTime()`) | ✅ |
| Conversation Create — createdAt is Date | ✅ |
| Learning Session — startedAt is Date | ✅ |
| Completion — completedAt is Date | ✅ |

`DATETIME_SMOKE_PASS` — 9/9. Date objects write and read back as `Date`; no `.getTime()` crash (the original failure mode under SQLite).

## Safety

| File | Status |
|------|--------|
| `server/db.ts` | ✅ untouched |
| `server/db.runtime.ts` | ✅ untouched |
| `server/db.sqlite.ts` | ✅ untouched |
| `package.json` | ✅ untouched |
| `drizzle/schema.sqlite.mvp.ts` | ✅ untouched (66 tables) |
| other routers | ✅ untouched |
| `DATABASE_PROVIDER` default | ✅ mysql |
| SQLite DB files | ✅ none remain |
| insertId (from 1-I.1a) | ✅ still 0 |

**MySQL forward-compat:** mysql2 accepts `Date` objects for timestamp columns, so the live MySQL path is not regressed; the router still calls `getDb()`.

## Result: PASS

## Report Answers
1. **toISOString 是否歸零** — ⚠️ **No (6 remain) — by design.** All datetime-string→timestamp DB writes are **0**; the 6 kept are text-date locals (3), API-response display strings (2), and one DATE()-entangled string deferred to 1-I.1d. Zeroing them would break correctness.
2. **datetime 修改數量** — **13** DB-write sites (+2 type decls)
3. **Smoke 是否 PASS** — ✅ PASS (9/9)
4. **是否留下 SQLite DB** — ❌ No (disposable deleted)
5. **是否建議進入 1-I.1c JSON Batch** — ✅ Yes

*Patch 1B — datetime only. No JSON/boolean/DATE/INSERT-IGNORE, no other file, MySQL default preserved.*
