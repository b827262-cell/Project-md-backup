# Phase 2D-B: SQLite Schema Remaining HIGH Gap Review

## Executive Summary
This report analyzes the remaining gap in the MVP SQLite schema following the successful execution of Phase 2D-A. The read-only audit confirmed that out of the original 110 missing tables, 104 remain. Of these, 10 are classified as HIGH priority due to their active integration in the server routers and client pages. Several of these remaining tables are actively fetched on primary entry points (like the Student Portal and the AI Chat page) and will cause immediate runtime crashes if not patched.

## Phase 2D-A Result Recap
- **Tables Migrated:** 6 (`practice_exams`, `practice_exam_questions`, `practice_records`, `practice_answers`, `exam_purchases`, `user_preferences`).
- **SQLite Table Count After 2D-A:** Increased from 66 to 72.
- **Build Status:** PASS. The practice exam active routing crashes were resolved successfully.
- **DB Leftovers:** 0 (all test artifacts cleaned up).

## Current SQLite Table Count
- **Total MySQL Tables:** 176
- **Current SQLite Tables:** 72
- **Missing Tables:** 104
- **Remaining HIGH Missing:** 10
- **Remaining MEDIUM Missing:** 35
- **Remaining LOW Missing:** 59

## Remaining HIGH Missing Tables (10)
1. `question_bank`
2. `question_bank_history`
3. `announcements`
4. `announcement_reads`
5. `qa_cache`
6. `banners`
7. `knowledge_base_pdfs`
8. `knowledge_base_pages`
9. `knowledge_base_categories`
10. `wrong_questions`

## Remaining HIGH Table Evidence & Categorization

### ACTIVE_RUNTIME_CRASH Candidates
These tables are explicitly tied to active routes, including main entry pages, and will crash upon mounting or core workflow execution:
- **`announcements` & `announcement_reads`**: 
  - **Evidence:** Fetched by `trpc.announcement.getAnnouncements` inside `<AnnouncementList />`, which is directly mounted on `<StudentPortal />` (the main student homepage). Missing these will crash the portal.
- **`banners`**:
  - **Evidence:** Fetched by `<TextBannerCarousel />`, which is directly mounted in `<Chat />` (the core AI tutor page). Missing this will crash the primary chat interface.
- **`wrong_questions`**:
  - **Evidence:** Sourced by `<WrongQuestions />` and `<QuizWrongQuestions />` pages. Accessing the wrong question review feature will crash.
- **`question_bank`**:
  - **Evidence:** Deeply wired into `server/routers.ts` and active student pages like `<ExamQuestions />` and `<KnowledgeBase />`.
- **`qa_cache`**:
  - **Evidence:** Imported actively by `server/lib/unifiedRAG.ts` and core question answering services. AI answers hitting the cache check will crash.
- **`knowledge_base_pdfs` & `knowledge_base_pages`**:
  - **Evidence:** Base requirements for the Knowledge Base UI (`<KnowledgeBase />`) and vector database interactions (`vectorDB.ts`).

### ADMIN_ONLY / DEFER Candidates
These tables either only affect admin workflows or can be safely deferred to a later patch cluster without breaking student-facing functionality.
- **`question_bank_history`**: 
  - **Evidence:** Used exclusively by `server/questionVersionControl.ts`. Admin-only version tracking.
- **`knowledge_base_categories`**:
  - **Evidence:** Primarily an admin grouping mechanic (`<AdminPdfCategories />` or backend tests). Can be deferred alongside the rest of the KB block.

## Recommended Phase 2D-C Patch Batch
Instead of patching all 10 remaining tables at once, we recommend grouping the immediate UI/Layout crashers and standalone tables to minimize risk and schema merge conflicts. 

**Target Batch for Phase 2D-C (4 Tables):**
1. `announcements`
2. `announcement_reads`
3. `banners`
4. `wrong_questions`

**Why not patch all remaining tables?**
The remaining 6 tables (`question_bank`, `question_bank_history`, `qa_cache`, `knowledge_base_pdfs`, `knowledge_base_pages`, `knowledge_base_categories`) represent a massive architectural cluster (Knowledge Base & Q&A). They contain heavy cross-references, numerous enum types, and high-complexity vector database interactions. Patching them alongside the simpler UI components (like banners) increases the risk of regressions. They should be isolated into a dedicated Phase 2D-D.

## Risk Notes
- `announcements` and `banners` contain boolean flags and simple enums. These must be cleanly mapped to SQLite `integer(mode: 'boolean')` and `text` to prevent tRPC Zod schema mismatches on the frontend.
- Until the Phase 2D-D Knowledge Base cluster is patched, navigating to the Question Bank or Knowledge Base will continue to throw 500 errors.

---
*Generated via Read-Only Audit.*
