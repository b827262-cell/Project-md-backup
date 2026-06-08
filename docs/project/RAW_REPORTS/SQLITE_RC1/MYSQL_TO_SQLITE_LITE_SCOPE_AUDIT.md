# MySQL → SQLite Lite Scope Audit

## 1. Executive Summary

- **SmartBook Lite 是否需要全量 179 張表？**
  不需要。專案中有大量已被封存的 RAG/VectorDB 欄位、自動同步日誌、舊版 AI 教室、語音播放清單等已停用或開發階段的遺留資料表（共計 79 張可直接 Defer/Archive）。
- **實際 MVP 需要幾張表？**
  核心 MVP 僅需要 **43 張表** (Must Migrate) 即可支援主體業務。如需完整保留目前的線上功能（包含考試系統、影片課程、講義管理等），則需要另外遷移 **57 張表** (Should Migrate)，共計 100 張表。
- **是否建議走 Lite MVP 遷移？**
  是。強烈建議僅遷移必需表與當前使用表（共計 100 張），將其餘 79 張無效資料表 Defer/Archive，能大幅簡化 Schema 方言轉換工作量並減少 SQLite 初始化與 Migrations 開銷。
- **是否存在會阻擋 SQLite 的 mysql2 原生依賴？**
  是。存在 2 個核心 Router 文件與 7 個腳本檔案直接依賴 `mysql2/promise`。在進行 SQLite 遷移前，這些直接連線必須重構為使用 Drizzle 或相容的 SQLite 連線。

---

## 2. Runtime Feature Table Usage

| Feature | Required Tables | Evidence Files | Risk |
|---|---|---|---|
| SmartBook / PDF Viewer | `smart_books`, `smart_book_chapters`, `smart_book_categories`, `smart_book_progress`, `smart_book_chapter_qa`, `smart_book_review_questions`, `smart_book_wrong_answers`, `smart_book_quiz_sessions`, `smart_book_saved_messages`, `smart_book_settings`, `smart_book_credits`, `smart_book_credit_transactions`, `smart_book_verifications`, `smart_book_conversations`, `smart_book_qa_viewed`, `smart_book_chapter_completions`, `smart_book_chapter_daily_verifications`, `smart_book_unit_qa`, `smart_book_unit_qa_answers`, `smart_book_learning_sessions`, `smart_book_question_shown`, `book_suggestion_cache`, `book_voucher_records`, `book_custom_suggestions`, `lesson_points`, `lesson_progress`, `pdf_categories` | `server/routers/smartBookRouter.ts`<br>`server/routers/smartBookLearningRouter.ts`<br>`server/routers/lessonPointsRouter.ts`<br>`server/pdf-proxy.ts` | **低**。均為標準資料結構，對應關係明確。 |
| TutorChat | `tutor_chat_sessions`, `tutor_chat_messages`, `tutor_subject_books`, `tutor_subject_exam_sources`, `tutor_subject_video_courses`, `tutor_subjects`, `conversations`, `messages` | `server/routers/tutorRouter.ts`<br>`server/tutorChatStream.ts`<br>`server/routers/adminConversationsRouter.ts` | **低至中**。部分對話歷史包含複雜文字及關聯，需注意外鍵級聯刪除。 |
| Exam System | `exam_questions`, `real_exam_questions`, `real_exam_attempts`, `exam_categories`, `exam_subjects`, `ai_generated_exams`, `ai_generated_questions`, `ai_exam_attempts`, `question_bank`, `question_groups`, `question_images`, `question_references`, `exam_sets`, `exam_set_questions`, `exam_set_sub_questions`, `exam_wrong_book`, `exam_notes`, `practice_exams`, `practice_exam_questions`, `practice_records`, `practice_answers`, `practice_wrong_book` | `server/routers/realExamRouter.ts`<br>`server/routers/examSetRouter.ts`<br>`server/routers/aiQuestionBankRouter.ts` | **中**。有複雜關聯與 JSON 欄位（儲存題目與答案結構），需注意序列化轉換。 |
| Video Course | `video_units`, `video_knowledge_points`, `video_progress`, `saved_qa`, `video_unit_questions` | `server/routers/videoCourseRouter.ts` | **低**。資料結構簡單，多為進度與對應關係。 |
| Auth / Login | `users` | `server/localAuth.ts`<br>`server/_core/context.ts` | **低**。標準帳密與 OpenID 驗證。 |
| User / Role | `users`, `user_usage_stats`, `credit_transactions`, `system_settings` | `server/routers/userManagement.ts` | **低**。使用者權限分級，基本無相容性問題。 |

---

## 3. Recommended SQLite MVP Tables

