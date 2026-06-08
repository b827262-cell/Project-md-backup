# SQLite Runtime Table Expansion Plan

> **Phase 1-C.6 — Planning Only / No Runtime Changes**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Source of truth: `SQLITE_RUNTIME_DEPENDENCY_AUDIT.md`
> **No schema, db.ts, package, migration, or DB changes were made in this phase.**

---

## Executive Summary

### Current MVP

**43 tables** (`drizzle/schema.sqlite.mvp.ts`, Must Migrate set).

### Missing Runtime Tables

The 43-table MVP does **not** compile against the currently-mounted routers.
`smartBookRouter.ts` and `tutorRouter.ts` (both core to Lite) import exam / AI-question / video / cache tables that are absent from the draft schema. Mounted peripheral routers (`videoCourseRouter`, `examSetRouter`, `learningMaterials`) reference more.

**18 tables** named in this phase's scope list, plus **5 additional FK-chain dependencies** discovered during planning (parent/relation tables the routers also import):

| Group | Missing Tables |
|-------|----------------|
| Exam / AI question (core) | `exam_categories`, `exam_subjects`, `exam_questions`, `real_exam_questions`, `ai_generated_exams`, `ai_generated_questions`, `ai_question_sources`, `practice_wrong_book` |
| Exam set / past exam | `exam_sets`, `exam_set_questions`, `exam_set_sub_questions`*, `exam_wrong_book`*, `exam_notes`*, `learning_material_exam_sets`* |
| Category linkage | `smart_book_category_exam_sources` |
| Page cache | `page_text_cache` |
| Video course | `video_courses`*, `video_units`, `video_knowledge_points`, `video_progress`, `video_unit_questions`, `saved_qa` |
| Learning materials | `learning_materials` |

`*` = FK-chain dependency discovered in planning (not in the original 18-table scope list, but required for compile-safety).

### Recommended Runtime Complete MVP

**66 tables** = 43 core + 18 scope-listed + 5 FK-chain dependencies.

All 23 additions are added as **schema definitions only (stubs)** — no data migration in Phase 1-D. Their purpose is to satisfy TypeScript / Drizzle imports so the mounted routers compile.

### Gate Prediction

**PASS WITH WARNINGS** — consistent with `SQLITE_RUNTIME_DEPENDENCY_AUDIT.md §7`.
Two blocker classes must be cleared before Phase 1-D wiring: (1) missing-table compile errors, (2) active `mysql2` direct drivers.

---

## Table Classification

Classification of the 18 scope-listed tables. Criterion: **which mounted router imports it**.
Core routers (`smartBookRouter`, `tutorRouter`) cannot be unmounted in Lite → their dependencies are **Must Add**. Peripheral-only references are **Optional Runtime**.

### A. Must Add Before Phase 1-D (13)

Referenced by the **core** `smartBookRouter.ts` and/or `tutorRouter.ts`. Cannot be avoided without refactoring core routers. Compile blocker + reachable runtime query.

| Table | Referenced By | Reason |
|-------|---------------|--------|
| `real_exam_questions` | smartBook, tutor | 考古題關聯查詢 |
| `exam_questions` | smartBook | 試卷題目關聯 |
| `exam_subjects` | smartBook | exam_questions 父表（FK 鏈） |
| `exam_categories` | smartBook | exam_subjects 父表（FK 鏈） |
| `ai_generated_exams` | smartBook, tutor | AI 題庫關聯 |
| `ai_generated_questions` | tutor | AI 題庫題目 |
| `ai_question_sources` | smartBook, tutor | AI 題目來源（Defer/Archive 但 active） |
| `exam_sets` | tutor | 考古題集關聯 |
| `exam_set_questions` | tutor | 考古題集題目 |
| `practice_wrong_book` | tutor | 通用錯題本 |
| `page_text_cache` | tutor | 頁面全文快取（Defer/Archive 但 active） |
| `smartBookCategoryExamSources` (`smart_book_category_exam_sources`) | smartBook | 書本考題來源（Defer/Archive 但 active） |
| `video_units` | videoCourse, **tutor** | tutor 也引用 → 升級為 Must Add |

### B. Optional Runtime (5)

