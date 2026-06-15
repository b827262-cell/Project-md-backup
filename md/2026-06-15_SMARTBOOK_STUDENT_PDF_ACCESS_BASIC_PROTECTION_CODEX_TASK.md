# 2026-06-15 SmartBook Codex Task: Student PDF Access Basic Protection

## 0. Language Rule

```text
All execution-facing work must be in English.

This includes:
- implementation notes
- command notes
- verification notes
- code review notes
- intermediate progress reports
- error/blocker reports during execution

Only the final termination report must be written in Traditional Chinese.
```

---

## 1. Task Name

```text
STUDENT_PDF_ACCESS_BASIC_PROTECTION
```

---

## 2. Goal

Implement the first-layer mandatory protection for student PDF viewing.

Important security statement:

```text
This task does not claim to make PDF download impossible.
If the browser can display a full PDF, advanced users may still extract network resources with DevTools.
The goal is to stop direct/public PDF exposure, enforce access checks, reduce casual downloading, add watermarking, and record access events.
```

---

## 3. Required Protection Layer

Implement these baseline protections:

```text
1. Do not place PDF source files in a public/static directory.
2. Do not expose real server filePath to the frontend.
3. Student frontend must read PDF through a protected student API.
4. Protected API must validate student session and read permission.
5. Blocked or invalid sessions must not access PDF.
6. Return PDF with Content-Disposition: inline.
7. Return no-store/no-cache headers.
8. Add a visible but non-intrusive frontend watermark overlay.
9. Log who viewed which book/file and when.
```

---

## 4. Current Context

Relevant existing work:

```text
- Admin raw file endpoint exists for admin-side file viewing.
- Student reader is moving toward PDF-native display.
- Admin account/session risk controls already exist.
- Blocked session checks exist for student chat/session APIs.
```

Do not reuse admin raw endpoint directly in the student reader.

The student reader must use a student-scoped protected endpoint.

---

## 5. Endpoint Requirement

Add a protected student endpoint similar to:

```text
GET /api/student/books/:bookId/files/:fileId/pdf-view
```

or, if the student reader only has one source PDF per book:

```text
GET /api/student/books/:bookId/pdf-view
```

The endpoint must:

```text
- Validate bookId exists.
- Validate fileId belongs to the book if fileId is used.
- Validate the file role is source_document.
- Validate file is PDF.
- Validate the student/session is allowed to read this book.
- Reject blocked sessions.
- Never return raw server filePath to the client.
- Stream/send the PDF from DB-stored filePath only after validation.
```

If the current project does not yet have full login/identity, use the existing anonymous/session mechanism and clearly report the limitation.

---

## 6. Response Headers

The protected PDF endpoint must return safe inline-view headers:

```http
Content-Type: application/pdf
Content-Disposition: inline; filename="reader.pdf"
Cache-Control: private, no-store, no-cache, must-revalidate
Pragma: no-cache
Expires: 0
X-Content-Type-Options: nosniff
```

Do not use `attachment` for the default student reader path.

---

## 7. Student Frontend Requirement

The student reader must not use:

```text
/admin/books/:bookId/files/:fileId/raw
/public/...pdf
/uploads/...pdf
real server filePath
```

Instead, it must use the protected student PDF URL.

Expected behavior:

```text
- Student reader displays PDF through the protected student API.
- The PDF URL should be scoped by book/file/session validation.
- If access is denied, display a friendly message instead of a broken viewer.
```

If the current viewer implementation uses iframe/PDF.js/browser PDF viewer, update the source URL only; do not rework the whole PDF viewer unless necessary.

---

## 8. Watermark Overlay Requirement

Add a frontend overlay watermark on top of the PDF viewer container.

Do not modify the original PDF binary in this phase.

Watermark should include available identifiers such as:

```text
- iBrain 智匯
- session id or student display id
- book id or book title
- timestamp/date if available
```

Example:

```text
iBrain 智匯 · session_xxxxx · book_xxxxx · 2026-06-15
```

Visual requirements:

```text
- low opacity
- repeated diagonal or subtle pattern
- pointer-events: none
- does not block reading or PDF controls
- visible enough to discourage screenshots/leaks
```

---

## 9. Access Log Requirement

Record PDF viewing access.

Minimum log fields:

```text
bookId
fileId
sessionId or student identifier
ip address if available
user agent if available
viewedAt timestamp
```

Preferred implementation:

```text
- Add a lightweight access log repository/table only if an existing logging table is not available.
- If adding DB schema, use idempotent migration.
- If avoiding DB change, log to existing audit/session log and clearly report limitation.
```

This task may add schema only if needed for access logs.

If schema is added, clearly report migration requirements.

---

## 10. Blocking / Permission Behavior

The endpoint must reject:

```text
- missing session
- blocked session
- invalid bookId/fileId
- file not belonging to book
- non-PDF file
- reference image file
```

Suggested HTTP responses:

```text
401: missing/invalid session
403: blocked or not allowed to read this book
404: book/file not found or not visible
400: file is not a PDF source document
```

Use existing student session conventions where possible.

---

## 11. UI Download/Print Controls

If using PDF.js viewer and download/print buttons are controlled by app UI:

```text
- Hide download button.
- Hide print button if feasible.
- Hide open-file button if present.
```

Do not claim this is complete download prevention.

This is UI-level deterrence only.

If using browser native PDF viewer and the download button cannot be reliably hidden, report as a limitation.

---

## 12. Non-Scope

Do not implement these in this task:

```text
- Full DRM
- Full DevTools/F10 blocking
- OCR
- Server-side per-page image rendering
- Short-lived signed token flow
- Rate limit / anti-scraping system
- Full admin auth hardening
- Payment/credit changes
- PDF parser or chapter builder changes
- Admin Files page parsing changes
```

Those are future hardening phases.

---

## 13. Expected Files

Likely files to inspect/change:

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/studentClient.ts
apps/AI-Stu-R1/src/components/ChatPanel.tsx if needed
apps/AI-Stu-R1/src/styles.css or equivalent student CSS
apps/AI-adm-D1/src/server/index.ts or shared server route file if student APIs live there
packages/db/src/repositories/* if access log is added
packages/db/src/schema.ts only if access log table is added
packages/db/src/migrate.ts only if access log table is added
packages/schema/src/* only if shared schema is needed
```

Keep changes narrowly scoped.

---

## 14. Required Read-Only Inspection

Start with:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -8

rg "pdf|PDF|raw|files/:fileId/raw|sendFile|Content-Disposition|Cache-Control|student|blocked|session" apps packages
rg "BookReaderPage|iframe|pdf-view|PDF.js|viewer|watermark" apps/AI-Stu-R1/src
rg "chat_sessions|isBlocked|rejectIfBlocked|sessionId|lastIp" apps packages
```

---

## 15. Verification Requirements

After implementation, run:

```bash
pnpm build
pnpm typecheck

git diff --name-only
git diff --stat
```

Manual/API verification:

```text
1. Student reader uses protected student PDF URL, not admin raw URL.
2. Direct admin raw endpoint is not used by student frontend.
3. Protected PDF endpoint returns Content-Type: application/pdf.
4. Protected PDF endpoint returns Content-Disposition: inline.
5. Protected PDF endpoint returns no-store/no-cache headers.
6. Missing/invalid session is rejected.
7. Blocked session is rejected.
8. Reference image file is rejected as PDF source.
9. Watermark overlay appears above PDF viewer.
10. Access log is written or existing logging limitation is clearly reported.
11. Existing AI chat/reader layout still works visually.
```

Use curl where possible:

```bash
curl -i "http://127.0.0.1:5173/api/student/books/<bookId>/files/<fileId>/pdf-view"
```

or the actual route implemented.

Do not run destructive DB commands.
Do not run broad `pkill`.
Do not use `git add .`.

Stage only relevant files explicitly.

Suggested commit message:

```bash
git commit -m "feat: protect student PDF viewing endpoint"
```

---

## 16. Final Termination Report Format

Final report must be in Traditional Chinese only.

Use this format:

```md
## 最終回報

- 最終狀態：
  - SUCCESS / FAILURE / BLOCKER / PERMISSION-HALT

- 本次是否有 commit：
  - 是 / 否

- commit SHA：
  - <short SHA or N/A>

- 主要修改範圍：
  - 受保護 PDF endpoint：
  - Student reader PDF URL：
  - session / blocked 檢查：
  - inline/no-store headers：
  - watermark overlay：
  - access log：

- PDF 是否仍不放 public 靜態目錄：
  - 是 / 否 / 既有狀態未確認

- 前端是否避免暴露真實 filePath：
  - 是 / 否

- student frontend 是否不使用 admin raw endpoint：
  - 是 / 否

- 受保護 API 是否檢查：
  - session：
  - bookId/fileId：
  - blocked session：
  - PDF source role：

- Response headers 驗證：
  - Content-Type application/pdf：
  - Content-Disposition inline：
  - Cache-Control no-store/no-cache：
  - X-Content-Type-Options nosniff：

- 浮水印驗證：
  - 是否顯示：
  - 是否不阻擋 PDF 操作：
  - 使用哪些識別文字：

- Access log 驗證：
  - 是否有記錄：
  - 記錄欄位：
  - 是否新增 DB schema：
  - 是否需要 migration：

- 下載防護限制：
  - 是否明確說明無法 100% 阻止 DevTools 下載：
  - 是否只做到第一層基本保護：

- 是否混入 unrelated 變更：
  - 否；若有請列出

- pnpm build：
  - PASS / FAIL / NOT RUN

- pnpm typecheck：
  - PASS / FAIL / ENVIRONMENT ERROR / NOT RUN

- git status --short：
  ```text
  <paste output>
  ```

- 合併 / 部署狀態：
  - NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY

- 結論：
  - <一句話說明本次基本保護是否可接受>
```

---

## 17. Acceptance Criteria

This task is acceptable only if:

```text
- Student reader no longer uses public/admin raw PDF URL directly.
- Protected student PDF endpoint validates access before streaming PDF.
- Response headers discourage download/cache.
- Watermark overlay is visible.
- PDF access is logged or logging limitation is explicitly reported.
- No unrelated backend/admin/parser work is mixed into the commit.
- build/typecheck pass.
```
