# 2026-06-15 SmartBook Codex Task: PDF Outline Preview and Reference Image Support

## 0. Language Rule

```text
All execution-facing work must be in English.

This includes:
- implementation notes
- code review notes
- command comments
- verification notes
- intermediate progress reports
- error/blocker explanation during execution

Only the final termination report must be written in Traditional Chinese.
```

---

## 1. Current Accepted Baseline

Do not rework or mix unrelated accepted commits.

### 1.1 Chapter / Content / Chat Linking

```text
Commit: b524857
Status: accepted
Scope: editable chapter page ranges and chapter-aware chat linking
Note: includes schema/db changes; deployment requires migration or equivalent DB update.
```

### 1.2 PDF Physical Page Alignment

```text
Commit: 2f44efa
Status: accepted
Scope: align parsed PDF pages with physical page numbers
Files:
- packages/book-core/src/chapter-builder.ts
- packages/book-core/src/pdf-parser.ts
```

Accepted rules:

```text
PDF physical page number is canonical.
PDF P1 = stored pageNumber 1.
PDF P100 = stored pageNumber 100.
Printed book page labels must not be used as canonical navigation pages.
```

The parser must fail fast if the PDF parser returns invalid page numbers:

```ts
if (!Number.isInteger(page.num) || page.num < 1) {
  throw new Error(
    `Invalid PDF page number from parser: ${page.num}. Expected 1-based physical page number.`
  );
}

const physicalPageNumber = page.num;
```

### 1.3 Admin Accounts IP / Risk Controls

```text
Commit: dfa659b
Status: AGY validation PASS
Scope: /admin/accounts IP tracking, risk labels, block/unblock controls
```

Do not mix this feature with the PDF outline preview work.

---

## 2. New Task Name

```text
PDF_OUTLINE_CHAPTER_PREVIEW_AND_REFERENCE_IMAGE_FLOW
```

---

## 3. Primary Page and Priority

Primary implementation target:

```text
/admin/books/:bookId/files
```

Concrete local page:

```text
http://127.0.0.1:5174/admin/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509/files
```

The `/chapters` page is not the primary parsing entry point.

Expected role separation:

```text
/files    = upload, parse, preview, reference image, apply entry point
/chapters = final applied chapter result management page
```

---

## 4. Main Functional Goal

When an administrator uploads or manages a PDF from the Files page, the Parse action should not blindly overwrite final chapters.

Required workflow:

```text
Admin uploads PDF
→ Admin opens /admin/books/:bookId/files
→ Admin clicks Parse / Re-parse Outline for a PDF file
→ System extracts PDF outline entries and physical PDF destination pages
→ System shows an editable chapter preview / mapping table
→ Admin reviews and edits chapter titles, enabled flags, PDF start/end pages, entry types, notes
→ Admin clicks Apply Chapters
→ System writes final chapters to DB
→ System links FileContent by physical PDF page range
→ /admin/books/:bookId/chapters shows the final applied result
```

---

## 5. Critical Page Number Rule

Canonical page number must always be the physical PDF page.

```text
PDF physical pageNumber must never be shifted by:
- zero-based index
- cover page offset
- TOC offset
- printed book page label
- outline title page range
- chapter start offset
- chunk order
```

Correct example:

```text
Outline title: 01—1~37第1章
Printed page range: 1~37
PDF physical start page: 10
PDF physical end page: 47
Canonical chapter pageStart: 10
Canonical chapter pageEnd: 47
```

Wrong example:

```text
第1章 pageStart = 1
```

---

## 6. Reference Image Support

The system should support administrator-provided reference images/screenshots as parsing and page-mapping hints.

Reference images are important because some PDFs show a reliable outline tree with visible physical page destination numbers.

Reference image support requirement:

```text
The admin may attach or view reference screenshots next to the editable chapter preview.
The screenshot helps the admin manually compare and correct chapter title / printed label / physical PDF page mapping.
```

Important:

```text
Reference images must not automatically override canonical PDF physical page numbers.
They are hints for manual review unless OCR is explicitly implemented in a future phase.
```

### 6.1 Version 1 Acceptable Scope

```text
- Allow or plan support for attaching/reference image metadata to the PDF file.
- Show the reference image alongside the editable chapter preview if available.
- Let the admin manually use the reference image to adjust rows.
- No OCR required in this phase.
```

### 6.2 Future Optional Scope

```text
- OCR reference image
- Extract outline rows from image text
- Auto-suggest chapter rows from image
- Compare PDF outline vs reference image and highlight mismatch
```

Do not implement OCR unless it is already available and safe in the current architecture.

---

## 7. Reference Outline Examples

### 7.1 Reference Example A