Referenced **only** by peripheral mounted routers (`videoCourseRouter`, `learningMaterials`). Schema stub required while those routers stay mounted; data migration deferred. Excludable only if the owning router is unmounted from `appRouter` for Lite.

| Table | Referenced By | Note |
|-------|---------------|------|
| `video_progress` | videoCourse | 影音進度（僅影音功能） |
| `video_unit_questions` | videoCourse | 影音單元考題 |
| `video_knowledge_points` | videoCourse | 影音知識點 |
| `saved_qa` | videoCourse | 影音收藏問答 |
| `learning_materials` | learningMaterials, examSet | 講義管理 |

### C. Dormant / Exclude (0 from scope list)

**None of the 18 scope-listed tables are pure dormant** — every one is imported by at least one mounted router. The dependency graph is tangled: `tutorRouter` pulls in exam *and* video tables, so no listed table can be excluded without refactoring core routers first.

For reference, the only confirmed dormant table from the broader audit is `knowledge_chunks` (RAG = `none`, queried solely by dead code in `db.ts`) — **outside** this phase's scope list and kept excluded.

---

## Runtime Feature Mapping

| Feature | Missing Tables | Why Needed | Build Blocker? | Runtime Blocker? |
|---------|----------------|------------|----------------|------------------|
| **SmartBook** | `smart_book_category_exam_sources`, `ai_question_sources`, `page_text_cache`, `real_exam_questions`, `exam_questions`, `exam_subjects`, `exam_categories`, `ai_generated_exams` | smartBookRouter 載入考題來源 / 頁面快取 / 關聯考題 | **Yes** | Yes (查詢時) |
| **TutorChat** | `exam_sets`, `exam_set_questions`, `ai_generated_questions`, `practice_wrong_book`, `video_units`, `ai_question_sources` | tutorRouter 載入錯題本 / 考題集 / AI 題目 / 影音 | **Yes** | Yes (查詢時) |
| **Exam System** | `exam_sets`, `exam_set_questions`, `exam_set_sub_questions`, `exam_wrong_book`, `exam_notes`, `learning_material_exam_sets` | examSetRouter（mounted）完整考古題測驗 | **Yes** | Yes (查詢時) |
| **Video Course** | `video_courses`, `video_units`, `video_knowledge_points`, `video_progress`, `video_unit_questions`, `saved_qa` | videoCourseRouter（mounted）影音課程 | **Yes** | Yes (查詢時) |
| **Learning Materials** | `learning_materials` | learningMaterials.ts（mounted） | **Yes** | Yes (查詢時) |
| **User System** | （無缺表） | users 已在 43 內 | No | No |

---

## Compile / Runtime Risk Analysis

**If the schema stays at 43 tables while all current routers remain mounted:**

| Question | Answer |
|----------|--------|
| TypeScript Compile Error | **Yes** — routers `import { realExamQuestions, ... } from "drizzle/schema"`; missing exports → `TS2305: Module has no exported member`. |
| Drizzle Import Error | **Yes** — imported symbols resolve to `undefined`; `db.select().from(undefined)` fails at build/type level. |
| Runtime Query Error | **Yes** — even if compiled, queries hit `SqliteError: no such table: <name>`. |
| Router Startup Error | **Partial** — tRPC procedures resolve lazily, so app boot mostly survives; failures occur on first request to the affected procedure. Top-level module imports of missing symbols still break the build before startup. |

### Per-Missing-Table Error Matrix

| Missing Table | Error Type | Severity |
|---------------|------------|----------|
| `real_exam_questions` | TS Compile + Runtime Query | High |
| `exam_questions` / `exam_subjects` / `exam_categories` | TS Compile + Runtime Query | High |
| `ai_generated_exams` / `ai_generated_questions` | TS Compile + Runtime Query | High |
| `ai_question_sources` | TS Compile + Runtime Query | High |
| `smart_book_category_exam_sources` | TS Compile + Runtime Query | High |
| `page_text_cache` | TS Compile + Runtime Query | High |
| `exam_sets` / `exam_set_questions` | TS Compile + Runtime Query | High |
| `exam_set_sub_questions` / `exam_wrong_book` / `exam_notes` / `learning_material_exam_sets` | TS Compile + Runtime Query | Medium |
| `practice_wrong_book` | TS Compile + Runtime Query | Medium |
| `video_units` | TS Compile + Runtime Query | Medium |
| `video_courses` / `video_progress` / `video_unit_questions` / `video_knowledge_points` / `saved_qa` | TS Compile + Runtime Query | Medium |
| `learning_materials` | TS Compile + Runtime Query | Medium |

