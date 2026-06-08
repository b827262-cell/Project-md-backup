# SQLite Schema Coverage Gap Report — Phase 2C

**Task:** SQLITE_SCHEMA_COVERAGE_AUDIT  
**Project:** `/home/b827262/project/smartbook-lite-rc1`  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-05  
**Mode:** Read-only audit. No files modified, no schema added, no commit, no push.

---

## Summary

| Metric | Count |
|--------|-------|
| MySQL tables (`schema.ts`) | 176 |
| SQLite tables (`schema.sqlite.mvp.ts`) | 66 |
| **Missing from SQLite** | **110** |
| Coverage | 37.5% |

---

## Special Confirmation

| Table | In SQLite? | Referenced in Runtime? |
|-------|-----------|----------------------|
| `user_preferences` | ❌ MISSING | ✅ YES — `server/routers.ts` lines 455–476 (sidebar order get/set) |
| `practice_exams` | ❌ MISSING | ✅ YES — heavily used in `server/db.ts` + `server/routers.ts` + 4 client pages |

---

## HIGH PRIORITY TABLES

Tables actively referenced by runtime routers/pages that will throw on first call.

| # | Table | Purpose | Referenced By (Server) | Referenced By (Client) | Complexity |
|---|-------|---------|----------------------|----------------------|------------|
| 1 | `practice_exams` | Exam paper definitions (title, category, subject, status, access type) | `server/db.ts` (25+ refs), `server/routers.ts` (practiceExams router) | `ExamPractice.tsx`, `PracticeExamManagement.tsx`, `QuestionSelector.tsx`, `PurchaseHistory.tsx` | MEDIUM — enum columns |
| 2 | `practice_exam_questions` | Maps questions to practice exams | `server/db.ts` (10+ refs) | Via practiceExams router | LOW |
| 3 | `practice_records` | Student test session records | `server/db.ts` (20+ refs) | Via practiceExams router | MEDIUM |
| 4 | `practice_answers` | Individual answer records per test | `server/db.ts` (14 refs) | Via practiceExams router | LOW |
| 5 | `exam_purchases` | Points-based exam unlock records | `server/routers.ts` (15+ refs) | `PurchaseHistory.tsx` | LOW |
| 6 | `wrong_questions` | Wrongly answered question tracker | `server/db.ts` (30+ refs), `server/routers.ts` | `WrongQuestions.tsx`, `QuizWrongQuestions.tsx` | MEDIUM |
| 7 | `question_bank` | Central question repository (PDF-extracted) | `server/db.ts` (50+ refs), `server/routers.ts` | `QuestionBankList.tsx`, `QuestionBankManagement.tsx`, `QuestionDetail.tsx`, `QuestionEditor.tsx`, `ExamQuestions.tsx` | HIGH — many enum columns |
| 8 | `question_bank_history` | Version history for question edits | `server/db.ts` | Admin pages | LOW |
| 9 | `announcements` | System announcements/notifications | `server/db.ts` (30+ refs), `server/routers/announcement.ts` | `AnnouncementManagement.tsx`, `AnnouncementList.tsx` | MEDIUM — enum columns |
| 10 | `announcement_reads` | Tracks which user read which announcement | `server/routers/announcement.ts` | Via announcements | LOW |
| 11 | `user_preferences` | User sidebar customization (order) | `server/routers.ts` lines 455–476 | None directly (called via tRPC) | LOW — simple table |
| 12 | `qa_cache` | AI answer cache (exam/learning Q&A) | 19 server files (routers, services, stream) | Multiple learning pages | HIGH — many columns, enums |
| 13 | `banners` | Homepage banner management | `server/db.ts`, `server/routers.ts` | Admin/student homepage | LOW |
| 14 | `knowledge_base_pdfs` | PDF document metadata for knowledge base | `server/db.ts` (heavy), `server/routers.ts` | `KnowledgeBase.tsx`, `PdfReader.tsx`, `AdminPdfCategories.tsx` | HIGH — many columns, enums |
| 15 | `knowledge_base_pages` | Page-level content from PDFs | `server/db.ts` | Via knowledge base features | MEDIUM |
| 16 | `knowledge_base_categories` | Category grouping for PDFs | `server/db.ts`, `server/routers.ts` | Admin pages | LOW |

