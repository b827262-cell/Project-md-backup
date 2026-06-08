# SQLite Schema Hardening Plan

> **Phase 1-C.8 — Design Only / No Runtime Changes**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Input: `SQLITE_RUNTIME_WIRING_DESIGN.md` · `drizzle/schema.sqlite.mvp.ts` (66 tables)
> **No schema / db.ts / package / migration / SQLite DB changes were made in this phase.**

---

## Executive Summary

The 66-table draft schema requires the following hardening before Phase 1-E wiring:

| Area | Current State | Required Action | Priority |
|------|---------------|-----------------|----------|
| **Indexes** | 0 indexes defined | Add 15 Must-Add + 14 High-priority | **Must do before Phase 1-E** |
| **Timestamp defaults** | 67 `TODO` markers, no SQL defaults | Add `DEFAULT (unixepoch())` to `created_at` columns | **Must do before Phase 1-E** |
| **Enum validation** | 47 text columns, no enforcement | Zod at API boundary (already via tRPC); CHECK constraints in Phase 1-G | Phase 1-G (deferred) |
| **Compile coverage** | 66 tables cover 7 core Lite routers | 30 additional stub tables needed for full server compile when remaining routers are migrated | Phase 1-E (per-router) |

**Recommendation: Phase 1-E can begin once indexes and timestamp defaults are applied.**

---

## Index Plan

### Design Pattern

SQLite index syntax for the schema file:
```typescript
// In schema.sqlite.mvp.ts, after table definition:
import { index } from "drizzle-orm/sqlite-core";

export const conversations = sqliteTable("conversations", {
  ...columns...
}, (table) => [
  index("idx_conversations_userId").on(table.userId),
  index("idx_conversations_lastMessageAt").on(table.lastMessageAt),
]);
```

### Must Add Indexes (15 tables — required before Phase 1-E wiring)

| # | Table | Index Name | Column(s) | Reason |
|---|-------|------------|-----------|--------|
| 1 | `conversations` | `idx_conversations_userId` | `userId` | Every conversation list page; top-N query per user |
| 2 | `conversations` | `idx_conversations_lastMessageAt` | `lastMessageAt` | Timeline sort on every list fetch |
| 3 | `messages` | `idx_messages_conversationId` | `conversationId` | Full chat thread load on every session open |
| 4 | `users` | `idx_users_openId` | `openId` | Auth lookup on every single API request |
| 5 | `users` | `idx_users_email` | `email` | Login by email |
| 6 | `smart_books` | `idx_smart_books_public_status` | `isPublic, processingStatus` | Book catalog pages filter on both |
| 7 | `smart_book_chapters` | `idx_sbc_bookId` | `bookId` | Chapter list always filters by bookId |
| 8 | `smart_book_conversations` | `idx_sbconv_bookId_userId` | `bookId, userId` | Per-user per-book chat history |
| 9 | `smart_book_progress` | `idx_sbp_bookId_userId` | `bookId, userId` | Progress read on every chapter navigation |
| 10 | `smart_book_review_questions` | `idx_sbrq_bookId_chapterId` | `bookId, chapterId` | Quiz question fetch per chapter |
| 11 | `smart_book_wrong_answers` | `idx_sbwa_userId_bookId` | `userId, bookId` | Error book fetch per user per book |
| 12 | `lesson_points` | `idx_lp_bookId_chapterId` | `bookId, chapterId` | Guided lesson point fetch per chapter |
| 13 | `lesson_progress` | `idx_lprog_userId_chapterId` | `userId, chapterId` | Per-user lesson completion check |
| 14 | `tutor_chat_sessions` | `idx_tcs_userId`, `idx_tcs_smartBookId` | `userId`; `smartBookId` | Session list per user; session list per book |
| 15 | `tutor_chat_messages` | `idx_tcm_sessionId` | `sessionId` | Full message thread load per session |

### High Priority Indexes (14 — add before production launch)

