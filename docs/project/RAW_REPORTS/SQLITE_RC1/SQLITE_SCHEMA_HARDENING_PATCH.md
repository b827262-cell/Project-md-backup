# SQLite Schema Hardening Patch

> **Phase 1-C.9 — Pending Human Review**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> **`drizzle/schema.sqlite.mvp.ts` was NOT modified.**
> Apply only after reviewing and approving the changes below.

---

## Patch Summary

| Change Type | Count | Action |
|-------------|-------|--------|
| Import line | 1 | Add `index` + `sql` imports |
| Timestamp `DEFAULT(unixepoch())` | 41 columns | Add `.default(sql\`(unixepoch())\`)` to write-once Convention A columns |
| Timestamp mode fix | 21 columns | Add `{ mode: "timestamp" }` to bare `integer()` Convention A columns |
| Must-Add indexes | 16 index definitions on 13 tables | Add `(table) => [...]` callback to 13 table definitions |
| TODO comment cleanup | 67 comments | Replace with convention-tagged comments |

---

## Part 1 — Import Line

**File:** `drizzle/schema.sqlite.mvp.ts` line 8

```diff
-import { sqliteTable, integer, text, real, blob } from "drizzle-orm/sqlite-core";
+import { sqliteTable, integer, text, real, blob, index } from "drizzle-orm/sqlite-core";
+import { sql } from "drizzle-orm";
```

---

## Part 2 — Timestamp Columns

### Convention A — Unix Seconds (add `DEFAULT(unixepoch())`)

These columns had `defaultNow()` or `sql\`CURRENT_TIMESTAMP\`` in the MySQL source.
All are write-once timestamps (created_at or equivalent first-write fields).

#### 2a — Columns already having `{ mode: "timestamp" }` (add `.default(sql\`(unixepoch())\`)` only)