---

## MEDIUM PRIORITY TABLES

Tables used by secondary features or admin-only workflows.

| # | Table | Purpose | Referenced By | Complexity |
|---|-------|---------|-------------|------------|
| 17 | `exam_questions` | Exam question records (公職考試) | `server/db.ts`, `server/routers.ts` | HIGH |
| 18 | `exam_subjects` | Exam subject categories | `server/db.ts` | LOW |
| 19 | `point_transactions` | Points deduction/charge log | `server/db.ts`, `server/routers.ts` | LOW |
| 20 | `user_points` | User points balance | `server/db.ts` | LOW |
| 21 | `user_points_log` | Detailed points change log | `server/db.ts` | LOW |
| 22 | `lecture_teachers` | Lecture instructor profiles | `server/routers.ts`, `lectureMaterialsRouter.ts` | MEDIUM |
| 23 | `lecture_teacher_subjects` | Teacher-subject many-to-many | `lectureMaterialsRouter.ts` | LOW |
| 24 | `teacher_materials` | Lecture PDF/video materials | `lectureMaterialsRouter.ts` | HIGH |
| 25 | `material_contents` | Chunked lecture content | `lectureMaterialsRouter.ts` | MEDIUM |
| 26 | `material_conversations` | Student-teacher Q&A on materials | `lectureMaterialsRouter.ts` | MEDIUM |
| 27 | `lecture_courses` | Course groups for lectures | `lectureMaterialsRouter.ts` | MEDIUM |
| 28 | `saved_answers` | Saved Q&A answers | `lectureMaterialsRouter.ts` | LOW |
| 29 | `essay_submissions` | Essay answer submissions | `essayManagementRouter.ts`, `essayGradingRouter.ts` | MEDIUM |
| 30 | `essay_gradings` | Essay grading results | `essayGradingRouter.ts` | MEDIUM |
| 31 | `feedback` | User bug reports/feature requests | `server/db.ts`, `server/routers.ts` | LOW |
| 32 | `student_questions` | Student-submitted questions | `server/db.ts`, `server/routers.ts` | MEDIUM |
| 33 | `question_images` | Image attachments for questions | `server/db.ts`, `server/routers.ts` | LOW |
| 34 | `question_groups` | Grouped question stems | `server/db.ts` | LOW |
| 35 | `question_learning_conversations` | Learning conversations per question | `server/db.ts` | MEDIUM |
| 36 | `learning_conversations` | PDF learning conversation sessions | `server/db.ts` | MEDIUM |
| 37 | `learning_outlines` | AI-generated study outlines | `server/db.ts` | LOW |
| 38 | `learning_progress` | Chapter-level study progress | `server/db.ts` | MEDIUM |
| 39 | `quiz_cache` | Cached quiz data by chapter | `server/db.ts` | LOW |
| 40 | `quiz_history` | Quiz attempt history | `server/db.ts` | LOW |
| 41 | `quiz_wrong_questions` | Wrong answers from quizzes | `server/db.ts` | LOW |
| 42 | `ai_exam_attempts` | AI-generated exam attempt records | `aiQuestionBankRouter.ts` | MEDIUM |
| 43 | `real_exam_attempts` | Real past exam attempt records | `realExamRouter.ts` | MEDIUM |
| 44 | `credit_transactions` | Detailed credit usage log | `server/db.ts`, `server/routers.ts` | MEDIUM |
| 45 | `conversations` | AI chat conversation sessions | `server/db.ts` (in SQLite but already covered) | Already in SQLite ✅ |
| 46 | `study_sessions` | Study duration tracking | `server/db.ts` | LOW |
| 47 | `user_practice_history` | Per-question practice history | `server/db.ts` | LOW |
| 48 | `user_question_stats` | User accuracy statistics per subject | `server/db.ts` | LOW |
| 49 | `knowledge_learning_sessions` | Knowledge base learning sessions | `server/routers.ts` | MEDIUM |
| 50 | `knowledge_learning_messages` | Messages in learning sessions | `server/routers.ts` | LOW |
| 51 | `knowledge_learning_topics` | Knowledge learning topics | `server/routers.ts` | LOW |

---

## LOW PRIORITY TABLES