| Table | Index Name | Column(s) | Reason |
|-------|------------|-----------|--------|
| `credit_transactions` | `idx_ct_userId` | `userId` | Transaction history per user |
| `smart_book_credits` | `idx_sbcred_bookId_userId` | `bookId, userId` | Credit balance lookup (hot path) |
| `user_usage_stats` | `idx_uus_userId_date` | `userId, date` | Daily stats lookup |
| `book_suggestion_cache` | `idx_bsc_bookId` | `bookId` | Suggestion fetch per book |
| `smart_book_question_shown` | `idx_sbqs_userId_chapterId` | `userId, chapterId` | Quiz dedup check |
| `smart_book_qa_viewed` | `idx_sbqav_userId_bookId` | `userId, bookId` | QA view dedup (one-time deduction) |
| `smart_book_chapter_daily_verifications` | `idx_sbcdv_bookId_userId_date` | `bookId, userId, verifiedDate` | Daily gate check on chapter switch |
| `exam_sets` | `idx_es_smartBookId_published` | `smartBookId, isPublished` | Exam set list per book |
| `exam_set_questions` | `idx_esq_examSetId` | `examSetId` | Question list per exam set |
| `video_units` | `idx_vu_courseId` | `courseId` | Unit list per video course |
| `video_progress` | `idx_vp_userId_unitId` | `userId, unitId` | Video progress lookup |
| `practice_wrong_book` | `idx_pwb_userId_sourceType` | `userId, sourceType` | Wrong book list per type |
| `system_settings` | `idx_ss_key` | `key` | Setting lookup by key (unique) |
| `page_text_cache` | `idx_ptc_bookId_page` | `bookId, page` | Page text cache hit |

### Medium / Low Priority Indexes (defer to post-launch)

| Table | Column(s) | Priority |
|-------|-----------|----------|
| `smart_book_verifications` | `bookId, userId` | Medium |
| `smart_book_chapter_completions` | `bookId, userId` | Medium |
| `smart_book_learning_sessions` | `bookId, userId` | Medium |
| `smart_book_saved_messages` | `userId, bookId` | Medium |
| `smart_book_unit_qa` | `bookId, chapterId` | Medium |
| `real_exam_questions` | `sourceId, year, subject` | Low |
| `ai_generated_questions` | `examId` | Low |
| `exam_wrong_book` | `userId, questionId` | Low |

---

## Timestamp Plan

Two storage conventions coexist in the draft schema. Both are valid; each must be used consistently per table.

### Convention A — Unix Seconds (`integer("col", { mode: "timestamp" })`)

Used for columns that originated from MySQL `timestamp({ mode: 'string' })`. Drizzle ORM stores as Unix epoch seconds, returns as JavaScript `Date`. Application code must pass `new Date()` (Drizzle converts automatically) or `Math.floor(Date.now() / 1000)`.

**SQL default to add**: `DEFAULT (unixepoch())` on `created_at` columns (write-once, auto-set).

### Convention B — Unix Milliseconds (plain `integer`, no mode)

Used for columns that originated from MySQL `bigint({ mode: "number" })`. Stored as `Date.now()` (milliseconds). Drizzle returns as plain JavaScript number. Application code must pass `Date.now()`.

**No SQL default available** for ms timestamps (SQLite `unixepoch()` returns seconds). Must always be set application-side.

### Per-Table Timestamp Mapping

#### Convention A — Unix Seconds (39 tables)

