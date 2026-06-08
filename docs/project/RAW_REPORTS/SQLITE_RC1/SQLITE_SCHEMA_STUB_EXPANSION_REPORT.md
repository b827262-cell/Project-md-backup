# SQLite Schema Stub Expansion Report

> **Phase 1-C.7 — Schema Draft Update Only**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> No runtime / db.ts / package / migration / SQLite DB changes were made.

---

## Summary

| Item | Value |
|------|-------|
| Previous table count | 43 |
| Added stub tables | 23 |
| **Final table count** | **66** |
| Runtime status | Not connected |
| Migration status | Not executed |
| Package status | `better-sqlite3` NOT installed |
| `schema.ts` modified | No |
| `server/db.ts` modified | No |

Verification command output:
```
$ grep -c "sqliteTable(" drizzle/schema.sqlite.mvp.ts
66
```

---

## Added Tables

### A — Must Add Before Phase 1-D (13)

Referenced by core mounted routers (`smartBookRouter.ts`, `tutorRouter.ts`).
Compile blockers — TypeScript `TS2305` without these definitions.

| # | Table | Referenced By |
|---|-------|---------------|
| 44 | `exam_categories` | smartBookRouter |
| 45 | `exam_subjects` | smartBookRouter |
| 46 | `exam_questions` | smartBookRouter |
| 47 | `real_exam_questions` | smartBookRouter, tutorRouter |
| 48 | `ai_question_sources` | smartBookRouter, tutorRouter |
| 49 | `ai_generated_exams` | smartBookRouter, tutorRouter |
| 50 | `ai_generated_questions` | tutorRouter |
| 51 | `exam_sets` | tutorRouter |
| 52 | `exam_set_questions` | tutorRouter |
| 53 | `practice_wrong_book` | tutorRouter |
| 54 | `page_text_cache` | tutorRouter |
| 55 | `smart_book_category_exam_sources` | smartBookRouter |
| 56 | `video_units` | videoCourseRouter, tutorRouter |

### B — Optional Runtime (5)

Referenced only by peripheral mounted routers (`videoCourseRouter`, `learningMaterials`).
Schema stub required while those routers remain mounted; data migration deferred.

| # | Table | Referenced By |
|---|-------|---------------|
| 57 | `video_progress` | videoCourseRouter |
| 58 | `video_unit_questions` | videoCourseRouter |
| 59 | `video_knowledge_points` | videoCourseRouter |
| 60 | `saved_qa` | videoCourseRouter |
| 61 | `learning_materials` | learningMaterials.ts, examSetRouter |

### FK-chain Dependencies (5)

Not in the original router reference list, but required as parent/join tables for compile-safe schema.

| # | Table | Why Needed |
|---|-------|------------|
| 62 | `exam_set_sub_questions` | Child of `exam_set_questions` — examSetRouter imports |
| 63 | `exam_wrong_book` | Joins `exam_sets` + `exam_set_questions` — examSetRouter imports |
| 64 | `exam_notes` | Joins `exam_set_questions` — examSetRouter imports |
| 65 | `learning_material_exam_sets` | Joins `learning_materials` + `exam_sets` — examSetRouter imports |
| 66 | `video_courses` (`videoCorses`) | Parent of `video_units` — videoCourseRouter imports |

---

## video_courses Export Name Verification

**Verification performed in Phase 1-C.7:**

| Source | Variable Name | Result |
|--------|---------------|--------|
| `drizzle/schema.ts` | `videoCorses` | Original has typo — canonical name |
| `server/routers/videoCourseRouter.ts` | `videoCorses` | Runtime uses the same typo |
| `drizzle/schema.sqlite.mvp.ts` | `videoCorses` | ✅ Matches — no fix needed |

The name `videoCorses` is a typo in the original codebase but is consistently used everywhere. The SQLite draft preserves this name to ensure import compatibility.

---

## What Was Not Changed

| Item | Status |
|------|--------|
| `server/db.ts` | **Not changed** — still uses MySQL/mysql2 |
| `drizzle/schema.ts` | **Not changed** — MySQL source schema intact |
| `package.json` | **Not changed** — no package installs |
| Migration files | **Not executed** — no migration |
| SQLite database file | **Not created** |
| Data import | **Not performed** |
| Runtime routers | **Not modified** |

---

## Remaining Blockers Before Phase 1-D Wiring

| # | Blocker | Severity | Description |
|---|---------|----------|-------------|
| 1 | `server/db.ts` mysql2 | **Critical** | Core DB connection still uses mysql2 dialect. Must be rewritten to support better-sqlite3 / libsql before any wiring. |
| 2 | `aiQuestionBankRouter.ts` mysql2/promise | **High** | Direct `mysql2/promise` connection. Must be rewritten as Drizzle ORM queries. |
| 3 | `learningMaterials.ts` mysql2/promise | **High** | Dynamic `mysql2/promise` import. Must be rewritten as Drizzle ORM queries. |
| 4 | Timestamp default strategy | **Medium** | All `defaultNow()` / `onUpdateNow()` / `CURRENT_TIMESTAMP` defaults are marked TODO. Strategy must be decided before Phase 1-D wiring (application-level set vs. `DEFAULT (unixepoch())`). |
| 5 | Enum validation | **Medium** | All `mysqlEnum` → `text` conversions have no DB-level enforcement. Zod schemas or SQLite CHECK constraints needed. |
| 6 | Indexes omitted | **Medium** | All index definitions are absent from the draft. Must be added before production wiring to avoid slow queries. |
| 7 | Foreign key enforcement strategy | **Low** | SQLite FK enforcement is off by default. Decision needed: `PRAGMA foreign_keys = ON` at connection time vs. application-level integrity. |

---

## Recommendation

**→ Phase 1-D Design Only is now unblocked for drafting.**

With 66 tables in the schema draft, `server/db.sqlite.ts` can be sketched without hitting missing-symbol compile errors. The design phase can:

1. Draft `server/db.sqlite.ts` (connection module using better-sqlite3)
2. Design Drizzle rewrite for the 3 mysql2 blockers (without executing code)
3. Decide timestamp default strategy
4. Plan index additions

**Phase 1-D Wiring** (installing better-sqlite3, actually connecting runtime) remains blocked until the 3 mysql2 blocker files are refactored.

---

*Schema Draft Update Only. No runtime / db.ts / package / migration / SQLite DB changes were made.*
