# SQLite Timestamp Remaining Audit

> **Phase 1-C.9b — Audit Only / No Schema Changes**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **`drizzle/schema.sqlite.mvp.ts` was NOT modified.**

---

## Summary

| Item | Value |
|------|-------|
| Current tables | **66** |
| Current strftime defaults | **15** (5 Batch 2A + 10 Batch 2B-1) |
| Index definitions | **0** |
| Remaining TODO timestamp markers | **52** |
| Schema modified | **No** |
| Runtime modified | **No** |

---

## Remaining Timestamp Inventory

### Complete List (52 items)

| # | Line | Table | Variable | Column | Type | Has `mode: "timestamp"` | Has `(was CURRENT_TIMESTAMP)` |
|---|------|-------|----------|--------|------|------------------------|-------------------------------|
| 1 | 28 | users | `users` | `updatedAt` | updatedAt | ✅ Yes | No |
| 2 | 29 | users | `users` | `lastSignedIn` | other | ✅ Yes | No |
| 3 | 65 | conversations | `conversations` | `updatedAt` | updatedAt | ✅ Yes | No |
| 4 | 66 | conversations | `conversations` | `lastMessageAt` | other | ✅ Yes | No |
| 5 | 104 | conversation_files | `conversationFiles` | `uploadedAt` | other (createdAt-equiv) | ✅ Yes | No |
| 6 | 112 | conversation_tags | `conversationTags` | `createdAt` | createdAt | ✅ Yes | No |
| 7 | 121 | tags | `tags` | `createdAt` | createdAt | ✅ Yes | No |
| 8 | 130 | system_settings | `systemSettings` | `createdAt` | createdAt | ✅ Yes | No |
| 9 | 131 | system_settings | `systemSettings` | `updatedAt` | updatedAt | ✅ Yes | No |
| 10 | 143 | credit_transactions | `creditTransactions` | `createdAt` | createdAt | ✅ Yes | No |
| 11 | 156 | credit_rules | `creditRules` | `updatedAt` | updatedAt | ✅ Yes | No |
| 12 | 157 | credit_rules | `creditRules` | `createdAt` | createdAt | ✅ Yes | No |
| 13 | 171 | user_usage_stats | `userUsageStats` | `createdAt` | createdAt | ✅ Yes | No |
| 14 | 172 | user_usage_stats | `userUsageStats` | `updatedAt` | updatedAt | ✅ Yes | No |
| 15 | 189 | pdf_categories | `pdfCategories` | `createdAt` | createdAt | ✅ Yes | No |
| 16 | 190 | pdf_categories | `pdfCategories` | `updatedAt` | updatedAt | ✅ Yes | No |
| 17 | 202 | smart_book_categories | `smartBookCategories` | `updatedAt` | updatedAt | ✅ Yes | No |
| 18 | 237 | smart_books | `smartBooks` | `updatedAt` | updatedAt | ✅ Yes | No |
| 19 | 256 | smart_book_chapters | `smartBookChapters` | `updatedAt` | updatedAt | ✅ Yes | No |
| 20 | 283 | smart_book_progress | `smartBookProgress` | `updatedAt` | updatedAt | ✅ Yes | No |
| 21 | 309 | smart_book_credits | `smartBookCredits` | `updatedAt` | updatedAt | ✅ Yes | No |
| 22 | 337 | smart_book_settings | `smartBookSettings` | `updatedAt` | updatedAt | ✅ Yes | No |
| 23 | 357 | smart_book_unit_qa | `smartBookUnitQA` | `updatedAt` | updatedAt | ✅ Yes | No |
| 24 | 368 | smart_book_unit_qa_answers | `smartBookUnitQAAnswers` | `answeredAt` | other (createdAt-equiv) | ❌ bare int | ✅ Yes |
| 25 | 376 | smart_book_learning_sessions | `smartBookLearningSessions` | `startedAt` | other (createdAt-equiv) | ❌ bare int | ✅ Yes |
| 26 | 377 | smart_book_learning_sessions | `smartBookLearningSessions` | `lastActiveAt` | other (updatedAt-equiv) | ❌ bare int | ✅ Yes |
| 27 | 390 | smart_book_chapter_daily_verifications | `smartBookChapterDailyVerifications` | `verifiedAt` | other (createdAt-equiv) | ❌ bare int | ✅ Yes |
| 28 | 401 | smart_book_chapter_completions | `smartBookChapterCompletions` | `completedAt` | other (createdAt-equiv) | ❌ bare int | ✅ Yes |
| 29 | 422 | smart_book_saved_messages | `smartBookSavedMessages` | `updatedAt` | updatedAt | ❌ bare int | ✅ Yes |
| 30 | 455 | lesson_points | `lessonPoints` | `updatedAt` | updatedAt | ✅ Yes | No |
| 31 | 482 | smart_book_review_questions | `smartBookReviewQuestions` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 32 | 499 | smart_book_wrong_answers | `smartBookWrongAnswers` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 33 | 511 | smart_book_quiz_sessions | `smartBookQuizSessions` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 34 | 522 | smart_book_question_shown | `smartBookQuestionShown` | `updatedAt` | updatedAt | ❌ bare int | ✅ Yes |
| 35 | 531 | smart_book_qa_viewed | `smartBookQAViewed` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 36 | 554 | smart_book_verifications | `smartBookVerifications` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 37 | 555 | smart_book_verifications | `smartBookVerifications` | `updatedAt` | updatedAt | ✅ Yes | No |
| 38 | 618 | tutor_subject_exam_sources | `tutorSubjectExamSources` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 39 | 678 | exam_categories | `examCategories` | `createdAt` | createdAt | ✅ Yes | No |
| 40 | 689 | exam_subjects | `examSubjects` | `createdAt` | createdAt | ✅ Yes | No |
| 41 | 711 | exam_questions | `examQuestions` | `updatedAt` | updatedAt | ✅ Yes | No |
| 42 | 747 | real_exam_questions | `realExamQuestions` | `createdAt` | createdAt | ✅ Yes | No |
| 43 | 748 | real_exam_questions | `realExamQuestions` | `updatedAt` | updatedAt | ✅ Yes | No |
| 44 | 780 | ai_question_sources | `aiQuestionSources` | `createdAt` | createdAt | ✅ Yes | No |
| 45 | 781 | ai_question_sources | `aiQuestionSources` | `updatedAt` | updatedAt | ✅ Yes | No |
| 46 | 808 | ai_generated_exams | `aiGeneratedExams` | `updatedAt` | updatedAt | ✅ Yes | No |
| 47 | 827 | ai_generated_questions | `aiGeneratedQuestions` | `createdAt` | createdAt | ✅ Yes | No |
| 48 | 828 | ai_generated_questions | `aiGeneratedQuestions` | `updatedAt` | updatedAt | ✅ Yes | No |
| 49 | 915 | smart_book_category_exam_sources | `smartBookCategoryExamSources` | `createdAt` | createdAt | ❌ bare int | ✅ Yes |
| 50 | 1006 | saved_qa | `savedQa` | `createdAt` | createdAt | ✅ Yes | No |
| 51 | 1022 | learning_materials | `learningMaterials` | `createdAt` | createdAt | ✅ Yes | No |
| 52 | 1023 | learning_materials | `learningMaterials` | `updatedAt` | updatedAt | ✅ Yes | No |

