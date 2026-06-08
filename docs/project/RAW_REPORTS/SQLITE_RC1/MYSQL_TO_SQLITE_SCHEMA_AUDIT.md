# MySQL → SQLite Audit

## Database Tables

| Table | Rows Estimate | Risk |
|---------|---------|---------|
| ai_classroom_lessons | 0 | Medium (JSON mapping required) |
| ai_classroom_records | 2 | Low (BigInt maps to dynamic integer) |
| ai_exam_attempts | 0 | Medium (JSON mapping required) |
| ai_generated_exams | 0 | Medium (JSON mapping required) |
| ai_generated_questions | 0 | Medium (JSON mapping required) |
| ai_question_sources | 0 | Medium (JSON mapping required) |
| announcement_reads | 0 | Low-Medium (Timestamp mapping) |
| announcements | 0 | Medium (JSON mapping required) |
| api_key_usage_logs | 0 | Low-Medium (Timestamp mapping) |
| api_keys | 0 | Low-Medium (Timestamp mapping) |
| auditory_playlists | 0 | Low-Medium (Timestamp mapping) |
| auditory_watch_progress | 0 | Low-Medium (Timestamp mapping) |
| auto_sync_jobs | 0 | Low-Medium (ENUM mapped to TEXT) |
| auto_sync_logs | 0 | Low-Medium (ENUM mapped to TEXT) |
| banners | 0 | Low-Medium (ENUM mapped to TEXT) |
| batch_extract_logs | 0 | Medium (JSON mapping required) |
| book_custom_suggestions | 0 | Low-Medium (ENUM mapped to TEXT) |
| book_suggestion_cache | 19 | Low (BigInt maps to dynamic integer) |
| book_voucher_records | 0 | Low (BigInt maps to dynamic integer) |
| books | 0 | Low-Medium (Timestamp mapping) |
| calendar_events | 0 | Low-Medium (ENUM mapped to TEXT) |
| checklist_submissions | 0 | Medium (JSON mapping required) |
| class_verifications | 0 | Low-Medium (ENUM mapped to TEXT) |
| cloud_knowledge_base_config | 0 | Low-Medium (Timestamp mapping) |
| conversation_files | 0 | Low-Medium (Timestamp mapping) |
| conversation_tags | 0 | Low-Medium (Timestamp mapping) |
| conversations | 0 | Low-Medium (Timestamp mapping) |
| course_access | 0 | Low-Medium (Timestamp mapping) |
| course_enrollments | 0 | Low-Medium (Timestamp mapping) |
| courses | 0 | Low-Medium (ENUM mapped to TEXT) |
| credit_rules | 0 | Low-Medium (Timestamp mapping) |
| credit_transactions | 8 | Low-Medium (ENUM mapped to TEXT) |
| essay_gradings | 0 | Medium (JSON mapping required) |
| essay_submissions | 0 | Low-Medium (Timestamp mapping) |
| exam_categories | 0 | Low-Medium (Timestamp mapping) |
| exam_download_history | 0 | Low-Medium (Timestamp mapping) |
| exam_notes | 0 | Low (BigInt maps to dynamic integer) |
| exam_purchases | 0 | Low-Medium (Timestamp mapping) |
| exam_questions | 0 | Low-Medium (ENUM mapped to TEXT) |
| exam_set_questions | 0 | Medium (JSON mapping required) |
| exam_set_sub_questions | 0 | Low (Standard types) |
| exam_sets | 0 | Low (BigInt maps to dynamic integer) |
| exam_subjects | 0 | Low-Medium (Timestamp mapping) |
| exam_wrong_book | 0 | Low (BigInt maps to dynamic integer) |
| external_resources | 0 | Medium (JSON mapping required) |
| external_search_buttons | 0 | Low-Medium (ENUM mapped to TEXT) |
| extraction_logs | 0 | Low-Medium (ENUM mapped to TEXT) |
| faq_feedback | 0 | Low-Medium (Timestamp mapping) |
| faqs | 0 | Low-Medium (ENUM mapped to TEXT) |
| feedback | 0 | Low-Medium (ENUM mapped to TEXT) |
| gaodian_exams | 0 | Low-Medium (ENUM mapped to TEXT) |
| gaodian_pdf_links_cache | 0 | Medium (JSON mapping required) |
| goldensun_sync_jobs | 0 | Low-Medium (ENUM mapped to TEXT) |
| google_drive_sync | 0 | Low-Medium (ENUM mapped to TEXT) |
| graduate_exam_downloads | 0 | Low-Medium (ENUM mapped to TEXT) |
| graduate_exams | 0 | Low-Medium (ENUM mapped to TEXT) |
| graduate_pdf_links_cache | 0 | Medium (JSON mapping required) |
| graduate_school_favorites | 0 | Low-Medium (Timestamp mapping) |
| graduate_schools | 0 | Low-Medium (ENUM mapped to TEXT) |
| ibrain_packages | 0 | Medium (JSON mapping required) |
| ibrain_questions | 0 | Medium (JSON mapping required) |
| knowledge_base_categories | 0 | Low-Medium (Timestamp mapping) |
| knowledge_base_pages | 0 | Low-Medium (Timestamp mapping) |
| knowledge_base_pdfs | 0 | Low-Medium (ENUM mapped to TEXT) |
| knowledge_chunks | 0 | Medium (JSON mapping required) |
| knowledge_learning_messages | 0 | Medium (JSON mapping required) |
| knowledge_learning_sessions | 2 | Low-Medium (ENUM mapped to TEXT) |
| knowledge_learning_topics | 0 | Low-Medium (Timestamp mapping) |
| knowledge_upload_history | 0 | Low-Medium (ENUM mapped to TEXT) |
| law_articles | 0 | Low-Medium (Timestamp mapping) |
| law_bookmarks | 0 | Low-Medium (Timestamp mapping) |
| law_learning_history | 0 | Medium (JSON mapping required) |
| law_quiz_mistakes | 0 | Medium (JSON mapping required) |
| learning_conversations | 0 | Medium (JSON mapping required) |
| learning_material_exam_sets | 0 | Low (BigInt maps to dynamic integer) |
| learning_materials | 0 | Medium (JSON mapping required) |
| learning_outlines | 0 | Medium (JSON mapping required) |
| learning_progress | 0 | Medium (JSON mapping required) |
| lecture_courses | 0 | Low-Medium (ENUM mapped to TEXT) |
| lecture_teacher_subjects | 0 | Low-Medium (Timestamp mapping) |
| lecture_teachers | 0 | Low-Medium (Timestamp mapping) |
| lesson_points | 1640 | Medium (JSON mapping required) |
| lesson_progress | 0 | Low-Medium (Timestamp mapping) |
| material_access | 0 | Low-Medium (Timestamp mapping) |
| material_contents | 0 | Low-Medium (Timestamp mapping) |
| material_conversations | 0 | Medium (JSON mapping required) |
| material_question_attempts | 0 | Low-Medium (Timestamp mapping) |
| material_reading_progress | 0 | Low-Medium (Timestamp mapping) |
| messages | 0 | Medium (JSON mapping required) |
| ollama_region_ip_rules | 0 | Low-Medium (Timestamp mapping) |
| ollama_regions | 0 | Low-Medium (Timestamp mapping) |
| page_ai_response_cache | 0 | Low (BigInt maps to dynamic integer) |
| page_text_cache | 8 | Low (BigInt maps to dynamic integer) |
| past_exam_papers | 0 | Low-Medium (ENUM mapped to TEXT) |
| pdf_categories | 5 | Low-Medium (ENUM mapped to TEXT) |
| point_transactions | 0 | Low-Medium (ENUM mapped to TEXT) |
| practice_answers | 0 | Low-Medium (Timestamp mapping) |
| practice_exam_questions | 0 | Low-Medium (Timestamp mapping) |
| practice_exams | 0 | Low-Medium (ENUM mapped to TEXT) |
| practice_records | 0 | Low-Medium (ENUM mapped to TEXT) |
| practice_wrong_book | 0 | Medium (JSON mapping required) |
| qa_cache | 0 | Medium (JSON mapping required) |
| qa_records | 0 | Medium (JSON mapping required) |
| question_attempts | 0 | Low-Medium (Timestamp mapping) |
| question_bank | 0 | Medium (JSON mapping required) |
| question_bank_history | 0 | Medium (JSON mapping required) |
| question_groups | 0 | Medium (JSON mapping required) |
| question_images | 0 | Medium (JSON mapping required) |
| question_learning_conversations | 0 | Medium (JSON mapping required) |
| question_references | 0 | Low-Medium (ENUM mapped to TEXT) |
| quiz_cache | 0 | Medium (JSON mapping required) |
| quiz_history | 0 | Medium (JSON mapping required) |
| quiz_wrong_questions | 0 | Medium (JSON mapping required) |
| real_exam_attempts | 0 | Medium (JSON mapping required) |
| real_exam_questions | 0 | Medium (JSON mapping required) |
| recommendation_logs | 0 | Low-Medium (ENUM mapped to TEXT) |
| saved_answers | 0 | Low-Medium (Timestamp mapping) |
| saved_qa | 0 | Low-Medium (Timestamp mapping) |
| smart_book_categories | 0 | Low-Medium (Timestamp mapping) |
| smart_book_category_exam_sources | 0 | Low-Medium (ENUM mapped to TEXT) |
| smart_book_chapter_completions | 0 | Low-Medium (Timestamp mapping) |
| smart_book_chapter_daily_verifications | 0 | Low-Medium (Timestamp mapping) |
| smart_book_chapter_qa | 35 | Low-Medium (Timestamp mapping) |
| smart_book_chapter_quizzes | 0 | Low-Medium (Timestamp mapping) |
| smart_book_chapters | 81 | Medium (JSON mapping required) |
| smart_book_conversations | 0 | Low-Medium (ENUM mapped to TEXT) |
| smart_book_credit_transactions | 0 | Low-Medium (ENUM mapped to TEXT) |
| smart_book_credits | 0 | Low-Medium (Timestamp mapping) |
| smart_book_learning_sessions | 0 | Low-Medium (Timestamp mapping) |
| smart_book_progress | 0 | Low-Medium (Timestamp mapping) |
| smart_book_qa_viewed | 0 | Low-Medium (Timestamp mapping) |
| smart_book_question_shown | 0 | Low-Medium (Timestamp mapping) |
| smart_book_quiz_sessions | 0 | Low-Medium (ENUM mapped to TEXT) |
| smart_book_review_questions | 553 | Medium (JSON mapping required) |
| smart_book_saved_messages | 20 | Low-Medium (Timestamp mapping) |
| smart_book_settings | 5 | Low-Medium (Timestamp mapping) |
| smart_book_unit_qa | 0 | Medium (JSON mapping required) |
| smart_book_unit_qa_answers | 0 | Low-Medium (Timestamp mapping) |
| smart_book_verifications | 0 | Low-Medium (ENUM mapped to TEXT) |
| smart_book_wrong_answers | 0 | Medium (JSON mapping required) |
| smart_books | 3 | Medium (JSON mapping required) |
| standard_answers | 0 | Low-Medium (ENUM mapped to TEXT) |
| student_behavior_alerts | 0 | Medium (JSON mapping required) |
| student_learning_sessions | 0 | Medium (JSON mapping required) |
| student_questions | 0 | Low-Medium (ENUM mapped to TEXT) |
| student_transcript_edits | 0 | Low-Medium (Timestamp mapping) |
| study_sessions | 0 | Low-Medium (Timestamp mapping) |
| subject_categories | 0 | Low-Medium (Timestamp mapping) |
| subjects | 0 | Low-Medium (Timestamp mapping) |
| system_settings | 0 | Low-Medium (Timestamp mapping) |
| tags | 0 | Low-Medium (Timestamp mapping) |
| teacher_materials | 0 | Low-Medium (ENUM mapped to TEXT) |
| teachers | 0 | Low-Medium (Timestamp mapping) |
| transcript_correction_requests | 0 | Low-Medium (ENUM mapped to TEXT) |
| tutor_chat_folders | 0 | Low (BigInt maps to dynamic integer) |
| tutor_chat_labels | 0 | Low (BigInt maps to dynamic integer) |
| tutor_chat_messages | 12 | Medium (JSON mapping required) |
| tutor_chat_session_labels | 0 | Low (BigInt maps to dynamic integer) |
| tutor_chat_sessions | 4 | Low (BigInt maps to dynamic integer) |
| tutor_subject_books | 2 | Low (BigInt maps to dynamic integer) |
| tutor_subject_exam_sources | 0 | Low-Medium (ENUM mapped to TEXT) |
| tutor_subject_video_courses | 0 | Low (BigInt maps to dynamic integer) |
| tutor_subjects | 3 | Low (BigInt maps to dynamic integer) |
| user_points | 0 | Low-Medium (Timestamp mapping) |
| user_points_log | 0 | Low-Medium (Timestamp mapping) |
| user_practice_history | 0 | Low-Medium (ENUM mapped to TEXT) |
| user_preferences | 0 | Low (BigInt maps to dynamic integer) |
| user_question_stats | 0 | Low-Medium (Timestamp mapping) |
| user_usage_stats | 0 | Low-Medium (Timestamp mapping) |
| user_warnings | 0 | Low-Medium (Timestamp mapping) |
| users | 0 | Low-Medium (ENUM mapped to TEXT) |
| video_courses | 0 | Low (BigInt maps to dynamic integer) |
| video_knowledge_points | 6 | Low (Standard types) |
| video_progress | 0 | Low (BigInt maps to dynamic integer) |
| video_unit_questions | 0 | Low (BigInt maps to dynamic integer) |
| video_units | 2 | Low (BigInt maps to dynamic integer) |
| watermark_settings | 0 | Low (BigInt maps to dynamic integer) |
| web_search_logs | 0 | Low-Medium (Timestamp mapping) |
| wrong_questions | 0 | Low-Medium (ENUM mapped to TEXT) |