| Line | Table | Column | Current | After Patch |
|------|-------|--------|---------|-------------|
| 26 | users | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 63 | conversations | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 82 | messages | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 103 | conversation_files | uploadedAt | `integer("uploadedAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 111 | conversation_tags | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 120 | tags | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 129 | system_settings | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 142 | credit_transactions | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 156 | credit_rules | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 170 | user_usage_stats | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 188 | pdf_categories | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 617 | tutor_subject_exam_sources | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 677 | exam_categories | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 688 | exam_subjects | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 709 | exam_questions | createdAt | `integer("createdAt", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 746 | real_exam_questions | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 779 | ai_question_sources | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 806 | ai_generated_exams | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 826 | ai_generated_questions | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 1005 | saved_qa | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |
| 1021 | learning_materials | createdAt | `integer("created_at", { mode: "timestamp" })` | add `.default(sql\`(unixepoch())\`)` |

**Subtotal: 21 columns**

#### 2b — Bare integer columns (add `{ mode: "timestamp" }` AND `.default(sql\`(unixepoch())\`)`)

These were originally `sql\`CURRENT_TIMESTAMP\`` in MySQL. The draft kept them as bare `integer()` without mode — they must gain both the mode and the default.

| Line | Table | Column | Current | After Patch |
|------|-------|--------|---------|-------------|
| 200 | smart_book_categories | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 235 | smart_books | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 254 | smart_book_chapters | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 270 | smart_book_conversations | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 294 | smart_book_chapter_qa | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 320 | smart_book_credit_transactions | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 355 | smart_book_unit_qa | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 367 | smart_book_unit_qa_answers | answeredAt | `integer("answered_at")` | `integer("answered_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 375 | smart_book_learning_sessions | startedAt | `integer("started_at")` | `integer("started_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 376 | smart_book_learning_sessions | lastActiveAt | `integer("last_active_at")` | `integer("last_active_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 389 | smart_book_chapter_daily_verifications | verifiedAt | `integer("verified_at")` | `integer("verified_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 400 | smart_book_chapter_completions | completedAt | `integer("completed_at")` | `integer("completed_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 420 | smart_book_saved_messages | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 453 | lesson_points | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 467 | lesson_progress | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 481 | smart_book_review_questions | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 498 | smart_book_wrong_answers | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 510 | smart_book_quiz_sessions | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 530 | smart_book_qa_viewed | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 553 | smart_book_verifications | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |
| 914 | smart_book_category_exam_sources | createdAt | `integer("created_at")` | `integer("created_at", { mode: "timestamp" }).default(sql\`(unixepoch())\`)` |

**Subtotal: 21 columns**

**Total timestamp columns patched: 42**

### Convention B — No Change

These tables use Unix milliseconds (`bigint` origin). No SQL default is possible with `unixepoch()` (which returns seconds). All remain as plain `integer()` — always set application-side with `Date.now()`. **No patch needed.**

Tables: `tutor_subjects`, `tutor_subject_books`, `tutor_chat_sessions`, `tutor_chat_messages`, `tutor_subject_video_courses`, `book_suggestion_cache`, `book_voucher_records`, `book_custom_suggestions`, `exam_sets`, `exam_set_questions`, `exam_set_sub_questions`, `exam_wrong_book`, `exam_notes`, `learning_material_exam_sets`, `video_courses (videoCorses)`, `video_units`, `video_progress`, `video_unit_questions`, `practice_wrong_book`, `page_text_cache`.

---

## Part 3 — Must-Add Indexes (16 definitions on 13 tables)

Each table below requires converting from:
```typescript
export const tableName = sqliteTable("name", { ...columns... });
```
to:
```typescript
export const tableName = sqliteTable("name", { ...columns... }, (table) => [
  index("idx_name").on(table.column),
]);
```

### Index List

| # | Table | Variable Name | Index Name | Column(s) | Line (approx.) |
|---|-------|---------------|------------|-----------|----------------|
| 1 | users | `users` | `idx_users_openId` | `openId` | 17–54 |
| 2 | users | `users` | `idx_users_email` | `email` | 17–54 |
| 3 | conversations | `conversations` | `idx_conversations_userId` | `userId` | 57–70 |
| 4 | conversations | `conversations` | `idx_conversations_lastMessageAt` | `lastMessageAt` | 57–70 |
| 5 | messages | `messages` | `idx_messages_conversationId` | `conversationId` | 73–90 |
| 6 | smart_books | `smartBooks` | `idx_smart_books_public_status` | `is_public, processing_status` | 205–237 |
| 7 | smart_book_chapters | `smartBookChapters` | `idx_sbc_bookId` | `book_id` | 240–256 |
| 8 | smart_book_conversations | `smartBookConversations` | `idx_sbconv_bookId_userId` | `book_id, user_id` | 259–271 |
| 9 | smart_book_progress | `smartBookProgress` | `idx_sbp_bookId_userId` | `book_id, user_id` | 274–283 |
| 10 | smart_book_review_questions | `smartBookReviewQuestions` | `idx_sbrq_bookId_chapterId` | `book_id, chapter_id` | 471–482 |
| 11 | smart_book_wrong_answers | `smartBookWrongAnswers` | `idx_sbwa_userId_bookId` | `user_id, book_id` | 485–499 |
| 12 | lesson_points | `lessonPoints` | `idx_lp_bookId_chapterId` | `book_id, chapter_id` | 425–455 |
| 13 | lesson_progress | `lessonProgress` | `idx_lprog_userId_chapterId` | `user_id, chapter_id` | 458–468 |
| 14 | tutor_chat_sessions | `tutorChatSessions` | `idx_tcs_userId` | `user_id` | 579–590 |
| 15 | tutor_chat_sessions | `tutorChatSessions` | `idx_tcs_smartBookId` | `smart_book_id` | 579–590 |
| 16 | tutor_chat_messages | `tutorChatMessages` | `idx_tcm_sessionId` | `session_id` | 593–607 |

---

## Part 4 — Diff Samples

Representative diffs for each type of change. Apply the same pattern to all rows in Part 2 and Part 3.

### Diff Type A — Add `.default(sql\`(unixepoch())\`)` to existing `{ mode: "timestamp" }` column

```diff
-  createdAt: integer("createdAt", { mode: "timestamp" }), // TODO SQLite timestamp default strategy
+  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(unixepoch())`), // Phase 1-C.9 — Unix seconds, DEFAULT(unixepoch())
```

### Diff Type B — Bare integer gets `{ mode: "timestamp" }` + default

```diff
-  createdAt: integer("created_at"), // TODO SQLite timestamp default strategy (was sql`CURRENT_TIMESTAMP`)
+  createdAt: integer("created_at", { mode: "timestamp" }).default(sql`(unixepoch())`), // Phase 1-C.9 — Unix seconds, DEFAULT(unixepoch())
```

### Diff Type C — `updated_at` comment cleanup (no default, stays app-side)

```diff
-  updatedAt: integer("updatedAt", { mode: "timestamp" }), // TODO SQLite timestamp default strategy
+  updatedAt: integer("updatedAt", { mode: "timestamp" }), // Application-side — set on update
```

### Diff Type D — Add index callback to a table (example: `users`)

```diff
-export const users = sqliteTable("users", {
+export const users = sqliteTable("users", {
   id: integer("id").primaryKey({ autoIncrement: true }),
   ...
   trialResetDate: text("trial_reset_date"),
-});
+}, (table) => [
+  index("idx_users_openId").on(table.openId),
+  index("idx_users_email").on(table.email),
+]);
```

### Diff Type E — Add index callback to a table (example: `conversations`)

```diff
-export const conversations = sqliteTable("conversations", {
+export const conversations = sqliteTable("conversations", {
   id: integer("id").primaryKey({ autoIncrement: true }),
   ...
   isTrialHidden: integer("is_trial_hidden", { mode: "boolean" }).notNull().default(false),
-});
+}, (table) => [
+  index("idx_conversations_userId").on(table.userId),
+  index("idx_conversations_lastMessageAt").on(table.lastMessageAt),
+]);
```

### Diff Type F — Add index callback to a table (example: `tutor_chat_sessions`)

```diff
-export const tutorChatSessions = sqliteTable("tutor_chat_sessions", {
+export const tutorChatSessions = sqliteTable("tutor_chat_sessions", {
   id: integer("id").primaryKey({ autoIncrement: true }),
   ...
   updatedAt: integer("updated_at").notNull(),
-});
+}, (table) => [
+  index("idx_tcs_userId").on(table.userId),
+  index("idx_tcs_smartBookId").on(table.smartBookId),
+]);
```

---

## Part 5 — TODO Comment Cleanup

Replace all 67 `// TODO SQLite timestamp default strategy` and `// TODO SQLite timestamp default strategy (was sql\`CURRENT_TIMESTAMP\`)` comments with one of:

| Condition | New Comment |
|-----------|-------------|
| Convention A `created_at` (gets `DEFAULT(unixepoch())`) | `// Phase 1-C.9 — Unix seconds, DEFAULT(unixepoch())` |
| Convention A `updated_at` (app-side, no default) | `// Application-side — set on update` |
| Convention A optional/conditional timestamp | `// Application-side — set when [condition]` |
| Convention B ms-timestamp (was already correct) | `// Convention B — Unix ms (bigint origin), application-side Date.now()` |

---

## Pending Human Review Checklist

Before applying this patch, please confirm:

- [ ] 42 timestamp columns to patch are correct (21 mode-only + 21 mode+default)
- [ ] Convention B tables are correctly NOT patched (20 tables with `Date.now()` pattern)
- [ ] 16 index definitions on 13 tables are correct and complete
- [ ] Index naming convention is acceptable (`idx_{short_table}_{columns}`)
- [ ] `sql\`(unixepoch())\`` syntax is correct for this version of drizzle-orm/sqlite-core
- [ ] No regression to existing column definitions (types, nullability, defaults)
- [ ] Table count remains 66 after patch

---

*Patch document only. `drizzle/schema.sqlite.mvp.ts` was NOT modified.*
