# Phase 2D-E: RC1 Runtime Gate Smoke Test

**Status: VALIDATION COMPLETE — NO PATCHES APPLIED**

---

## Current Truth

- RC1_STUDENT_RUNTIME_GATE = PASS
- SQLITE_TABLE_COUNT = 76
- SQLITE_SCHEMA_IMPORT_OK = YES
- SQLITE_PUSH_SMOKE = PASS
- RC1_INSERT_SELECT_SMOKE = PASS (16/16 tables)
- PROVIDER_MODE_SMOKE = PASS (isSqliteMode=true, 16/16 tables present with rows)
- PNPM_BUILD = PASS (5 pre-existing warnings, no errors)
- SQLITE_LEFTOVERS = 0 (Phase 2D-E temporary smoke artifacts only)
- PUSH_METHOD = direct drizzle-kit CLI with `--url=/tmp/phase2d-e-rc1-smoke.db --force`
- FORMAL_DB_TOUCHED = NO
- No schema / router / client / db.ts changes in this phase

---

## Scope

This phase validates the RC1 SQLite student runtime gate after completion of the Phase 2D patch series (2D-A through 2D-D). The goal is to confirm that the 76-table SQLite MVP schema is production-ready for the student main-line, and that all required tables support clean insert/select operations before RC1 delivery.

**Strict constraints applied:**
- No modifications to `drizzle/schema.sqlite.mvp.ts`, `drizzle/schema.ts`, `server/db.ts`, any router, any client file, or `package.json`
- No additional table patches
- No use of production `./data/smartbook.db`
- No formal / production DB touched
- All tests used disposable DB at `/tmp/phase2d-e-rc1-smoke.db`
- All smoke artifacts deleted after test completion
- No `git commit`

---

## No-Patch Confirmation

```
PATCH_DONE = NO
Files modified this phase  = NONE (schema, routers, client, db.ts, package.json untouched)
Files created (temp)       = smoke-test.ts, drizzle.config.smoke.ts (both deleted after use)
Files created (permanent)  = docs/project/sqlite/PHASE_2D_E_RC1_RUNTIME_GATE_SMOKE_TEST.md (this report)
```

Schema diff (`git diff -- drizzle/schema.sqlite.mvp.ts`) contains exactly two hunks, both from the earlier 2D-A/2D-C patches and unchanged by this phase:
- `@@ -5,7 +5,7 @@` — `uniqueIndex` added to imports
- `@@ -1132,3 +1132,197 @@` — 10 table definitions (2D-A: 6, 2D-C: 4)

---

## Phase 2D Series Recap

| Phase | Action | Tables Added | SQLite Count | Result |
|-------|--------|-------------|--------------|--------|
| 2D-A | Minimal gap patch: practice chain + user_preferences | 6 | 72 | PASS |
| 2D-B | Read-only HIGH gap review | 0 | 72 | REPORT |
| 2D-C | Active runtime crash patch: announcements, announcement_reads, banners, wrong_questions | 4 | 76 | PASS |
| 2D-D | No-patch re-adjudication: confirmed 0 active runtime crash remaining | 0 | 76 | REPORT |
| **2D-E** | **RC1 runtime gate smoke test (this phase)** | **0** | **76** | **PASS** |

---

## SQLite Table Count

```
sqliteTable definitions in drizzle/schema.sqlite.mvp.ts = 76
(grep -n "sqliteTable" schema.sqlite.mvp.ts | grep -v import-line | wc -l)
```

---

## Validation Commands & Results

### 1. SQLite Schema Import Smoke

```bash
pnpm exec tsx -e 'import("./drizzle/schema.sqlite.mvp.ts").then(() => console.log("SQLITE_SCHEMA_IMPORT_OK"))'
```

**Result: `SQLITE_SCHEMA_IMPORT_OK`** — all 76 table definitions import without TypeScript or runtime errors.

### 2. Disposable SQLite Schema Push Smoke

```bash
./node_modules/.bin/drizzle-kit push --dialect=sqlite --schema=./drizzle/schema.sqlite.mvp.ts --url=/tmp/phase2d-e-rc1-smoke.db --force
```

