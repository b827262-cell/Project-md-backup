# 2026-06-15 SmartBook Codex Task: Student PDF Native Reader Toolbar and Notes

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
STUDENT_PDF_NATIVE_READER_TOOLBAR_AND_NOTES
```

---

## 2. Background

Commit `eb8e117` implemented first-layer student PDF access protection and passed AGY validation.

The student reader is now moving away from the old MD/text display. The final reader direction is:

```text
PDF original layout = primary student reading view
PDF physical page number = canonical page navigation
PDF/app outline = chapter navigation
Parsed MD/text chunks = AI/search backend only, not visible reading body
```

Current manual test shows the page still has old MD reader controls and body below the protected PDF view. The user wants the PDF reader itself to provide the original toolbar functions.

---

## 3. User Requirements

The PDF reader must provide these visible functions:

```text
1. Use outline/chapter lookup directly against the PDF reader.
2. Adjustable article/PDF zoom percentage, default 100%.
3. 貼圖筆記 using screenshot/capture functionality.
4. Ratio adjustment: 6:4, 1:1, 4:6.
5. Add 收合AI / 展開AI button similar to 收合章節.
6. Remove the old MD visible content panel from the reader UI.
```

---

## 4. Critical Technical Note

If the current implementation uses a browser-native PDF iframe, then reliable screenshot/capture of PDF content may not be possible because browser PDF viewers are often opaque/plugin-like content.

Therefore:

```text
- Prefer PDF.js canvas rendering for page control, zoom control, page screenshot, and note capture.
- If PDF.js migration is too large for this commit, implement only the safe frontend changes and clearly report the screenshot limitation as BLOCKER/PARTIAL.
- Do not fake screenshot support.
```

Do not claim screenshot capture works unless it is actually verified.

---

## 5. Goals

Implement a PDF-native student reader layout and toolbar:

```text
- Protected PDF viewer is the only main reading body.
- Old MD/text reader body is removed or hidden when PDF source exists.
- Chapter outline/dropdown jumps to PDF physical pages.
- Zoom percentage controls the PDF viewer scale.
- Ratio buttons 6:4 / 1:1 / 4:6 control PDF area vs AI area layout.
- AI panel can be collapsed/expanded.
- 貼圖筆記 button supports a real screenshot flow if technically feasible; otherwise report precise blocker.
```

---

## 6. Scope

Frontend-first changes.

Likely files:

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/components/ReaderViewport.tsx only if bypassing old MD UI
apps/AI-Stu-R1/src/components/ChatPanel.tsx only if needed
apps/AI-Stu-R1/src/studentClient.ts only if PDF URL/page helpers are centralized
apps/AI-Stu-R1/src/styles.css
```

Avoid backend changes unless a true blocker is found.

Do not modify unless required:

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

Keep the protected endpoint behavior from `eb8e117` unchanged.

---

## 7. Required UI Layout

Desktop target layout:

```text
Top Header
PDF Toolbar
[Chapter Outline / Dropdown] [Protected PDF Viewer] [AI Chat]
```

When AI is collapsed:

```text
[Chapter Outline / Dropdown] [Protected PDF Viewer full expanded width]
```

When chapter outline is collapsed:

```text
[Protected PDF Viewer] [AI Chat]
```

When both are collapsed:

```text
[Protected PDF Viewer full width]
```

---

## 8. Toolbar Requirements

The PDF toolbar should include the following controls:

```text
- 收合章節 / 展開章節
- Chapter dropdown / outline lookup
- Current page display if available
- Zoom percentage control, default 100%
- 貼圖筆記 button
- Ratio buttons: 6:4, 1:1, 4:6
- 收合AI / 展開AI
- 問AI button may remain if useful, but should not duplicate confusing behavior
```

The toolbar should control PDF-native state, not the old MD reader.

---

## 9. Chapter Outline / PDF Page Navigation

Requirements:

```text
- Use existing applied chapters from the book data.
- Chapter labels/order must follow the PDF outline/applied chapter list.
- chapter.pageStart/pageEnd must be treated as PDF physical page numbers.
- Clicking a chapter or selecting from dropdown jumps the PDF viewer to chapter.pageStart.
- Do not use printed book page labels as canonical navigation pages.
```

Canonical rule:

```text
PDF physical pageNumber is the navigation source of truth.
```

If using iframe as a temporary implementation:

```text
Use URL fragment such as #page=<physicalPage>&zoom=<percent>&toolbar=0&navpanes=0.
```

If using PDF.js:

```text
Use PDF.js page rendering / scroll-to-page logic and keep page state in React.
```

---

## 10. Zoom Percentage Control

Default:

```text
100%
```

Expected behavior:

```text
- User can change the zoom percentage.
- The visible PDF page scale changes accordingly.
- Zoom state is displayed as a percentage.
- Existing old MD zoom logic should not be used as the primary visible reader control.
```

Minimum acceptable values:

```text
75%
90%
100%
110%
125%
150%
```

If a direct numeric input already exists, keep it but make sure it controls the PDF viewer.

---

## 11. 貼圖筆記 / Screenshot Notes

User requirement:

```text
貼圖筆記，使用截圖功能
```

Required behavior if technically feasible:

```text
- User clicks 貼圖筆記.
- System captures the current visible PDF page or visible PDF viewport.
- System creates a note draft with the screenshot image attached or shown in a note panel.
- The note should be associated with current bookId, current PDF physical page, and active chapter if available.
```

Minimum first-phase UI if persistence is not ready:

```text
- Show the captured screenshot preview in a note draft area/modal.
- Let user type note text.
- Do not lose the current PDF page context.
```

Important:

```text
- Do not fake screenshot capture.
- If native iframe prevents screenshot capture, report that screenshot requires PDF.js canvas rendering.
- If implementing PDF.js is out of scope, leave 貼圖筆記 disabled with a clear user-facing message and final report blocker/limitation.
```

Do not implement backend persistence unless it is already available and safe.

Do not add DB schema for notes in this task unless explicitly necessary and approved.

---

## 12. Ratio Buttons

Required ratios:

```text
6:4
1:1
4:6
```

Meaning:

```text
6:4 = PDF area wider, AI/chat narrower
1:1 = PDF and AI balanced
4:6 = AI/chat wider, PDF narrower
```

If AI is collapsed, ratio should not squeeze the PDF; PDF should use available width.

If chapter outline is collapsed, ratio applies to PDF vs AI only.

---

## 13. 收合AI / 展開AI

Add AI collapse control similar to 收合章節.

Expected labels:

```text
收合AI
展開AI
```

Behavior:

```text
- Default can be expanded.
- Clicking 收合AI hides the right AI chat column.
- Clicking 展開AI restores the right AI chat column.
- When AI is collapsed, the PDF viewer expands horizontally.
- ChatPanel behavior must remain unchanged when expanded.
```

---

## 14. Remove Old MD Visible Body

When PDF source is available, remove/hide:

```text
- Old ReaderViewport body
- Old MD/text cards
- "這個章節還沒有內容" as main reading body
- Old extracted-content visible reader panel
```

Keep parsed text/MD backend usage for AI/search. Do not delete backend parse-content logic.

If no PDF source exists, show a clean fallback:

```text
尚未提供 PDF 教材。
```

---

## 15. Preserve Existing Protected PDF Behavior

Do not break:

```text
/api/student/books/:bookId/session
/api/student/books/:bookId/files/:fileId/pdf-view
X-Student-Session-Id header
pdf_access_logs
inline/no-store headers
blocked session checks
watermark overlay
```

---

## 16. Required Read-Only Inspection

Run first:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -8

rg "ReaderViewport|ChapterSidebar|ChatPanel|student-pdf|pdfUrl|pdfSessionId|activeChapter|pageStart|pageEnd|收合章節|問 AI|問AI|貼圖筆記|ratio|zoom" apps/AI-Stu-R1/src
```

---

## 17. Implementation Verification

After changes:

```bash
pnpm build
pnpm typecheck

git diff --name-only
git diff --stat
```

Do not use:

```bash
git add .
```

Stage only relevant files explicitly.

Suggested commit message:

```bash
git commit -m "feat: make student reader PDF-native"
```

---

## 18. Manual Verification

Open:

```text
http://127.0.0.1:5173/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509
```

Verify:

```text
1. Protected PDF is the only main visible reading body.
2. Old MD/text content panel is not visible when PDF exists.
3. Chapter outline/dropdown uses the book's applied PDF chapters.
4. Selecting chapter jumps to correct PDF physical page.
5. Zoom percentage changes PDF scale.
6. 貼圖筆記 either captures a real screenshot or clearly reports unsupported limitation.
7. Ratio buttons 6:4 / 1:1 / 4:6 adjust PDF vs AI layout.
8. 收合AI hides the AI panel.
9. 展開AI restores the AI panel.
10. 收合章節 still works.
11. Watermark overlay remains visible.
12. PDF still loads from /api/student/.../pdf-view.
13. Student frontend does not use /api/admin/.../raw.
14. AI chat still works visually when expanded.
```

---

## 19. Final Termination Report

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
  - PDF 原生閱讀主體：
  - 移除/隱藏舊 MD 顯示：
  - PDF 大綱/章節跳頁：
  - 文章比例 / zoom 百分比：
  - 貼圖筆記 / screenshot：
  - 6:4 / 1:1 / 4:6 比例：
  - 收合AI / 展開AI：
  - watermark 是否保留：
  - protected endpoint 是否未改：

- PDF physical page 是否仍為 canonical：
  - 是 / 否

- screenshot 驗證：
  - 是否真能截圖：
  - 若不能，原因：
  - 是否需要 PDF.js：

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

## 20. Acceptance Criteria

Accept only if:

```text
- Old MD visible reader body is gone when PDF exists.
- PDF is the main reading area.
- Chapter lookup controls PDF page navigation.
- Zoom controls PDF scale.
- Ratio buttons affect PDF/AI layout.
- AI can be collapsed/expanded.
- Protected PDF endpoint from eb8e117 remains intact.
- build/typecheck pass.
```

If screenshot notes cannot be implemented due to native iframe/browser PDF limitations, this can be accepted only as `PARTIAL_SUCCESS` if the limitation is honestly reported and no fake feature is shipped.