---

## Column Type Breakdown

| Type | Count |
|------|-------|
| `createdAt` / `created_at` | **21** |
| `updatedAt` / `updated_at` | **22** |
| Other timestamps (`uploadedAt`, `lastSignedIn`, `lastMessageAt`, `answeredAt`, `startedAt`, `lastActiveAt`, `verifiedAt`, `completedAt`) | **9** |
| **Total** | **52** |

### Convention Analysis

| Convention | Count | Description |
|-----------|-------|-------------|
| Convention A — Unix seconds, has `{ mode: "timestamp" }` | **37** | Already have mode; need decision on default |
| Convention A — Unix seconds, bare `integer()` (was `CURRENT_TIMESTAMP`) | **15** | Need both `{ mode: "timestamp" }` and default decision |

### Default Strategy Analysis

| Column Role | Should add `DEFAULT(strftime('%s','now'))` | Should remain application-side | Count |
|-------------|---------------------------------------------|-------------------------------|-------|
| `createdAt` (write-once) | ✅ Yes | — | **17** |
| `uploadedAt` (write-once equivalent) | ✅ Yes | — | **1** |
| `answeredAt` (write-once equivalent) | ✅ Yes | — | **1** |
| `startedAt` (write-once equivalent) | ✅ Yes | — | **1** |
| `verifiedAt` (write-once equivalent) | ✅ Yes | — | **1** |
| `completedAt` (write-once equivalent) | ✅ Yes | — | **1** |
| `updatedAt` (app-side, set on update) | — | ✅ Application-side | **22** |
| `lastSignedIn` (conditional, app-side) | — | ✅ Application-side | **1** |
| `lastMessageAt` (conditional, app-side) | — | ✅ Application-side | **1** |
| `lastActiveAt` (conditional, app-side) | — | ✅ Application-side | **1** |
| **Subtotal: should add default** | | | **22** |
| **Subtotal: should remain app-side** | | | **25** |
| **Subtotal: borderline** (see notes below) | | | **5** |

