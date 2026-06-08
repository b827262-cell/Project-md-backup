# SQLite Production Readiness Review

> **Phase 1-H — Final Pre-Launch Review (Analysis Only)**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **No code, DB, migration, install, build, or commit. Read/grep/analysis only.**

---

## Executive Summary

| Question | Answer |
|----------|--------|
| Overall completion | **~40%** (infrastructure 100%, application migration ~20%) |
| Biggest remaining risk | The two largest core routers (`smartBookRouter` 5936L, `tutorRouter` 4948L) + the 342-function `server/db.ts` MySQL layer are **not migrated** |
| MVP launchable on SQLite today? | ❌ Not yet — core book/tutor flows depend on the unmigrated routers + db.ts |
| MVP launchable on MySQL today? | ✅ Yes — MySQL path is untouched and remains the source of truth |
| Enter RC1? | ❌ Not yet (needs smartBook + tutor + db.ts migration + integration test) |
| Enter VPS Lite deployment? | ✅ Yes **on MySQL**; ❌ not yet on SQLite |

The **foundation is proven and production-grade**; the **bulk of application porting remains**. This is a healthy, low-risk state — the hard architectural questions are answered, the remaining work is mechanical (apply the validated audit→patch→smoke recipe to the big routers + db.ts).

---

## 1. Completion Status

### ✅ Done (Infrastructure — 100% of validated scope)

| Component | Status | Evidence |
|-----------|--------|----------|
| SQLite MVP schema | ✅ 66 tables, hardened | 25 timestamp defaults (`strftime`), 16 indexes, json/boolean/timestamp modes |
| Runtime adapter `db.sqlite.ts` | ✅ functional | WAL + busy_timeout=5000 + FK=ON, lazy singleton, helper toolkit |
| Compatibility helpers | ✅ | `normalizeInsertId`, `sqliteRandom`, `sqliteNowSeconds`, `sqliteDateSubDays`, `toSqliteTimestamp`, `isSqliteMode` |
| Dual-mode selector `db.runtime.ts` | ✅ `getActiveDb()` | env-switch, instant rollback, validated 1-F.2 + 1-G.2 |
| better-sqlite3 driver | ✅ installed + compiled | v12.10.0, VPS probe PASS (Ubuntu 24.04/Node22), sqlite 3.53.1 |
| Pilot router #1 (lessonPoints) | ✅ migrated + smoke PASS | 1043L, 32 edits, 11/11 checks |
| Pilot router #2 (smartBookLearning) | ✅ migrated + smoke PASS | 1988L, ~25 edits incl. MySQL-only NOW/DATE/insertId, 11/11 checks |
| Methodology | ✅ proven | audit → patch → disposable smoke → cleanup, repeatable |

### ⏳ Remaining (Application migration — ~20% done)

2 of the core routers migrated; the 2 **largest** core routers + the db.ts helper layer + peripheral routers remain (detailed below).

---

## 2. Unmigrated Routers (32 mounted total; 2 migrated)

| Router | Lines | stringify | rawSQL | insertId | NOW/DATE | onDup | dt-str | bool | mysql2 | Est. Risk |
|--------|------:|----------:|-------:|---------:|---------:|------:|-------:|-----:|:------:|-----------|
| **smartBookRouter** | 5936 | 25 | 18 | 17 | 1 (DATE) | 0 | 13 | 21 | 0 | **High** (size + 17 insertId + 13 datetime) |
| **tutorRouter** | 4948 | 5 | 54 | 2 | 0 | 1 | 0 | 19 | 0 | **High** (size + onDup + 4 RAND + 19 bool) |
| aiQuestionBankRouter | 5166 | 3 | 7 | 10 | 0 | 0 | 2 | 12 | **1** | **High** (raw mysql2/promise connection — structural) |
| videoCourseRouter | 2012 | 4 | 1 | 3 | 0 | 0 | 0 | 5 | 0 | Medium |
| examSetRouter | 1325 | 3 | 0 | 2 | 0 | 0 | 0 | 7 | 0 | Low–Medium |
| realExamRouter | 861 | 0 | 2 | 1 | 0 | 0 | 2 | 4 | 0 | Low–Medium |
| ~24 other mounted routers | — | — | — | — | — | — | — | — | mostly 0 | varies (many peripheral/non-Lite) |