### Must Migrate (43 Tables)
必須遷移的核心資料表，支援 SmartBook 閱讀、TutorChat 互動與使用者額度/點數模組：
- `book_custom_suggestions`
- `book_suggestion_cache`
- `book_voucher_records`
- `conversation_files`
- `conversation_tags`
- `conversations`
- `credit_rules`
- `credit_transactions`
- `lesson_points`
- `lesson_progress`
- `messages`
- `pdf_categories`
- `smart_book_categories`
- `smart_book_chapter_completions`
- `smart_book_chapter_daily_verifications`
- `smart_book_chapter_qa`
- `smart_book_chapters`
- `smart_book_conversations`
- `smart_book_credit_transactions`
- `smart_book_credits`
- `smart_book_learning_sessions`
- `smart_book_progress`
- `smart_book_qa_viewed`
- `smart_book_question_shown`
- `smart_book_quiz_sessions`
- `smart_book_review_questions`
- `smart_book_saved_messages`
- `smart_book_settings`
- `smart_book_unit_qa`
- `smart_book_unit_qa_answers`
- `smart_book_verifications`
- `smart_book_wrong_answers`
- `smart_books`
- `system_settings`
- `tags`
- `tutor_chat_messages`
- `tutor_chat_sessions`
- `tutor_subject_books`
- `tutor_subject_exam_sources`
- `tutor_subject_video_courses`
- `tutor_subjects`
- `user_usage_stats`
- `users`

### Should Migrate (57 Tables)
建議遷移的資料表，支援考試、影片課程、教材講義管理、系統公告與申論題批改功能，以確保全量功能正常運作：
- `ai_exam_attempts`
- `ai_generated_exams`
- `ai_generated_questions`
- `announcement_reads`
- `announcements`
- `banners`
- `books`
- `calendar_events`
- `course_access`
- `course_enrollments`
- `courses`
- `essay_gradings`
- `essay_submissions`
- `exam_categories`
- `exam_notes`
- `exam_questions`
- `exam_set_questions`
- `exam_set_sub_questions`
- `exam_sets`
- `exam_subjects`
- `exam_wrong_book`
- `faq_feedback`
- `faqs`
- `feedback`
- `graduate_exams`
- `graduate_pdf_links_cache`
- `graduate_school_favorites`
- `graduate_schools`
- `learning_conversations`
- `learning_materials`
- `lecture_courses`
- `lecture_teacher_subjects`
- `lecture_teachers`
- `material_contents`
- `material_conversations`
- `practice_answers`
- `practice_exam_questions`
- `practice_exams`
- `practice_records`
- `practice_wrong_book`
- `question_bank`
- `question_bank_history`
- `question_groups`
- `question_images`
- `question_references`
- `real_exam_attempts`
- `real_exam_questions`
- `saved_answers`
- `saved_qa`
- `subject_categories`
- `teacher_materials`
- `teachers`
- `video_knowledge_points`
- `video_progress`
- `video_unit_questions`
- `video_units`
- `watermark_settings`

### Defer / Archive (79 Tables)
暫不遷移的資料表。主要包含已被停用的向量檢索 (RAG)、Google Drive 同步機制，以及開發中廢棄的遺留資料結構：
- `ai_classroom_lessons`
- `ai_classroom_records`
- `ai_question_sources`
- `api_key_usage_logs`
- `api_keys`
- `auditory_playlists`
- `auditory_watch_progress`
- `auto_sync_jobs`
- `auto_sync_logs`
- `batch_extract_logs`
- `checklist_submissions`
- `class_verifications`
- `cloud_knowledge_base_config`
- `exam_download_history`
- `exam_purchases`
- `external_resources`
- `external_search_buttons`
- `extraction_logs`
- `gaodian_exams`
- `gaodian_pdf_links_cache`
- `goldensun_sync_jobs`
- `google_drive_sync`
- `graduate_exam_downloads`
- `ibrain_packages`
- `ibrain_questions`
- `knowledge_base_categories`
- `knowledge_base_pages`
- `knowledge_base_pdfs`
- `knowledge_chunks`
- `knowledge_learning_messages`
- `knowledge_learning_sessions`
- `knowledge_learning_topics`
- `knowledge_upload_history`
- `law_articles`
- `law_bookmarks`
- `law_learning_history`
- `law_quiz_mistakes`
- `learning_material_exam_sets`
- `learning_outlines`
- `learning_progress`
- `material_access`
- `material_question_attempts`
- `material_reading_progress`
- `ollama_region_ip_rules`
- `ollama_regions`
- `page_ai_response_cache`
- `page_text_cache`
- `past_exam_papers`
- `point_transactions`
- `qa_cache`
- `qa_records`
- `question_attempts`
- `question_learning_conversations`
- `quiz_cache`
- `quiz_history`
- `quiz_wrong_questions`
- `recommendation_logs`
- `smart_book_category_exam_sources`
- `smart_book_chapter_quizzes`
- `standard_answers`
- `student_behavior_alerts`
- `student_learning_sessions`
- `student_questions`
- `student_transcript_edits`
- `study_sessions`
- `subjects`
- `transcript_correction_requests`
- `tutor_chat_folders`
- `tutor_chat_labels`
- `tutor_chat_session_labels`
- `user_points`
- `user_points_log`
- `user_practice_history`
- `user_preferences`
- `user_question_stats`
- `user_warnings`
- `video_courses`
- `web_search_logs`
- `wrong_questions`

