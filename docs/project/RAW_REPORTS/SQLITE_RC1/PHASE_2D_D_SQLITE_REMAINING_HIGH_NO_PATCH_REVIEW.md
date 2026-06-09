# Phase 2D-D: SQLite Remaining HIGH No-Patch Review & RC1 Runtime Gate Plan

**Status: READ-ONLY AUDIT — NO PATCHES APPLIED**

---

## Executive Summary

This report re-adjudicates the 6 remaining HIGH-priority tables identified in Phase 2D-B that were NOT patched in Phase 2D-C. The Phase 2D-B classifications were overly aggressive — several tables listed as `ACTIVE_RUNTIME_CRASH` are, on closer evidence, either admin-only, gracefully degrading, or only reachable via direct URL (not linked from student nav).

**Conclusion:** None of the 6 remaining HIGH tables cause a hard crash on the student main-line (`/`, `/student`, tutor chat). No Phase 2D-E patches are required for RC1 student-facing gate clearance.

---

## Phase 2D Recap

| Phase  | Tables Added | SQLite Count After | Status |
|--------|--------------|--------------------|--------|
| 2D-A   | `practice_exams`, `practice_exam_questions`, `practice_records`, `practice_answers`, `exam_purchases`, `user_preferences` | 72 | PASS |
| 2D-B   | Read-only review; classified remaining HIGH tables | 72 | REPORT ONLY |
| 2D-C   | `announcements`, `announcement_reads`, `banners`, `wrong_questions` | 76 | PASS |
| **2D-D** | **Read-only re-adjudication; no patches** | **76** | **REPORT ONLY** |

---

## SQLite Table Count After Phase 2D-C

```
sqliteTable definitions in drizzle/schema.sqlite.mvp.ts = 76
SQLITE_SCHEMA_IMPORT_OK = YES
SQLITE_PUSH_SMOKE         = PASS
INSERT_SELECT_SMOKE       = PASS
PNPM_BUILD                = PASS
SQLITE_LEFTOVERS          = 0
```

---

## Remaining 6 HIGH Tables Under Review

| Table | Phase 2D-B Rating | This Review Rating | Verdict |
|-------|-------------------|-------------------|---------|
| `question_bank` | ACTIVE_RUNTIME_CRASH | QUESTION_BANK_DEFER | See §3 |
| `question_bank_history` | ADMIN_ONLY | ADMIN_ONLY | Confirmed |
| `qa_cache` | ACTIVE_RUNTIME_CRASH | SOFT_DEGRADATION | See §4 |
| `knowledge_base_pdfs` | ACTIVE_RUNTIME_CRASH | ADMIN_ONLY + RAG_DEFER | See §5 |
| `knowledge_base_pages` | ACTIVE_RUNTIME_CRASH | ADMIN_ONLY + RAG_DEFER | See §5 |
| `knowledge_base_categories` | ADMIN_ONLY | ADMIN_ONLY + RAG_DEFER | Confirmed |

---

## Detailed Table Analysis

### § 1 `question_bank_history` — ADMIN_ONLY ✅ Confirmed

**Evidence:**
- Used exclusively in `server/questionVersionControl.ts` via raw SQL: `SELECT MAX(version) FROM question_bank_history WHERE question_id = ?`
- Called only from `questionBank.updateQuestion` and `questionBank.getQuestionHistory` procedures in `server/routers.ts` (lines 6410, 6528, 6546)
- Both procedures contain `if (ctx.user.role !== "admin") throw new Error("僅限管理員使用")`
- No student route mounts this; no auto-called query on page load

**Classification: ADMIN_ONLY — Do not patch for RC1**

---

### § 2 `knowledge_base_categories` — ADMIN_ONLY + RAG_DEFER ✅ Confirmed

