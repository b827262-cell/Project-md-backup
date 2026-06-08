# smartBookLearningRouter SQLite Readiness Audit

> **Phase 1-G.0 — Analysis Only / No Code Changed**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Target: `server/routers/smartBookLearningRouter.ts` (1981 lines, 14 tables, 43 `getDb()` calls)
> **Nothing modified. Audit only.**

---

## Executive Summary

| Category | Count | Verdict |
|----------|-------|---------|
| **P0 — runtime crash / wrong result under SQLite** | **11 sites** | Must fix |
| **P1 — type/convention correctness** | 9 sites | Should fix |
| **MySQL-only blockers** (subset of P0, need semantic rewrite) | **7 sites** | Must fix — harder than lessonPoints |
| Structural (mysql2 import, createConnection, onDuplicateKeyUpdate, transaction, .execute) | **0** | ✅ none |

This router is **a step up from lessonPoints**: it introduces **MySQL-only SQL** (`NOW()`, `DATE()`) and **`insertId`** reads that lessonPoints did not have. There is still **no `mysql2` import, no `createConnection`, no `onDuplicateKeyUpdate`, no `transaction`, no `.execute()`**. Suitable as the 2nd pilot, at Medium risk.

---

## Pattern Scan Results (16 checks)

| # | Pattern | Found | DB-relevant sites |
|---|---------|-------|-------------------|
| 1 | `JSON.stringify` | ⚠️ Yes | 3 DB-write (1454, 1492, 1678) + 2 hash (keep) |
| 2 | `JSON.parse` | ⚠️ Yes | 4 guarded-read (safe) + 3 LLM-content (keep) |
| 3 | boolean `1/0` | ⚠️ Yes | 5 writes (P1) |
| 4 | `eq(col, 1/0)` | ⚠️ Yes | 4 (398, 495, 692, 841) |
| 5/6 | `toISOString()` | ⚠️ Mixed | 1 P0 (line 266, →timestamp col) + 6 safe (→text date cols) |
| 7 | `insertId` | ⚠️ Yes | **3 (605, 1253, 1461) — MySQL-only** |
| 8 | `onDuplicateKeyUpdate` | ❌ None | 0 |
| 9 | `RAND()` | ❌ None | 0 |
| 10 | `DATE_SUB()` | ❌ None | 0 |
| 11 | `.execute()` | ❌ None | 0 |
| 12 | raw `` sql`` `` | ⚠️ Yes | 8 — `NOW()`×3 (P0), `DATE()`×1 (P0), `IS NULL`×4 (safe) |
| 13 | mysql2 import | ❌ None | 0 |
| 14 | createConnection/Pool | ❌ None | 0 |
| 15 | transaction | ❌ None | 0 (the 2 hits at 210–211 are a local var `transactions`) |
| 16 | custom MySQL syntax | ⚠️ Yes | `NOW()`×3, `DATE()`×1 (counted above); `Date.now()` for job-id strings = safe |

---

## P0 — Hard Blockers (must fix)

### P0-A · Datetime string → `integer({mode:"timestamp"})` column (1 site)
| Line | Snippet | Problem | Fix | Risk |
|------|---------|---------|-----|------|
| 266 | `balanceExpiresAt = expiresDate.toISOString().slice(0,19).replace('T',' ')` → inserted to `smartBookCredits.balanceExpiresAt` (timestamp mode) | `.getTime()` on a string → crash/garbage | assign the `Date` object (`balanceExpiresAt = expiresDate`) | **High** |

### P0-B · `JSON.stringify(options)` → json-mode column (3 sites)
`smartBookUnitQA.options` / `smartBookReviewQuestions.options` are `text({mode:"json"})` — auto-serialized; manual stringify double-encodes.
| Line | Snippet | Fix |
|------|---------|-----|
| 1454 | `options: input.options ? JSON.stringify(input.options) : null` | `options: input.options ?? null` |
| 1492 | `updates.options = input.options ? JSON.stringify(input.options) : null` | `updates.options = input.options ?? null` |
| 1678 | `options: item.options ? JSON.stringify(item.options) : null` | `options: item.options ?? null` |

### P0-D · MySQL-only `sql\`NOW()\`` → timestamp columns (3 sites)
`endedAt` / `lastActiveAt` (`smartBookLearningSessions`) are timestamp-mode. SQLite has **no `NOW()`** (and it returns a text datetime, wrong for an integer column).
| Line | Snippet | Fix |
|------|---------|-----|
| 593 | `.set({ endedAt: sql\`NOW()\` })` | `.set({ endedAt: new Date() })` or `sqliteNowSeconds()` (mode-aware) |
| 617 | `.set({ lastActiveAt: sql\`NOW()\` })` | `.set({ lastActiveAt: new Date() })` |
| 654 | `.set({ endedAt: sql\`NOW()\` })` | `.set({ endedAt: new Date() })` |

### P0-E · MySQL-only `sql\`DATE(...) = today\`` (1 site)
| Line | Snippet | Problem | Fix |
|------|---------|---------|-----|
| 875 | `sql\`DATE(${smartBookCreditTransactions.createdAt}) = ${today}\`` | SQLite `DATE(integer)` treats the value as a **Julian day**, not Unix seconds → wrong rows | mode-aware: SQLite `date(createdAt,'unixepoch') = ${today}`, or a Unix-seconds range `createdAt >= startOfDay AND < nextDay` (portable, preferred) |