---

## 4. mysql2 Dependency Audit

| File | mysql2 Usage | Runtime Feature | SQLite Risk | Refactor Recommendation |
|---|---|---|---|---|
| `server/db.ts` | `import { drizzle } from "drizzle-orm/mysql2";` | 資料庫初始化核心入口 | **高** (直接阻擋 SQLite) | 改為 `import { drizzle } from "drizzle-orm/better-sqlite3";` 並依據 DATABASE_URL 動態加載。 |
| `server/routers/aiQuestionBankRouter.ts` | `import mysql from "mysql2/promise";`<br>`mysql.createConnection(process.env.DATABASE_URL)` | 題庫上傳與解析 | **高** (直接阻擋 SQLite) | 重構為使用 Drizzle ORM 物件操作資料庫，避免直接調用 mysql2 連線。 |
| `server/learningMaterials.ts` | `const { default: mysql2 } = await import('mysql2/promise');`<br>`mysql2.createConnection(process.env.DATABASE_URL!)` | 講義材料查詢與處理 | **高** (直接阻擋 SQLite) | 移除 mysql2 動態加載，將其重寫為 Drizzle SQL 執行語法。 |
| `server/import_to_database.ts` | `import mysql from 'mysql2/promise';`<br>`import { drizzle } from 'drizzle-orm/mysql2';` | 資料庫導入腳本 | **低** (開發/運維工具) | 改用 SQLite 資料轉入專用 node 腳本，避免直接調用 mysql 驅動。 |
| `server/seed-questions.mjs` | `import mysql from "mysql2/promise";` | 題庫種子資料導入工具 | **低** (開發工具) | 重構為以 Drizzle 或 better-sqlite3 執行種子寫入。 |
| `scripts/fix_extracted_text_slow.mjs` | `import mysql from 'mysql2/promise';` | 講義文字緊急修復工具 | **低** (運維工具) | 重構為使用 SQLite 相容連線。 |
| `scripts/fix-smart-book-pdf-keys.ts` | `import mysql from "mysql2/promise";` | 書籍 PDF 鍵值修復工具 | **低** (運維工具) | 重構為使用 SQLite 相容連線。 |
| `scripts/seed-exam-data.mjs` | `import { drizzle } from "drizzle-orm/mysql2";` | 考卷資料種子工具 | **低** (開發工具) | 修改 drizzle import 方言為 better-sqlite3。 |
| `scripts/fix_extracted_text.mjs` | `import mysql from 'mysql2/promise';` | 講義文字修復工具 | **低** (運維工具) | 重構為使用 SQLite 相容連線。 |

---

## 5. SQLite Migration Strategy

### Option A — Full Migration (179 Tables)
全量資料表轉換，保留所有資料庫定義。
- **估計工時**：約 30 ~ 36 小時 (大部分時間消耗在處理大量不活躍表的方言錯誤與測試調整中)。
- **風險**：較高。179 張表中有大量測試和棄用表，在 SQLite 中強制運行會增加維護負擔、產生無意義的 Migrations 歷史。
- **是否建議**：**否**。

### Option B — Lite MVP Migration (100 Tables)
僅遷移 SmartBook Lite runtime 所需的核心表與當前使用表（43 Must + 57 Should），對其餘 79 張表進行 Defer/Archive。
- **估計工時**：19 小時 (專注於核心 100 張表的相容性測試)。
- **風險**：低。已停用的向量與同步模組被精確隔離，不會影響線上主體服務。
- **是否建議**：**是 (強烈建議)**。

---

## 6. Final Recommendation

**Recommendation**: **Lite MVP Migration** (Option B)

**Reason**:
在 VPS 記憶體受限的環境下，僅轉換核心的 100 張活躍表，可以大幅降低 SQLite 的初始化開銷與代碼重構成本。被 Defer/Archive 的 79 張表多為已停用的 RAG 模組與舊代碼遺留，排除這些表能使 Schema 更加精簡高效。

**Estimated Work**:
19 小時

**Top 3 Risks**:
1. **直接 mysql2 連線調用**：`aiQuestionBankRouter.ts` 與 `learningMaterials.ts` 中的原生連線程式碼，在切換到 SQLite 後會直接報錯崩潰，必須在 Phase 1-C 完成重構。
2. **多行程併發寫入鎖定**：SQLite 在處理高併發寫入時容易出現 `SQLITE_BUSY`。需啟用 WAL 模式並嚴格管理連線池。
3. **JSON 與 Timestamp 資料格式失真**：由於 SQLite 沒有原生 JSON 和 TIMESTAMP 型別，在資料從 MySQL 遷移至 SQLite 時，可能發生序列化格式與時區偏離。

**Next Phase**: **Phase 1-C SQLite MVP Schema Draft**