| Table | created_at default | updated_at handling | Other timestamp columns |
|-------|--------------------|---------------------|-------------------------|
| `users` | `DEFAULT (unixepoch())` | Application-side | `lastSignedIn`, `bannedAt`, `subscriptionExpiresAt` — app-side |
| `conversations` | `DEFAULT (unixepoch())` | Application-side | `lastMessageAt` — app-side |
| `messages` | `DEFAULT (unixepoch())` | — | `flaggedAt` — app-side |
| `conversation_files` | `DEFAULT (unixepoch())` | — | — |
| `conversation_tags` | `DEFAULT (unixepoch())` | — | — |
| `tags` | `DEFAULT (unixepoch())` | — | — |
| `system_settings` | `DEFAULT (unixepoch())` | Application-side | — |
| `credit_transactions` | `DEFAULT (unixepoch())` | — | — |
| `credit_rules` | `DEFAULT (unixepoch())` | Application-side | — |
| `user_usage_stats` | `DEFAULT (unixepoch())` | Application-side | `date` — app-side |
| `pdf_categories` | `DEFAULT (unixepoch())` | Application-side | `courseOutlineGeneratedAt` — app-side |
| `smart_book_categories` | `DEFAULT (unixepoch())` | Application-side | — |
| `smart_books` | `DEFAULT (unixepoch())` | Application-side | — |
| `smart_book_chapters` | `DEFAULT (unixepoch())` | Application-side | — |
| `smart_book_conversations` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_progress` | — | Application-side | `completedAt` — app-side |
| `smart_book_chapter_qa` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_credits` | — | Application-side | `balanceExpiresAt` — app-side |
| `smart_book_settings` | — | Application-side | — |
| `smart_book_unit_qa` | `DEFAULT (unixepoch())` | Application-side | — |
| `smart_book_unit_qa_answers` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_learning_sessions` | `DEFAULT (unixepoch())` | — | `lastActiveAt` — default; `endedAt`, `reminderSentAt` — app-side |
| `smart_book_chapter_daily_verifications` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_chapter_completions` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_saved_messages` | `DEFAULT (unixepoch())` | Application-side | — |
| `lesson_points` | `DEFAULT (unixepoch())` | Application-side | `publishedAt`, `scriptGeneratedAt`, `classroomQuizGeneratedAt` — app-side |
| `lesson_progress` | `DEFAULT (unixepoch())` | — | `completedAt` — app-side |
| `smart_book_review_questions` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_wrong_answers` | `DEFAULT (unixepoch())` | — | `learnedAt` — app-side |
| `smart_book_verifications` | `DEFAULT (unixepoch())` | Application-side | `passedAt`, `expiredAt`, `suspendedUntil`, `lockedUntil` — app-side |
| `saved_qa` | `DEFAULT (unixepoch())` | — | — |
| `learning_materials` | `DEFAULT (unixepoch())` | Application-side | `questionsExtractedAt` — app-side |
| `exam_questions` | `DEFAULT (unixepoch())` | Application-side | `reviewedAt` — app-side |
| `real_exam_questions` | `DEFAULT (unixepoch())` | Application-side | — |
| `ai_question_sources` | `DEFAULT (unixepoch())` | Application-side | `processingStartedAt` — app-side |
| `ai_generated_exams` | `DEFAULT (unixepoch())` | Application-side | — |
| `ai_generated_questions` | `DEFAULT (unixepoch())` | Application-side | — |
| `tutor_subject_exam_sources` | `DEFAULT (unixepoch())` | — | — |
| `smart_book_category_exam_sources` | `DEFAULT (unixepoch())` | — | — |

**Total `created_at` columns needing `DEFAULT (unixepoch())`**: 34

#### Convention B — Unix Milliseconds (21 tables, plain integer — NO SQL default)

| Table | Timestamp Columns | All application-side |
|-------|--------------------|----------------------|
| `tutor_subjects` | `createdAt`, `updatedAt` | ✅ |
| `tutor_subject_books` | `createdAt` | ✅ |
| `tutor_chat_sessions` | `createdAt`, `updatedAt` | ✅ |
| `tutor_chat_messages` | `teacherNoteAt`, `createdAt` | ✅ |
| `tutor_subject_video_courses` | `createdAt` | ✅ |
| `book_suggestion_cache` | `createdAt` | ✅ |
| `book_voucher_records` | `createdAt` | ✅ |
| `book_custom_suggestions` | `createdAt`, `updatedAt` | ✅ |
| `exam_sets` | `createdAt`, `updatedAt` | ✅ |
| `exam_set_questions` | `createdAt`, `updatedAt` | ✅ |
| `exam_wrong_book` | `lastAnsweredAt`, `resolvedAt`, `createdAt` | ✅ |
| `exam_notes` | `createdAt`, `updatedAt` | ✅ |
| `learning_material_exam_sets` | `createdAt` | ✅ |
| `video_courses` | `createdAt`, `updatedAt` | ✅ |
| `video_units` | `createdAt`, `updatedAt` | ✅ |
| `video_progress` | `updatedAt` | ✅ |
| `video_unit_questions` | `createdAt`, `updatedAt` | ✅ |
| `practice_wrong_book` | `resolvedAt`, `createdAt`, `updatedAt` | ✅ |
| `page_text_cache` | `createdAt`, `updatedAt` | ✅ |
| `smart_book_quiz_sessions` | `createdAt` | ✅ |
| `smart_book_question_shown` | `updatedAt` | ✅ |