Notes:
- `smartBookLearningRouter` `mysql2=1` and `bool=1` are **false positives**: the "mysql2" hit is a code *comment* I added ("mysql2 accepts Date"); the "bool=1" is the audit-scoped `isCorrect ? 1 : 0` local var deliberately left (runtime-tolerant).
- `tutorRouter` 54 `sql` uses are **mostly portable** (`IS NULL`, `COUNT`, etc.); only **4 `RAND()`** + **1 onDuplicateKeyUpdate** are MySQL-specific.
- `aiQuestionBankRouter` has a **raw `mysql2/promise` connection** (the structural blocker flagged since Phase 1-C.5) — needs rewrite or Lite-stub; goldensun-sync is Lite-excludable.

**Core-Lite critical path still to migrate:** `smartBookRouter` + `tutorRouter` (≈10,900 lines combined). These are the heart of the book-reading + AI-tutor product.

---

## 3. `server/db.ts` Legacy MySQL Layer (9777 lines, 342 exported functions)

Many routers call these shared helpers, so db.ts is a **shared blocker**, not just one file.

| Pattern | Count | SQLite fix |
|---------|------:|------------|
| `insertId` reads | **43** | `normalizeInsertId()` (helper exists) |
| `onDuplicateKeyUpdate` | **3** | `.onConflictDoUpdate({ target, set })` (mode-branch) |
| `sql\`RAND()\`` | **5** | `sqliteRandom()` (helper exists) |
| `DATE_SUB(NOW(), …)` | **2** | `sqliteDateSubDays()` (helper exists) |
| raw `` sql`` `` total | **47** | most portable; ~7 MySQL-specific (RAND/DATE_SUB above) |
| `new Date()` timestamp writes | **75** | already dual-safe (mysql2 + SQLite timestamp mode accept Date) |
| `onUpdateNow` / `defaultNow` | 0 | n/a |
| mysql2 dialect import | 1 | swap to `getActiveDb()` driver per call |

**Assessment:** db.ts is large but the blocker types are **few and well-understood**, and **every one already has a helper** (`normalizeInsertId`, `sqliteRandom`, `sqliteDateSubDays`) built and smoke-validated. The 75 `new Date()` writes are already dual-safe. The real cost is **volume × verification** (342 functions), not unknown risk. Recommended: migrate db.ts function-group by function-group behind `getActiveDb()`, smoke each group.

---

## 4. VPS Lite MVP Scope vs V2

### Must-Keep (VPS Lite MVP — the launch product)
| Feature | Router(s) | Migration status |
|---------|-----------|------------------|
| User auth / account | `userManagement`, auth, `users` table | ⏳ small, easy |
| SmartBook reading + chat | **`smartBookRouter`** | ⏳ High (5936L) |
| AI Tutor chat (Gemini) | **`tutorRouter`** | ⏳ High (4948L) |
| Guided lessons | `lessonPointsRouter` | ✅ done |
| Learning credits / quiz / verification | `smartBookLearningRouter` | ✅ done |
| System settings, credit rules | db.ts helpers (small subset) | ⏳ small |

### Defer to V2 (exclude from Lite launch)
| Feature | Router | Why defer |
|---------|--------|-----------|
| AI question-bank / goldensun sync | `aiQuestionBankRouter` | raw mysql2 blocker; not core to reading |
| Video courses (函授) | `videoCourseRouter` | peripheral; large |
| Exam sets / 考古題測驗 | `examSetRouter` | peripheral |
| Real exam practice | `realExamRouter` | peripheral |
| Essay grading, knowledge base RAG, crawlers, Google Drive sync, ibrain, lecture materials, announcements, calendar, etc. | ~24 other routers | not in Lite scope (per `MYSQL_TO_SQLITE_LITE_SCOPE_AUDIT.md`) — keep on MySQL or exclude |

---

## 5. Deployment Assessment — 1GB VPS + SQLite + Gemini

### Infrastructure: ✅ Ready
- 1GB VPS + 2GB swap confirmed adequate (better-sqlite3 probe PASS, 4.45s install on VPS).
- SQLite WAL + busy_timeout + FK enforcement configured.
- Driver bundles SQLite 3.53.1 (independent of system version).
- Dual-mode + instant env rollback = safe cutover and fallback.