**Result: `[✓] Changes applied`** — 76 tables pushed to fresh disposable SQLite DB without errors.
`PUSH_METHOD = direct drizzle-kit CLI with --url=/tmp/phase2d-e-rc1-smoke.db --force`
`sqlite_master` after push:

```text
76 user tables + sqlite_sequence
```

### 3. RC1 Minimum Insert/Select Smoke

All 16 required tables tested with full insert + select round-trip on a fresh disposable DB. FK relationships chained using returned ids from prior inserts.

| # | Table | Result |
|---|-------|--------|
| 1 | `users` | PASS |
| 2 | `smart_books` | PASS |
| 3 | `smart_book_chapters` | PASS |
| 4 | `lesson_points` | PASS |
| 5 | `lesson_progress` | PASS |
| 6 | `tutor_chat_sessions` | PASS |
| 7 | `tutor_chat_messages` | PASS |
| 8 | `announcements` | PASS |
| 9 | `announcement_reads` | PASS |
| 10 | `banners` | PASS |
| 11 | `wrong_questions` | PASS |
| 12 | `practice_exams` | PASS |
| 13 | `practice_exam_questions` | PASS |
| 14 | `practice_records` | PASS |
| 15 | `practice_answers` | PASS |
| 16 | `user_preferences` | PASS |

**Result: 16/16 PASS — `RC1_INSERT_SELECT_SMOKE = PASS`**

**Test-data alignment notes (smoke-test.ts only — schema NOT modified):**
- `users.openId` is `NOT NULL` (no default) — test provides `openId`
- `smart_books.pdfUrl`, `pdfKey` are `NOT NULL` — test provides placeholder values
- `smart_book_chapters.chapterNumber`, `startPage`, `endPage` are `NOT NULL`
- `lesson_points.explanation`, `question`, `options` (json), `correctIndex` are `NOT NULL`
- `lesson_progress.chapterId` is `NOT NULL`
- `tutor_chat_sessions.smartBookId`, `createdAt`, `updatedAt` are `NOT NULL` (bigint ms epoch)
- `tutor_chat_messages.userId`, `createdAt` are `NOT NULL` (bigint ms epoch)
- `announcements.type` is `NOT NULL` (no default)
- `practice_records.startTime`, `totalScore` are `NOT NULL`

All constraints are correctly enforced by the SQLite schema — the schema is **strict and correct**.

### 4. Provider Mode Smoke

```bash
DATABASE_PROVIDER=sqlite SQLITE_PATH=/tmp/phase2d-e-rc1-smoke.db pnpm exec tsx -e '
import { isSqliteMode } from "./server/db.sqlite";
// isSqliteMode() === true
// raw sqlite_master query confirms all 16 RC1 gate tables present + row counts
'
```

**Result:**

```
DATABASE_PROVIDER = sqlite
SQLITE_PATH       = /tmp/phase2d-e-rc1-smoke.db
isSqliteMode()    = true
SQLite table count: 77 (76 user tables + sqlite_sequence)

All 16 RC1 gate tables present with rows=1 each
PROVIDER_MODE_TABLES_PRESENT = 16/16
PROVIDER_MODE_SMOKE = PASS
```

### 5. Cleanup / Leftover Check

All smoke artifacts removed after test:

| Artifact | Status |
|----------|--------|
| `/tmp/phase2d-e-rc1-smoke.db` (+ `-shm`, `-wal`) | Deleted |
| `smoke-test.ts` | Deleted |
| `drizzle.config.smoke.ts` | Deleted |
| `drizzle/migrations-smoke/` | Not produced / removed |

```
SQLITE_LEFTOVERS = 0
FORMAL_DB_TOUCHED = NO
```

Clarification:
- `SQLITE_LEFTOVERS = 0` refers only to Phase 2D-E disposable smoke artifacts under `/tmp` and temporary repo files.
- `./data/smartbook.db` and `./data/smartbook-lite.db` (+ `-wal` / `-shm`) are pre-existing repo-local dev DB artifacts and were not created, modified, migrated, or used by this phase.

