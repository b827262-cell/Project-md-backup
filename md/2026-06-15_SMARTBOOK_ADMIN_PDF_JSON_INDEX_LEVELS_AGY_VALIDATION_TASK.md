# 2026-06-15 SmartBook AGY Validation Task: Admin PDF JSON Index Levels

## 0. Language Rule

```text
All execution-facing inspection, command notes, code review notes, and verification reasoning must be in English.

Only the final termination report must be written in Traditional Chinese.
```

---

## 1. Validation Target

Feature name:

```text
ADMIN_PDF_JSON_INDEX_LEVELS_AND_REMOVE_REFERENCE_IMAGE_UPLOAD
```

Validate current HEAD.

Codex reported commit:

```text
cff8887 feat: add PDF JSON index generation levels
```

Codex reported status:

```text
SUCCESS
pnpm build: PASS
pnpm typecheck: PASS
working tree clean
```

---

## 2. Expected Implementation Summary

The Admin Files page should be converted from a PDF + reference-image workflow into a PDF parsing / JSON index generation page.

Expected behavior:

```text
- Upload Reference Image removed from the Admin Files page.
- Attach as Reference Image removed from the Admin Files page.
- Reference image preview panel removed from chapter preview.
- Existing reference_image rows are kept as legacy/read-only rows with View/Delete only.
- PDF upload remains.
- Parse/Re-parse Content remains.
- Parse/Re-parse Outline remains.
- Apply Chapters remains the only final chapter-writing action.
- New JSON index generation API exists.
- New JSON index UI exists with 5 levels.
```

---

## 3. Required Repository Inspection

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
- HEAD is cff8887 or a later commit that includes cff8887.
- working tree clean.
- changed files match the Admin/schema/book-core scope.
```

Reported changed files:

```text
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
apps/AI-adm-D1/src/server/index.ts
apps/AI-adm-D1/src/styles.css
packages/book-core/src/index.ts
packages/book-core/src/pdf-index-builder.ts
packages/schema/src/index.ts
packages/schema/src/pdfIndex.schema.ts
```

---

## 4. Validate Image Upload Removal

Run:

```bash
rg -n "Upload Reference Image|Attach as Reference Image|View Reference Image|referenceInputRef|referenceTargetFileId|selectedReferenceImage|files-reference-panel|files-reference-image|Reference Hint" apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx apps/AI-adm-D1/src/styles.css
```

Expected:

```text
- No Upload Reference Image button in FilesTab.
- No Attach as Reference Image UI in FilesTab.
- No reference image preview panel in chapter preview.
- No Reference Hint column in chapter preview table.
- Existing reference_image rows may still show as legacy rows with View/Delete only.
```

Manual verification:

```text
Open /admin/books/:bookId/files.
Confirm the page no longer provides image upload/attach/reference-preview workflow.
```

Important:

```text
Do not require deletion of existing reference_image rows.
No data loss should occur.
```

---

## 5. Validate PDF Parse Workflow Preservation

Run:

```bash
rg -n "parse-content|outline-preview|apply-chapters|Parse Content|Re-parse Content|Parse Outline|Re-parse Outline|Apply Chapters" apps/AI-adm-D1/src apps/AI-adm-D1/src/server/index.ts
```

Expected:

```text
- Parse/Re-parse Content remains for PDF source rows.
- Parse/Re-parse Outline remains for PDF source rows.
- Apply Chapters remains unchanged as the only final chapter-writing action.
- Outline preview still does not directly overwrite chapters.
```

Manual verification:

```text
1. Open Admin Files page.
2. Confirm PDF source row still has Re-parse Content.
3. Confirm PDF source row still has Re-parse Outline.
4. Run outline preview and confirm Apply Chapters is still required to write chapters.
```

---

## 6. Validate JSON Index API

Run:

```bash
rg -n "generate-json-index|generatePdfJsonIndex|buildPdfJsonIndex|generatePdfJsonIndexInputSchema|PdfJsonIndex|pdfJsonIndex" apps packages
```

Expected:

```text
- POST /api/admin/books/:bookId/files/:fileId/generate-json-index exists.
- Endpoint validates bookId.
- Endpoint validates fileId belongs to bookId.
- Endpoint validates file.role === source_document.
- Endpoint validates file is PDF.
- Endpoint validates input level.
- Endpoint returns { index }.
- No DB migration is added.
```

Optional API smoke test if admin server is running:

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"level":"page"}' \
  "http://127.0.0.1:5174/api/admin/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509/files/file_4c57bcc3-1ad2-4be3-9bfe-2bae8d78fbc1/generate-json-index" \
  | head -c 1000
```