> **Borderline items (5):**
> - `lastActiveAt` (L377): Has `CURRENT_TIMESTAMP` in MySQL source, suggesting a default. But semantically it's updated on every activity, so app-side is more correct. **Recommend: app-side.**
> - `completedAt` (L401): Write-once, but set when an action completes (not on row creation). **Recommend: app-side — set explicitly on completion.**
> - `answeredAt` (L368): Write-once, set when answer is submitted. **Recommend: default — acts like createdAt for the answer row.**
> - `verifiedAt` (L390): Write-once, set when verification occurs. **Recommend: default — acts like createdAt for the verification row.**
> - `startedAt` (L376): Write-once, set when session starts. **Recommend: default — acts like createdAt for the session row.**

**Final recommendation after borderline resolution:**

| Action | Count |
|--------|-------|
| Add `DEFAULT(strftime('%s','now'))` | **22** (17 createdAt + 1 uploadedAt + 1 answeredAt + 1 startedAt + 1 verifiedAt + 1 completedAt) |
| Remain application-side (comment cleanup only) | **25** (22 updatedAt + 1 lastSignedIn + 1 lastMessageAt + 1 lastActiveAt) |
| Need `{ mode: "timestamp" }` added (bare int) | **15** of the 52 |
| **Total** | **52** ¹ |

> ¹ Note: 5 items appear in both "add default" and "need mode" groups — they need both changes.

---

## Priority Classification

### A. Runtime Critical (26 items)

Tables actively used by the 7 core Lite routers (`smartBookRouter`, `smartBookLearningRouter`, `lessonPointsRouter`, `tutorRouter`, `videoCourseRouter`, `examSetRouter`, `userManagement`).

