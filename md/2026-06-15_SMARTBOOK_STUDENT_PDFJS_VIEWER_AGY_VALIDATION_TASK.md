# 2026-06-15 SmartBook AGY Validation Task: Student PDF.js Viewer

## 0. Language Rule

```text
All execution-facing inspection, command notes, code review notes, and verification reasoning must be in English.

Only the final termination report must be written in Traditional Chinese.
```

---

## 1. Validation Target

Feature name:

```text
STUDENT_PDF_READER_RESIZABLE_PANES_AND_RELIABLE_NAV_ZOOM
```

Validate current HEAD.

Codex report states the visible PDF layer has migrated from native iframe to PDF.js canvas rendering because real-browser testing showed native iframe `#page=` / `#zoom=` behavior was unreliable.

Expected summary:

```text
- PDF.js is now used for visible PDF rendering.
- Native iframe is no longer used as the primary visible PDF viewer.
- Protected PDF blob fetch remains unchanged.
- PDF page navigation is deterministic via PDF.js render/go-to-page behavior.
- Zoom 50%~200% is deterministic via PDF.js render scale.
- Drag resize panes are implemented and persisted.
- AI and chapter collapse are preserved.
- Watermark is preserved.
- No backend changes.
- No DB/migration changes.
- pdfjs-dist@5.4.296 added as frontend dependency.
```

---

## 2. Required Repository Inspection