### Timestamp Hardening Action Summary

| Action | Count | When |
|--------|-------|------|
| Add `.default(sql\`(unixepoch())\`)` to `created_at` columns | 34 columns | Before Phase 1-E |
| No change to ms-timestamp columns (Convention B) | 21 tables | None needed |
| Resolve remaining 67 `TODO` markers with decision comment | 67 markers | Before Phase 1-E |

---

## Enum Plan

### Current State

**47 `text` columns** converted from `mysqlEnum` across the 66-table schema. None have DB-level enforcement.

### Enum Column Register

| # | Table | Column | Values | Security Level |
|---|-------|--------|--------|----------------|
| 1 | `users` | `role` | user, admin, assistant, teacher, academic_affairs, editor | **Security-Critical** |
| 2 | `users` | `subscriptionPlan` | free, standard, premium | **Security-Critical** |
| 3 | `users` | `examType` | 6 values | Business |
| 4 | `users` | `studentStatus` | 4 values | Business |
| 5 | `users` | `studentType` | general, class_member | Business |
| 6 | `users` | `teachingRole` | teacher, assistant | Business |
| 7 | `users` | `gender` | male, female | Business |
| 8 | `users` | `chatStyle` | 11 values | Feature |
| 9 | `users` | `identityType` | ibrain, gaodian, book_buyer, trial, unset | Business |
| 10 | `conversations` | `chatStyle` | (inherited) | Feature |
| 11 | `messages` | `role` | user, assistant | **Security-Critical** |
| 12 | `messages` | `aiModel` | manus | Feature |
| 13 | `messages` | `contentFlag` | normal, inappropriate, offtopic, spam | Moderation |
| 14 | `pdf_categories` | `isActive` | true, false | Feature |
| 15 | `pdf_categories` | `isPublic` | true, false | Feature |
| 16 | `smart_books` | `verificationMode` | ai_quiz, purchase_link, both | Flow-control |
| 17 | `smart_books` | `processingStatus` | pending, processing, ready, failed | Flow-control |
| 18 | `smart_books` | `language` | zh, en | Feature |
| 19 | `smart_books` | `contentType` | book, handout | Feature |
| 20 | `smart_book_conversations` | `role` | user, assistant | **Security-Critical** |
| 21 | `credit_transactions` | `type` | 28 values | Accounting |
| 22 | `smart_book_unit_qa` | `qaType` | case_study, question, notice | Flow-control |
| 23 | `smart_book_review_questions` | `difficulty` | easy, medium, hard | Feature |
| 24 | `smart_book_quiz_sessions` | `mode` | chapter, mock | Feature |
| 25 | `smart_book_verifications` | `status` | pending, passed, failed | Flow-control |
| 26 | `tutor_chat_messages` | `role` | user, assistant | **Security-Critical** |
| 27 | `tutor_chat_messages` | `aiAccuracy` | correct, incorrect, partial | Feature |
| 28 | `tutor_subject_exam_sources` | `sourceType` | exam_set, real_exam, ai_exam, past_exam | Feature |
| 29 | `book_custom_suggestions` | `source` | manual, ai_generated, from_chapter | Feature |
| 30 | `smart_book_category_exam_sources` | `sourceType` | real_exam, ai_exam, past_exam | Feature |
| 31 | `exam_questions` | `questionType` | multiple_choice, essay | Feature |
| 32 | `exam_questions` | `difficulty` | easy, medium, hard | Feature |
| 33 | `exam_questions` | `status` | pending, approved, rejected | Flow-control |
| 34 | `exam_questions` | `source` | public, private | Access |
| 35 | `exam_questions` | `accessType` | free, paid, class_only | Business |
| 36 | `real_exam_questions` | `questionType` | multiple_choice, essay | Feature |
| 37 | `real_exam_questions` | `difficulty` | easy, medium, hard | Feature |
| 38 | `ai_question_sources` | `sourceType` | lecture, exam | Feature |
| 39 | `ai_question_sources` | `sourceOrigin` | manual_upload, goldensun_sync, url_import | Feature |
| 40 | `ai_question_sources` | `fileType` | pdf, word | Feature |
| 41 | `ai_question_sources` | `status` | uploading, processing, ready, error | Flow-control |
| 42 | `ai_generated_exams` | `difficulty` | easy, medium, hard, mixed | Feature |
| 43 | `ai_generated_exams` | `status` | generating, ready, published, archived, error | Flow-control |
| 44 | `ai_generated_questions` | `questionType` | multiple_choice, fill_blank, essay | Feature |
| 45 | `ai_generated_questions` | `difficulty` | easy, medium, hard | Feature |
| 46 | `exam_set_questions` | `questionType` | choice, essay | Feature |
| 47 | `practice_wrong_book` | `sourceType` | exam_set, real_exam, ai_exam | Feature |