| # | Line | Table | Column | Role | Should Add Default? | Needs Mode Fix? | Priority |
|---|------|-------|--------|------|---------------------|-----------------|----------|
| 1 | 28 | users | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 2 | 29 | users | `lastSignedIn` | other | ❌ App-side | No | P1 |
| 3 | 65 | conversations | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 4 | 66 | conversations | `lastMessageAt` | other | ❌ App-side | No | P1 |
| 5 | 143 | credit_transactions | `createdAt` | createdAt | ✅ Add default | No | **P0** |
| 6 | 171 | user_usage_stats | `createdAt` | createdAt | ✅ Add default | No | **P0** |
| 7 | 172 | user_usage_stats | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 8 | 202 | smart_book_categories | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 9 | 237 | smart_books | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 10 | 256 | smart_book_chapters | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 11 | 283 | smart_book_progress | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 12 | 309 | smart_book_credits | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 13 | 337 | smart_book_settings | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 14 | 357 | smart_book_unit_qa | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 15 | 368 | smart_book_unit_qa_answers | `answeredAt` | other (write-once) | ✅ Add default | ✅ Yes | **P0** |
| 16 | 376 | smart_book_learning_sessions | `startedAt` | other (write-once) | ✅ Add default | ✅ Yes | **P0** |
| 17 | 377 | smart_book_learning_sessions | `lastActiveAt` | other (updatedAt-equiv) | ❌ App-side | ✅ Yes (mode only) | P1 |
| 18 | 390 | smart_book_chapter_daily_verifications | `verifiedAt` | other (write-once) | ✅ Add default | ✅ Yes | **P0** |
| 19 | 401 | smart_book_chapter_completions | `completedAt` | other (write-once) | ✅ Add default | ✅ Yes | **P0** |
| 20 | 422 | smart_book_saved_messages | `updatedAt` | updatedAt | ❌ App-side | ✅ Yes (mode only) | P1 |
| 21 | 455 | lesson_points | `updatedAt` | updatedAt | ❌ App-side | No | P1 |
| 22 | 482 | smart_book_review_questions | `createdAt` | createdAt | ✅ Add default | ✅ Yes | **P0** |
| 23 | 499 | smart_book_wrong_answers | `createdAt` | createdAt | ✅ Add default | ✅ Yes | **P0** |
| 24 | 531 | smart_book_qa_viewed | `createdAt` | createdAt | ✅ Add default | ✅ Yes | **P0** |
| 25 | 522 | smart_book_question_shown | `updatedAt` | updatedAt | ❌ App-side | ✅ Yes (mode only) | P1 |
| 26 | 1006 | saved_qa | `createdAt` | createdAt | ✅ Add default | No | **P0** |

### B. Runtime Optional (16 items)

Tables referenced by routers, but not core Lite runtime paths.

| # | Line | Table | Column | Role | Should Add Default? | Needs Mode Fix? | Priority |
|---|------|-------|--------|------|---------------------|-----------------|----------|
| 1 | 104 | conversation_files | `uploadedAt` | other (write-once) | ✅ Add default | No | P1 |
| 2 | 511 | smart_book_quiz_sessions | `createdAt` | createdAt | ✅ Add default | ✅ Yes | P1 |
| 3 | 554 | smart_book_verifications | `createdAt` | createdAt | ✅ Add default | ✅ Yes | P1 |
| 4 | 555 | smart_book_verifications | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 5 | 618 | tutor_subject_exam_sources | `createdAt` | createdAt | ✅ Add default | ✅ Yes | P1 |
| 6 | 678 | exam_categories | `createdAt` | createdAt | ✅ Add default | No | P1 |
| 7 | 689 | exam_subjects | `createdAt` | createdAt | ✅ Add default | No | P1 |
| 8 | 711 | exam_questions | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 9 | 747 | real_exam_questions | `createdAt` | createdAt | ✅ Add default | No | P1 |
| 10 | 748 | real_exam_questions | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 11 | 780 | ai_question_sources | `createdAt` | createdAt | ✅ Add default | No | P1 |
| 12 | 781 | ai_question_sources | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 13 | 808 | ai_generated_exams | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 14 | 827 | ai_generated_questions | `createdAt` | createdAt | ✅ Add default | No | P1 |
| 15 | 828 | ai_generated_questions | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 16 | 915 | smart_book_category_exam_sources | `createdAt` | createdAt | ✅ Add default | ✅ Yes | P1 |

### C. Admin Only (4 items)