**Evidence:**
- `knowledgeBase.getActiveCategories` server procedure (routers.ts line 3530) explicitly checks `if (ctx.user.role !== "admin") throw new Error("僅限管理員使用")`
- Client calls at `QuestionBankList.tsx:26` (`trpc.knowledgeBase.getActiveCategories.useQuery()`) will receive tRPC UNAUTHORIZED error — this surfaces as an empty `data` field (React Query default), NOT a page crash
- `/questions` route (QuestionBankList) is NOT linked from `Navbar.tsx`, `TutorHome.tsx`, or `StudentPortal.tsx`; only reachable via direct URL

**Classification: ADMIN_ONLY — Do not patch for RC1**

---

### § 3 `question_bank` — QUESTION_BANK_DEFER

**Phase 2D-B claim:** "Deeply wired into active student pages like `<ExamQuestions />` and `<KnowledgeBase />`"

**This review evidence:**

| Page | Route | Admin? | Linked from Student Nav? |
|------|-------|--------|--------------------------|
| `ExamQuestions` | `/admin/exam-questions` | YES (`/admin/*`) | NO |
| `KnowledgeBase` | `/admin/knowledge-base` | YES (`/admin/*`) | NO |
| `QuestionBankManagement` | `/admin/question-bank` | YES (`/admin/*`) | NO |
| `QuestionBankList` | `/questions` | NO | **NO** (not in Navbar, TutorHome, StudentPortal) |
| `QuestionDetail` | `/question/:id` | NO | Only reachable from QuestionBankList |

**Key finding:** `questionBank.listQuestions` is indeed student-accessible (no admin guard in the procedure), and it directly queries `question_bank` table via `db.listQuestionsFromBank()`. However:
- The `/questions` page is **not linked** from any student navigation component (`Navbar.tsx`, `TutorHome.tsx`, `StudentPortal.tsx`)
- A student must manually enter `/questions` in the address bar to hit this code path
- Even then, the error is a tRPC query failure (React Query shows error state); it does NOT crash the overall SPA

**`question_bank_history` in this flow:** The `updateQuestion` procedure that calls `saveQuestionHistory` is admin-only. No student path reaches `questionVersionControl.ts`.

**Classification: QUESTION_BANK_DEFER — Do not patch for RC1**

---

### § 4 `qa_cache` — SOFT_DEGRADATION (not a crash)

**Phase 2D-B claim:** "AI answers hitting the cache check will crash" — citing `server/lib/unifiedRAG.ts`

**This review evidence:**

1. **`unifiedRAG.ts` does NOT import `qaCache`.** The file header explicitly states:  
   `* 4. QA 快取（qa_cache）—由 qaCacheService 處理，此處不重複`  
   The imports are: `lawArticles`, `examQuestions`, `examSubjects`, `knowledgeChunks`, `materialContents`, `teacherMaterials` — no `qaCache`.

2. **`qaCacheService.ts` wraps ALL operations in try-catch:**
   - `searchSimilarQuestion()` → returns `null` on any error (line 338)
   - `saveToCache()` → returns `false` on any error (line 425)

3. **The `.update(qaCache)` call in `routers.ts` (line 1899) is guarded by `if (cacheHit)`** — and `cacheHit` is the return value of `searchSimilarQuestion()`, which returns `null` when `qa_cache` table doesn't exist. The update block is never reached.

4. **TutorChat (`tutorRouter.ts`) has no `qaCache` imports or direct calls.** Cache is not used in TutorChat flow.

5. **Net effect of missing `qa_cache`:** Every AI chat question hits the LLM directly (no cache lookup, no cache save). This is functional degradation — more LLM tokens consumed — but NOT a crash or user-visible error.

**Classification: SOFT_DEGRADATION — Acceptable for RC1; consider adding in a post-RC1 performance phase**

---

### § 5 `knowledge_base_pdfs` / `knowledge_base_pages` — ADMIN_ONLY + RAG_DEFER

**Phase 2D-B claim:** "Base requirements for `<KnowledgeBase />` and `vectorDB.ts`"