### 6. pnpm Build

```bash
pnpm build
```

**Result:**
```
✓ 7787 modules transformed.
✓ built in 27.64s
5 warnings (pre-existing duplicate-key warnings in smartBookRouter — not introduced by 2D patches)
⚡ Done in 127ms
exit 0

PNPM_BUILD = PASS (with pre-existing warnings)
```

---

## RC1 Runtime Gate Verdict

### Student Main-Line Gate (Pass Criteria)

| Criterion | Status |
|-----------|--------|
| SQLITE_SCHEMA_IMPORT_OK | YES |
| SQLITE_PUSH_SMOKE | PASS |
| RC1_INSERT_SELECT_SMOKE (16/16) | PASS |
| PROVIDER_MODE_SMOKE (isSqliteMode=true) | PASS |
| PNPM_BUILD | PASS |
| SQLITE_LEFTOVERS | 0 |
| ACTIVE_RUNTIME_CRASH_REMAINING (from 2D-D) | 0 |

**`RC1_STUDENT_RUNTIME_GATE = PASS`**

---

## Remaining Deferred Clusters (Non-Blocker for RC1)

Per Phase 2D-D findings, the following tables remain absent from SQLite MVP by design:

| Cluster | Tables | Reason | Impact |
|---------|--------|--------|--------|
| Question Bank | `question_bank`, `question_bank_history` | Not linked from student nav; complex cross-refs | Admin-only + `/questions` direct URL only |
| QA Cache | `qa_cache` | Graceful degradation (try-catch); LLM called directly | Higher token cost; no user-visible error |
| Knowledge Base | `knowledge_base_pdfs`, `knowledge_base_pages`, `knowledge_base_categories` | All procedures admin-only | Admin-only workflows degrade on SQLite |

These clusters are explicitly deferred to post-RC1 or SmartBook Pro scope. None cause student main-line crashes.

---

## Recommendation

**RC1 SQLite VPS deployment is cleared to proceed.**

The 76-table SQLite MVP schema satisfies all student-facing runtime requirements:
- TutorHome (`/`) — tutor subject listing, book search
- TutorChat (`/tutor/chat/:bookId`) — full session + message storage
- StudentPortal (`/student`) — announcements rendered, wrong questions tracked
- Chat (`/chat`) — banners displayed, practice exam flows functional
- Practice chain — practice exams, records, answers all operational
- SmartBook learning — smart books, chapters, lesson points, progress all operational

**Next recommended phase:** RC1 VPS Deployment Validation (`DATABASE_PROVIDER=sqlite`, `SQLITE_PATH=/data/smartbook.db`).

---

## Next Actions

- Proceed to RC1 VPS Deployment Validation on the target VPS environment.
- Keep deferred clusters (qa_cache, question_bank, knowledge_base*) out of the SQLite MVP cutover; revisit post-RC1.

---

## Final Status

```
PHASE_2D_E_DONE                 = YES
PATCH_DONE                      = NO
SQLITE_TABLE_COUNT              = 76
SQLITE_SCHEMA_IMPORT_OK         = YES
SQLITE_PUSH_SMOKE               = PASS
PUSH_METHOD                     = direct drizzle-kit CLI with --url=/tmp/phase2d-e-rc1-smoke.db --force
RC1_INSERT_SELECT_SMOKE         = PASS
RC1_INSERT_SELECT_TABLES_PASSED = 16/16
PROVIDER_MODE_SMOKE             = PASS
PNPM_BUILD                      = PASS
SQLITE_LEFTOVERS                = 0
FORMAL_DB_TOUCHED               = NO
RC1_STUDENT_RUNTIME_GATE        = PASS
FILES_CHANGED                   = docs/project/sqlite/PHASE_2D_E_RC1_RUNTIME_GATE_SMOKE_TEST.md
NEXT_RECOMMENDED_PHASE          = RC1 VPS Deployment Validation
```

---

*Generated via smoke test execution. No schema, router, client, or db.ts files were modified.*