Expected response begins with:

```json
{"index":{"schemaVersion":"smartbook-pdf-index-v1"
```

---

## 7. Validate 5-Level JSON Index Builder

Run:

```bash
sed -n '1,320p' packages/book-core/src/pdf-index-builder.ts
sed -n '1,140p' packages/schema/src/pdfIndex.schema.ts
```

Validate levels:

```text
page      = 簡單 / 分頁數
chapter   = 進階 / 分章節
clause    = 複雜 / 分逗號
line      = 高階 / 分行
sentence  = 頂級 / 分句
```

### 7.1 簡單 / 分頁數

Expected:

```text
- One item per PDF physical page.
- Empty physical pages are still represented at page level.
- pageStart/pageEnd are 1-based physical PDF pages.
```

### 7.2 進階 / 分章節

Expected:

```text
- Uses applied chapters from DB.
- Uses chapter.pageStart and chapter.pageEnd.
- Invalid chapter physical page ranges are skipped and recorded in notes.
- Does not use printed labels as canonical pages.
```

### 7.3 複雜 / 分逗號

Expected:

```text
- Splits by comma-like punctuation: ，、；：,;:
- Keeps page mapping.
- This is deterministic punctuation segmentation, not semantic NLP.
```

### 7.4 高階 / 分行

Expected:

```text
- Uses newline splits from stored page text.
- Does not invent PDF bbox/geometry.
- Adds notes explaining true PDF line geometry/bbox is unavailable.
```

### 7.5 頂級 / 分句

Expected:

```text
- Splits by sentence-ending punctuation: 。！？；.!?;
- Keeps punctuation attached to the segment.
- Keeps PDF physical page mapping.
```

---

## 8. Validate JSON Schema Contract

Run:

```bash
sed -n '1,160p' packages/schema/src/pdfIndex.schema.ts
```

Expected metadata:

```text
schemaVersion = smartbook-pdf-index-v1
bookId
fileId
fileName
level
levelLabel
generatedAt
pageCount
itemCount
source.pageNumberMode = pdf_physical_page
items[]
```

Every item should include:

```text
id
type
pageStart
pageEnd
text
charCount
optional chapterId
optional chapterTitle
```

---

## 9. Validate Admin Files UI

Run:

```bash
rg -n "JSON_INDEX_LEVEL_OPTIONS|Generate JSON Index|View JSON|Download JSON|JSON Index Result|files-json-preview|PdfJsonIndexLevel" apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx apps/AI-adm-D1/src/styles.css
```

Expected:

```text
- Level selector exists with 5 labels.
- Generate JSON Index button exists on PDF source rows.
- View JSON and Download JSON are available after generation.
- JSON preview area exists.
```

Manual verification:

```text
1. Open /admin/books/:bookId/files.
2. Select each level.
3. Generate JSON Index.
4. Confirm JSON result shows schemaVersion, bookId, fileId, level, pageCount, itemCount, items.
5. Click Download JSON and confirm file downloads.
```

---

## 10. Validate PDF Physical Page Canonical Invariant

Run:

```bash
rg -n "pdf_physical_page|pageStart|pageEnd|printed|Printed|pageNumber|zero-based|0-based" packages/book-core/src/pdf-index-builder.ts apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
```

Expected:

```text
- pageNumberMode is pdf_physical_page.
- pageStart/pageEnd use physical PDF page numbers.
- printed labels remain display metadata only.
- No zero-based page number is used for JSON index output.
```

---

## 11. Build / Typecheck

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

Note:

```text
If the first typecheck attempt fails due environment/sandbox pnpm database access, rerun once with normal permission.
Only TypeScript diagnostic failures count as real typecheck failures.
```

