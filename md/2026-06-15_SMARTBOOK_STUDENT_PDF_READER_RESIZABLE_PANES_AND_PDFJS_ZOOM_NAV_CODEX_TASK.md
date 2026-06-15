# 2026-06-15 SmartBook Codex Task: Student PDF Reader Resizable Panes and Reliable PDF Navigation

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
STUDENT_PDF_READER_RESIZABLE_PANES_AND_RELIABLE_NAV_ZOOM
```

---

## 2. Background

Commit `0a756e2` converted the student reader into a PDF-native reader and passed AGY validation with notes.

Manual browser testing after AGY validation found three remaining UX/behavior issues:

```text
1. The layout still wastes space because chapter/PDF/AI widths are fixed or semi-fixed.
2. The chapter outline/dropdown is not reliably integrated with the PDF viewer's actual visible page.
3. The zoom percentage control appears ineffective in the browser-native PDF iframe.
```

Important context:

```text
- Commit eb8e117 protected the student PDF endpoint and must remain intact.
- The student reader currently uses a protected PDF blob and a browser-native PDF iframe.
- Browser-native PDF iframe behavior for #page= and #zoom= is not fully controllable from React.
```

---

## 3. Goal

Fix the reader UX so the student can:

```text
1. Resize the chapter/PDF/AI panes by dragging split handles.
2. Use chapter outline/dropdown to reliably change the PDF visible page.
3. Use zoom percentage to actually change PDF scale.
```

If native iframe cannot support reliable page/zoom control, migrate the visible PDF rendering layer to PDF.js canvas/viewer while keeping the protected PDF endpoint unchanged.

---

## 4. Required Behaviors

### 4.1 Resizable panes

Add user-controlled resizing for horizontal layout.

Expected:

```text
- User can drag between Chapter TOC and PDF viewer.
- User can drag between PDF viewer and AI panel.
- Resizing should reduce wasted blank space.
- Pane widths should persist in localStorage per browser/session.
- Provide sensible min/max width constraints.
- If chapter is collapsed, PDF uses the freed width.
- If AI is collapsed, PDF uses the freed width.
```

Suggested min widths:

```text
Chapter TOC: 220px minimum, 420px maximum
AI panel: 300px minimum, 560px maximum
PDF area: flexible, never below 480px on desktop
```

Suggested UX:

```text
- Thin vertical drag handle between panels.
- Cursor: col-resize.
- No text selection while dragging.
- Double-click handle can reset widths if simple to implement.
```

Do not depend only on fixed 6:4 / 1:1 / 4:6 buttons. Keep those ratio buttons as quick presets if they still make sense, but manual drag must be the primary solution.

---

### 4.2 Reliable chapter-to-PDF navigation

The chapter outline/dropdown must update the actual visible PDF page.

Requirement:

```text
- Clicking a chapter must navigate to chapter.pageStart.
- Dropdown chapter selection must navigate to chapter.pageStart.
- chapter.pageStart is a PDF physical page number and remains canonical.
- Do not use printed book page labels as canonical page navigation.
```

If staying with native iframe temporarily:

```text
- Update iframe src to include #page=<physicalPage>.
- Force iframe reload by changing iframe key when page changes.
- Verify in real Chromium browser that the visible PDF page actually changes.
```

If native iframe does not reliably navigate:

```text
- Implement PDF.js-based rendering/viewer for the protected blob.
- Use PDF.js page APIs to render target page directly.
- Chapter navigation must call PDF.js render/goToPage logic.
```

Do not mark chapter navigation as PASS if only React state changes but the visible PDF page does not move.

---

### 4.3 Reliable zoom percentage

The zoom percentage must actually control PDF scale.

Required:

```text
- Default zoom = 100%.
- User can change zoom between at least 50% and 200%.
- Prefer options: 50%, 75%, 90%, 100%, 110%, 125%, 150%, 175%, 200%.
- Visible PDF page must change scale when zoom changes.
```

If using native iframe:

```text
- Try #zoom=<percent> and force iframe reload with key changes.
- Verify visually in Chromium.
```

If native iframe zoom remains ineffective:

```text
- Migrate to PDF.js rendering so scale is controlled by React state.
- Do not fake the zoom control.
```

---

## 5. Strong Recommendation: PDF.js if native iframe fails

Native browser PDF iframe has known limitations:

```text
- React cannot directly control internal PDF plugin state.
- #page= may only apply on initial load or may not react to repeated updates.
- #zoom= may be ignored or inconsistently applied by Chromium's built-in PDF viewer.
- Screenshot notes cannot be implemented against iframe/plugin pixels.
```

Therefore, if reliable navigation and zoom cannot be achieved with iframe, use PDF.js.

Acceptable PDF.js phase scope:

```text
- Render current page to canvas.
- Keep protected PDF blob loading through /api/student/.../pdf-view.
- Implement page navigation from chapter.pageStart.
- Implement zoom via PDF.js render scale.
- Keep watermark overlay.
- Keep AI/chat layout and collapse behavior.
```

PDF.js screenshot note can remain future work unless easy after canvas rendering. If a canvas is available, implement screenshot capture only if it can be verified.

---

## 6. Preserve Existing Protected Behavior

Do not break or modify the protected endpoint behavior from `eb8e117`.

Do not change unless absolutely necessary:

```text
/api/student/books/:bookId/session
/api/student/books/:bookId/files/:fileId/pdf-view
X-Student-Session-Id behavior
pdf_access_logs
inline/no-store headers
blocked session validation
```

Student frontend must continue to avoid:

```text
/api/admin/.../raw
public PDF URL
uploads PDF URL
real server filePath exposure
```

---

## 7. Scope

Frontend-first.

Likely files:

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/components/PdfReaderToolbar.tsx
apps/AI-Stu-R1/src/components/StickyNoteModal.tsx only if screenshot/note UI is adjusted
apps/AI-Stu-R1/src/styles.css
apps/AI-Stu-R1/src/studentClient.ts only if PDF blob helper needs adjustment
```

