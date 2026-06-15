# 2026-06-15 SmartBook Codex Task: Student Reader Drag Resize Panes

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
STUDENT_READER_DRAG_RESIZE_PANES
```

---

## 2. Background

The protected PDF reader and PDF zoom are already working.

Manual testing shows the remaining issue is layout width control:

```text
1. Chapter outline / PDF / AI panes still waste horizontal space on large screens.
2. The user wants a window-like resize tool.
3. Dragging left/right should resize the adjacent pane immediately.
```

User requirement:

```text
往左拉，欄位就在往左放大。
往右拉，欄位就在往右放大。
```

Interpretation:

```text
- Chapter pane right-edge handle:
  - drag right => chapter pane becomes wider
  - drag left => chapter pane becomes narrower, PDF gains space

- AI pane left-edge handle:
  - drag left => AI pane becomes wider
  - drag right => AI pane becomes narrower, PDF gains space

- PDF pane fills the remaining available width.
```

---

## 3. Goal

Add draggable split handles to the student PDF reader layout.

Expected layout:

```text
[ Chapter TOC ] |drag| [ PDF Viewer ] |drag| [ AI Chat ]
```

Requirements:

```text
- User can drag the Chapter/PDF divider.
- User can drag the PDF/AI divider.
- Pane widths update visually while dragging.
- Widths persist in localStorage.
- PDF viewer uses remaining available width.
- Collapsing chapter or AI still works.
- Existing PDF zoom, page navigation, watermark, and protected PDF endpoint remain unchanged.
```

---

## 4. Scope

Frontend-only.

Likely files:

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/components/PdfReaderToolbar.tsx only if toolbar reset buttons are added
apps/AI-Stu-R1/src/styles.css
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

## 5. Resize Behavior

### 5.1 Chapter pane handle

Handle position:

```text
between chapter outline and PDF viewer
```

Behavior:

```text
- drag right: chapter pane width increases
- drag left: chapter pane width decreases
- PDF pane adjusts automatically
```

Suggested constraints:

```text
min chapter width: 220px
max chapter width: 460px
```

### 5.2 AI pane handle

Handle position:

```text
between PDF viewer and AI panel
```

Behavior:

```text
- drag left: AI panel width increases
- drag right: AI panel width decreases
- PDF pane adjusts automatically
```

Suggested constraints:

```text
min AI width: 300px
max AI width: 620px
```

### 5.3 PDF area

Requirements:

```text
- PDF pane should fill all remaining width.
- PDF pane should not collapse below a usable desktop width.
- Suggested minimum PDF width: 480px.
```

If viewport becomes too narrow, prefer preserving PDF usability and clamp side panels.

---

## 6. Implementation Guidance

Use CSS grid with variables or inline style.

Suggested state:

```ts
type ReaderPaneSizes = {
  tocWidth: number;
  aiWidth: number;
};
```

Suggested localStorage key:

```text
smartbook.reader.paneSizes
```

Suggested grid template when both side panes are visible:

```css
.reader-pdf-grid {
  grid-template-columns: var(--toc-width, 280px) 8px minmax(480px, 1fr) 8px var(--ai-width, 380px);
}
```

When chapter is collapsed:

```css
.reader-pdf-grid.toc-collapsed {
  grid-template-columns: minmax(480px, 1fr) 8px var(--ai-width, 380px);
}
```

When AI is collapsed:

```css
.reader-pdf-grid.ai-collapsed {
  grid-template-columns: var(--toc-width, 280px) 8px minmax(480px, 1fr);
}
```

When both are collapsed:

```css
.reader-pdf-grid.toc-collapsed.ai-collapsed {
  grid-template-columns: minmax(480px, 1fr);
}
```

Use the actual class names in the codebase.

---

## 7. Drag Handle UX

Add visible but subtle split handles.

Requirements:

```text
- cursor: col-resize
- handle is easy enough to grab
- avoid accidental text selection while dragging
- update width during pointer movement
- stop dragging on pointerup / pointercancel
- support mouse and touch via Pointer Events if possible
```

Suggested handle attributes:

```tsx
role="separator"
aria-orientation="vertical"
aria-label="調整章節欄寬度"
aria-label="調整 AI 欄寬度"
```

Optional:

```text
- double click handle resets that pane width
- add a small reset layout button if easy
```

---

## 8. Preserve Existing Toolbar Controls

Do not remove:

```text
- 收合章節 / 展開章節
- 章節 dropdown
- PDF page display
- zoom control
- 貼圖筆記
- 6:4 / 1:1 / 4:6 ratio buttons if still present
- 收合AI / 展開AI
- 問AI
```

If ratio buttons conflict with manual resizing:

```text
- Keep them as quick presets.
- Clicking 6:4 / 1:1 / 4:6 should set pane widths to preset values.
- Manual drag should override the preset afterward.
```

---

## 9. Preserve Protected PDF Behavior

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

## 10. Required Read-Only Inspection

Run first:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -8

rg "student-pdf|reader-pdf|tocCollapsed|aiCollapsed|ratio-6-4|ratio-1-1|ratio-4-6|PdfReaderToolbar|ChapterSidebar|reader-chat-col|收合AI|收合章節" apps/AI-Stu-R1/src
```

---

## 11. Verification

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
git commit -m "feat: add draggable student reader panes"
```

---

## 12. Manual Browser Verification

Open:

```text
http://127.0.0.1:5173/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509
```

Verify:

```text
1. A vertical drag handle exists between chapter outline and PDF viewer.
2. Dragging the Chapter/PDF handle right makes the chapter pane wider.
3. Dragging the Chapter/PDF handle left makes the chapter pane narrower and PDF wider.
4. A vertical drag handle exists between PDF viewer and AI panel.
5. Dragging the PDF/AI handle left makes the AI panel wider.
6. Dragging the PDF/AI handle right makes the AI panel narrower and PDF wider.
7. PDF viewer immediately uses the changed available width.
8. Widths persist after page refresh.
9. 收合章節 still hides the chapter pane and PDF expands.
10. 收合AI still hides the AI pane and PDF expands.
11. Ratio buttons still work as quick presets if retained.
12. PDF zoom still works.
13. Protected PDF still loads from /api/student/.../pdf-view.
14. No /api/admin/.../raw is used by student frontend.
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
  - Chapter/PDF 拖拉分隔線：
  - PDF/AI 拖拉分隔線：
  - pane width localStorage：
  - ratio preset 是否保留：
  - 收合章節是否保留：
  - 收合AI 是否保留：
  - protected endpoint 是否未改：

- 手動驗證：
  - 往右拉 Chapter/PDF：
  - 往左拉 Chapter/PDF：
  - 往左拉 PDF/AI：
  - 往右拉 PDF/AI：
  - refresh 後是否保留寬度：
  - PDF 是否吃滿剩餘空間：

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
- User can drag the chapter/PDF divider.
- User can drag the PDF/AI divider.
- The adjacent pane width changes in the expected drag direction.
- PDF uses the remaining width.
- Widths persist after refresh.
- build/typecheck pass.
- No backend/DB changes are included.
```