Run:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git branch --show-current
git log --oneline -10
git rev-parse --short HEAD
git status --short
git show --stat --oneline HEAD
git show --name-only --oneline HEAD
```

Expected:

```text
- working tree clean
- latest commit is the Codex PDF.js viewer implementation commit
- changed files are limited to apps/AI-Stu-R1/* and pnpm-lock/package metadata if pdfjs-dist was added
```

Reported changed areas:

```text
apps/AI-Stu-R1/package.json
apps/AI-Stu-R1/src/vite-env.d.ts
apps/AI-Stu-R1/src/components/ProtectedPdfViewer.tsx
apps/AI-Stu-R1/src/components/PdfReaderToolbar.tsx
apps/AI-Stu-R1/src/components/ChapterSidebar.tsx
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/styles.css
pnpm-lock.yaml
```

Verify no backend or DB files changed in this commit:

```text
apps/AI-adm-D1/src/server/index.ts
packages/db/src/schema.ts
packages/db/src/migrate.ts
packages/db/src/repositories/pdfAccessLog.repo.ts
packages/book-core/src/chapter-builder.ts
packages/book-core/src/pdf-parser.ts
admin Files page
admin accounts/risk controls
payment/credit/login/auth
AI provider logic
```

---

## 3. Validate PDF.js Migration

Run:

```bash
rg -n "pdfjs|pdfjs-dist|GlobalWorkerOptions|PDFDocumentProxy|PDFPageProxy|canvas|ProtectedPdfViewer|pdf.worker" apps/AI-Stu-R1 package.json pnpm-lock.yaml
rg -n "iframe|#page=|#zoom=|student-pdf-iframe" apps/AI-Stu-R1/src
```

Expected:

```text
- pdfjs-dist@5.4.296 is present in apps/AI-Stu-R1/package.json or relevant workspace dependency.
- ProtectedPdfViewer renders PDF to canvas or PDF.js-controlled rendering surface.
- Native iframe is not the primary visible PDF viewer.
- There is no fake success based only on URL fragments.
- Vite worker integration is valid.
```

Check build output warning:

```text
A chunk >500KB warning is acceptable if build succeeds; it is a performance/code-splitting note, not a functional failure.
```

---

## 4. Validate Protected PDF Flow Is Intact

The backend from `eb8e117` must remain unchanged.

Run:

```bash
rg -n "pdf-view|/session|X-Student-Session-Id|getProtectedPdfBlob|pdf_access_logs|Content-Disposition|Cache-Control|/api/admin|/raw" apps packages
```

Expected:

```text
- Student frontend still fetches protected PDF through /api/student/.../pdf-view.
- X-Student-Session-Id is still used.
- No /api/admin/.../raw is used by student frontend.
- No public/uploads PDF URL is used.
- No real server filePath is exposed.
- Backend protected endpoint was not modified in this commit.
```

Optional runtime smoke if 5174 is running:

```bash
SESSION=$(curl -s -X POST -H "Content-Type: application/json" -d '{}' \
  "http://127.0.0.1:5174/api/student/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509/session" \
  | grep -o '"sessionId":"[^"]*' | grep -o '[^"]*$')

echo "Session: $SESSION"

curl -i -s -H "X-Student-Session-Id: $SESSION" \
  "http://127.0.0.1:5174/api/student/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509/files/file_4c57bcc3-1ad2-4be3-9bfe-2bae8d78fbc1/pdf-view" \
  | head -n 20
```

Expected headers:

```text
HTTP 200
Content-Type: application/pdf
Content-Disposition: inline
Cache-Control: private, no-store, no-cache, must-revalidate
X-Content-Type-Options: nosniff
```

---

## 5. Validate Deterministic Page Navigation

Run code inspection:

```bash
rg -n "pageStart|pdfPage|setPdfPage|renderPage|currentPage|goToPage|numPages|PDF physical|pageNumber" apps/AI-Stu-R1/src
```

Expected:

```text
- chapter.pageStart remains canonical.
- Selecting a chapter updates PDF.js current page state.
- PDF.js renders the target page, not merely a React label.
- The page display uses actual PDF page count if available.
```

Manual browser validation:

```text
1. Open student reader page.
2. Select 全部內容 / page 1.
3. Select chapter with a later physical page, for example 第6章 or 第9章.
4. Confirm the visible PDF canvas changes to the selected chapter page.
5. Confirm page indicator updates consistently.
```

Codex reported headless Chromium verification:

```text
- Page 1 and page 100 render different visible content.
- Non-white pixel counts differ significantly.
```

AGY must still perform or request human visual verification if possible.

---

## 6. Validate Reliable Zoom

Run:

```bash
rg -n "50|75|90|100|110|125|150|175|200|pdfZoom|zoom|scale|renderScale|viewport" apps/AI-Stu-R1/src/components apps/AI-Stu-R1/src/pages
```

Expected:

```text
- Zoom range supports at least 50% to 200%.
- Zoom controls PDF.js render scale.
- It is not dependent on native iframe #zoom.
- Page canvas size changes when zoom changes.
```

Manual browser validation:

```text
1. Set zoom to 75%.
2. Set zoom to 100%.
3. Set zoom to 125%.
4. Set zoom to 150%.
5. Set zoom to 200%.
6. Confirm the visible PDF scale changes each time.
```

Codex reported headless Chromium validation:

```text
- Page 1 @100% rendered 595×842.
- Page 1 @200% rendered 1190×1684.
- This proves PDF.js render scale changed exactly 2x.
```

---

## 7. Validate Drag Resize Panes

Run:

```bash
rg -n "pointerdown|pointermove|pointerup|col-resize|pane|resize|tocWidth|aiWidth|localStorage|reader.pane|ChapterSidebar|reader-chat-col" apps/AI-Stu-R1/src
```

Expected:

```text
- Chapter/PDF divider is implemented.
- PDF/AI divider is implemented.
- Dragging updates layout live.
- Width constraints are enforced.
- Widths persist to localStorage.
- PDF area uses remaining available space.
```

Manual browser validation:

```text
1. Drag Chapter/PDF divider right.
2. Confirm chapter pane becomes wider and PDF adjusts.
3. Drag Chapter/PDF divider left.
4. Confirm chapter pane becomes narrower and PDF expands.
5. Drag PDF/AI divider left.
6. Confirm AI pane becomes wider and PDF adjusts.
7. Drag PDF/AI divider right.
8. Confirm AI pane becomes narrower and PDF expands.
9. Refresh and confirm widths persist.
```

If the user later corrected the desired behavior to outer blank-space handles, report whether this implementation is internal pane resize or outer-space resize. Do not overstate compliance.

---

## 8. Validate Collapse Behavior

Run:

```bash
rg -n "tocCollapsed|collapsed|aiCollapsed|收合章節|展開章節|收合AI|展開AI" apps/AI-Stu-R1/src
```

Expected:

```text
- 收合章節 still hides chapter pane.
- 展開章節 restores chapter pane.
- 收合AI hides ChatPanel.
- 展開AI restores ChatPanel.
- PDF expands when side panes are hidden.
```

Manual browser validation:

```text
1. Click 收合章節.
2. Confirm PDF expands.
3. Click 展開章節.
4. Confirm chapter pane returns.
5. Click 收合AI.
6. Confirm PDF expands.
7. Click 展開AI.
8. Confirm AI panel returns.
```

---

## 9. Validate Watermark and Notes

Run:

```bash
rg -n "watermark|student-pdf-watermark|StickyNote|貼圖筆記|screenshot|canvas.toDataURL|toBlob" apps/AI-Stu-R1/src
```

Expected:

```text
- Watermark remains above PDF render surface.
- pointer-events remains none.
- Sticky note modal remains usable.
- If screenshot capture was added after PDF.js migration, verify it actually uses canvas data.
- If screenshot remains future work, verify UI does not claim fake screenshot capture.
```

---

## 10. Build / Typecheck

Run:

```bash
pnpm build
pnpm typecheck
```

Expected:

```text
pnpm build: PASS
pnpm typecheck: PASS
```

Acceptable note:

```text
Vite chunk size warning due to pdfjs-dist is acceptable as a performance/code-splitting note, not a failure.
```

---

## 11. Dependency / Deployment Notes

Validate:

```text
- pdfjs-dist@5.4.296 is added only where needed.
- pnpm-lock.yaml changed consistently.
- Deployment must run pnpm install before build if dependencies are not already installed.
- Vite emits PDF worker asset under dist/assets/.
- Static hosting must deploy all dist/assets files.
- No DB migration is required for this commit.
```

---

## 12. Final Termination Report

Final report must be in Traditional Chinese only.

Use this format:

```md
## AGY 驗收回報

- 最終狀態：
  - PASS / PASS_WITH_NOTES / PARTIAL_SUCCESS / FAIL / BLOCKER / PERMISSION-HALT

- 驗收對象：
  - STUDENT_PDF_READER_RESIZABLE_PANES_AND_RELIABLE_NAV_ZOOM

- commit SHA：
  - <short SHA>

- 實際修改檔案：
  - <file list>

- git status --short：
  ```text
  <paste output>
  ```

- 是否 working tree clean：
  - 是 / 否

- 技術選擇：
  - PDF.js / native iframe
  - 若為 PDF.js，新增依賴：
  - worker 資產是否正常：

- Protected PDF 行為：
  - 是否仍使用 /api/student/.../pdf-view：
  - 是否仍使用 X-Student-Session-Id：
  - 是否未使用 /api/admin/.../raw：
  - headers smoke test：
  - protected endpoint 是否未改：

- PDF page navigation：
  - 是否使用 chapter.pageStart：
  - 是否以 PDF physical page 為 canonical：
  - 是否由 PDF.js 實際 render 目標頁：
  - 瀏覽器/Headless 驗證結果：

- Zoom：
  - 是否支援 50~200%：
  - 是否由 PDF.js scale 控制：
  - 75/100/125/150/200 實測結果：

- Resize panes：
  - Chapter/PDF divider：
  - PDF/AI divider：
  - 是否 live resize：
  - 是否 localStorage 持久化：
  - 是否為內部分隔線或外側空白分隔線：

- Collapse behavior：
  - 收合章節：
  - 展開章節：
  - 收合AI：
  - 展開AI：
  - PDF 是否展開：

- Watermark / notes：
  - watermark 是否保留：
  - 是否不阻擋操作：
  - 貼圖筆記狀態：

- 是否有修改後端：
  - 是 / 否

- 是否有修改 DB / migration：
  - 是 / 否

- 是否混入 unrelated 變更：
  - 否；若有請列出

- build/typecheck：
  - pnpm build：
  - pnpm typecheck：

- 部署備註：
  - 是否需 pnpm install：
  - 是否需部署 dist/assets/pdf.worker：
  - 是否需 DB migration：

- 合併 / 部署狀態：
  - NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY

- 結論：
  - <一句話說明此 commit 是否可接受，以及是否仍需另開 outer-space resize task>
```

---

## 13. Suggested Judgment Rule

Use:

```text
PASS
```

if:

```text
- PDF.js renders visible PDF pages.
- Chapter navigation changes actual visible page.
- Zoom changes actual visible scale.
- Protected PDF flow is intact.
- Drag resize and collapse work as claimed.
- build/typecheck pass.
```

Use:

```text
PASS_WITH_NOTES
```

if:

```text
- PDF.js page/zoom is correct, but drag resize still needs human visual confirmation or is internal splitter only.
```

Use:

```text
PARTIAL_SUCCESS
```

if:

```text
- PDF.js page/zoom is correct but resize behavior does not match the final outer blank-space requirement.
```

Use:

```text
FAIL
```

if:

```text
- Visible PDF still depends on iframe page/zoom behavior.
- Zoom/page only changes React state but not actual PDF rendering.
- Protected endpoint was broken.
- build/typecheck fails.
```