If adding PDF.js dependency, update only the necessary package manifest / lockfile and report it clearly.

Avoid backend changes.

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

## 8. Required Read-Only Inspection

Run first:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -8

rg "PdfReaderToolbar|StickyNoteModal|student-pdf|iframe|pdfUrl|pdfPage|pdfZoom|zoom|pageStart|ratio-6-4|ratio-1-1|ratio-4-6|aiCollapsed|ChapterSidebar" apps/AI-Stu-R1/src
rg "pdfjs|pdf.js|react-pdf|PDFDocumentProxy|canvas" apps package.json pnpm-lock.yaml
```

---

## 9. Implementation Strategy

### Strategy A: Native iframe patch attempt

Use only if it can be visually verified.

Implement:

```text
- iframe src = `${pdfUrl}#page=${pdfPage}&zoom=${pdfZoom}&toolbar=0&navpanes=0`
- iframe key changes when pdfPage or pdfZoom changes.
- chapter select updates pdfPage.
- zoom select updates pdfZoom.
```

Acceptance requires manual browser verification that page and zoom actually change.

### Strategy B: PDF.js migration

Use if Strategy A fails or is unreliable.

Implement:

```text
- Load protected PDF Blob/ArrayBuffer.
- Render selected page to canvas using PDF.js.
- Current page state is controlled by React.
- Zoom state controls PDF.js render scale.
- Chapter select renders chapter.pageStart.
- Keep watermark overlay above canvas.
```

Do not migrate unrelated pages.

---

## 10. Verification

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

Stage only relevant files explicitly.

Suggested commit messages:

```bash
git commit -m "fix: make student PDF navigation and zoom reliable"
```

or, if PDF.js is added:

```bash
git commit -m "feat: render student PDF with controllable viewer"
```

---

## 11. Manual Browser Verification

Open:

```text
http://127.0.0.1:5173/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509
```

Verify:

```text
1. Drag the Chapter/PDF divider left and right.
2. Drag the PDF/AI divider left and right.
3. Confirm empty space is reduced and PDF uses the available width.
4. Collapse chapter panel; PDF expands.
5. Collapse AI panel; PDF expands.
6. Select several chapters from the chapter list/dropdown.
7. Confirm the actual visible PDF page changes to chapter.pageStart.
8. Change zoom to 75%, 100%, 125%, 150%, 200%.
9. Confirm the actual visible PDF scale changes.
10. Confirm watermark remains visible and does not block interaction.
11. Confirm protected PDF still loads from /api/student/.../pdf-view.
12. Confirm no /api/admin/.../raw is used by student frontend.
```

If any browser-native PDF limitation remains, report it clearly and do not mark as full PASS.

---

## 12. Final Termination Report

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
  - 可拖拉左右 pane：
  - 章節跳 PDF 實體頁：
  - zoom 0~200% / 50~200% 控制：
  - iframe patch 或 PDF.js：
  - AI 收合 / 章節收合是否保留：
  - watermark 是否保留：
  - protected endpoint 是否未改：

- 技術選擇：
  - native iframe / PDF.js
  - 若仍用 iframe，請說明 page/zoom 是否已實測有效：
  - 若改 PDF.js，請列出新增依賴：

- PDF physical page 是否仍為 canonical：
  - 是 / 否

- 手動瀏覽器驗證：
  - 拖拉 Chapter/PDF divider：
  - 拖拉 PDF/AI divider：
  - 章節選擇跳頁：
  - zoom 75/100/125/150/200：
  - AI 收合後 PDF 是否展開：
  - 章節收合後 PDF 是否展開：

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

## 13. Acceptance Criteria

Accept only if:

```text
- User can manually resize pane widths.
- Chapter selection changes the actual visible PDF page.
- Zoom changes the actual visible PDF scale.
- PDF remains protected through /api/student/.../pdf-view.
- No admin raw endpoint is used.
- build/typecheck pass.
```

Do not accept as full success if only React state changes but the visible PDF page/zoom does not change.