---

## MySQL Specific Types

| Table | Column | MySQL Type | SQLite Mapping | Risk |
|---------|---------|---------|---------|---------|
| ai_classroom_lessons | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| ai_classroom_lessons | is_edited | tinyint | integer() | Low (Acts as boolean or small int) |
| ai_classroom_lessons | knowledge_points | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_classroom_lessons | status | varchar | text() | Low |
| ai_classroom_lessons | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| ai_classroom_records | completed_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| ai_classroom_records | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| ai_classroom_records | is_completed | tinyint | integer() | Low (Acts as boolean or small int) |
| ai_classroom_records | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| ai_exam_attempts | answers | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_exam_attempts | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_exam_attempts | started_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_exam_attempts | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_exam_attempts | submitted_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_generated_exams | category | varchar | text() | Low |
| ai_generated_exams | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_generated_exams | custom_category | varchar | text() | Low |
| ai_generated_exams | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_generated_exams | essay_is_public | tinyint | integer() | Low (Acts as boolean or small int) |
| ai_generated_exams | exam_group | varchar | text() | Low |
| ai_generated_exams | is_public | tinyint | integer() | Low (Acts as boolean or small int) |
| ai_generated_exams | question_types | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_generated_exams | selected_chapters | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_generated_exams | source_ids | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_generated_exams | source_types | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_generated_exams | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_generated_exams | title | varchar | text() | Low |
| ai_generated_exams | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_generated_questions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_generated_questions | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_generated_questions | is_edited | tinyint | integer() | Low (Acts as boolean or small int) |
| ai_generated_questions | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_generated_questions | question_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_generated_questions | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_question_sources | category | varchar | text() | Low |
| ai_question_sources | chapters | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ai_question_sources | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_question_sources | custom_category | varchar | text() | Low |
| ai_question_sources | detected_subject | varchar | text() | Low |
| ai_question_sources | exam_group | varchar | text() | Low |
| ai_question_sources | extracted_text | longtext | text() | Low |
| ai_question_sources | file_key | varchar | text() | Low |
| ai_question_sources | file_name | varchar | text() | Low |
| ai_question_sources | file_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_question_sources | file_url | varchar | text() | Low |
| ai_question_sources | is_published | tinyint | integer() | Low (Acts as boolean or small int) |
| ai_question_sources | processing_started_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_question_sources | processing_step | varchar | text() | Low |
| ai_question_sources | source_origin | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_question_sources | source_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_question_sources | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ai_question_sources | teacher_name | varchar | text() | Low |
| ai_question_sources | title | varchar | text() | Low |
| ai_question_sources | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ai_question_sources | year | varchar | text() | Low |
| announcement_reads | readAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| announcements | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| announcements | expiresAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| announcements | isPinned | tinyint | integer() | Low (Acts as boolean or small int) |
| announcements | priority | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| announcements | publishedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| announcements | source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| announcements | targetAudience | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| announcements | targetUserIds | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| announcements | title | varchar | text() | Low |
| announcements | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| announcements | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| api_key_usage_logs | anomaly_reason | varchar | text() | Low |
| api_key_usage_logs | caller_ip | varchar | text() | Low |
| api_key_usage_logs | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| api_key_usage_logs | is_anomaly | tinyint | integer() | Low (Acts as boolean or small int) |
| api_keys | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| api_keys | expires_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| api_keys | is_active | tinyint | integer() | Low (Acts as boolean or small int) |
| api_keys | is_anomaly_locked | tinyint | integer() | Low (Acts as boolean or small int) |
| api_keys | key_hash | varchar | text() | Low |
| api_keys | key_prefix | varchar | text() | Low |
| api_keys | last_reset_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| api_keys | last_used_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| api_keys | lock_reason | varchar | text() | Low |
| api_keys | name | varchar | text() | Low |
| api_keys | total_token_count | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| api_keys | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auditory_playlists | category | varchar | text() | Low |
| auditory_playlists | corrected_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auditory_playlists | corrected_transcript_text | longtext | text() | Low |
| auditory_playlists | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auditory_playlists | is_active | tinyint | integer() | Low (Acts as boolean or small int) |
| auditory_playlists | title | varchar | text() | Low |
| auditory_playlists | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auditory_playlists | youtube_playlist_id | varchar | text() | Low |
| auditory_watch_progress | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auto_sync_jobs | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auto_sync_jobs | lastRunAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auto_sync_jobs | nextRunAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auto_sync_jobs | scheduleTime | varchar | text() | Low |
| auto_sync_jobs | scheduleType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| auto_sync_jobs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| auto_sync_jobs | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auto_sync_logs | fileId | varchar | text() | Low |
| auto_sync_logs | fileName | varchar | text() | Low |
| auto_sync_logs | processedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| auto_sync_logs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| banners | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| banners | isActive | tinyint | integer() | Low (Acts as boolean or small int) |
| banners | targetAudience | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| banners | title | varchar | text() | Low |
| banners | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| batch_extract_logs | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| batch_extract_logs | results | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| batch_extract_logs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| book_custom_suggestions | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| book_custom_suggestions | is_active | tinyint | integer() | Low (Acts as boolean or small int) |
| book_custom_suggestions | question | varchar | text() | Low |
| book_custom_suggestions | source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| book_custom_suggestions | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| book_suggestion_cache | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| book_suggestion_cache | question | varchar | text() | Low |
| book_voucher_records | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| book_voucher_records | voucher_code | varchar | text() | Low |
| books | author | varchar | text() | Low |
| books | category | varchar | text() | Low |
| books | coverImage | varchar | text() | Low |
| books | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| books | examType | varchar | text() | Low |
| books | id | varchar | text() | Low |
| books | productUrl | varchar | text() | Low |
| books | sourceWebsite | varchar | text() | Low |
| books | title | varchar | text() | Low |
| books | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| calendar_events | color | varchar | text() | Low |
| calendar_events | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| calendar_events | end_time | varchar | text() | Low |
| calendar_events | event_date | varchar | text() | Low |
| calendar_events | event_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| calendar_events | is_pinned | tinyint | integer() | Low (Acts as boolean or small int) |
| calendar_events | start_time | varchar | text() | Low |
| calendar_events | title | varchar | text() | Low |
| calendar_events | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| calendar_events | visibility | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| checklist_submissions | checklist_items | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| checklist_submissions | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| checklist_submissions | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| checklist_submissions | tested_module | varchar | text() | Low |
| checklist_submissions | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| checklist_submissions | user_name | varchar | text() | Low |
| checklist_submissions | user_role | varchar | text() | Low |
| class_verifications | expires_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| class_verifications | resource_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| class_verifications | student_id | varchar | text() | Low |
| class_verifications | verified_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| cloud_knowledge_base_config | apiKey | varchar | text() | Low |
| cloud_knowledge_base_config | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| cloud_knowledge_base_config | isActive | tinyint | integer() | Low (Acts as boolean or small int) |
| cloud_knowledge_base_config | lastUsedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| conversation_files | extractedContent | longtext | text() | Low |
| conversation_files | fileName | varchar | text() | Low |
| conversation_files | mimeType | varchar | text() | Low |
| conversation_files | uploadedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| conversation_tags | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| conversations | chatStyle | varchar | text() | Low |
| conversations | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| conversations | is_trial_hidden | tinyint | integer() | Low (Acts as boolean or small int) |
| conversations | lastMessageAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| conversations | subject | varchar | text() | Low |
| conversations | title | varchar | text() | Low |
| conversations | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| course_access | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| course_enrollments | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| course_enrollments | enrolledAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| course_enrollments | expiresAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| course_enrollments | isActive | tinyint | integer() | Low (Acts as boolean or small int) |
| course_enrollments | note | varchar | text() | Low |
| course_enrollments | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| courses | category | varchar | text() | Low |
| courses | courseType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| courses | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| courses | duration | varchar | text() | Low |
| courses | examType | varchar | text() | Low |
| courses | id | varchar | text() | Low |
| courses | instructor | varchar | text() | Low |
| courses | previewUrl | varchar | text() | Low |
| courses | productUrl | varchar | text() | Low |
| courses | sourceWebsite | varchar | text() | Low |
| courses | targetAudience | varchar | text() | Low |
| courses | title | varchar | text() | Low |
| courses | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| credit_rules | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| credit_rules | description | varchar | text() | Low |
| credit_rules | isEnabled | tinyint | integer() | Low (Acts as boolean or small int) |
| credit_rules | ruleKey | varchar | text() | Low |
| credit_rules | ruleName | varchar | text() | Low |
| credit_rules | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| credit_transactions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| credit_transactions | description | varchar | text() | Low |
| credit_transactions | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| essay_gradings | grade | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| essay_gradings | gradedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| essay_gradings | keyPointsCovered | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| essay_gradings | keyPointsMissed | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| essay_gradings | paragraphFeedback | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| essay_submissions | submittedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_categories | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_categories | name | varchar | text() | Low |
| exam_download_history | category_code | varchar | text() | Low |
| exam_download_history | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_download_history | exam_code | varchar | text() | Low |
| exam_download_history | subject_code | varchar | text() | Low |
| exam_download_history | task_id | varchar | text() | Low |
| exam_notes | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_notes | note_text | longtext | text() | Low |
| exam_notes | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_purchases | purchasedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_questions | accessControl | varchar | text() | Low |
| exam_questions | accessType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| exam_questions | correctAnswer | varchar | text() | Low |
| exam_questions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_questions | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| exam_questions | questionNumberInPdf | varchar | text() | Low |
| exam_questions | questionType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| exam_questions | reviewedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_questions | source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| exam_questions | sourceHash | varchar | text() | Low |
| exam_questions | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| exam_questions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_set_questions | answer_text | longtext | text() | Low |
| exam_set_questions | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_set_questions | explanation | longtext | text() | Low |
| exam_set_questions | has_answer | tinyint | integer() | Low (Acts as boolean or small int) |
| exam_set_questions | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| exam_set_questions | question_no | varchar | text() | Low |
| exam_set_questions | question_text | longtext | text() | Low |
| exam_set_questions | question_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| exam_set_questions | reference_pages | varchar | text() | Low |
| exam_set_questions | source_exam | varchar | text() | Low |
| exam_set_questions | source_year | varchar | text() | Low |
| exam_set_questions | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_set_sub_questions | answer_text | longtext | text() | Low |
| exam_set_sub_questions | question_text | longtext | text() | Low |
| exam_set_sub_questions | sub_no | varchar | text() | Low |
| exam_sets | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_sets | is_published | tinyint | integer() | Low (Acts as boolean or small int) |
| exam_sets | pdf_key | varchar | text() | Low |
| exam_sets | title | varchar | text() | Low |
| exam_sets | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_sets | year_range | varchar | text() | Low |
| exam_subjects | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| exam_subjects | name | varchar | text() | Low |
| exam_wrong_book | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_wrong_book | is_resolved | tinyint | integer() | Low (Acts as boolean or small int) |
| exam_wrong_book | last_answer | longtext | text() | Low |
| exam_wrong_book | last_answered_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| exam_wrong_book | resolved_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| external_resources | category | varchar | text() | Low |
| external_resources | crawledAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| external_resources | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| external_resources | source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| external_resources | tags | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| external_resources | targetExamTargets | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| external_resources | targetExamTypes | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| external_resources | title | varchar | text() | Low |
| external_resources | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| external_resources | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| external_search_buttons | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| external_search_buttons | encoding | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| external_search_buttons | icon | varchar | text() | Low |
| external_search_buttons | isActive | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| external_search_buttons | name | varchar | text() | Low |
| external_search_buttons | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| external_search_buttons | urlTemplate | varchar | text() | Low |
| extraction_logs | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| extraction_logs | pdfTitle | varchar | text() | Low |
| extraction_logs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| faq_feedback | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| faq_feedback | isHelpful | tinyint | integer() | Low (Acts as boolean or small int) |
| faqs | category | varchar | text() | Low |
| faqs | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| faqs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| faqs | topic | varchar | text() | Low |
| faqs | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| feedback | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| feedback | repliedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| feedback | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| feedback | title | varchar | text() | Low |
| feedback | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| feedback | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| gaodian_exams | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| gaodian_exams | departmentName | varchar | text() | Low |
| gaodian_exams | examCategory | varchar | text() | Low |
| gaodian_exams | examType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| gaodian_exams | parsedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| gaodian_exams | parseStatus | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| gaodian_exams | schoolName | varchar | text() | Low |
| gaodian_exams | subjectName | varchar | text() | Low |
| gaodian_exams | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| gaodian_pdf_links_cache | cacheKey | varchar | text() | Low |
| gaodian_pdf_links_cache | crawledAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| gaodian_pdf_links_cache | examType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| gaodian_pdf_links_cache | expiresAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| gaodian_pdf_links_cache | keyword | varchar | text() | Low |
| gaodian_pdf_links_cache | links | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| gaodian_pdf_links_cache | success | tinyint | integer() | Low (Acts as boolean or small int) |
| goldensun_sync_jobs | completed_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| goldensun_sync_jobs | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| goldensun_sync_jobs | exam_group | varchar | text() | Low |
| goldensun_sync_jobs | filter_type | varchar | text() | Low |
| goldensun_sync_jobs | filter_year | varchar | text() | Low |
| goldensun_sync_jobs | started_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| goldensun_sync_jobs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| google_drive_sync | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| google_drive_sync | folderId | varchar | text() | Low |
| google_drive_sync | folderName | varchar | text() | Low |
| google_drive_sync | lastSyncAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| google_drive_sync | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| google_drive_sync | tokenExpiresAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| google_drive_sync | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_exam_downloads | downloadedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_exam_downloads | fileSize | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| graduate_exam_downloads | pdfTitle | varchar | text() | Low |
| graduate_exam_downloads | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| graduate_exam_downloads | suggestedFilename | varchar | text() | Low |
| graduate_exams | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_exams | department | varchar | text() | Low |
| graduate_exams | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| graduate_exams | subject | varchar | text() | Low |
| graduate_exams | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_pdf_links_cache | crawledAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_pdf_links_cache | expiresAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_pdf_links_cache | isManuallyEdited | tinyint | integer() | Low (Acts as boolean or small int) |
| graduate_pdf_links_cache | links | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| graduate_pdf_links_cache | success | tinyint | integer() | Low (Acts as boolean or small int) |
| graduate_school_favorites | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_schools | crawlerStatus | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| graduate_schools | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_schools | examType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| graduate_schools | lastCrawledAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| graduate_schools | schoolName | varchar | text() | Low |
| graduate_schools | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_packages | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_packages | fileName | varchar | text() | Low |
| ibrain_packages | metadata | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ibrain_packages | packageHash | varchar | text() | Low |
| ibrain_packages | processedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_packages | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ibrain_packages | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_packages | uploadedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_questions | correctAnswer | varchar | text() | Low |
| ibrain_questions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_questions | questionType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ibrain_questions | rawData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| ibrain_questions | reviewedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ibrain_questions | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ibrain_questions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_categories | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_categories | name | varchar | text() | Low |
| knowledge_base_categories | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_pages | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_pages | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_pdfs | accessType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_base_pdfs | category | varchar | text() | Low |
| knowledge_base_pdfs | contentStatus | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_base_pdfs | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_pdfs | extractedContent | longtext | text() | Low |
| knowledge_base_pdfs | fileName | varchar | text() | Low |
| knowledge_base_pdfs | lastExtractedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_pdfs | pdfType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_base_pdfs | source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_base_pdfs | sourceCategory | varchar | text() | Low |
| knowledge_base_pdfs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_base_pdfs | subject | varchar | text() | Low |
| knowledge_base_pdfs | title | varchar | text() | Low |
| knowledge_base_pdfs | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_base_pdfs | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_base_pdfs | uploadSource | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_chunks | category | varchar | text() | Low |
| knowledge_chunks | chunkHash | varchar | text() | Low |
| knowledge_chunks | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_chunks | documentId | varchar | text() | Low |
| knowledge_chunks | documentTitle | varchar | text() | Low |
| knowledge_chunks | documentType | varchar | text() | Low |
| knowledge_chunks | embeddingModel | varchar | text() | Low |
| knowledge_chunks | tags | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| knowledge_chunks | uploadBatchId | varchar | text() | Low |
| knowledge_learning_messages | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_learning_messages | role | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_learning_messages | sources | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| knowledge_learning_sessions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_learning_sessions | dailyDate | varchar | text() | Low |
| knowledge_learning_sessions | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_learning_sessions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_learning_topics | learned_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_learning_topics | topic | varchar | text() | Low |
| knowledge_upload_history | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| knowledge_upload_history | documentId | varchar | text() | Low |
| knowledge_upload_history | documentTitle | varchar | text() | Low |
| knowledge_upload_history | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| knowledge_upload_history | uploadBatchId | varchar | text() | Low |
| law_articles | articleNo | varchar | text() | Low |
| law_articles | book | varchar | text() | Low |
| law_articles | chapter | varchar | text() | Low |
| law_articles | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_articles | lawName | varchar | text() | Low |
| law_articles | section | varchar | text() | Low |
| law_bookmarks | articleNo | varchar | text() | Low |
| law_bookmarks | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_bookmarks | lawName | varchar | text() | Low |
| law_bookmarks | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_learning_history | conversationData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| law_learning_history | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_learning_history | lawName | varchar | text() | Low |
| law_learning_history | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_quiz_mistakes | correctAnswer | varchar | text() | Low |
| law_quiz_mistakes | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_quiz_mistakes | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| law_quiz_mistakes | isLearned | tinyint | integer() | Low (Acts as boolean or small int) |
| law_quiz_mistakes | lawName | varchar | text() | Low |
| law_quiz_mistakes | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| law_quiz_mistakes | relatedArticles | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| law_quiz_mistakes | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| law_quiz_mistakes | userAnswer | varchar | text() | Low |
| learning_conversations | conversationData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| learning_conversations | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_conversations | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_material_exam_sets | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| learning_materials | access_mode | varchar | text() | Low |
| learning_materials | category | varchar | text() | Low |
| learning_materials | class_code | varchar | text() | Low |
| learning_materials | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_materials | extracted_questions | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| learning_materials | fileSize | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| learning_materials | fullText | longtext | text() | Low |
| learning_materials | isPublic | tinyint | integer() | Low (Acts as boolean or small int) |
| learning_materials | questions_extracted_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_materials | subject_name | varchar | text() | Low |
| learning_materials | title | varchar | text() | Low |
| learning_materials | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_outlines | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_outlines | outlineData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| learning_outlines | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_progress | chapterTitle | varchar | text() | Low |
| learning_progress | conversationData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| learning_progress | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| learning_progress | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| learning_progress | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lecture_courses | accessMode | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| lecture_courses | classCode | varchar | text() | Low |
| lecture_courses | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lecture_courses | isActive | tinyint | integer() | Low (Acts as boolean or small int) |
| lecture_courses | isPublic | tinyint | integer() | Low (Acts as boolean or small int) |
| lecture_courses | name | varchar | text() | Low |
| lecture_courses | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lecture_teacher_subjects | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lecture_teachers | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lecture_teachers | isActive | tinyint | integer() | Low (Acts as boolean or small int) |
| lecture_teachers | name | varchar | text() | Low |
| lecture_teachers | styleContent | longtext | text() | Low |
| lecture_teachers | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_points | classroom_quiz | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| lesson_points | classroom_quiz_generated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_points | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_points | image_hint | varchar | text() | Low |
| lesson_points | image_url | varchar | text() | Low |
| lesson_points | is_published | tinyint | integer() | Low (Acts as boolean or small int) |
| lesson_points | needs_image | tinyint | integer() | Low (Acts as boolean or small int) |
| lesson_points | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| lesson_points | published_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_points | question_type | varchar | text() | Low |
| lesson_points | script_generated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_points | script_status | varchar | text() | Low |
| lesson_points | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_points | word_part_of_speech | varchar | text() | Low |
| lesson_progress | completed | tinyint | integer() | Low (Acts as boolean or small int) |
| lesson_progress | completed_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| lesson_progress | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| material_access | unlockedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| material_contents | chapterTitle | varchar | text() | Low |
| material_contents | content | longtext | text() | Low |
| material_contents | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| material_conversations | answer | longtext | text() | Low |
| material_conversations | conversationContext | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| material_conversations | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| material_conversations | isAddedToCache | tinyint | integer() | Low (Acts as boolean or small int) |
| material_conversations | materialIds | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| material_conversations | sources | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| material_question_attempts | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| material_question_attempts | is_correct | tinyint | integer() | Low (Acts as boolean or small int) |
| material_question_attempts | question_type | varchar | text() | Low |
| material_question_attempts | selected_answer | varchar | text() | Low |
| material_question_attempts | submitted | tinyint | integer() | Low (Acts as boolean or small int) |
| material_question_attempts | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| material_reading_progress | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| messages | aiModel | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| messages | attachments | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| messages | contentFlag | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| messages | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| messages | flaggedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| messages | metadata | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| messages | modelName | varchar | text() | Low |
| messages | role | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| ollama_region_ip_rules | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ollama_region_ip_rules | description | varchar | text() | Low |
| ollama_region_ip_rules | ip_cidr | varchar | text() | Low |
| ollama_region_ip_rules | is_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| ollama_regions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| ollama_regions | description | varchar | text() | Low |
| ollama_regions | is_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| ollama_regions | name | varchar | text() | Low |
| ollama_regions | ollama_endpoint | varchar | text() | Low |
| ollama_regions | ollama_model | varchar | text() | Low |
| ollama_regions | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| page_ai_response_cache | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| page_ai_response_cache | question_type | varchar | text() | Low |
| page_ai_response_cache | response | longtext | text() | Low |
| page_ai_response_cache | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| page_text_cache | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| page_text_cache | text | longtext | text() | Low |
| page_text_cache | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| past_exam_papers | category | varchar | text() | Low |
| past_exam_papers | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| past_exam_papers | department | varchar | text() | Low |
| past_exam_papers | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| past_exam_papers | examType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| past_exam_papers | extractedContent | longtext | text() | Low |
| past_exam_papers | fileName | varchar | text() | Low |
| past_exam_papers | mimeType | varchar | text() | Low |
| past_exam_papers | school | varchar | text() | Low |
| past_exam_papers | semester | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| past_exam_papers | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| past_exam_papers | subject | varchar | text() | Low |
| past_exam_papers | title | varchar | text() | Low |
| past_exam_papers | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| pdf_categories | color | varchar | text() | Low |
| pdf_categories | courseOutlineGeneratedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| pdf_categories | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| pdf_categories | displayName | varchar | text() | Low |
| pdf_categories | icon | varchar | text() | Low |
| pdf_categories | isActive | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| pdf_categories | isPublic | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| pdf_categories | name | varchar | text() | Low |
| pdf_categories | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| point_transactions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| point_transactions | related_type | varchar | text() | Low |
| point_transactions | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| practice_answers | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_answers | isCorrect | tinyint | integer() | Low (Acts as boolean or small int) |
| practice_answers | isMarked | tinyint | integer() | Low (Acts as boolean or small int) |
| practice_exam_questions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_exams | accessType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| practice_exams | category | varchar | text() | Low |
| practice_exams | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_exams | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| practice_exams | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| practice_exams | subject | varchar | text() | Low |
| practice_exams | title | varchar | text() | Low |
| practice_exams | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_records | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_records | endTime | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_records | startTime | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| practice_records | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| practice_wrong_book | chapter_name | varchar | text() | Low |
| practice_wrong_book | correct_answer | varchar | text() | Low |
| practice_wrong_book | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| practice_wrong_book | is_resolved | tinyint | integer() | Low (Acts as boolean or small int) |
| practice_wrong_book | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| practice_wrong_book | resolved_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| practice_wrong_book | source_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| practice_wrong_book | tags | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| practice_wrong_book | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| practice_wrong_book | user_answer | varchar | text() | Low |
| qa_cache | category | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| qa_cache | contextId | varchar | text() | Low |
| qa_cache | contextType | varchar | text() | Low |
| qa_cache | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| qa_cache | lastHitAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| qa_cache | questionEmbedding | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| qa_cache | sessionId | varchar | text() | Low |
| qa_cache | source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| qa_cache | subject | varchar | text() | Low |
| qa_cache | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| qa_cache | year | varchar | text() | Low |
| qa_records | answer_source | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| qa_records | context_id | varchar | text() | Low |
| qa_records | context_type | varchar | text() | Low |
| qa_records | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| qa_records | is_accurate | tinyint | integer() | Low (Acts as boolean or small int) |
| qa_records | question_embedding | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| qa_records | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| qa_records | verified_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_attempts | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_attempts | isCorrect | tinyint | integer() | Low (Acts as boolean or small int) |
| question_bank | access_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank | category | varchar | text() | Low |
| question_bank | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_bank | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank | examDepartment | varchar | text() | Low |
| question_bank | examSchool | varchar | text() | Low |
| question_bank | examYear | varchar | text() | Low |
| question_bank | hasImages | tinyint | integer() | Low (Acts as boolean or small int) |
| question_bank | isGroupQuestion | tinyint | integer() | Low (Acts as boolean or small int) |
| question_bank | needsImageUpload | tinyint | integer() | Low (Acts as boolean or small int) |
| question_bank | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_bank | owner_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank | questionNumberInPdf | varchar | text() | Low |
| question_bank | reviewedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_bank | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank | tags | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_bank | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_bank | validationIssues | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_bank | validationStatus | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank | validationWarnings | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_bank_history | category | varchar | text() | Low |
| question_bank_history | change_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank_history | changed_by_name | varchar | text() | Low |
| question_bank_history | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_bank_history | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank_history | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_bank_history | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_bank_history | tags | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_bank_history | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_groups | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_groups | stemImages | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_groups | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_images | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_images | cropInfo | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_images | fileName | varchar | text() | Low |
| question_images | mimeType | varchar | text() | Low |
| question_learning_conversations | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_learning_conversations | label | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| question_learning_conversations | messages | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| question_learning_conversations | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_references | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| question_references | referenceType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| quiz_cache | chapterTitle | varchar | text() | Low |
| quiz_cache | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| quiz_cache | quizData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| quiz_cache | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| quiz_history | chapterTitle | varchar | text() | Low |
| quiz_history | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| quiz_history | quizData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| quiz_wrong_questions | chapterTitle | varchar | text() | Low |
| quiz_wrong_questions | correctAnswer | varchar | text() | Low |
| quiz_wrong_questions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| quiz_wrong_questions | isMastered | tinyint | integer() | Low (Acts as boolean or small int) |
| quiz_wrong_questions | questionData | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| quiz_wrong_questions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| real_exam_attempts | answers | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| real_exam_attempts | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| real_exam_attempts | question_ids | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| real_exam_attempts | started_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| real_exam_attempts | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| real_exam_attempts | submitted_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| real_exam_questions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| real_exam_questions | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| real_exam_questions | exam_group | varchar | text() | Low |
| real_exam_questions | is_verified | tinyint | integer() | Low (Acts as boolean or small int) |
| real_exam_questions | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| real_exam_questions | question_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| real_exam_questions | subject | varchar | text() | Low |
| real_exam_questions | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| real_exam_questions | year | varchar | text() | Low |
| recommendation_logs | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| recommendation_logs | reviewedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| recommendation_logs | sentAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| recommendation_logs | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| saved_answers | answer | longtext | text() | Low |
| saved_answers | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| saved_answers | subject | varchar | text() | Low |
| saved_qa | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| saved_qa | screenshot_url | mediumtext | text() | Low |
| saved_qa | unit_title | varchar | text() | Low |
| smart_book_categories | color | varchar | text() | Low |
| smart_book_categories | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_categories | icon | varchar | text() | Low |
| smart_book_categories | name | varchar | text() | Low |
| smart_book_categories | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_category_exam_sources | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_category_exam_sources | source_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_chapter_completions | completed_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_chapter_completions | quiz_completed | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_chapter_daily_verifications | verified_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_chapter_daily_verifications | verified_date | varchar | text() | Low |
| smart_book_chapter_qa | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_chapter_qa | is_recommended | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_chapter_quizzes | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_chapters | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_chapters | embedding | mediumtext | text() | Low |
| smart_book_chapters | guide_questions | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_book_chapters | is_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_chapters | split_status | varchar | text() | Low |
| smart_book_chapters | title | varchar | text() | Low |
| smart_book_chapters | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_conversations | chat_answered | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_conversations | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_conversations | role | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_credit_transactions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_credit_transactions | description | varchar | text() | Low |
| smart_book_credit_transactions | type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_credits | balance_expires_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_credits | daily_reset_at | varchar | text() | Low |
| smart_book_credits | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_learning_sessions | ended_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_learning_sessions | last_active_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_learning_sessions | reminder_sent_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_learning_sessions | started_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_progress | completed_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_progress | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_qa_viewed | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_question_shown | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_quiz_sessions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_quiz_sessions | mode | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_review_questions | content_hash | varchar | text() | Low |
| smart_book_review_questions | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_review_questions | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_review_questions | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_book_saved_messages | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_saved_messages | folder_name | varchar | text() | Low |
| smart_book_saved_messages | subject_name | varchar | text() | Low |
| smart_book_saved_messages | title | varchar | text() | Low |
| smart_book_saved_messages | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_settings | challenge_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_settings | chapter_verify_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_settings | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_unit_qa | case_label | varchar | text() | Low |
| smart_book_unit_qa | correct_answer | varchar | text() | Low |
| smart_book_unit_qa | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_unit_qa | is_active | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_unit_qa | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_book_unit_qa | qa_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_unit_qa | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_unit_qa_answers | answered_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_unit_qa_answers | is_correct | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_unit_qa_answers | selected_answer | varchar | text() | Low |
| smart_book_verifications | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_verifications | expired_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_verifications | locked_until | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_verifications | passed_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_verifications | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_book_verifications | suspended_until | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_verifications | unlocked_by_admin | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_verifications | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_wrong_answers | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_wrong_answers | is_learned | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_book_wrong_answers | learned_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_book_wrong_answers | options | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_books | author | varchar | text() | Low |
| smart_books | batch_qa_progress | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_books | bypass_password | varchar | text() | Low |
| smart_books | content_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_books | cover_image_url | varchar | text() | Low |
| smart_books | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_books | exam_type | varchar | text() | Low |
| smart_books | extracted_text | longtext | text() | Low |
| smart_books | has_page_numbers | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_books | is_public | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_books | language | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_books | member_join_url | varchar | text() | Low |
| smart_books | page_index | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_books | pdf_key | varchar | text() | Low |
| smart_books | pdf_toc | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| smart_books | pdf_url | varchar | text() | Low |
| smart_books | processing_status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| smart_books | processing_step | varchar | text() | Low |
| smart_books | purchase_url | varchar | text() | Low |
| smart_books | require_verification | tinyint | integer() | Low (Acts as boolean or small int) |
| smart_books | title | varchar | text() | Low |
| smart_books | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| smart_books | verification_mode | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| standard_answers | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| standard_answers | isVerified | tinyint | integer() | Low (Acts as boolean or small int) |
| standard_answers | sourceType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| standard_answers | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| standard_answers | verifiedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_behavior_alerts | alertType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_behavior_alerts | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_behavior_alerts | evidence | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| student_behavior_alerts | isResolved | tinyint | integer() | Low (Acts as boolean or small int) |
| student_behavior_alerts | resolvedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_behavior_alerts | sessionId | varchar | text() | Low |
| student_behavior_alerts | severity | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_learning_sessions | behaviorFlags | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| student_learning_sessions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_learning_sessions | endTime | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_learning_sessions | sessionId | varchar | text() | Low |
| student_learning_sessions | sessionType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_learning_sessions | startTime | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_learning_sessions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_questions | category | varchar | text() | Low |
| student_questions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_questions | difficulty | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_questions | priority | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_questions | questionTitle | varchar | text() | Low |
| student_questions | repliedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_questions | sourceType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_questions | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| student_questions | topic | varchar | text() | Low |
| student_questions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_transcript_edits | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| student_transcript_edits | timestamp | varchar | text() | Low |
| student_transcript_edits | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| study_sessions | endTime | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| study_sessions | startTime | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| subject_categories | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| subject_categories | is_active | tinyint | integer() | Low (Acts as boolean or small int) |
| subject_categories | name | varchar | text() | Low |
| subject_categories | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| subjects | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| subjects | name | varchar | text() | Low |
| subjects | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| system_settings | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| system_settings | key | varchar | text() | Low |
| system_settings | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| tags | category | varchar | text() | Low |
| tags | color | varchar | text() | Low |
| tags | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| tags | name | varchar | text() | Low |
| teacher_materials | accessType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| teacher_materials | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| teacher_materials | fileName | varchar | text() | Low |
| teacher_materials | isActive | tinyint | integer() | Low (Acts as boolean or small int) |
| teacher_materials | isProcessed | tinyint | integer() | Low (Acts as boolean or small int) |
| teacher_materials | isReleased | tinyint | integer() | Low (Acts as boolean or small int) |
| teacher_materials | title | varchar | text() | Low |
| teacher_materials | transcript | longtext | text() | Low |
| teacher_materials | transcriptProgress | varchar | text() | Low |
| teacher_materials | transcriptStartedAt | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| teacher_materials | transcriptStatus | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| teacher_materials | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| teacher_materials | videoSummary | longtext | text() | Low |
| teachers | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| teachers | id | varchar | text() | Low |
| teachers | name | varchar | text() | Low |
| teachers | photoUrl | varchar | text() | Low |
| teachers | sourceUrl | varchar | text() | Low |
| teachers | sourceWebsite | varchar | text() | Low |
| teachers | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| transcript_correction_requests | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| transcript_correction_requests | reason | varchar | text() | Low |
| transcript_correction_requests | review_note | varchar | text() | Low |
| transcript_correction_requests | reviewed_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| transcript_correction_requests | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| transcript_correction_requests | timestamp | varchar | text() | Low |
| tutor_chat_folders | color | varchar | text() | Low |
| tutor_chat_folders | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_folders | name | varchar | text() | Low |
| tutor_chat_folders | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_labels | color | varchar | text() | Low |
| tutor_chat_labels | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_labels | name | varchar | text() | Low |
| tutor_chat_messages | ai_accuracy | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| tutor_chat_messages | content | longtext | text() | Low |
| tutor_chat_messages | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_messages | image_urls | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| tutor_chat_messages | role | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| tutor_chat_messages | sources | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| tutor_chat_messages | teacher_images | json | text("...", { mode: "json" }) | Medium (Serialization in app layer) |
| tutor_chat_messages | teacher_note | longtext | text() | Low |
| tutor_chat_messages | teacher_note_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_session_labels | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_sessions | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_chat_sessions | is_hidden_by_user | tinyint | integer() | Low (Acts as boolean or small int) |
| tutor_chat_sessions | title | varchar | text() | Low |
| tutor_chat_sessions | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_subject_books | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_subject_exam_sources | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| tutor_subject_exam_sources | source_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| tutor_subject_video_courses | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_subjects | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| tutor_subjects | icon_emoji | varchar | text() | Low |
| tutor_subjects | is_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| tutor_subjects | name | varchar | text() | Low |
| tutor_subjects | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| user_points | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_points | updated_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_points_log | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_points_log | reason | varchar | text() | Low |
| user_points_log | ref_type | varchar | text() | Low |
| user_practice_history | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_practice_history | isCorrect | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| user_practice_history | userAnswer | varchar | text() | Low |
| user_preferences | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| user_question_stats | lastPracticeAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_question_stats | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_usage_stats | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_usage_stats | date | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_usage_stats | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_warnings | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| user_warnings | is_read | tinyint | integer() | Low (Acts as boolean or small int) |
| user_warnings | read_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| users | banned_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| users | chat_style | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| users | daily_earned_date | varchar | text() | Low |
| users | email | varchar | text() | Low |
| users | examTarget | varchar | text() | Low |
| users | examType | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | gender | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | identity_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | is_banned | tinyint | integer() | Low (Acts as boolean or small int) |
| users | is_first_login | tinyint | integer() | Low (Acts as boolean or small int) |
| users | last_daily_grant_date | varchar | text() | Low |
| users | lastSignedIn | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| users | loginMethod | varchar | text() | Low |
| users | member_account | varchar | text() | Low |
| users | nickname | varchar | text() | Low |
| users | openId | varchar | text() | Low |
| users | password_hash | varchar | text() | Low |
| users | role | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | student_type | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | studentStatus | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | subject_category | varchar | text() | Low |
| users | subscriptionExpiresAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| users | subscriptionPlan | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | teaching_role | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| users | trial_reset_date | varchar | text() | Low |
| users | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| users | username | varchar | text() | Low |
| video_courses | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| video_courses | is_published | tinyint | integer() | Low (Acts as boolean or small int) |
| video_courses | title | varchar | text() | Low |
| video_courses | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| video_knowledge_points | title | varchar | text() | Low |
| video_progress | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| video_unit_questions | correct_answer | varchar | text() | Low |
| video_unit_questions | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| video_unit_questions | difficulty | varchar | text() | Low |
| video_unit_questions | question_type | varchar | text() | Low |
| video_unit_questions | status | varchar | text() | Low |
| video_unit_questions | unit_title | varchar | text() | Low |
| video_unit_questions | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| video_units | ai_status | varchar | text() | Low |
| video_units | corrected_srt | mediumtext | text() | Low |
| video_units | created_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| video_units | srt_content | mediumtext | text() | Low |
| video_units | subtitles_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| video_units | title | varchar | text() | Low |
| video_units | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| watermark_settings | font_color | varchar | text() | Low |
| watermark_settings | image_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| watermark_settings | image_key | varchar | text() | Low |
| watermark_settings | image_url | varchar | text() | Low |
| watermark_settings | is_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| watermark_settings | text_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| watermark_settings | text_template | varchar | text() | Low |
| watermark_settings | updated_at | bigint | integer() / integer({ mode: "number" }) | Low (SQLite integer supports up to 8 bytes) |
| watermark_settings | voucher_enabled | tinyint | integer() | Low (Acts as boolean or small int) |
| watermark_settings | voucher_prompt | varchar | text() | Low |
| web_search_logs | created_at | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| web_search_logs | engine | varchar | text() | Low |
| web_search_logs | is_admin | tinyint | integer() | Low (Acts as boolean or small int) |
| web_search_logs | query | varchar | text() | Low |
| web_search_logs | success | tinyint | integer() | Low (Acts as boolean or small int) |
| wrong_questions | createdAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |
| wrong_questions | status | mysqlEnum | text() | Low-Medium (Check constraints or app validation) |
| wrong_questions | updatedAt | timestamp | integer({ mode: "timestamp" }) | Low-Medium (Requires datetime function updates) |

