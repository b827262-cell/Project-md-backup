# 2026-06-15 SmartBook PDF Outline Preview and Reference Image Flow 驗收紀錄

## 1. 驗收對象

- 專案：AI-SmartBook-R1
- 功能名稱：PDF_OUTLINE_CHAPTER_PREVIEW_AND_REFERENCE_IMAGE_FLOW
- 主要入口頁：`/admin/books/:bookId/files`
- 範例頁面：`http://127.0.0.1:5174/admin/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509/files`
- commit SHA：`25d3ca2`
- commit message：`feat: add PDF outline chapter preview from files page`

---

## 2. AGY 驗收結果

AGY 回報最終狀態：

```text
PASS
```

驗收對象：

```text
PDF outline chapter preview and reference image flow
```

整體判定：

```text
PDF_OUTLINE_PREVIEW_REFERENCE_IMAGE_FLOW_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
DEPLOYMENT_MIGRATION_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

---

## 3. 實際修改檔案

```text
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/pages/ChaptersPage.tsx
apps/AI-adm-D1/src/pages/tabs/ChaptersTab.tsx
apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
apps/AI-adm-D1/src/server/index.ts
apps/AI-adm-D1/src/styles.css
packages/book-core/src/chapter-builder.ts
packages/db/src/migrate.ts
packages/db/src/repositories/bookFile.repo.ts
packages/db/src/schema.ts
packages/schema/src/bookFile.schema.ts
packages/schema/src/chapter.schema.ts
```

---

## 4. 核心功能驗收

### 4.1 `/files` 是否為主要入口

AGY 判定：PASS。

```text
解析與套用章節的工作流皆已整合至檔案管理頁面。
```

正確流程：

```text
/files
→ Upload PDF
→ Parse / Re-parse Outline
→ Preview Chapters
→ Admin edits rows
→ Apply Chapters
→ Final chapters are written
→ /chapters displays applied result
```

### 4.2 `/chapters` 是否改為結果管理頁

AGY 判定：PASS。

```text
舊有的一鍵重置建立按鈕已被移除，並加入明確引導提示使用者回到 /files 操作章節生成。
```

---

## 5. Parse / Preview / Apply 驗收

### 5.1 Parse / Re-parse Outline

| 項目 | 結果 |
|---|---|
| 是否產生 preview | PASS |
| 是否避免直接覆寫 final chapters | PASS |

AGY 說明：

```text
Parse 僅執行文件文字擷取與目錄提取，產生 JSON 給前端，不會更動 book_chapters 資料表。
```

### 5.2 Preview table

| 可編輯項目 | 結果 |
|---|---|
| enabled / disabled | PASS |
| title / suggestedTitle | PASS |
| printed label | PASS |
| PDF pageStart / pageEnd | PASS |
| entry type | PASS |
| sort order | PASS |
| admin note | PASS |

### 5.3 Apply Chapters

| 項目 | 結果 |
|---|---|
| 是否只有按 Apply 才寫入 chapters | PASS |
| 是否重新 link FileContent | PASS |
| `/chapters` 是否顯示套用後結果 | PASS |

AGY 說明：

```text
明確呼叫 /apply-chapters 才會執行刪除並重建；寫入章節後會自動重新綁定 FileContent 區塊。
```

---

## 6. PDF physical page canonical 驗收

| 項目 | 結果 |
|---|---|
| 是否仍以 PDF physical page 為 canonical | PASS |
| 是否避免 printed label 作為 canonical pageStart/pageEnd | PASS |
| 範例第 1 章是否為 PDF P10 而非 printed page 1 | PASS |

AGY 說明：

```text
章節預設抓取的範圍使用實體頁碼。提取的印刷頁碼僅放入 printedPageLabel 中，並未覆寫 pageStart。
```

保留規則：

```text
PDF physical page number is canonical.
Printed page labels are display metadata only.
Reference images are visual/manual hints only.
```

---

## 7. Reference image 驗收

| 項目 | 結果 |
|---|---|
| 是否可 upload | PASS |
| 是否可 view | PASS |
| 是否 linked to PDF | PASS |
| 是否僅作為顯示輔助 / 手動校正 | PASS |
| OCR 是否未實作 | PASS，未實作 OCR |

AGY 說明：

```text
圖片僅作為肉眼校對用的輔助顯示功能，並無執行 OCR 或自動覆寫欄位。
```

這符合第一階段設計：

```text
Reference image = 顯示輔助 / 手動校正
OCR = 不在本階段
```

---

## 8. DB / Migration 驗收

本次新增：

```text
book_files.role
book_files.related_file_id
```

| 項目 | 結果 |
|---|---|
| 是否新增 `book_files.role` | PASS，預設 `source_document` |
| 是否新增 `book_files.related_file_id` | PASS |
| migration 是否 idempotent | PASS，使用 `addColumnIfMissing` |
| 是否需要 deployment migration | 是，需執行現有 DB migration 程序，啟動時會自動呼叫 |

部署注意：

```text
正式部署前需確認 runMigrations() 或等價 migration 流程已成功套用。
```

---

## 9. Raw file endpoint 安全性

新增 endpoint：

```text
GET /api/admin/books/:bookId/files/:fileId/raw
```

| 項目 | 結果 |
|---|---|
| 是否限制 bookId | PASS |
| 是否只使用 DB stored filePath | PASS |
| 是否存在 admin auth 架構限制 | 是，屬既有架構限制 |

AGY 說明：

```text
API 內會檢查 bookId 是否與檔案相符，並以 res.sendFile(file.filePath) 回傳 DB 中已儲存的檔案路徑，無使用者可控路徑輸入。
```

既有限制：

```text
目前系統未建立全局 Admin 驗證機制，這屬於架構上的現有限制，但路由均封裝在 /api/admin/ 底下。
```

---

## 10. Delete behavior 驗收

| 項目 | 結果 |
|---|---|
| 刪除 PDF 是否清除相關 reference images | PASS |
| 刪除 reference image 是否不影響 PDF | PASS |

AGY 說明：

```text
刪除主檔案時會一併清除其 relatedFileId 關聯之檔案；刪除 reference image 不影響 PDF。
```

---

## 11. Build / Typecheck

| 項目 | 結果 |
|---|---|
| pnpm build | PASS |
| pnpm typecheck | PASS |
| working tree | clean |
| unrelated 變更 | 無 |

---

## 12. 驗收可接受項目

本次 commit `25d3ca2` 可接受，原因：

- `/files` 已成為 PDF outline preview / apply 主流程入口。
- `/chapters` 已改為套用後結果管理頁。
- Parse / Re-parse Outline 只產生 preview，不直接覆寫 final chapters。
- Apply Chapters 才正式寫入 chapters 並重新 link FileContent。
- PDF physical page 仍為 canonical。
- Printed label 僅作顯示 metadata，不覆寫 pageStart / pageEnd。
- Reference image 已支援人工顯示輔助與手動校正。
- OCR 未混入本階段，降低誤判風險。
- DB migration 採 idempotent 設計。
- build/typecheck 通過。
- 未混入 unrelated 變更。

---

## 13. 部署前注意事項

目前仍不建議直接 final merge / deploy。

部署前需確認：

1. `book_files.role` 與 `book_files.related_file_id` migration 已成功套用。
2. 既有 PDF 檔案會以 `role = source_document` 預設處理。
3. Reference image 檔案儲存與 raw file endpoint 在正式環境路徑可正常讀取。
4. 若正式環境尚未有全局 admin auth，`/api/admin/` raw file endpoint 仍依既有架構暴露於 admin API 下，需另開 admin auth hardening 任務。
5. OCR 不在本階段，後續若要支援 OCR 應另開任務並獨立驗收。

---

## 14. 最終結論

`25d3ca2` 可接受為：

```text
PDF outline chapter preview and reference image flow
```

AGY 驗收結果：

```text
PASS
```

目前狀態：

```text
PDF_OUTLINE_PREVIEW_REFERENCE_IMAGE_FLOW_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
DEPLOYMENT_MIGRATION_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```