---

## 12. Risk Review

AGY should explicitly check these risks:

```text
1. Generate JSON Index calls parsePdfToContents directly, so it reparses the PDF on demand.
   - This is acceptable for first implementation, but may be slow for large PDFs.
   - Report performance note if pageCount is large.

2. Existing attach-reference-image backend route may still exist.
   - Acceptable if UI no longer exposes it and no data loss occurs.
   - Report as backward-compatible legacy route.

3. Line level uses newline split, not real PDF line geometry.
   - Acceptable only if notes clearly state bbox/geometry limitation.

4. No DB persistence for generated JSON.
   - Acceptable if UI provides View/Download and final report states JSON is generated on demand.
```

---

## 13. Final Termination Report

Final report must be in Traditional Chinese only.

Use this format:

```md
## AGY 驗收回報

- 最終狀態：
  - PASS / PASS_WITH_NOTES / PARTIAL_SUCCESS / FAIL / BLOCKER / PERMISSION-HALT

- 驗收對象：
  - ADMIN_PDF_JSON_INDEX_LEVELS_AND_REMOVE_REFERENCE_IMAGE_UPLOAD

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

- 圖片上傳功能：
  - Upload Reference Image 是否移除：
  - Attach as Reference Image 是否移除：
  - Reference image preview panel 是否移除：
  - legacy reference_image rows 如何處理：

- PDF parse workflow：
  - Upload PDF 是否保留：
  - Parse/Re-parse Content 是否保留：
  - Parse/Re-parse Outline 是否保留：
  - Apply Chapters 是否仍為唯一寫入 chapters 的動作：

- JSON Index API：
  - endpoint：
  - 是否驗證 bookId/fileId：
  - 是否驗證 PDF source document：
  - 是否回傳 JSON：
  - 是否新增 DB schema：

- 5 級索引驗證：
  - 簡單 / 分頁數：
  - 進階 / 分章節：
  - 複雜 / 分逗號：
  - 高階 / 分行：
  - 頂級 / 分句：

- JSON schema：
  - schemaVersion：
  - bookId/fileId/fileName：
  - level/levelLabel：
  - pageCount/itemCount：
  - source.pageNumberMode：
  - items pageStart/pageEnd：

- PDF physical page canonical：
  - 是否維持：
  - 是否未使用 printed labels 作為 canonical：
  - 是否未使用 zero-based page：

- UI 驗證：
  - 5 級 selector：
  - Generate JSON Index：
  - View JSON：
  - Download JSON：

- 限制 / 風險：
  - JSON 是否 on-demand 產生：
  - 大 PDF 效能風險：
  - line level 是否僅 newline split：
  - attach-reference-image backend route 是否仍保留為 legacy：

- 是否有修改後端：
  - 是 / 否

- 是否有修改 DB / migration：
  - 是 / 否

- 是否混入 unrelated 變更：
  - 否；若有請列出

- build/typecheck：
  - pnpm build：
  - pnpm typecheck：

- 合併 / 部署狀態：
  - NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY

- 結論：
  - <一句話說明此 commit 是否可接受，以及是否需另開 persistent index / embedding pipeline task>
```

---

## 14. Suggested Judgment Rule

Use:

```text
PASS
```

if:

```text
- Image upload/attach UI is removed.
- PDF parse content/outline is preserved.
- JSON index API and UI work for all 5 levels.
- JSON schema is complete.
- PDF physical page is canonical.
- build/typecheck pass.
```

Use:

```text
PASS_WITH_NOTES
```

if:

```text
- Core feature works, but JSON is generated on demand and may be slow for large PDFs.
- Line-level index is newline-based rather than true PDF line geometry.
- Legacy backend attach-reference-image route remains for compatibility.
```

Use:

```text
PARTIAL_SUCCESS
```

if:

```text
- UI exists but one or more index levels are not fully implemented.
- Manual browser verification was not performed.
```

Use:

```text
FAIL
```

if:

```text
- Upload Reference Image is still visible.
- PDF parse workflow breaks.
- JSON index endpoint fails.
- JSON uses non-physical or zero-based page numbers.
- build/typecheck fails.
```