### Enum Validation Strategy

| Phase | Strategy | Scope | Action |
|-------|----------|-------|--------|
| Phase 1-E | **Zod at tRPC boundary** | All 47 columns | Already enforced via tRPC router inputs; TypeScript types prevent invalid values in internal code |
| Phase 1-G | **SQLite CHECK constraints** | 5 Security-Critical columns | Add to migration SQL: `users.role`, `users.subscriptionPlan`, `messages.role`, `smart_book_conversations.role`, `tutor_chat_messages.role` |
| Phase 1-G | **CHECK constraints** | Flow-control columns | `smart_book_verifications.status`, `smart_books.processingStatus`, `credit_transactions.type` (or application-level Zod) |

**Total Security-Critical enum columns requiring Phase 1-G CHECK constraints: 5**

---

## Compile Coverage

This section audits whether the 66-table SQLite schema covers every table import in the **currently mounted routers**. Coverage is assessed against switching any given router from `drizzle/schema` (MySQL) to `drizzle/schema.sqlite.mvp` (SQLite).

### Core Lite Routers — Full Coverage ✅

All 7 core Lite router files have 100% table coverage in the 66-table schema:

| Router | Import Count | Tables Used | Coverage |
|--------|--------------|-------------|----------|
| `smartBookRouter.ts` | 31 | smart_books, smart_book_chapters, smart_book_verifications, smart_book_conversations, smart_book_progress, smart_book_chapter_qa, smart_book_credits, smart_book_credit_transactions, smart_book_chapter_daily_verifications, lesson_progress, lesson_points, users, user_usage_stats, smart_book_review_questions, smart_book_wrong_answers, smart_book_question_shown, smart_book_qa_viewed, smart_book_quiz_sessions, smart_book_categories, smart_book_category_exam_sources, ai_question_sources, ai_generated_exams, real_exam_questions, exam_subjects, exam_categories, exam_questions, book_suggestion_cache | ✅ 100% |
| `tutorRouter.ts` | 15 | tutor_subjects, tutor_subject_books, tutor_subject_exam_sources, tutor_subject_video_courses, tutor_chat_sessions, tutor_chat_messages, smart_book_chapters, smart_book_chapter_qa, smart_book_unit_qa, ai_question_sources, ai_generated_exams, exam_subjects, practice_wrong_book, page_text_cache, book_suggestion_cache | ✅ 100% |
| `smartBookLearningRouter.ts` | 12 | smart_book_credits, smart_book_credit_transactions, smart_book_settings, smart_book_unit_qa, smart_book_unit_qa_answers, smart_book_learning_sessions, smart_book_chapter_daily_verifications, smart_book_chapter_qa, smart_books, smart_book_chapters, smart_book_saved_messages, smart_book_chapter_completions, smart_book_review_questions, users | ✅ 100% |
| `lessonPointsRouter.ts` | 4 | lesson_points, lesson_progress, smart_book_chapters, smart_books | ✅ 100% |
| `videoCourseRouter.ts` | 6 | video_courses (videoCorses), video_units, video_knowledge_points, video_progress, saved_qa, video_unit_questions | ✅ 100% |
| `examSetRouter.ts` | 8 | exam_sets, exam_set_questions, exam_set_sub_questions, exam_wrong_book, exam_notes, smart_books, learning_material_exam_sets, learning_materials | ✅ 100% |
| `userManagement.ts` | 1 | users | ✅ 100% |

