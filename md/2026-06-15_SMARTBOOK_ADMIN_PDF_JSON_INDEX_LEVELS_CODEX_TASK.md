# 2026-06-15 SmartBook Codex Task: Admin PDF JSON Index Levels

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
ADMIN_PDF_JSON_INDEX_LEVELS_AND_REMOVE_REFERENCE_IMAGE_UPLOAD
```

---

## 2. Background

The Admin Files page currently contains PDF upload / parse actions and also reference-image upload actions.

Current user decision:

```text
Remove image upload/reference-image functionality from this page.
Keep the page focused on PDF parsing and PDF-derived JSON index generation.
```

The user wants to enhance PDF decomposition into JSON index files with 5 levels:

```text
1. 簡單：分頁數
2. 進階：分章節
3. 複雜：分逗號
4. 高階：分行
5. 頂級：分句
```

Interpretation:

```text
These 5 levels are segmentation/index granularity levels for Chinese PDF text.
They should produce structured JSON index output for downstream search, AI QA, RAG, and debugging.
```

---

## 3. Goals

### 3.1 Remove reference image upload from Admin Files page

Remove or hide the reference-image upload functions from:

```text
/admin/books/:bookId/files
```

Required UI changes:

```text
- Remove Upload Reference Image button from PDF rows.
- Remove reference-image upload input/action from this page if present.
- Do not encourage image-based outline/reference flow on this page.
- Keep PDF upload and PDF parse/index actions.
```

Existing reference image records:

```text
- Do not delete existing files from disk or DB automatically.
- If existing reference_image rows exist, either hide them from the main PDF parse table or show them as legacy/read-only rows with View/Delete only.
- Do not create data-loss behavior.
```

Backend endpoints related to reference-image upload may remain for backward compatibility unless safe removal is explicitly scoped and verified.

---

### 3.2 Add 5-level PDF JSON index generation

Add UI and API support to generate/download/store JSON index output from a PDF source document.

Admin should be able to choose one of the 5 levels and generate JSON.

Suggested UI:

```text
PDF source row actions:
- Re-parse Content
- Re-parse Outline
- Generate JSON Index
- Level selector: 簡單 / 進階 / 複雜 / 高階 / 頂級
- Download JSON Index or View JSON Index result
```

Do not break the current PDF parsing flow.

---

## 4. Five JSON Index Levels

### Level 1: 簡單 / page

User label:

```text
簡單：分頁數
```

Granularity:

```text
One JSON index item per physical PDF page.
```

Source of truth:

```text
PDF physical page number.
```

Example structure:

```json
{
  "level": "page",
  "items": [
    {
      "id": "p_0001",
      "type": "page",
      "pageStart": 1,
      "pageEnd": 1,
      "text": "...",
      "charCount": 1234
    }
  ]
}
```

---

### Level 2: 進階 / chapter

User label:

```text
進階：分章節
```

Granularity:

```text
One JSON index item per applied chapter.
```

Source of truth:

```text
Existing applied chapters and chapter.pageStart/pageEnd.
```

Important:

```text
chapter.pageStart and chapter.pageEnd are PDF physical page numbers.
Do not use printed book page labels as canonical navigation pages.
```

Example structure:

```json
{
  "level": "chapter",
  "items": [
    {
      "id": "chapter_001",
      "type": "chapter",
      "chapterId": "...",
      "title": "第1章",
      "pageStart": 10,
      "pageEnd": 47,
      "text": "...",
      "charCount": 45678
    }
  ]
}
```

---

### Level 3: 複雜 / clause-by-comma

User label:

```text
複雜：分逗號
```

Granularity:

```text
Split page/chapter text into smaller clause-like units using Chinese punctuation.
```

Suggested separators:

```text
， 、 ； ： , ; :
```

Optional sentence-ending punctuation may remain with the current clause if needed:

```text
。 ！ ？ . ! ?
```

Implementation note:

```text
This is not semantic NLP. It is deterministic punctuation-based segmentation.
Keep original page number mapping.
```

Example structure:

```json
{
  "level": "clause",
  "items": [
    {
      "id": "p_0010_c_0001",
      "type": "clause",
      "pageStart": 10,
      "pageEnd": 10,
      "chapterId": "chapter_001",
      "order": 1,
      "text": "...，",
      "charCount": 42
    }
  ]
}
```

---

### Level 4: 高階 / line

User label:

```text
高階：分行
```

Granularity:

```text
One JSON index item per text line.
```

Preferred source:

```text
Use PDF parser line information if available.
```

Fallback:

```text
If the current parser only stores page text, split by newline characters.
If no reliable line breaks exist, report limitation clearly and do not fake visual line positions.
```

Example structure:

```json
{
  "level": "line",
  "items": [
    {
      "id": "p_0010_l_0001",
      "type": "line",
      "pageStart": 10,
      "pageEnd": 10,
      "lineNumber": 1,
      "chapterId": "chapter_001",
      "text": "...",
      "charCount": 28
    }
  ]
}
```

If bounding boxes are available later, add optional metadata only:

```json
{
  "bbox": { "x": 0, "y": 0, "width": 100, "height": 16 }
}
```

Do not invent bbox values.

---

### Level 5: 頂級 / sentence

User label:

```text
頂級：分句
```

Granularity:

```text
One JSON index item per sentence.
```

Suggested separators:

```text
。 ！ ？ ；
. ! ? ;
```

Chinese-specific note:

```text
Keep punctuation attached to the sentence.
Handle common abbreviations and numeric punctuation conservatively.
This can be deterministic regex-based first; do not require external NLP service in this task.
```

Example structure:

```json
{
  "level": "sentence",
  "items": [
    {
      "id": "p_0010_s_0001",
      "type": "sentence",
      "pageStart": 10,
      "pageEnd": 10,
      "chapterId": "chapter_001",
      "order": 1,
      "text": "這是一個句子。",
      "charCount": 7
    }
  ]
}
```

---

## 5. JSON Index Metadata

Every generated JSON index should include metadata:

```json
{
  "schemaVersion": "smartbook-pdf-index-v1",
  "bookId": "...",
  "fileId": "...",
  "fileName": "...",
  "level": "page | chapter | clause | line | sentence",
  "levelLabel": "簡單 | 進階 | 複雜 | 高階 | 頂級",
  "generatedAt": "ISO timestamp",
  "pageCount": 943,
  "itemCount": 123,
  "source": {
    "pageNumberMode": "pdf_physical_page",
    "parser": "existing project PDF parser"
  },
  "items": []
}
```

Required invariant:

```text
PDF physical page number remains canonical.
No zero-based page numbers.
No printed book page labels as canonical pageStart/pageEnd.
```

---

## 6. API Design

Add a student/admin-safe admin endpoint for JSON index generation.

Suggested endpoint:

```text
POST /api/admin/books/:bookId/files/:fileId/generate-json-index
```

Body:

```json
{
  "level": "page"
}
```

Supported level values:

```text
page
chapter
clause
line
sentence
```

Response options:

### Option A: Return JSON directly

```json
{
  "index": { ... }
}
```

### Option B: Return downloadable file

```json
{
  "indexFileName": "book_..._page_index.json",
  "index": { ... }
}
```

Choose the simpler safe approach for this commit. Do not add DB schema unless clearly necessary.

---

## 7. Storage Decision

Preferred first implementation:

```text
Generate JSON on demand and allow download/view from the admin UI.
```

Avoid DB migration unless necessary.

If saving generated JSON to disk is implemented:

```text
- Save under an existing safe generated-files/uploads area.
- Never overwrite source PDF.
- Use deterministic safe file name.
- Report storage path behavior clearly.
```

If no persistent storage is added:

```text
- Report that JSON is generated on demand.
- The admin can download the JSON.
```

---

## 8. UI Requirements

On Admin Files page:

```text
- Keep Upload PDF.
- Keep Parse/Re-parse Content.
- Keep Parse/Re-parse Outline if still needed.
- Remove Upload Reference Image.
- Add JSON index level selector.
- Add Generate JSON Index action.
- Add download/view JSON result if implemented.
```

Suggested level labels:

```text
簡單：分頁數
進階：分章節
複雜：分逗號
高階：分行
頂級：分句
```

---

## 9. Important Non-Goals

Do not implement in this task:

```text
- OCR
- Image reference upload
- Semantic vector embedding
- RAG re-indexing pipeline
- External NLP service
- LLM-based sentence segmentation
- DB schema migration unless absolutely required
- Student frontend changes
- PDF.js reader changes
- Payment/credit/auth changes
```

---

## 10. Expected Files

Likely:

```text
apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/server/index.ts
packages/book-core/src/* if shared index builder is added
packages/schema/src/* if request/response schema is added
```

Keep changes narrowly scoped.

---

## 11. Required Read-Only Inspection

Run first:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -10

rg "Upload Reference Image|View Reference Image|reference_image|attach-reference-image|parse-content|outline-preview|apply-chapters|book_contents|FileContent|pageNumber|chapter.pageStart|pdf-parser|buildChapters" apps packages
```

---

## 12. Verification

Run:

```bash
pnpm build
pnpm typecheck

git diff --name-only
git diff --stat
```

Manual/admin verification:

```text
1. Open /admin/books/:bookId/files.
2. Confirm Upload Reference Image is removed.
3. Confirm PDF upload remains.
4. Confirm Parse/Re-parse Content remains.
5. Confirm Parse/Re-parse Outline remains if still part of workflow.
6. Select each JSON index level.
7. Generate JSON index for each level.
8. Confirm JSON has schemaVersion, bookId, fileId, level, generatedAt, pageCount, itemCount, items.
9. Confirm page-level index has one item per physical PDF page.
10. Confirm chapter-level index uses applied chapters and physical pageStart/pageEnd.
11. Confirm clause-level index splits Chinese punctuation by comma-like punctuation.
12. Confirm line-level index uses line/newline data and reports limitation if true line data is unavailable.
13. Confirm sentence-level index splits by sentence-ending punctuation.
14. Confirm no DB migration unless explicitly reported.
```

Do not use:

```bash
git add .
```

Stage only relevant files explicitly.

Suggested commit message:

```bash
git commit -m "feat: add PDF JSON index generation levels"
```

or if UI removal is dominant:

```bash
git commit -m "feat: simplify admin PDF files page with JSON index levels"
```

---

## 13. Final Termination Report

Final report must be in Traditional Chinese only.

Use this format:

```md
## 最終回報

- 最終狀態：
  - SUCCESS / PARTIAL_SUCCESS / FAILURE / BLOCKER / PERMISSION-HALT

- 本次是否有 commit：
  - 是 / 否

- commit SHA：
  - <short SHA or N/A>

- 主要修改範圍：
  - 移除圖片上傳功能：
  - PDF parse content 是否保留：
  - PDF parse outline 是否保留：
  - JSON index 產生 API：
  - JSON index UI：

- 5 級索引：
  - 簡單 / 分頁數：
  - 進階 / 分章節：
  - 複雜 / 分逗號：
  - 高階 / 分行：
  - 頂級 / 分句：

- JSON 格式：
  - schemaVersion：
  - bookId / fileId：
  - level / levelLabel：
  - pageCount / itemCount：
  - items 是否包含 pageStart/pageEnd：

- PDF physical page 是否仍為 canonical：
  - 是 / 否

- 是否有修改後端：
  - 是 / 否

- 是否有修改 DB / migration：
  - 是 / 否

- 是否混入 unrelated 變更：
  - 否；若有請列出

- pnpm build：
  - PASS / FAIL / NOT RUN

- pnpm typecheck：
  - PASS / FAIL / NOT RUN

- git status --short：
  ```text
  <paste output>
  ```

- 合併 / 部署狀態：
  - NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

---

## 14. Acceptance Criteria

Accept only if:

```text
- Image/reference-image upload is removed from the Admin Files page.
- PDF upload remains.
- Existing content/outline parse workflow is not broken.
- Admin can generate JSON indexes at 5 levels.
- JSON uses PDF physical page numbers as canonical.
- build/typecheck pass.
- No unrelated frontend/student/backend features are modified.
```