Tables for crawler/batch/admin-only features, external integrations, or niche subsystems unlikely to be used in Lite mode.

| # | Table | Purpose | Complexity |
|---|-------|---------|------------|
| 52 | `books` | Scraped book catalog | LOW |
| 53 | `courses` | Scraped course catalog | LOW |
| 54 | `teachers` | Scraped teacher profiles | LOW |
| 55 | `external_resources` | External resource links | LOW |
| 56 | `external_search_buttons` | External search engine buttons | LOW |
| 57 | `gaodian_exams` | Gaodian exam crawl data | MEDIUM |
| 58 | `gaodian_pdf_links_cache` | Gaodian PDF link cache | LOW |
| 59 | `graduate_schools` | Graduate school catalog | LOW |
| 60 | `graduate_exams` | Graduate exam papers | LOW |
| 61 | `graduate_exam_downloads` | Graduate exam download history | LOW |
| 62 | `graduate_pdf_links_cache` | Graduate PDF cache | LOW |
| 63 | `graduate_school_favorites` | User favorites for schools | LOW |
| 64 | `ibrain_packages` | iBrain question packages | MEDIUM |
| 65 | `ibrain_questions` | iBrain questions | MEDIUM |
| 66 | `batch_extract_logs` | Batch question extraction logs | LOW |
| 67 | `extraction_logs` | Single PDF extraction logs | LOW |
| 68 | `exam_download_history` | Exam file download history | LOW |
| 69 | `law_articles` | Law article text | MEDIUM |
| 70 | `law_bookmarks` | User law bookmarks | LOW |
| 71 | `law_learning_history` | Law study history | LOW |
| 72 | `law_quiz_mistakes` | Law quiz mistake tracker | LOW |
| 73 | `knowledge_chunks` | Vector embedding chunks | HIGH |
| 74 | `knowledge_upload_history` | Knowledge upload logs | LOW |
| 75 | `cloud_knowledge_base_config` | Cloud KB API config | LOW |
| 76 | `past_exam_papers` | Past exam paper catalog | MEDIUM |
| 77 | `standard_answers` | Standard answer reference | LOW |
| 78 | `qa_records` | Q&A interaction logs | MEDIUM |
| 79 | `question_attempts` | Question attempt records | LOW |
| 80 | `question_references` | Question references in conversations | LOW |
| 81 | `recommendation_logs` | Resource recommendation logs | LOW |
| 82 | `subject_categories` | Subject category hierarchy | LOW |
| 83 | `faq_feedback` | FAQ helpfulness voting | LOW |
| 84 | `faqs` | FAQ entries | LOW |
| 85 | `student_learning_sessions` | Student learning behavior sessions | LOW |
| 86 | `student_behavior_alerts` | Behavior anomaly alerts | LOW |
| 87 | `subjects` | Academic subject list | LOW |
| 88 | `student_transcript_edits` | Subtitle correction edits | LOW |
| 89 | `transcript_correction_requests` | Subtitle correction review | LOW |
| 90 | `material_access` | Material unlock records | LOW |
| 91 | `material_question_attempts` | Material question attempts | LOW |
| 92 | `material_reading_progress` | Material reading progress | LOW |
| 93 | `auditory_playlists` | YouTube playlist management | LOW |
| 94 | `auditory_watch_progress` | Video watch progress | LOW |
| 95 | `class_verifications` | Class member verification | LOW |
| 96 | `course_access` | Course unlock records | LOW |
| 97 | `course_enrollments` | Course enrollment records | LOW |
| 98 | `api_keys` | API key management | MEDIUM |
| 99 | `api_key_usage_logs` | API usage logging | LOW |
| 100 | `web_search_logs` | Web search usage logs | LOW |
| 101 | `user_warnings` | Admin-issued user warnings | LOW |
| 102 | `goldensun_sync_jobs` | Goldensun sync batch jobs | LOW |
| 103 | `smart_book_chapter_quizzes` | SmartBook chapter quiz definitions | LOW |
| 104 | `calendar_events` | Calendar events | LOW |
| 105 | `checklist_submissions` | Checklist form submissions | LOW |
| 106 | `ai_classroom_lessons` | AI classroom lesson plans | LOW |
| 107 | `ai_classroom_records` | AI classroom session records | LOW |
| 108 | `ollama_regions` | Ollama region config | LOW |
| 109 | `ollama_region_ip_rules` | Ollama IP routing rules | LOW |
| 110 | `page_ai_response_cache` | Page-level AI response cache | LOW |
| 111 | `watermark_settings` | Watermark configuration | LOW |
| 112 | `tutor_chat_folders` | Chat folder organization | LOW |
| 113 | `tutor_chat_labels` | Chat label definitions | LOW |
| 114 | `tutor_chat_session_labels` | Chat session label mapping | LOW |