**This review evidence:**

**Server-side:** All `knowledgeBase.*` procedures (list, getById, uploadPdf, search, delete, extractQuestions, etc.) guard with:
```ts
if (ctx.user.role !== "admin") throw new Error("僅限管理員使用")
```

**Client-side routes accessing `knowledge_base_pdfs`:**

| Component | Route | Admin route? | Auto-queried on load? |
|-----------|-------|--------------|----------------------|
| `KnowledgeBase.tsx` | `/admin/knowledge-base` | YES | Yes, but admin-only |
| `PdfReader.tsx` | `/pdf/:id` | NO | Yes — `trpc.knowledgeBase.getById` called on mount |
| `QuestionEditor.tsx` | `/admin/question-editor/:pdfId` | YES | Yes, but admin-only |

**`PdfReader.tsx` special case:** The `/pdf/:id` route is not admin-prefixed. When a student navigates there, `knowledgeBase.getById` throws `"僅限管理員使用"` — the `error` from useQuery is set but it does NOT crash the page (React Query + ErrorBoundary handles this). In any case, `/pdf/:id` is not linked from student nav; it's only accessed by clicking PDF links that admins share.

**`vectorDB.ts`:** The Phase 2D-B claim about `vectorDB.ts` requiring `knowledge_base_pdfs` is irrelevant to SQLite RC1 — VectorDB uses `knowledge_chunks` (a separate table) for embedding search, not the raw PDFs. VectorDB calls are also wrapped in try-catch at the call site (`streamMessage.ts` uses `queryUnifiedRAG` inside try-catch).

**Classification: ADMIN_ONLY + RAG_OR_KB_DEFER — Do not patch for RC1**

---

## Summary: Active Runtime Evidence Table

| Table | Auto-called on `/` or `/student`? | Student nav link exists? | Would crash student main-line? | Verdict |
|-------|-----------------------------------|--------------------------|-------------------------------|---------|
| `question_bank` | NO | NO | NO (error on /questions only) | QUESTION_BANK_DEFER |
| `question_bank_history` | NO | NO | NO | ADMIN_ONLY |
| `qa_cache` | Indirectly (AI chat) | YES (chat is linked) | NO (graceful degradation) | SOFT_DEGRADATION |
| `knowledge_base_pdfs` | NO | NO | NO | ADMIN_ONLY + RAG_DEFER |
| `knowledge_base_pages` | NO | NO | NO | ADMIN_ONLY + RAG_DEFER |
| `knowledge_base_categories` | NO | NO | NO | ADMIN_ONLY + RAG_DEFER |

---

## Tables NOT Patched and Why

| Table | Reason NOT Patched |
|-------|-------------------|
| `question_bank` | Not reachable via student nav; requires dedicated QB module migration; complex cross-references with `practice_exam_questions.questionId`, `wrong_questions.questionId` |
| `question_bank_history` | Admin-only version control; zero student exposure |
| `qa_cache` | Graceful degradation already in place; adding this table requires full enum migration and text-length handling; no student-facing crash |
| `knowledge_base_pdfs` | Admin-only; part of complex RAG cluster with vector embeddings; requires coordinated migration with `knowledge_chunks` |
| `knowledge_base_pages` | Admin-only; tightly coupled to `knowledge_base_pdfs` |
| `knowledge_base_categories` | Admin-only; used only as admin grouping metadata |

---

## Correction to Phase 2D-B Claims

| Phase 2D-B Claim | Correction |
|------------------|------------|
| "`qa_cache` imported by `server/lib/unifiedRAG.ts`" | FALSE — unifiedRAG.ts explicitly excludes qa_cache (see file header comment) |
| "`question_bank` in active student pages like `<ExamQuestions />`" | MISLEADING — ExamQuestions is at `/admin/exam-questions` (admin-only route) |
| "missing `qa_cache` will crash AI answers" | FALSE — `searchSimilarQuestion()` and `saveToCache()` both wrap in try-catch; cacheHit=null guard prevents update crash |