---

## DB Connection

server/db.ts

目前：
- `mysql2` (driver: `mysql2/promise`)
- `drizzle-orm/mysql-core` (dialect: `mysql`)

實際連線方式與 Drizzle 初始化方式：
- `server/db.ts` 中使用懶加載方式 (`getDb()` 函數) 初始化 `_db = drizzle(process.env.DATABASE_URL)`。
- 其他代碼（如 `server/routers/aiQuestionBankRouter.ts`、`server/learningMaterials.ts`、`server/import_to_database.ts` 等）在部分操作中直接使用 `mysql2/promise` 的 `mysql.createConnection(process.env.DATABASE_URL)` 建立底層原生連接，這是潛在的重構重點，因為 SQLite 無法直接使用 `mysql2` 連線。

---

## Migration Readiness

**Partial**

### Readiness Analysis:
- **Drizzle schema**: 需要將 `drizzle-orm/mysql-core` 替換為 `drizzle-orm/sqlite-core`，並調整對應的欄位型別（如 `mysqlEnum` 轉 `text`、`json` 轉 `text({ mode: "json" })` 等）。
- **Drizzle configuration**: 需要將 `drizzle.config.ts` 的 `dialect` 改為 `sqlite`。
- **MySQL Migration files**: 項目中目前僅存在 MySQL 的 Migration SQL 歷史文件，無任何 SQLite 兼容的 Migration 腳本，需要在 Schema 調整完成後重新生成。
- **Direct DB references**: 項目中有多處直接依賴 `mysql2/promise` 驅動建立連線的腳本，這些需要被替換為 SQLite 兼容的文件讀寫或 Drizzle 查詢。

---

## Estimated Work

- **Schema Conversion**: 4 小時 (更換 schema.ts 與 schema-google-drive.ts 中的方言與型別，並修改 config)
- **Data Migration**: 6 小時 (編寫腳本導出 MySQL 資料並寫入 SQLite)
- **Testing**: 8 小時 (更新 vitest 環境使其加載 dotenv / 使用 sqlite 記憶體庫進行測試，修復測試斷言)
- **Rollback Plan**: 1 小時 (保留 MySQL 設定分支，配置 DATABASE_URL 回滾環境)