---

## Recommended Migration Order

### 🔴 Phase 1 — Must-add (breaks active student/admin pages)

**Recommend adding first: `practice_exams` cluster**

1. `practice_exams` — central to exam practice feature
2. `practice_exam_questions` — required by practice_exams
3. `practice_records` — required for test sessions
4. `practice_answers` — required for answer recording
5. `exam_purchases` — required for paid exam unlock
6. `wrong_questions` — required for wrong question review
7. `user_preferences` — required for sidebar customization

**Estimated effort:** ~2–3 hours (7 tables, mostly straightforward column mappings, enum→text conversions)

### 🟡 Phase 2 — Question Bank + Knowledge Base

8. `question_bank` — large table, many enums
9. `question_bank_history` — simple
10. `announcements` + `announcement_reads` — medium
11. `banners` — simple
12. `knowledge_base_pdfs` — large, complex
13. `knowledge_base_pages` — medium
14. `knowledge_base_categories` — simple
15. `qa_cache` — large, many columns

**Estimated effort:** ~4–6 hours (8 tables, complex enum mappings)

### 🟢 Phase 3 — Lecture System + Essay

16–28. Lecture teacher/material/course tables + essay tables

**Estimated effort:** ~3–4 hours

### ⚪ Phase 4+ — Low priority / Lite-excluded features

29+. Crawler tables, law tables, external integrations, etc.

---

## Final Answer

### HIGH PRIORITY TABLES (16)
`practice_exams`, `practice_exam_questions`, `practice_records`, `practice_answers`, `exam_purchases`, `wrong_questions`, `question_bank`, `question_bank_history`, `announcements`, `announcement_reads`, `user_preferences`, `qa_cache`, `banners`, `knowledge_base_pdfs`, `knowledge_base_pages`, `knowledge_base_categories`

### MEDIUM PRIORITY TABLES (35)
`exam_questions`, `exam_subjects`, `point_transactions`, `user_points`, `user_points_log`, `lecture_teachers`, `lecture_teacher_subjects`, `teacher_materials`, `material_contents`, `material_conversations`, `lecture_courses`, `saved_answers`, `essay_submissions`, `essay_gradings`, `feedback`, `student_questions`, `question_images`, `question_groups`, `question_learning_conversations`, `learning_conversations`, `learning_outlines`, `learning_progress`, `quiz_cache`, `quiz_history`, `quiz_wrong_questions`, `ai_exam_attempts`, `real_exam_attempts`, `credit_transactions`, `study_sessions`, `user_practice_history`, `user_question_stats`, `knowledge_learning_sessions`, `knowledge_learning_messages`, `knowledge_learning_topics`, `smart_book_chapter_quizzes`

### LOW PRIORITY TABLES (59)
All remaining tables (crawlers, external integrations, law, graduate, cloud KB, etc.)

---

### 🎯 建議先補哪一張表

**`practice_exams`**

理由：
1. 它是整個模擬考功能的核心表，被 4 個 client 頁面直接呼叫
2. 它串聯 `practice_exam_questions`、`practice_records`、`practice_answers`、`exam_purchases` 形成完整功能鏈
3. 缺少此表，學生進入「模擬考」頁面會直接 crash
4. 表結構中等複雜度（有 enum 但不多），可作為後續批量補表的模板
5. `user_preferences` 雖然也缺，但影響範圍只有 sidebar 自訂順序，屬於 nice-to-have

建議以 `practice_exams` 為起點，一次補完整個 practice 功能鏈（5 張表），再補 `user_preferences`（1 張簡單表），共 6 張表即可覆蓋最高優先級的 runtime 缺口。

---

*Read-only audit. No files modified. No schema added. No commit. No push.*