---

## Runtime Complete MVP

### Core Runtime (43)

Existing `drizzle/schema.sqlite.mvp.ts` — Must Migrate set. Unchanged.

### Required Expansion (+23 → schema stubs, no data)

Everything needed to compile the currently-mounted routers:

- **A bucket (13):** `real_exam_questions`, `exam_questions`, `exam_subjects`, `exam_categories`, `ai_generated_exams`, `ai_generated_questions`, `ai_question_sources`, `exam_sets`, `exam_set_questions`, `practice_wrong_book`, `page_text_cache`, `smart_book_category_exam_sources`, `video_units`
- **B bucket (5):** `video_progress`, `video_unit_questions`, `video_knowledge_points`, `saved_qa`, `learning_materials`
- **FK-chain dependencies (5):** `exam_set_sub_questions`, `exam_wrong_book`, `exam_notes`, `learning_material_exam_sets`, `video_courses`

### Optional Expansion (later)

Data migration for B-bucket / exam-set features once those features are confirmed active on the VPS Lite deployment. If a peripheral router is unmounted for Lite, its tables drop from Required → Optional/Excluded.

### Dormant (keep excluded)

`knowledge_chunks` and the remaining Defer/Archive 79 set not referenced by mounted routers. RAG / Qdrant / Google Drive sync / crawler tables stay out.

### Table Count Recalculation

| Stage | Count |
|-------|-------|
| Current | **43** |
| New (Required Expansion stubs) | **+23** |
| **Final — Runtime Complete MVP** | **66** |

---

## mysql2 Blockers

| File | Active Runtime | Severity | Must Fix Before Phase 1-D |
|------|----------------|----------|---------------------------|
| `server/db.ts` | **Yes** — core DB connection (mysql2 dialect) | **Critical** | **Yes** — must support better-sqlite3 / libsql before any wiring |
| `server/routers/aiQuestionBankRouter.ts` | **Yes** — mounted; direct `mysql2/promise` connection | **High** | **Yes** — rewrite raw connection as Drizzle |
| `server/learningMaterials.ts` | **Yes** — mounted; dynamic `mysql2/promise` import | **High** | **Yes** — rewrite raw connection as Drizzle |
| `scripts/*` | No — ops/dev only | Low | No (later) |

**Critical / active blockers: 3** (`db.ts` is the critical-path single point; the two routers are high-severity but localized). All three execute on the live runtime and will crash under SQLite until refactored.

---

## Recommended Next Step

> Selecting exactly one of the three allowed options.

### → 1. Update `schema.sqlite.mvp.ts` first

**Rationale:** Phase 1-D ("Design Only") cannot produce a compiling skeleton while 23 imported tables are missing — any `server/db.sqlite.ts` draft that imports the schema would fail typecheck. Adding the 23 Required-Expansion **stub definitions** (definition only, zero data, zero `mysql2` change) is the smallest, lowest-risk unblock and a precondition for meaningful Phase 1-D design.

**Sequenced plan after this phase:**
1. (Next phase) Expand `schema.sqlite.mvp.ts` 43 → 66 with stub definitions for the A + B + FK-chain tables. No data, no db.ts change.
2. Then Phase 1-D **Design Only**: draft `server/db.sqlite.ts` + Drizzle rewrite design for the 3 `mysql2` blockers, still without installing `better-sqlite3`.
3. Then Phase 1-D Wiring: install driver, rewrite blockers, smoke-test.

Option 2 (Phase 1-D Design Only) remains the immediate follow-on; Option 3 (Stop) is not warranted — the gate is PASS WITH WARNINGS, not BLOCKED.

---

*Planning Only. No schema / db.ts / package / migration / SQLite DB changes were made.*
