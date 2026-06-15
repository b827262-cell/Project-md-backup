# 2026-06-15 SmartBook Codex Task: Student Reader Outer Space Resize Handles

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
STUDENT_READER_OUTER_SPACE_RESIZE_HANDLES
```

---

## 2. Corrected Requirement

The previous requirement was interpreted as internal split panes:

```text
[章節目錄] |drag| [PDF] |drag| [AI問答]
```

That is not the desired behavior.

The corrected requirement is to use the blank space outside the reader and make it adjustable:

```text
[空白區] [章節目錄] [PDF] [AI問答] [空白區]
        ↑(1號)                         ↑(2號)
     分隔線1                         分隔線2
```

Meaning:

```text
- The user wants to reclaim or release the blank space on both sides of the reader.
- The PDF reader should grow when the outer reader boundary expands.
- The whole reader workbench should feel like it can be stretched left/right.
```

---

## 3. Handle 1: Left Outer Boundary / 章節目錄外

Position:

```text
Between left blank area and the chapter outline.
```

Behavior:

```text
- Drag right: chapter outline becomes narrower.
- Drag left: chapter outline becomes wider, PDF becomes wider, AI panel also becomes wider if space allows.
```

Interpretation:

```text
- Dragging the left boundary left expands the whole reader workbench into the left blank area.
- Dragging the left boundary right shrinks the reader workbench from the left side.
- The reader content should redistribute space so the PDF gains usable width when the workbench expands.
```

---

## 4. Handle 2: Right Outer Boundary / AI 外側

Position:

```text
Between the AI panel and the right blank area.
```

Behavior:

```text
- Drag left: AI panel becomes narrower.
- Drag right: AI panel becomes wider and PDF also becomes wider if space allows.
```

Interpretation:

```text
- Dragging the right boundary right expands the whole reader workbench into the right blank area.
- Dragging the right boundary left shrinks the reader workbench from the right side.
- The reader content should redistribute space so the PDF gains usable width when the workbench expands.
```

---

## 5. Important Difference from Internal Splitters

Do not implement only this:

```text
[章節目錄] |drag| [PDF] |drag| [AI問答]
```

That only changes internal column widths and does not solve the blank-space problem.

The desired solution must address this:

```text
[空白區] |outer drag| [章節目錄] [PDF] [AI問答] |outer drag| [空白區]
```

The blank space outside the reader must become adjustable.

---

## 6. Goal

Add two outer resize handles to control the reader workbench width and side whitespace.

Expected result:

```text
- User can drag the left outer handle to reclaim or release left blank space.
- User can drag the right outer handle to reclaim or release right blank space.
- PDF area expands when there is more available workbench width.
- Chapter and AI panels remain usable.
- Existing collapse controls still work.
- Existing PDF zoom/page navigation remain unchanged.
```

---

## 7. Recommended Layout Model

Use a parent layout with adjustable side gutters:

```text
[ left gutter ] [ reader workbench ] [ right gutter ]
```

State example:

```ts
type ReaderOuterLayout = {
  leftGutter: number;
  rightGutter: number;
  tocWidth: number;
  aiWidth: number;
};
```

Or simpler:

```ts
type ReaderOuterLayout = {
  leftOffset: number;
  rightOffset: number;
};
```

Suggested localStorage key:

```text
smartbook.reader.outerLayout
```

The inner workbench may still use existing ratio presets and collapse states.

---

## 8. CSS Direction

The reader should not be trapped inside a fixed `max-width` centered container.

Use the actual class names in the codebase, but conceptually:

```css
.reader-outer-shell {
  width: 100vw;
  max-width: none;
  display: grid;
  grid-template-columns: var(--left-gutter) minmax(0, 1fr) var(--right-gutter);
}

