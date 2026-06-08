# SQLite Schema Expansion Policy

## 1. Principle

只遷移目前 runtime 實際使用資料表。
未來功能需要時，再透過 migration 新增 table / column。

不因為「舊資料存在」或「MySQL 有這張表」而增加 SQLite 表。
每新增一張表，必須有明確的 runtime feature 驅動原因。

## 2. Current Scope

Phase 1-C only includes Must Migrate 43 tables.

| Table | Purpose |
|-------|---------|
| users | 用戶帳號與狀態 |
| conversations | AI 對話主表 |
| messages | 對話訊息 |
| conversation_files | 對話附件 |
| conversation_tags | 對話標籤關聯 |
| tags | 標籤主表 |
| system_settings | 系統全域設定 |
| credit_transactions | 點數交易記錄 |
| credit_rules | 點數扣點規則 |
| user_usage_stats | 用戶使用統計 |
| pdf_categories | PDF 類科分類 |
| smart_book_categories | 智能書本大分類 |
| smart_books | 智能書本主表 |
| smart_book_chapters | 書本章節 |
| smart_book_conversations | 書本學習對話 |
| smart_book_progress | 書本學習進度 |
| smart_book_chapter_qa | 章節 QA |
| smart_book_credits | 書本專屬點數 |
| smart_book_credit_transactions | 書本點數交易 |
| smart_book_settings | 書本點數設定 |
| smart_book_unit_qa | 互動學習備課 QA |
| smart_book_unit_qa_answers | 學生互動 QA 作答 |
| smart_book_learning_sessions | 學習計時 |
| smart_book_chapter_daily_verifications | 每日章節驗證 |
| smart_book_chapter_completions | 章節完成摘要 |
| smart_book_saved_messages | 收藏訊息 |
| lesson_points | 引導式學習知識點 |
| lesson_progress | 學生知識點進度 |
| smart_book_review_questions | 複習題庫 |
| smart_book_wrong_answers | 錯題本 |
| smart_book_quiz_sessions | 測驗記錄 |
| smart_book_question_shown | 題目出現次數 |
| smart_book_qa_viewed | QA 查看記錄 |
| smart_book_verifications | 購書驗證記錄 |
| tutor_subjects | AI 助教類科 |
| tutor_subject_books | 類科書本關聯 |
| tutor_chat_sessions | AI 助教對話 Session |
| tutor_chat_messages | AI 助教對話訊息 |
| tutor_subject_exam_sources | 類科考題來源 |
| tutor_subject_video_courses | 類科影音課程關聯 |
| book_suggestion_cache | 書本建議問題快取 |
| book_voucher_records | 購書憑證記錄 |
| book_custom_suggestions | 書本自訂建議問題 |

## 3. Deferred Scope

### Should Migrate（57 tables）— 未包含

這 57 張表將視功能啟用情況逐步加入。
每次只針對實際上線功能加入所需表格。

### Defer / Archive（79 tables）— 排除

以下類型的表格**永久排除**（除非有明確的商業理由重新評估）：
- RAG / Qdrant 相關表（knowledge_chunks, knowledgeLearningSessions 等）
- Google Drive sync 相關表
- 考古題爬蟲相關表（gaodian, graduate_schools 等）
- 舊式練習題系統（practice_exams, practice_records 等）
- 批次萃取記錄（batch_extract_logs, extraction_logs 等）
- 管理後台報表輔助表（recommendation_logs 等）
- Legacy 模組（ibrain_packages, ibrain_questions 等）

## 4. Future Add Table Process

當需要增加新表時，遵守以下流程：

1. **Confirm feature is active** — 確認該功能已在 VPS runtime 上線
2. **Identify required tables / columns** — 明確列出需要的表格與欄位
3. **Add SQLite schema definition** — 在 `schema.sqlite.mvp.ts` 中加入 (或建立獨立檔案)
4. **Generate migration** — 使用 `drizzle-kit generate` 生成遷移檔
5. **Add data migration if needed** — 如有舊資料需要搬移，撰寫資料遷移腳本
6. **Test feature** — 在本地完整測試功能
7. **Document migration reason** — 在 git commit message 或 PR 中說明為何加入此表

## 5. Do Not Add Tables For

不要因為以下原因新增表：

- 舊資料存在於 MySQL 但 runtime 未使用
- Legacy 功能（未在 VPS 版上線）
- RAG / Qdrant 已封存的功能
- Google Drive sync（未啟用）
- Demo / test / obsolete module
- 「以後可能用到」的假設性需求
- 為了資料完整性而搬「相關表」（只搬 runtime 實際呼叫的表）

## 6. SQLite Safety Rules

以下安全規則必須在 Phase 1-D（Runtime 接線）前確認或實作：

| Rule | Status | Note |
|------|--------|------|
| WAL mode | 必須啟用 | `PRAGMA journal_mode=WAL;` |
| busy_timeout | 必須設定 | `PRAGMA busy_timeout=5000;` |
| Daily backup | 必須規劃 | 建議每日自動備份 `.db` 檔 |
| Schema version tracking | 建議加入 | Drizzle migration 本身提供 |
| Rollback path | 必須規劃 | 保留 MySQL 作為回退來源 |
| Foreign key enforcement | 選擇性 | SQLite 預設關閉，可用 `PRAGMA foreign_keys=ON;` |

## 7. Column Expansion Policy

增加欄位（ALTER TABLE ADD COLUMN）比增加整張表更輕量，可以更積極執行。

規則：
- 新欄位必須有 DEFAULT 值或允許 NULL（SQLite ALTER TABLE 限制）
- 不直接修改 schema.sqlite.mvp.ts，而是透過 migration 加入
- 舊欄位不輕易刪除（可標記為 deprecated）

## 8. Schema Version Tracking

Phase 1-D 起使用 Drizzle migration 管理 schema 版本。
Migration 檔統一存放於 `drizzle/migrations/sqlite/` 目錄。