### Peripheral Routers — Partial Coverage (migrate per-router in Phase 1-E)

These routers are mounted in `server/routers.ts` but reference tables outside the 66-table scope. They can remain on MySQL until their specific router is migrated in Phase 1-E.

| Router | Missing Tables | Impact |
|--------|----------------|--------|
| `routers.ts` (inline) | `qaCache`, `lawBookmarks`, `lawQuizMistakes`, `lawLearningHistory`, `practiceExams`, `questionBank`, `examPurchases`, `knowledgeBasePdfs`, `knowledgeLearningSessions`, `knowledgeLearningTopics`, `knowledgeLearningMessages` | 11 tables — main router file compile blocker when migrated |
| `studentLearningRouter.ts` | `qaCache`, `studentLearningSessions`, `studentBehaviorAlerts` | 3 tables |
| `essayGradingRouter.ts` | `essaySubmissions`, `essayGradings`, `qaCache` | 3 tables |
| `watermarkRouter.ts` | `watermarkSettings` | 1 table |
| `announcement.ts` | `announcements`, `announcementReads` | 2 tables |
| `calendarRouter.ts` | `calendarEvents` | 1 table |
| `ibrainPackage.ts` | `ibrainPackages`, `ibrainQuestions` | 2 tables |
| `apiKeyRouter.ts` | `apiKeys`, `apiKeyUsageLogs` | 2 tables |
| `lectureMaterialsRouter.ts` | `materialContents`, `classVerifications`, `materialAccess`, `teacherMaterials`, `lectureTeachers` | 5 tables |
| `adminConversationsRouter.ts` | `userWarnings` | 1 table |
| `featureTogglesRouter.ts` | `classVerifications` | 1 table |
| `checklistRouter.ts` | `checklistSubmissions` | 1 table |
| `learningResources.ts` | `books`, `courses`, `teachers` | 3 tables |

**Total additional stub tables needed for full server migration: ~30**
**Strategy: Add stubs incrementally as each peripheral router is migrated in Phase 1-E.**

### Auth & Local Auth Coverage

| Component | Tables Used | Coverage |
|-----------|-------------|----------|
| `server/auth.ts` / `server/localAuth.ts` | `users` | ✅ Covered |
| `server/db.ts` (direct imports) | Multiple legacy tables (lawBookmarks, knowledgeChunks, etc.) | ❌ Not needed — `db.ts` will not switch to SQLite until router-by-router migration |

---

## Index Migration Design

All indexes will be added to `drizzle/schema.sqlite.mvp.ts` using the Drizzle SQLite `index()` function inside the table definition callback.

### Template for Adding Indexes

Current table definition (no indexes):
```typescript
export const conversations = sqliteTable("conversations", {
  ...columns...
});
```