Tables used only by admin/management routers or feature toggle flows.

| # | Line | Table | Column | Role | Should Add Default? | Needs Mode Fix? | Priority |
|---|------|-------|--------|------|---------------------|-----------------|----------|
| 1 | 130 | system_settings | `createdAt` | createdAt | ✅ Add default | No | P2 |
| 2 | 131 | system_settings | `updatedAt` | updatedAt | ❌ App-side | No | P2 |
| 3 | 189 | pdf_categories | `createdAt` | createdAt | ✅ Add default | No | P2 |
| 4 | 190 | pdf_categories | `updatedAt` | updatedAt | ❌ App-side | No | P2 |

### D. Dormant / Defer (6 items)

Tables not referenced by any currently mounted Lite router.

| # | Line | Table | Column | Role | Should Add Default? | Needs Mode Fix? | Priority |
|---|------|-------|--------|------|---------------------|-----------------|----------|
| 1 | 112 | conversation_tags | `createdAt` | createdAt | ✅ Add default | No | Defer |
| 2 | 121 | tags | `createdAt` | createdAt | ✅ Add default | No | Defer |
| 3 | 156 | credit_rules | `updatedAt` | updatedAt | ❌ App-side | No | Defer |
| 4 | 157 | credit_rules | `createdAt` | createdAt | ✅ Add default | No | Defer |
| 5 | 1022 | learning_materials | `createdAt` | createdAt | ✅ Add default | No | Defer |
| 6 | 1023 | learning_materials | `updatedAt` | updatedAt | ❌ App-side | No | Defer |

---

## Priority Summary Table

