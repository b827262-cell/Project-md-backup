# 2026-06-15 SmartBook Student PDF Access Basic Protection 驗收紀錄

## 1. 驗收對象

- 專案：AI-SmartBook-R1
- 功能名稱：STUDENT_PDF_ACCESS_BASIC_PROTECTION
- commit SHA：`eb8e117`
- commit message：`feat: protect student PDF viewing endpoint`
- 驗收結果：AGY PASS

---

## 2. AGY 最終驗收判定

```text
PASS
```

整體狀態：

```text
STUDENT_PDF_ACCESS_BASIC_PROTECTION_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
DB_MIGRATION_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

---

## 3. 實際修改檔案

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/studentClient.ts
apps/AI-Stu-R1/src/styles.css
apps/AI-adm-D1/src/server/index.ts
packages/db/src/migrate.ts
packages/db/src/repositories/index.ts
packages/db/src/repositories/pdfAccessLog.repo.ts
packages/db/src/schema.ts
```

---

## 4. 核心功能驗收

### 4.1 受保護 PDF Endpoint

新增：

```text
/api/student/books/:bookId/files/:fileId/pdf-view
```

AGY 驗證結果：

| 項目 | 結果 |
|---|---|
| 是否檢查 bookId | PASS，透過 `findPublishedBook(bookId)` 確保存在且對學生可見 |
| 是否檢查 fileId | PASS，確認檔案存在且 `bookId` 與請求相符 |
| 是否檢查 PDF source role | PASS，驗證 `file.role === "source_document"` 且副檔名為合法 PDF |
| 是否拒絕 reference image | PASS，非 `source_document` 一律拒絕 |
| 是否拒絕 blocked session | PASS，`resolveStudentSession` 內部呼叫 `rejectIfBlocked` |
| 是否避免暴露 real filePath | PASS，僅後端以 `res.sendFile(file.filePath)` 回傳二進位檔案流 |

---

## 5. Student Reader PDF URL 驗收

| 項目 | 結果 |
|---|---|
| 是否使用 `/api/student/.../pdf-view` | PASS |
| 是否不使用 admin raw endpoint | PASS |
| 是否不使用 public/uploads PDF URL | PASS |
| 是否避免前端暴露真實 filePath | PASS |

AGY 說明：

```text
前台使用自定義 API 去 fetch PDF Blob，並以 URL.createObjectURL(blob) 顯示，避免實際路徑曝光。
```

---

## 6. Session 驗收

新增：

```text
/api/student/books/:bookId/session
```

| 項目 | 結果 |
|---|---|
| 是否建立 / 確認 reader session | PASS |
| 是否使用 `X-Student-Session-Id` | PASS |
| invalid session 是否拒絕 | PASS，回傳 401 Unauthorized |
| cross-book session 是否拒絕 | PASS，強制比對 session 綁定的 `bookId` |
| blocked session 是否拒絕 | PASS |

---

## 7. Response Headers 驗收

| Header | 結果 |
|---|---|
| `Content-Type: application/pdf` | PASS |
| `Content-Disposition: inline; filename="reader.pdf"` | PASS |
| `Cache-Control: private, no-store, no-cache, must-revalidate` | PASS |
| `Pragma: no-cache` | PASS |
| `Expires: 0` | PASS |
| `X-Content-Type-Options: nosniff` | PASS |

目的：

```text
降低一般下載與快取風險，但不宣稱可 100% 阻止 DevTools 取得資源。
```

---

## 8. Watermark 驗收

| 項目 | 結果 |
|---|---|
| 是否顯示 | PASS |
| 是否包含 session/book/timestamp 等識別 | PASS |
| 是否不阻擋 PDF 操作 | PASS，設定 `pointer-events: none` |
| 是否不修改 PDF binary | PASS，使用前端 overlay |

使用識別文字：

```text
iBrain 智匯
session ${pdfSessionId}
book.title 或 book.id
timestamp
```

---

## 9. Access Log 驗收

新增：

```text
pdf_access_logs
```

新增 repo：

```text
packages/db/src/repositories/pdfAccessLog.repo.ts
```

記錄欄位：

```text
bookId
fileId
sessionId
ipAddress
userAgent
viewedAt
```

AGY 驗證結果：

| 項目 | 結果 |
|---|---|
| 是否新增 `pdf_access_logs` | PASS |
| 是否記錄 bookId | PASS |
| 是否記錄 fileId | PASS |
| 是否記錄 sessionId | PASS |
| 是否記錄 ipAddress/userAgent | PASS |
| 是否記錄 viewedAt | PASS |
| migration 是否 idempotent | PASS，使用 `CREATE TABLE IF NOT EXISTS` 與 `CREATE INDEX IF NOT EXISTS` |
| 是否需要 deployment migration | 是 |

---

## 10. Build / Typecheck

| 項目 | 結果 |
|---|---|
| pnpm build | PASS |
| pnpm typecheck | PASS |
| git status | working tree clean |
| unrelated 變更 | 無 |

---

## 11. 下載防護限制

AGY 已確認本次實作有明確承認：

```text
無法 100% 防止進階使用者透過 DevTools 取得瀏覽器已載入的 PDF 資源。
```

本次屬於第一層基本保護：

```text
受保護 student endpoint
session / blocked 檢查
inline / no-store headers
frontend watermark overlay
access log
避免學生端使用 admin raw endpoint
避免前端暴露真實 filePath
```

非本次範圍：

```text
Full DRM
DevTools/F10 完全阻擋
短效 signed token
逐頁圖片 render
tile viewer
rate limit / anti-scraping
```

---

## 12. 部署前注意事項

此 commit 新增 DB schema：

```text
pdf_access_logs
```

正式部署前必須確認：

1. `runMigrations()` 或等價 migration 流程已成功執行。
2. `pdf_access_logs` table 與 index 已建立。
3. Student reader 的 PDF 來源已改用 `/api/student/.../pdf-view`。
4. 不應讓學生端直接使用 `/api/admin/.../raw`。
5. 本次不等於完整 DRM；後續若要更高保護，應另開短效 token、rate limit、server-side page rendering 任務。

---

## 13. 最終結論

`eb8e117` 可接受為 SmartBook 學生端 PDF 第一層基本防護 commit。

AGY 驗收結果：

```text
PASS
```

目前狀態：

```text
STUDENT_PDF_ACCESS_BASIC_PROTECTION_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
DB_MIGRATION_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```
