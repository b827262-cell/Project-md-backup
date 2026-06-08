# SQLite Runtime Dependency Audit

## 1. Executive Summary

- **43 張 Must Migrate 表是否足夠支撐 SmartBook Lite 核心 runtime？**
  **不足夠。** 儘管從業務邏輯來看，SmartBook Lite 核心功能（書籍閱讀與 Tutor 聊天）僅需要 43 張表，但在代碼層面上，`smartBookRouter.ts` 與 `tutorRouter.ts` 內仍有直接導入並查詢 \`Should Migrate 57\` (如 \`real_exam_questions\`, \`ai_generated_exams\`) 與 \`Defer / Archive 79\` (如 \`ai_question_sources\`, \`page_text_cache\`) 關聯表的邏輯。若 SQLite Schema 僅包含 43 張表，TypeScript 編譯將會報錯。
- **邊些 Should Migrate 表目前其實會被 runtime 觸發？**
  下列資料表在活躍的 Router 中被直接 Import 並呼叫：
  - \`real_exam_questions\`, \`exam_subjects\`, \`exam_categories\`, \`exam_questions\`, \`ai_generated_exams\` (被 \`smartBookRouter.ts\` 呼叫)
  - \`practice_wrong_book\`, \`exam_sets\`, \`exam_set_questions\`, \`ai_generated_questions\` (被 \`tutorRouter.ts\` 呼叫)
  - \`video_units\`, \`video_knowledge_points\`, \`video_progress\`, \`saved_qa\`, \`video_unit_questions\` (被 \`videoCourseRouter.ts\` 呼叫)
- **哪些 mysql2 檔案是 Phase 1-D 前必須處理？**
  - \`server/db.ts\` (必須改用 better-sqlite3)
  - \`server/routers/aiQuestionBankRouter.ts\` (含有 mysql2/promise 連線依賴)
  - \`server/learningMaterials.ts\` (動態加載 mysql2/promise)
- **是否可以維持不安裝 better-sqlite3 進入下一步設計？**
  **可以**。Phase 1-D 可以先進行「純架構設計」(Design Only)，設計 \`server/db.sqlite.ts\` 並草擬轉接層程式碼，而不安裝 runtime 依賴。

---

## 2. Runtime Mounted Routers

| Router | Mounted | Feature | Tables Used | Scope Category | Risk |
|---|---|---|---|---|---|
| \`smartBookStudent\` / \`smartBookAdmin\` | Yes | SmartBook 主體 | \`smart_books\`, \`smart_book_chapters\`, \`smart_book_categories\`, \`smart_book_progress\`, \`smart_book_chapter_qa\`, \`smart_book_review_questions\`, \`smart_book_wrong_answers\`, \`smart_book_quiz_sessions\`, \`smart_book_saved_messages\`, \`smart_book_settings\`, \`smart_book_credits\`, \`smart_book_credit_transactions\`, \`smart_book_verifications\`, \`smart_book_conversations\`, \`smart_book_qa_viewed\`, \`smart_book_chapter_completions\`, \`smart_book_chapter_daily_verifications\`, \`smart_book_unit_qa\`, \`smart_book_unit_qa_answers\`, \`smart_book_learning_sessions\`, \`smart_book_question_shown\`, \`book_suggestion_cache\`, \`book_voucher_records\` | Must Migrate 43 | **低** |
| \`tutorChat\` / \`tutorPublic\` | Yes | TutorChat AI 助教 | \`tutor_subjects\`, \`tutor_subject_books\`, \`tutor_subject_exam_sources\`, \`tutor_subject_video_courses\`, \`tutor_chat_sessions\`, \`tutor_chat_messages\`, \`smart_book_chapters\`, \`smart_book_chapter_qa\`, \`smart_book_unit_qa\`, \`book_suggestion_cache\`, \`book_custom_suggestions\`, \`smart_book_review_questions\` | Must Migrate 43 | **低** |
| \`userManagement\` | Yes | 用戶管理 | \`users\` | Must Migrate 43 | **低** |
| \`videoCourseStudent\` / \`videoCourseAdmin\` | Yes | 影音課程 | \`video_units\`, \`video_knowledge_points\`, \`video_progress\`, \`saved_qa\`, \`video_unit_questions\` | Should Migrate 57 | **中** (缺表阻擋編譯) |
| \`examSetStudent\` / \`examSetAdmin\` | Yes | 考古題測驗 | \`exam_sets\`, \`exam_set_questions\`, \`exam_set_sub_questions\`, \`exam_wrong_book\`, \`exam_notes\`, \`smart_books\`, \`learning_material_exam_sets\`, \`learning_materials\` | Should Migrate 57 / Defer 79 | **中** (缺表阻擋編譯) |

---

## 3. Must Migrate Coverage

| Feature | Required Tables | Covered by 43? | Missing Tables | Risk |
|---|---|---|---|---|
| SmartBook / PDF | 27 tables | Yes | None | **低** |
| TutorChat | 6 tables | Yes | None | **低** |
| Auth & User | 4 tables | Yes | None | **低** |
| Conversations | 5 tables | Yes | None | **低** |
| Credit Rules | 1 table | Yes | None | **低** |

---

## 4. Should Migrate Runtime Check

| Table | Feature | Runtime Required Now | Evidence | Decision |
|---|---|---|---|---|
| \`exam_questions\` | 考試系統 | Optional | 被 \`smartBookRouter.ts\` 引用於試卷關聯 | **Include in SQLite Schema** (以避免編譯錯誤，但暫不遷移資料) |
| \`real_exam_questions\` | 考試系統 | Optional | 被 \`smartBookRouter.ts\` 引用於考古題關聯 | **Include in SQLite Schema** (以避免編譯錯誤，但暫不遷移資料) |
| \`ai_generated_exams\` | AI 題庫 | Optional | 被 \`smartBookRouter.ts\` 與 \`tutorRouter.ts\` 引用 | **Include in SQLite Schema** (以避免編譯錯誤，但暫不遷移資料) |
| \`exam_sets\` | 考古題專區 | Optional | 被 \`tutorRouter.ts\` 與 \`examSetRouter.ts\` 引用 | **Include in SQLite Schema** (以避免編譯錯誤，但暫不遷移資料) |
| \`video_units\` | 影片課程 | Optional | 被 \`videoCourseRouter.ts\` 與 \`tutorRouter.ts\` 引用 | **Include in SQLite Schema** (以避免編譯錯誤，但暫不遷移資料) |
| \`learning_materials\` | 講義管理 | Optional | 被 \`learningMaterials.ts\` 引用 | **Include in SQLite Schema** (以避免編譯錯誤，但暫不遷移資料) |

---

## 5. Defer / Archive Runtime Check

| Component/Table | Runtime Active? | Evidence | Decision |
|---|---|---|---|
| \`knowledge_chunks\` | **No (Dormant)** | RAG 被設定為 none。雖然 \`server/db.ts\` 中有 \`getKnowledgeCategoriesWithDocuments\` 查詢此表，但該函式已被判定為無人呼叫之死代碼。 | **Dormant**，為使 \`db.ts\` 編譯通過，可選擇在 Schema 中以最小定義保留或重構移除該死代碼。 |
| \`smartBookCategoryExamSources\` | **Yes** | 被 \`smartBookRouter.ts\` 查詢以加載書籍考題來源。 | **Active**, 必須包含於 SQLite Schema 中以避免編譯錯誤。 |
| \`ai_question_sources\` | **Yes** | 被 \`smartBookRouter.ts\` 與 \`tutorRouter.ts\` 查詢以獲得 AI 題目來源。 | **Active**, 必須包含於 SQLite Schema 中以避免編譯錯誤。 |
| \`page_text_cache\` | **Yes** | 被 \`tutorRouter.ts\` 查詢以加載頁面快取。 | **Active**, 必須包含於 SQLite Schema 中以避免編譯錯誤。 |

---

## 6. mysql2 Active Dependency Audit

| File | Active Runtime? | SQLite Blocker | Recommended Action |
|---|---|---|---|
| \`server/db.ts\` | **Yes** (核心 DB 連線) | **Yes** (採用 mysql2 方言) | 在 Phase 1-D 重構為支援 better-sqlite3 動態連線。 |
| \`server/routers/aiQuestionBankRouter.ts\` | **Yes** (題庫解析掛載) | **Yes** (直接連線 mysql2/promise) | 重寫為 Drizzle ORM 語法。 |
| \`server/learningMaterials.ts\` | **Yes** (講義材料掛載) | **Yes** (直接連線 mysql2/promise) | 移除原生 mysql2 連線，重寫為 Drizzle SQL。 |
| \`scripts/*\` | **No** (僅維運/開發使用) | **No** (不影響線上執行) | 於後續階段重構。 |

---

## 7. Phase 1-D Gate Decision

**Gate Result**: **PASS WITH WARNINGS**

### Blocker Warnings (必須於 Phase 1-D Wiring 前處理解決)：
1. **Compilation Errors (缺表阻擋編譯)**: 雖然 43 張表涵蓋了業務 MVP，但因為其他 Router (如 \`videoCourseRouter\`, \`lectureMaterialsRouter\` 等) 仍被掛載在 \`appRouter\` 中並有 Schema 引用，若直接切換 Schema 會導致 TypeScript 編譯錯誤。**解決方案：在 SQLite Schema 中保留這些被引用表的定義 (只定義不遷資料)，以確保編譯通過。**
2. **mysql2 Active Drivers**: \`aiQuestionBankRouter.ts\` 與 \`learningMaterials.ts\` 中的直連程式碼在 SQLite 下會崩潰。**解決方案：在 Wire 進程中同步重構為 Drizzle。**

---

## 8. Recommended Next Step

**Recommended Next Step**: **Phase 1-D Design Only**

*說明：在不引入 better-sqlite3 依賴的前提下，先行草擬 \"server/db.sqlite.ts\" 設計，並規劃在 Drizzle Schema 中以 Stub (存根) 方式定義其他 136 張表以滿足 TypeScript 編譯需求。*