| Table | Column | Role | Runtime Used? | Priority | Recommendation |
|-------|--------|------|---------------|----------|----------------|
| users | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| users | lastSignedIn | other | ✅ Core | P1 | App-side — comment cleanup only |
| conversations | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| conversations | lastMessageAt | other | ✅ Core | P1 | App-side — comment cleanup only |
| credit_transactions | createdAt | createdAt | ✅ Core | **P0** | Add `DEFAULT(strftime('%s','now'))` |
| user_usage_stats | createdAt | createdAt | ✅ Core | **P0** | Add `DEFAULT(strftime('%s','now'))` |
| user_usage_stats | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_categories | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_books | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_chapters | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_progress | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_credits | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_settings | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_unit_qa | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_unit_qa_answers | answeredAt | write-once | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_learning_sessions | startedAt | write-once | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_learning_sessions | lastActiveAt | updatedAt-equiv | ✅ Core | P1 | Add mode only — app-side value |
| smart_book_chapter_daily_verifications | verifiedAt | write-once | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_chapter_completions | completedAt | write-once | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_saved_messages | updatedAt | updatedAt | ✅ Core | P1 | Add mode only — app-side value |
| lesson_points | updatedAt | updatedAt | ✅ Core | P1 | App-side — comment cleanup only |
| smart_book_review_questions | createdAt | createdAt | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_wrong_answers | createdAt | createdAt | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_qa_viewed | createdAt | createdAt | ✅ Core | **P0** | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_question_shown | updatedAt | updatedAt | ✅ Core | P1 | Add mode only — app-side value |
| saved_qa | createdAt | createdAt | ✅ Core | **P0** | Add `DEFAULT(strftime('%s','now'))` |
| conversation_files | uploadedAt | write-once | Optional | P1 | Add `DEFAULT(strftime('%s','now'))` |
| smart_book_quiz_sessions | createdAt | createdAt | Optional | P1 | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_verifications | createdAt | createdAt | Optional | P1 | Add mode + `DEFAULT(strftime('%s','now'))` |
| smart_book_verifications | updatedAt | updatedAt | Optional | P2 | App-side — comment cleanup only |
| tutor_subject_exam_sources | createdAt | createdAt | Optional | P1 | Add mode + `DEFAULT(strftime('%s','now'))` |
| exam_categories | createdAt | createdAt | Optional | P1 | Add `DEFAULT(strftime('%s','now'))` |
| exam_subjects | createdAt | createdAt | Optional | P1 | Add `DEFAULT(strftime('%s','now'))` |
| exam_questions | updatedAt | updatedAt | Optional | P2 | App-side — comment cleanup only |
| real_exam_questions | createdAt | createdAt | Optional | P1 | Add `DEFAULT(strftime('%s','now'))` |
| real_exam_questions | updatedAt | updatedAt | Optional | P2 | App-side — comment cleanup only |
| ai_question_sources | createdAt | createdAt | Optional | P1 | Add `DEFAULT(strftime('%s','now'))` |
| ai_question_sources | updatedAt | updatedAt | Optional | P2 | App-side — comment cleanup only |
| ai_generated_exams | updatedAt | updatedAt | Optional | P2 | App-side — comment cleanup only |
| ai_generated_questions | createdAt | createdAt | Optional | P1 | Add `DEFAULT(strftime('%s','now'))` |
| ai_generated_questions | updatedAt | updatedAt | Optional | P2 | App-side — comment cleanup only |
| smart_book_category_exam_sources | createdAt | createdAt | Optional | P1 | Add mode + `DEFAULT(strftime('%s','now'))` |
| system_settings | createdAt | createdAt | Admin | P2 | Add `DEFAULT(strftime('%s','now'))` |
| system_settings | updatedAt | updatedAt | Admin | P2 | App-side — comment cleanup only |
| pdf_categories | createdAt | createdAt | Admin | P2 | Add `DEFAULT(strftime('%s','now'))` |
| pdf_categories | updatedAt | updatedAt | Admin | P2 | App-side — comment cleanup only |
| conversation_tags | createdAt | createdAt | Dormant | Defer | Add `DEFAULT(strftime('%s','now'))` when activated |
| tags | createdAt | createdAt | Dormant | Defer | Add `DEFAULT(strftime('%s','now'))` when activated |
| credit_rules | updatedAt | updatedAt | Dormant | Defer | App-side — defer |
| credit_rules | createdAt | createdAt | Dormant | Defer | Add `DEFAULT(strftime('%s','now'))` when activated |
| learning_materials | createdAt | createdAt | Dormant | Defer | Add `DEFAULT(strftime('%s','now'))` when activated |
| learning_materials | updatedAt | updatedAt | Dormant | Defer | App-side — defer |

---

## Runtime Critical Items (P0)

**10 columns** require `DEFAULT(strftime('%s','now'))` before Phase 1-E:

| # | Table | Column | Needs Mode Fix? | Router |
|---|-------|--------|-----------------|--------|
| 1 | credit_transactions | `createdAt` | No (has mode) | smartBookLearningRouter |
| 2 | user_usage_stats | `createdAt` | No (has mode) | smartBookRouter |
| 3 | smart_book_unit_qa_answers | `answeredAt` | ✅ Yes (bare int) | smartBookLearningRouter |
| 4 | smart_book_learning_sessions | `startedAt` | ✅ Yes (bare int) | smartBookLearningRouter |
| 5 | smart_book_chapter_daily_verifications | `verifiedAt` | ✅ Yes (bare int) | smartBookRouter, smartBookLearningRouter |
| 6 | smart_book_chapter_completions | `completedAt` | ✅ Yes (bare int) | smartBookLearningRouter |
| 7 | smart_book_review_questions | `createdAt` | ✅ Yes (bare int) | smartBookRouter, smartBookLearningRouter, tutorRouter |
| 8 | smart_book_wrong_answers | `createdAt` | ✅ Yes (bare int) | smartBookRouter |
| 9 | smart_book_qa_viewed | `createdAt` | ✅ Yes (bare int) | smartBookRouter |
| 10 | saved_qa | `createdAt` | No (has mode) | videoCourseRouter |

### P0 Change Types

