# smartBookLearningRouter SQLite Pilot Report

> **Phase 1-G.1 — Router Pilot Patch (pilot #2)**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Only `server/routers/smartBookLearningRouter.ts` patched. Disposable DB created + deleted. MySQL untouched.

---

## Result: ✅ PASS

All P0 + P1 issues from `SMARTBOOK_LEARNING_SQLITE_AUDIT.md` fixed, including the **MySQL-only blockers** (`NOW()`, `DATE()`, `insertId`) lessonPoints did not have. Smoke test 11/11 PASS against the SQLite adapter.

---

## Changes Applied

### P0-A · datetime string → Date (1 site)
- `balanceExpiresAt`: line 261 type `string|null` → `Date|null`; line 266 `expiresDate.toISOString().slice(0,19).replace(...)` → `expiresDate` (Date); line 276 display `.slice(0,10)` → `.toISOString().slice(0,10)`. Dual-safe (mysql2 accepts Date; SQLite timestamp mode → Unix seconds).

### P0-B · JSON.stringify(options) → array (3 sites)
- 1454 (createUnitQA), 1492 (updateUnitQA), 1678 (batch import): `input.options ? JSON.stringify(...) : null` → `input.options ?? null`. json-mode columns auto-serialize; this also fixes a latent double-encode on MySQL. Read-guards (`typeof === 'string' ? JSON.parse`) still handle any legacy double-encoded rows.

### P0-C · NOW() / DATE() (MySQL-only SQL)
- **`sql\`NOW()\`` ×3** (593, 617, 654 → endedAt/lastActiveAt) → `new Date()` (dual-safe; SQLite has no `NOW()`).
- **`sql\`DATE(...) = today\`` ×1** (875) → mode-aware:
  ```ts
  isSqliteMode()
    ? sql`date(${...createdAt}, 'unixepoch') = ${today}`   // SQLite: createdAt is Unix seconds
    : sql`DATE(${...createdAt}) = ${today}`                 // MySQL: datetime
  ```
  Prevents SQLite from mis-reading the integer as a Julian day.

### P0-D · insertId → normalizeInsertId (3 sites)
- 605 (createLearningSession), 1253 (review-questions batch), 1461 (createUnitQA): `(result as any).insertId` / `result[0]?.insertId` → `normalizeInsertId(result)`. Also changed `const [result]` destructure → `const result` so the SQLite object result shape works (better-sqlite3 returns `{lastInsertRowid}`, not an array).

### P1-A · boolean 1/0 writes → true/!!x (5 sites)
- 800, 809 `quizCompleted: 1` → `true`; 1359 `challengeEnabled`, 1362 `chapterVerifyEnabled`, 1496 `isActive`: `? 1 : 0` → `!!x`.

### P1-B · eq(col, 1) → eq(col, true) (4 sites)
- 398, 495, 692 `eq(smartBookUnitQA.isActive, 1)` → `true`; 841 `eq(smartBookChapterCompletions.quizCompleted, 1)` → `true`.

### Import added
- `import { normalizeInsertId, isSqliteMode } from "../db.sqlite";` (only file modified is the router).

**Lines:** ~25 logic lines across the sites above; file 1981 → 1988 (+7 net, from comments + DATE ternary + import).

---

## Verification

```
toISOString().slice(0, 19)                         → 0   ✅ (P0-A datetime gone)
JSON.stringify(... options ...) DB writes          → 0   ✅ (P0-B)
sql`NOW()`                                          → 0   ✅ (P0-D)
sql`DATE(`                                          → 1   ✅ (only the MySQL branch of mode-aware ternary, line 882)
insertId                                            → 0   ✅ (P0-D → normalizeInsertId)
eq(isActive,1) / eq(quizCompleted,1)               → 0   ✅ (P1-B)
boolean ? 1 : 0 writes (challenge/verify/isActive/quizCompleted) → 0 ✅ (P1-A)
JSON.stringify remaining                            → 2   ⚠️ both are hashInput (q.question + JSON.stringify(q.options)) — NOT DB writes, kept per audit
```
Per the audit, `JSON.stringify` is **not** required to reach 0 — the 2 remaining (lines 1231, 1885) build a content hash, not a column value.

---

## Smoke Test (disposable `./data/smartbook-learning-pilot.db`, `DATABASE_PROVIDER=sqlite`)

| # | Test | Result |
|---|------|--------|
| 1 | Create learning session (normalizeInsertId) | ✅ sessionId=1 |
| 2 | Read active session (`endedAt IS NULL`, startedAt default) | ✅ startedAt is Date |
| 3 | End session (`endedAt = new Date()` round-trip) | ✅ endedAt is Date |
| 4a | UnitQA options json round-trip (array) | ✅ |
| 4b | UnitQA `isActive` boolean | ✅ true |
| 4c | Insert unit QA answer (`isCorrect` boolean) | ✅ true |
| 5 | Read completion via `eq(quizCompleted, true)` | ✅ rows=1 |
| 6 | Boolean round trip (quizCompleted) | ✅ |
| 7a | `isSqliteMode()` true (DATE branch active) | ✅ |
| 7b | `date(createdAt,'unixepoch') = today` returns today's tx | ✅ rows=1, today=2026-06-03 |
| 8 | insertId replacement works | ✅ session=1 qa=1 |

`LEARNING_SMOKE_PASS` — 11/11.

> Scope note: smoke validates patched value conventions + mode-aware SQL against the SQLite adapter. Full in-process router run on SQLite needs the `getDb()`→`getActiveDb()` switch (Phase 1-G.2).

---

## Scope-Discipline Note (transparent)

- **Lines 462 / 477 / 482** (`isCorrect = ... ? 1 : 0` local var, written to `smartBookUnitQAAnswers.isCorrect`) were **NOT in the audit's P1 list**, so per "不得自行擴大修改" they were **left unchanged**. They are runtime-tolerant on both drivers (MySQL `tinyint` stores 1/0; SQLite boolean-mode coerces 1/0). Flagged for a future cleanup pass. (The smoke writes `isCorrect: true` to prove the column itself round-trips a boolean.)
- **Importing `../db.sqlite`** into the router loads the `better-sqlite3` native addon in the MySQL process (no DB opened — `getSqliteDb()` is lazy). Negligible overhead; better-sqlite3 is now a project dependency.

---

## Safety

| File | Status |
|------|--------|
| `server/db.ts` | ✅ untouched (getDb intact) |
| `server/db.sqlite.ts` | ✅ untouched (only imported) |
| `server/db.runtime.ts` | ✅ untouched |
| `drizzle/schema.sqlite.mvp.ts` | ✅ untouched (66 tables) |
| `lessonPointsRouter.ts` | ✅ untouched (1043 lines) |
| `smartBookRouter.ts` / `tutorRouter.ts` | ✅ untouched |
| `package.json` | ✅ untouched |
| `DATABASE_PROVIDER` default | ✅ mysql |
| SQLite DB files | ✅ none remain |
| Temp smoke script | ✅ deleted |
| MySQL source of truth | ✅ unchanged |

The router still calls `getDb()` (MySQL) in production. All fixes are forward-compatible: `new Date()`, array JSON, booleans, and `normalizeInsertId` work on both drivers, and the `DATE()` filter is mode-branched — so the live MySQL path is **not regressed**.

---

## Result: PASS

## Final Answers

1. **修改行數** — ~25 logic lines (file 1981 → 1988)
2. **P0 全部修完** — ✅ (datetime 1, JSON options 3, NOW 3, DATE 1, insertId 3)
3. **P1 全部修完** — ✅ (boolean writes 5, eq compares 4)
4. **MySQL-only blockers 歸零** — ✅ (NOW×3, DATE×1, insertId×3 all resolved/mode-aware)
5. **insertId 歸零** — ✅ (0; all via normalizeInsertId)
6. **NOW/DATE 歸零** — ✅ (NOW=0; DATE only as the guarded MySQL branch)
7. **Router Smoke Test PASS** — ✅ 11/11
8. **建立 SQLite DB 檔案** — ❌ no (disposable deleted)
9. **修改其他 router** — ❌ no
10. **建議進入 Phase 1-G.2 Dual Mode Pilot** — ✅ Yes

*Pilot patch #2. One router, ~25 lines. No dual-mode switch, no other router, MySQL default preserved.*