```text
000前1~2自序                         PDF P1
000前3~6目錄                         PDF P2
00—1~4第0章                          PDF P6
01—1~37第1章                         PDF P10
02—1~62第2章                         PDF P48
03—1~24第3章                         PDF P110
04—1~173第4章                        PDF P134
05—1~118第5章                        PDF P308
06—1~84第6章                         PDF P426
07—01~92第7章之1                     PDF P510
07—93~184第7章之2                    PDF P602
08—1~69+1第8章                       PDF P694
09—1~179第9章                        PDF P764
09—180版權頁                         PDF P943
```

Expected suggested physical ranges:

```text
自序       P1   ~ P1
目錄       P2   ~ P5
第0章      P6   ~ P9
第1章      P10  ~ P47
第2章      P48  ~ P109
第3章      P110 ~ P133
第4章      P134 ~ P307
第5章      P308 ~ P425
第6章      P426 ~ P509
第7章之1   P510 ~ P601
第7章之2   P602 ~ P693
第8章      P694 ~ P763
第9章      P764 ~ P942
版權頁     P943 ~ P943
```

### 7.2 Reference Example B

```text
000前期（2頁）
00—前01~2序1版
00—前03~6本書使用方式及建議
00—前07~08目錄                 PDF P1
01—1~7+1第1章                  PDF P3
02—1~9+1第2章                  PDF P11
03—1~10第3章                   PDF P21
04—1~28第4章                   PDF P31
05—1~22第5章                   PDF P59
06—1~30第6章                   PDF P81
07—1~55+3MEMO第7章             PDF P111
08—1~24第8章                   PDF P169
09—1~49+3MEMO第9章             PDF P193
10—1~46第10章                  PDF P245
11—1~41+1第11章                PDF P291
12—1~24第12章                  PDF P333
13—1~13+1第13章                PDF P357
14—1~24第14章                  PDF P371
15—1~48第15章                  PDF P395
16—1~38第16章                  PDF P443
17—1~7第17章                   PDF P481
17—18高點網路書店
後1~3高普考（有作者名）
後4版權頁                      PDF P498
後5~6後期（2頁）
```

Important behavior for Reference Example B:

```text
- Do not assume every outline row is a final chapter.
- Some rows are group/header rows without physical destination pages.
- Rows without physical destination pages should default to disabled or group/unknown.
- Admin may manually enable and assign a physical page range if needed.
```

Correct interpretation:

```text
Outline title: 07—1~55+3MEMO第7章
Printed label/range: 1~55+3MEMO
Suggested title: 第7章
Canonical pageStart: 111
```

Wrong interpretation:

```text
Canonical pageStart: 1
```

---

## 8. Preview Table Requirements

The editable preview table should show:

```text
Enabled
Original PDF outline title
Reference image title / note
Suggested chapter title
Printed page label / range
PDF physical start page
PDF physical end page
Entry type
Sort order
Admin note
Apply status
```

Suggested entry types:

```text
front_matter
toc
chapter
appendix
copyright
back_matter
group
unknown
```

Admin must be able to edit:

```text
- enabled / disabled
- chapter title
- printed label / range
- PDF physical start page
- PDF physical end page
- entry type
- sort order
- admin note
```

Rows without a physical destination page:

```text
PDF physical start page: null
PDF physical end page: null
Enabled: false by default
Entry type: group or unknown
```

---

## 9. Files Page UI Requirements

On `/admin/books/:bookId/files`, provide actions such as:

```text
Parse Outline
Re-parse Outline
Preview Chapters
Upload Reference Image
View Reference Image
Apply Chapters
```

If implementing all actions at once is too large, use a safe staged implementation and clearly report what is completed vs pending.

Minimum acceptable Version 1:

```text
- Files page has Parse/Re-parse Outline entry point.
- Files page can show editable chapter preview before final apply.
- Admin can edit rows before applying.
- Apply writes final chapters.
- Reference image can be displayed or its support is clearly staged.
```

---

## 10. Backend/API Requirements

Expected backend capabilities:

```text
- Extract PDF outline for a selected PDF file.
- Return preview rows without immediately overwriting final chapters.
- Accept edited preview rows from admin.
- Apply selected rows as official chapters.
- Link FileContent using physical PDF pageStart/pageEnd.
```

Suggested API shape:

```ts
parsePdfOutlinePreview(bookId, fileId): ChapterPreviewRow[]
applyChapterPreview(bookId, fileId, rows: ChapterPreviewRow[]): ApplyResult
```

Suggested preview row model:

```ts
type ChapterPreviewRow = {
  id?: string;
  enabled: boolean;
  originalTitle: string;
  suggestedTitle: string;
  printedPageLabel?: string | null;
  printedPageStart?: string | null;
  printedPageEnd?: string | null;
  pageStart: number | null; // physical PDF page
  pageEnd: number | null;   // physical PDF page
  entryType: "front_matter" | "toc" | "chapter" | "appendix" | "copyright" | "back_matter" | "group" | "unknown";
  sortOrder: number;
  adminNote?: string | null;
};
```