Hardened table definition (with indexes):
```typescript
import { sqliteTable, integer, text, index } from "drizzle-orm/sqlite-core";

export const conversations = sqliteTable("conversations", {
  ...columns...
}, (table) => [
  index("idx_conversations_userId").on(table.userId),
  index("idx_conversations_lastMessageAt").on(table.lastMessageAt),
]);
```

### Migration Script Pattern (Phase 1-E, after driver is installed)

```sql
-- Generated by drizzle-kit push --dialect sqlite
-- Must-Add indexes
CREATE INDEX IF NOT EXISTS idx_conversations_userId ON conversations(userId);
CREATE INDEX IF NOT EXISTS idx_conversations_lastMessageAt ON conversations(lastMessageAt);
CREATE INDEX IF NOT EXISTS idx_messages_conversationId ON messages(conversationId);
CREATE INDEX IF NOT EXISTS idx_users_openId ON users(openId);
-- ... (15 Must-Add + 14 High-priority)
```

### Index Naming Convention

`idx_{table_short}_{columns_with_underscores}`
- Examples: `idx_conversations_userId`, `idx_sbp_bookId_userId`, `idx_tcs_userId`
- Prefix table name with abbreviated form for long table names (e.g., `sbp` = smart_book_progress)

---

## Remaining Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | **No indexes yet** — queries on 66-table schema will be full-table scans | High | Add Must-Add indexes before first load test |
| 2 | **67 TODO timestamp markers** — inserts without explicit `created_at` will store NULL | High | Add `DEFAULT (unixepoch())` SQL defaults before Phase 1-E |
| 3 | **Enum silently accepts invalid values** — text columns take any string | Medium | tRPC Zod validation covers API boundary; TypeScript types cover internal calls |
| 4 | **30 additional tables** needed for full server compile coverage (peripheral routers) | Medium | Handled incrementally in Phase 1-E per-router migration |
| 5 | **`updated_at` always requires explicit app-side set** — will silently be NULL if forgotten | Medium | Document in `db.sqlite.ts` header; add TypeScript assertion pattern |
| 6 | **ms vs seconds timestamp mixing** — passing ms timestamp to a seconds column silently stores ~50-year-in-future date | Medium | Document conventions; add runtime sanity check in `getSqliteDb()` |
| 7 | **`smart_book_quiz_sessions.createdAt` TODO** — currently plain integer with TODO, but should be `DEFAULT (unixepoch())` based on source | Low | Confirm in next schema update |
| 8 | **`video_progress` has no `created_at`** — only `updatedAt` (ms); no TODO markers needed | Low | Already handled correctly |

---

## Recommendation

### Pre-Phase-1-E Checklist

| # | Action | File | Priority |
|---|--------|------|----------|
| 1 | Add `DEFAULT (unixepoch())` to 34 `created_at` columns | `schema.sqlite.mvp.ts` | **Critical** |
| 2 | Add `index()` callbacks to 15 Must-Add table definitions | `schema.sqlite.mvp.ts` | **Critical** |
| 3 | Replace 67 `// TODO SQLite timestamp default strategy` markers with confirmed convention note | `schema.sqlite.mvp.ts` | High |
| 4 | Add `import { index } from "drizzle-orm/sqlite-core"` to schema imports | `schema.sqlite.mvp.ts` | High |
| 5 | Create `drizzle.config.sqlite.ts` (sqlite dialect, points to schema.sqlite.mvp.ts) | New file | High |
| 6 | Confirm VPS Node.js version ≥ 14 for `better-sqlite3` native bindings | VPS environment | High |

### Is Phase 1-E Ready to Begin?

**Phase 1-E can begin immediately after actions #1 and #2 above are applied to `schema.sqlite.mvp.ts`.**

The schema will then be production-ready for the dual-mode wiring approach:
- `server/db.sqlite.ts` (new, imports from `schema.sqlite.mvp.ts`)
- `server/db.ts` (unchanged, MySQL, remains live until full cut-over)
- Core Lite routers migrate one-by-one, each validated before the next

---

*Design Only. No db.ts / schema.ts / schema.sqlite.mvp.ts / package / migration / SQLite DB changes were made in this phase.*