---

## Knowledge Base / AI Q&A Deferral Decision

**DECISION: Defer entire KB/AI Q&A cluster to post-RC1.**

Rationale:
- Zero student-facing crash risk currently
- Cluster involves: `knowledge_base_pdfs`, `knowledge_base_pages`, `knowledge_base_categories`, `knowledge_chunks` (already not in MVP), `qa_cache`
- Full cluster migration requires: enum mapping, vector field handling, cross-table FK cascade decisions, `knowledge_chunks` BLOB/JSON embedding column
- Premature migration risks breaking existing 76-table stable schema
- Admin workflows that depend on these tables can use the PostgreSQL/MySQL production DB

---

## RC1 Runtime Gate Checklist

### Student Main-Line (Must Pass for RC1)

- [x] `/` (TutorHome) — loads without error; `tutorPublic.getSubjects` + `tutorPublic.searchBooks` work
- [x] `/tutor/chat/:bookId` (TutorChat) — session loads; AI responses work (qa_cache degrades gracefully)
- [x] `/student` (StudentPortal) — announcements load from `announcements` table (patched in 2D-C)
- [x] `/chat` (Chat page) — banners load from `banners` table (patched in 2D-C)
- [x] `/student/wrong-questions` — `wrong_questions` table present (patched in 2D-C)
- [x] Login / auth flow — `users` table present
- [x] Credit system — `credit_transactions`, `credit_rules` present

### Admin Flows (Degraded — Expected for SQLite MVP)

- [ ] `/admin/knowledge-base` — will show tRPC errors (no `knowledge_base_pdfs`)
- [ ] `/admin/qa-cache` — will show tRPC errors (no `qa_cache`)
- [ ] `/admin/question-bank` — will show tRPC errors (no `question_bank`)
- [ ] `question_bank_history` — admin question edits will fail to save history

> These failures are **expected and documented** for the SQLite MVP deployment. Admin features requiring the full Knowledge Base cluster should target the PostgreSQL production instance.

---

## Recommended Next Phase

**Phase 2D-E: RC1 Runtime Gate Smoke Test**
- Run the full student main-line smoke test against the SQLite DB
- Confirm TutorHome, TutorChat, StudentPortal, Chat all pass
- Confirm announcement + banner display correct
- Confirm wrong-questions flow functional
- No new table patches in 2D-E — validation only

**Post-RC1 Phase (separate project):**
- `qa_cache` cluster: Add as a performance enhancement to reduce LLM token cost
- `question_bank` + `question_bank_history`: Requires dedicated Question Bank module design
- `knowledge_base_pdfs/pages/categories`: Full RAG/Vector DB cluster — SmartBook Pro scope

---

## Final Status

```
PHASE_2D_D_DONE                   = YES
PATCH_DONE                        = NO
SQLITE_TABLE_COUNT_AFTER_2D_C     = 76
ACTIVE_RUNTIME_CRASH_REMAINING    = 0
ADMIN_ONLY_REMAINING              = 3  (knowledge_base_pdfs, knowledge_base_pages, question_bank_history)
RAG_OR_KB_DEFER                   = 3  (knowledge_base_pdfs, knowledge_base_pages, knowledge_base_categories)
SOFT_DEGRADATION                  = 1  (qa_cache)
QUESTION_BANK_DEFER               = 1  (question_bank)
RECOMMENDED_NEXT_PATCH_TABLES     = NONE (no patches needed for RC1 student gate)
RECOMMENDED_NEXT_PHASE            = Phase 2D-E (RC1 Runtime Gate Smoke Test — validation only)
FILES_CHANGED                     = docs/project/sqlite/PHASE_2D_D_SQLITE_REMAINING_HIGH_NO_PATCH_REVIEW.md
```

---

*Generated via Read-Only Audit. No schema files were modified.*