| Change Type | Count |
|-------------|-------|
| Add mode + default (Diff Type B) | 7 |
| Add default only (Diff Type A) | 3 |
| **Total P0** | **10** |

---

## Defer Items

6 columns in 4 tables — no router references found in core Lite:

| Table | Column | Reason |
|-------|--------|--------|
| conversation_tags | `createdAt` | No router references |
| tags | `createdAt` | Only in `faqs.ts`, `teacherQuestions.ts`, `studentQuestions.ts` (non-Lite) |
| credit_rules | `createdAt`, `updatedAt` | No router references |
| learning_materials | `createdAt`, `updatedAt` | Only in `convertChineseRouter`, `tutorRouter`, `examSetRouter` (peripheral) |

---

## P1 Items Requiring `{ mode: "timestamp" }` Fix (No Default)

3 bare `integer()` columns that are `updatedAt`-equivalent — need mode fix but NO default:

| # | Table | Column | Line |
|---|-------|--------|------|
| 1 | smart_book_learning_sessions | `lastActiveAt` | 377 |
| 2 | smart_book_saved_messages | `updatedAt` | 422 |
| 3 | smart_book_question_shown | `updatedAt` | 522 |

These should get `{ mode: "timestamp" }` added but remain app-side (no `DEFAULT`).

---

## Recommendation

### Should Batch 2B-2 proceed?

**Yes, but with a reduced scope.**

Batch 2B-2 should target **P0 only** (10 columns) to unblock Phase 1-E. This is consistent with the incremental batching strategy from Batches 2A and 2B-1.

### Suggested Batch 2B-2 Scope (10 columns)

| # | Table | Column | Change Type |
|---|-------|--------|-------------|
| 1 | credit_transactions | `createdAt` | Diff Type A — add default only |
| 2 | user_usage_stats | `createdAt` | Diff Type A — add default only |
| 3 | saved_qa | `createdAt` | Diff Type A — add default only |
| 4 | smart_book_unit_qa_answers | `answeredAt` | Diff Type B — add mode + default |
| 5 | smart_book_learning_sessions | `startedAt` | Diff Type B — add mode + default |
| 6 | smart_book_chapter_daily_verifications | `verifiedAt` | Diff Type B — add mode + default |
| 7 | smart_book_chapter_completions | `completedAt` | Diff Type B — add mode + default |
| 8 | smart_book_review_questions | `createdAt` | Diff Type B — add mode + default |
| 9 | smart_book_wrong_answers | `createdAt` | Diff Type B — add mode + default |
| 10 | smart_book_qa_viewed | `createdAt` | Diff Type B — add mode + default |

### Expected After Batch 2B-2

```
grep -c "strftime('%s','now')" schema.sqlite.mvp.ts  → 25  (15 + 10)
grep -c "TODO SQLite timestamp" schema.sqlite.mvp.ts → 42  (52 − 10)
```

### Remaining After Batch 2B-2

| Category | Remaining | Action |
|----------|-----------|--------|
| P1 createdAt defaults | 12 | Batch 2B-3 |
| P1 mode-only fixes | 3 | Batch 2B-3 |
| P1/P2 comment cleanup (updatedAt/app-side) | 21 | Batch 2C (comment-only pass) |
| Defer | 6 | Deferred |
| **Total remaining** | **42** | |

---

## Verification Checklist

```
grep -c "sqliteTable(" schema.sqlite.mvp.ts          → 66   ✅ (unchanged)
grep -c "strftime('%s','now')" schema.sqlite.mvp.ts  → 15   ✅ (unchanged — audit only)
grep -c "index(" schema.sqlite.mvp.ts                →  0   ✅ (unchanged)
grep -c "TODO SQLite timestamp" schema.sqlite.mvp.ts → 52   ✅ (unchanged — audit only)
```

---

*Audit Only. `drizzle/schema.sqlite.mvp.ts` was NOT modified. No runtime changes.*