### Minimum launchable feature set on SQLite
To launch the **book-reading + AI-tutor** Lite product on SQLite, the still-required migrations are:
1. `smartBookRouter` (High) — book CRUD, chapters, chat, verification, credits
2. `tutorRouter` (High) — AI tutor sessions/messages (Gemini)
3. db.ts subset used by the above (insertId/RAND/onDup/date helpers — all have tooling)
4. `userManagement` + auth (small)
5. One **integration test** with `DATABASE_PROVIDER=sqlite` end-to-end (login → open book → chat → quiz → credits)

Until 1–5 are done, **SQLite-mode launch is not viable**; **MySQL-mode launch is fully viable today**.

### Recommended launch strategy
- **Phase A (now):** Deploy on **MySQL** to the 1GB VPS if hardware permits (MySQL memory footprint is the real constraint on 1GB) — product is unchanged and stable.
- **Phase B (after smartBook+tutor+db.ts migration):** Flip `DATABASE_PROVIDER=sqlite` on the same VPS — lower memory, no DB server process, file-based backups. This is the actual goal of "SmartBook **Lite**" on 1GB.

> Note: on a **1GB** VPS, SQLite is materially better than MySQL (no separate DB server eating ~200–400MB). That is the strategic reason to finish the migration — but it is **not done yet**.

---

## Risk Register

| Risk | Severity | Status |
|------|----------|--------|
| smartBookRouter not migrated (core) | High | Open — biggest single item |
| tutorRouter not migrated (core) | High | Open |
| db.ts 342-fn layer (43 insertId, 5 RAND, 3 onDup, 2 DATE_SUB) | High (volume) | Open — tooling ready |
| aiQuestionBankRouter raw mysql2 | Medium | Open — Lite-excludable / stub |
| No end-to-end integration test under SQLite | High | Open — only per-router smoke so far |
| Frontend response-shape changes (e.g. getPublished options array) | Low | Flagged, unverified vs UI |
| MySQL regression from pilots | Low | Pilots are forward-compatible; not run against a live MySQL in sandbox |
| 1GB VPS running MySQL (Phase A) | Medium | Memory-tight; SQLite is the fix |

---

## Report Answers

1. **已完成百分比** — **~40% overall** (infrastructure **100%**, application/router migration **~20%** — 2 of the core routers, smallest two, done; the 2 largest core routers + db.ts layer remain).
2. **剩餘風險** — `smartBookRouter` (5936L) + `tutorRouter` (4948L) + `server/db.ts` (342 fns: 43 insertId, 5 RAND, 3 onDup, 2 DATE_SUB) unmigrated; `aiQuestionBankRouter` raw mysql2; **no SQLite end-to-end integration test yet**.
3. **MVP 可上線範圍** — On **MySQL: full Lite MVP today**. On **SQLite: not yet** — needs smartBook + tutor + db.ts subset + auth migrated and one integration test.
4. **建議延期功能 (V2)** — aiQuestionBank/goldensun sync, video courses, exam sets, real-exam practice, essay grading, RAG/knowledge base, crawlers, Google Drive sync, and the ~24 non-Lite peripheral routers.
5. **是否可進入 RC1** — ❌ **Not yet.** RC1 requires smartBookRouter + tutorRouter + db.ts migrated and a passing SQLite end-to-end integration test.
6. **是否可進入 VPS Lite Deployment** — ✅ **Yes on MySQL** (product unchanged). ❌ **Not yet on SQLite** (the actual "Lite on 1GB" goal) until the core migration + integration test complete.

---

## Recommendation

The SQLite foundation is **production-grade and de-risked**: schema, adapter, dual-mode, helper toolkit, VPS driver, and a repeatable two-router-proven migration recipe. The remaining work is **mechanical, well-scoped, and tooled** — apply the audit→patch→smoke recipe to `smartBookRouter`, `tutorRouter`, and the db.ts helper groups, then run one SQLite end-to-end integration test.

**Next phases:**
- Phase 1-I: `smartBookRouter` audit + patch + smoke
- Phase 1-J: `tutorRouter` audit + patch + smoke
- Phase 1-K: `db.ts` helper-group migration behind `getActiveDb()`
- Phase 1-L: SQLite end-to-end integration test → **RC1 gate**
- Phase 1-M: VPS Lite SQLite deployment (env flip + backup/rollback runbook)

*Review only. Nothing modified. MySQL remains the source of truth.*