.reader-workbench {
  min-width: 0;
  width: 100%;
}
```

Outer handles:

```css
.reader-outer-resize-handle {
  width: 8px;
  cursor: col-resize;
  user-select: none;
}
```

The final structure can be:

```text
left blank area
left outer handle
reader workbench: [chapter] [PDF] [AI]
right outer handle
right blank area
```

or an equivalent structure that visually behaves the same.

---

## 9. Constraints

Suggested constraints:

```text
Minimum left blank area: 0px
Maximum left blank area: 360px
Minimum right blank area: 0px
Maximum right blank area: 360px
Minimum total reader workbench width: 1000px on desktop if viewport allows
PDF pane minimum width: 480px
Chapter outline minimum width: 220px
AI panel minimum width: 300px
```

If viewport is too narrow, prioritize PDF usability.

---

## 10. Drag Behavior

Use pointer events.

Requirements:

```text
- Drag should update layout live.
- Avoid accidental text selection while dragging.
- Stop dragging on pointerup / pointercancel.
- Persist gutter/outer width values to localStorage.
- Refresh should keep the adjusted layout.
```

Handle labels:

```tsx
role="separator"
aria-orientation="vertical"
aria-label="調整左側閱讀空間"
aria-label="調整右側閱讀空間"
```

Optional:

```text
- Double-click handle resets the corresponding side gutter.
- Add a reset layout button if easy.
```

---

## 11. Preserve Existing Features

Do not remove:

```text
- 收合章節 / 展開章節
- 章節 dropdown
- PDF page display
- PDF zoom control
- 貼圖筆記
- 6:4 / 1:1 / 4:6 ratio buttons
- 收合AI / 展開AI
- 問AI
- watermark overlay
```

If existing ratio buttons exist:

```text
- They may continue to control inner PDF/AI proportions.
- The new outer handles control the external blank-space boundaries.
```

---

## 12. Preserve Protected PDF Behavior

Do not break:

```text
/api/student/books/:bookId/session
/api/student/books/:bookId/files/:fileId/pdf-view
X-Student-Session-Id
pdf_access_logs
inline/no-store headers
blocked session checks
watermark overlay
```

Student frontend must still not use:

```text
/api/admin/.../raw
public PDF URL
uploads PDF URL
real server filePath
```

---

## 13. Scope

Frontend-only.

Likely files:

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/styles.css
apps/AI-Stu-R1/src/components/PdfReaderToolbar.tsx only if reset/preset UI is added
```

Do not modify backend or DB.

Do not modify:

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

## 14. Required Read-Only Inspection

Run first:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -8

rg "student-pdf|reader-pdf|reader-workbench|reader-shell|reader-page|tocCollapsed|aiCollapsed|ratio-6-4|ratio-1-1|ratio-4-6|PdfReaderToolbar|ChapterSidebar|reader-chat-col|收合AI|收合章節" apps/AI-Stu-R1/src
```

---

## 15. Verification

After implementation:

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

Stage only relevant frontend files explicitly.

Suggested commit message:

```bash
git commit -m "feat: add outer resize handles to student reader"
```

---

## 16. Manual Browser Verification

Open:

```text
http://127.0.0.1:5173/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509
```

Verify:

```text
1. A left outer drag handle exists between the left blank area and chapter outline.
2. Drag left handle right: chapter outline becomes narrower.
3. Drag left handle left: chapter outline becomes wider, PDF gains width, and AI can gain width if space allows.
4. A right outer drag handle exists between AI panel and right blank area.
5. Drag right handle left: AI panel becomes narrower.
6. Drag right handle right: AI panel becomes wider, PDF gains width if space allows.
7. The blank space outside the reader visibly changes.
8. PDF area expands when the workbench gains width.
9. Refresh keeps the adjusted layout.
10. 收合章節 still works.
11. 收合AI still works.
12. PDF zoom still works.
13. Protected PDF still loads from /api/student/.../pdf-view.
14. No /api/admin/.../raw is used by student frontend.
```

---

## 17. Final Termination Report

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
  - 左外側分隔線：
  - 右外側分隔線：
  - 外側空白區調整：
  - reader workbench 是否可變寬：
  - localStorage 是否保留：
  - 收合章節是否保留：
  - 收合AI 是否保留：
  - protected endpoint 是否未改：

- 手動驗證：
  - 1號分隔線往右拉：
  - 1號分隔線往左拉：
  - 2號分隔線往左拉：
  - 2號分隔線往右拉：
  - 外側空白是否可被回收：
  - PDF 是否吃到新增空間：
  - refresh 後是否保留：

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

## 18. Acceptance Criteria

Accept only if:

```text
- The two handles are outer-space handles, not only internal column splitters.
- Left handle controls the left blank area / chapter side boundary.
- Right handle controls the right blank area / AI side boundary.
- Blank space outside the reader can be reclaimed or released.
- PDF grows when the reader workbench gets more width.
- Layout persists after refresh.
- build/typecheck pass.
- No backend/DB changes are included.
```