### P0-F · `insertId` (3 sites) — MySQL-only result shape
better-sqlite3 returns `lastInsertRowid`, not `insertId`.
| Line | Snippet | Fix |
|------|---------|-----|
| 605 | `return { sessionId: (result as any).insertId }` | `normalizeInsertId(result)` or `.returning({ id })` |
| 1253 | `savedIds.push(Number(result[0]?.insertId ?? 0))` | `normalizeInsertId(result)` |
| 1461 | `return { success: true, id: (result as any).insertId }` | `normalizeInsertId(result)` |

**P0 total: 11 sites** (1 + 3 + 3 + 1 + 3). Of these, **7 are MySQL-only** (NOW×3, DATE×1, insertId×3) requiring semantic rewrites, not just value swaps.

---

## P1 — Correctness (should fix)

### P1-A · boolean `1/0` writes → boolean-mode columns (5 sites)
| Line | Column | Fix |
|------|--------|-----|
| 800 | `quizCompleted: 1` | `quizCompleted: true` |
| 809 | `quizCompleted: 1` | `quizCompleted: true` |
| 1359 | `challengeEnabled: input.challengeEnabled ? 1 : 0` | `= !!input.challengeEnabled` |
| 1362 | `chapterVerifyEnabled: ... ? 1 : 0` | `= !!input.chapterVerifyEnabled` |
| 1496 | `isActive: input.isActive ? 1 : 0` | `= !!input.isActive` |

### P1-B · `eq(col, 1)` boolean comparisons (4 sites)
| Line | Snippet | Fix |
|------|---------|-----|
| 398 | `eq(smartBookUnitQA.isActive, 1)` | `eq(..., true)` |
| 495 | `eq(smartBookUnitQA.isActive, 1)` | `eq(..., true)` |
| 692 | `eq(smartBookUnitQA.isActive, 1)` | `eq(..., true)` |
| 841 | `eq(smartBookChapterCompletions.quizCompleted, 1)` | `eq(..., true)` |

---

## Keep As-Is (safe / not DB)

| Item | Lines | Why safe |
|------|-------|----------|
| `JSON.stringify` for content hash | 1224, 1878 | not a DB column |
| `JSON.parse` of LLM response content | 1214, 1655, 1657 | parses AI output, not a column |
| **Guarded** `JSON.parse` options reads | 430, 716, 1419, 1869 | `typeof x === 'string' ? JSON.parse(x) : x` — under json mode the value is already an object → returned as-is. **Runtime-safe in both drivers.** (optional cleanup later) |
| `toISOString().slice(0,10)` date strings | 59, 101, 145, 526, 548, 853 | written to **text** columns (`dailyResetAt`, `verifiedDate`) — valid in SQLite |
| `sql\`ended_at IS NULL\`` | 597, 621, 631, 658 | `IS NULL` is standard SQL; raw column name matches — portable |
| `isCorrect === 1` write | 482 | already a boolean expression |
| `Date.now()` in job-id strings | 1572, 1742 | string building, DB-agnostic |
| insert→re-select pattern | throughout | portable ✅ |

---

## Output Summary

### 1. 總行數
**1981 lines.**

### 2. P0 Blocker
**11 sites** — datetime-string ×1, JSON.stringify(options) ×3, `NOW()` ×3, `DATE()` ×1, `insertId` ×3.

### 3. P1 Blocker
**9 sites** — boolean `1/0` writes ×5, `eq(col,1)` ×4.

### 4. MySQL-only Blocker
**7 sites** — `sql\`NOW()\`` ×3, `sql\`DATE()\`` ×1, `insertId` ×3. (This is the key escalation vs lessonPoints, which had **0** MySQL-only blockers.) Still **no** mysql2 import / createConnection / onDuplicateKeyUpdate / transaction / .execute.

### 5. 預估修改行數
**~20 mandatory** (P0: 11 + P1: 9), plus ~4 optional (simplify guarded JSON.parse reads). **Total ≈ 20–24 lines.** The 7 MySQL-only sites need *semantic* rewrites (mode-aware helpers / range filter / normalizeInsertId), so they are heavier than lessonPoints' pure value swaps.

### 6. 預估風險
**Medium** (lessonPoints was Low). Reasons:
- `DATE()` filter (875) is a **logic rewrite** — must preserve "transactions today" semantics across drivers (recommend a Unix-seconds day-range, which is portable and index-friendly).
- `NOW()` writes must become mode-aware (`sqliteNowSeconds()` / `new Date()`) to keep BOTH drivers correct if the router stays dual-mode.
- 3 `insertId` reads must route through `normalizeInsertId()`.
- Larger surface (1981 lines, 14 tables, 43 db calls) → more verification.

### 7. 是否適合成為第二個 SQLite Pilot Router
**✅ Yes — recommended.** It deliberately exercises the **harder MySQL-only patterns** (`NOW()`, `DATE()`, `insertId`) that lessonPoints could not, while remaining free of the truly structural blockers (raw mysql2 connections, transactions, upserts). The `db.sqlite.ts` helpers (`normalizeInsertId`, `sqliteNowSeconds`, `sqliteDateSubDays`) already exist to absorb most of these. A good, controlled escalation for pilot #2.

---

*Audit only. smartBookLearningRouter / db.ts / schema / db.sqlite.ts unchanged. No DB, no migration, no build, no install.*