Only add DB schema if persistent draft/preview storage is required.

If the preview can be generated and applied in memory from the UI state, avoid unnecessary schema changes.

---

## 11. Expected Implementation Areas

Likely files:

```text
apps/AI-adm-D1/src/pages/BookFilesPage.tsx or equivalent files page
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/server/index.ts
packages/book-core/src/chapter-builder.ts
packages/book-core/src/pdf-parser.ts only if needed, but do not regress accepted invariant behavior
packages/db/src/repositories/chapter.repo.ts
packages/schema/src/chapter.schema.ts
```

If persistent reference image metadata or persistent preview rows are added, also inspect:

```text
packages/db/src/schema.ts
packages/db/src/migrate.ts
```

---

## 12. Strict Non-Scope

Do not mix this task with:

```text
admin accounts
risk controls
appearance
header
hero
theme
payment
credit
login
auth unrelated changes
PDF physical page invariant rework beyond necessary integration
student reader unrelated UX
```

---

## 13. Required Read-Only Inspection

Start with:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git branch --show-current
git log --oneline -5

rg "files" apps/AI-adm-D1/src
rg "Parse|parse|reparse|build-chapters|outline|chapters" apps packages
rg "chapter" apps/AI-adm-D1/src packages/book-core/src packages/db/src packages/schema/src
```

---

## 14. Verification Requirements

After implementation, verify:

```text
1. The Files page is the primary parse/preview/apply entry point.
2. Clicking Parse/Re-parse does not blindly overwrite final chapters.
3. A preview table appears before Apply.
4. Admin can edit enabled/title/pageStart/pageEnd/type/sort/note before applying.
5. PDF physical page is canonical.
6. Printed labels are display metadata only.
7. Rows without physical pages are not automatically applied as navigable chapters.
8. After Apply, /chapters displays the applied result.
9. Content linking uses physical PDF page ranges.
10. Reference-image workflow is supported or clearly staged.
```

Run:

```bash
pnpm build
pnpm typecheck

git diff --name-only
git diff --stat
```

If `pnpm typecheck` is not available, report `NOT AVAILABLE`.

---

## 15. Git Rules

Do not use:

```bash
git add .
```

Stage only relevant files explicitly.

Suggested commit message:

```bash
git commit -m "feat: add PDF outline chapter preview from files page"
```

Do not merge.
Do not deploy.
Do not run `pnpm db:push` unless explicitly instructed later.

---

## 16. Final Termination Report Format

The final report must be written in Traditional Chinese only.

Use this format:

```md
## 最終回報

- 最終狀態：
  - SUCCESS / FAILURE / BLOCKER / PERMISSION-HALT

- 本次是否有 commit：
  - 是 / 否

- commit SHA：
  - <short SHA or N/A>

- 主要入口頁：
  - /admin/books/:bookId/files

- 實際修改檔案：
  - <file list>

- Files 頁功能：
  - Parse / Re-parse Outline：
  - Preview Chapters：
  - Apply Chapters：
  - Upload / View Reference Image：

- 是否支援參考附圖：
  - 是 / 否 / 部分完成

- 參考附圖用途：
  - 顯示輔助 / 手動校正 / OCR 自動解析 / 未實作

- 是否仍保留 PDF physical page 為 canonical：
  - 是 / 否

- 是否避免 printed page label 作為 canonical pageStart/pageEnd：
  - 是 / 否

- 管理者是否可先調整再套用：
  - 是 / 否

- /chapters 頁是否顯示套用後結果：
  - 是 / 否

- 是否需要 DB migration：
  - 是 / 否

- OCR 是否實作：
  - 是 / 否 / 不在本階段

- 是否混入 unrelated 變更：
  - 否；若有請列出

- pnpm build：
  - PASS / FAIL / NOT RUN

- pnpm typecheck：
  - PASS / FAIL / NOT AVAILABLE / NOT RUN

- git status --short：
  ```text
  <paste output>
  ```

- git show --stat --oneline HEAD：
  ```text
  <paste output>
  ```

- 合併 / 部署狀態：
  - NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY

- 注意事項：
  - <migration/reference-image/OCR/re-parse notes>
```

---

## 17. Acceptance Summary

This task is accepted only when:

```text
- /files is the primary parse/preview/apply entry point.
- Admin can review and edit outline rows before applying.
- Canonical navigation uses PDF physical page numbers.
- Printed labels and reference images are only aids unless explicitly confirmed by admin.
- Build and typecheck pass.
- No unrelated features are mixed into the commit.
```
