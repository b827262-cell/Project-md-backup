# 2026-06-15 SmartBook Codex Task: Student Reader Normal / 150 View Toggle

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
STUDENT_READER_NORMAL_150_VIEW_TOGGLE
```

---

## 2. Background

Manual browser testing shows that the previous layout/full-width fixes still do not produce the desired visual effect.

The user wants two explicit viewing-mode buttons:

```text
1. 正常
2. 放大
```

The expected visual result:

```text
正常 = current normal reader scale
放大 = visually similar to setting Chrome browser zoom to about 150%
```

Important browser limitation:

```text
A normal web page cannot directly control the user's Chrome browser zoom setting for security/user-preference reasons.
Therefore, implement an application-level reader zoom mode that visually mimics Chrome 150% zoom.
Do not claim that the app changes the actual browser zoom value.
```

---

## 3. Goal

Add a user-facing `正常 / 放大` view mode toggle to the student PDF reader.

Expected behavior:

```text
- 正常: use the current/default reader layout and scale.
- 放大: enlarge the student reader UI and PDF reading area to approximate Chrome 150% zoom.
- The toggle should be visible in the reader toolbar.
- The selected mode should persist in localStorage.
- The PDF, chapter list, toolbar controls, and AI panel should remain usable.
```

---

## 4. Scope

Frontend-only.

Likely files:

```text
apps/AI-Stu-R1/src/pages/BookReaderPage.tsx
apps/AI-Stu-R1/src/components/PdfReaderToolbar.tsx
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

## 5. UI Requirements

Add two buttons near the existing reader toolbar controls:

```text
正常
放大
```

Suggested placement:

```text
near 6:4 / 1:1 / 4:6, 收合AI / 問AI, or near the zoom selector
```

Visual behavior:

```text
- The active mode should be visually highlighted.
- Buttons should match existing toolbar button style.
- The toggle should not be confused with PDF zoom percentage.
```

Label wording:

```text
正常
放大
```

Optional tooltip/title:

```text
正常：標準閱讀大小
放大：放大閱讀介面，約等同瀏覽器 150% 檢視
```

---

## 6. Implementation Requirements

### 6.1 State

Add a state such as:

```ts
type ReaderViewMode = "normal" | "large";
const [readerViewMode, setReaderViewMode] = useState<ReaderViewMode>(...);
```

Persist to localStorage:

```text
smartbook.reader.viewMode
```

### 6.2 CSS class

Apply a class to the main reader root:

```text
reader-view-normal
reader-view-large
```

or:

```text
reader-scale-normal
reader-scale-150
```

### 6.3 Large mode effect

Large mode should approximate browser 150% zoom.

Acceptable approaches:

```text
- Use CSS variables to enlarge fonts, controls, toolbar height, PDF canvas/iframe container, and panel sizes.
- Or use CSS zoom: 1.5 on the reader workbench area if it works well in Chromium.
- Or combine wider/full-width layout with larger PDF zoom default.
```

Do not rely on changing actual Chrome browser zoom.

Recommended CSS variable approach:

```css
.reader-view-large {
  --reader-ui-scale: 1.5;
  --reader-font-scale: 1.25;
  --reader-toolbar-scale: 1.15;
}
```

Then adjust actual classes used in the codebase, for example:

```css
.reader-view-large .pdf-reader-toolbar button,
.reader-view-large .pdf-reader-toolbar select {
  font-size: calc(14px * var(--reader-toolbar-scale));
  min-height: 40px;
}

.reader-view-large .chapter-sidebar,
.reader-view-large .reader-chat-col {
  font-size: calc(16px * var(--reader-font-scale));
}

.reader-view-large .student-pdf-frame {
  min-height: calc(720px * 1.15);
}
```

Use actual class names found in the repository. Do not add unused selectors.

### 6.4 Relation to PDF zoom

The `正常 / 放大` toggle is an app-level view mode.

It is separate from the PDF zoom percentage control.

Expected behavior:

```text
- In normal mode, keep PDF zoom as selected by the user.
- In large mode, either preserve selected PDF zoom or optionally set default to 150% only when entering large mode if that is clearly implemented.
- Do not break the existing PDF zoom selector.
```

If using browser-native iframe and PDF zoom remains unreliable, report that PDF internal zoom remains a known limitation from native iframe behavior.

---

## 7. Preserve Existing Behavior

Do not break:

```text
- Protected PDF loading through /api/student/.../pdf-view
- X-Student-Session-Id
- pdf_access_logs
- watermark overlay
- chapter outline
- chapter collapse
- AI collapse
- ChatPanel
- ratio buttons 6:4 / 1:1 / 4:6
- sticky note modal
```

Student frontend must still not use:

```text
/api/admin/.../raw
public PDF URL
uploads PDF URL
real server filePath
```

---

## 8. Required Read-Only Inspection

Run first:

```bash
cd /home/b827262/project/AI-SmartBook-R1

git status --short
git log --oneline -8

rg "PdfReaderToolbar|readerViewMode|viewMode|student-pdf|reader-view|ratio|zoom|收合AI|問AI|貼圖筆記|正常|放大" apps/AI-Stu-R1/src
```

---

## 9. Verification

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
git commit -m "feat: add normal and large reader view toggle"
```

---

## 10. Manual Browser Verification

Open:

```text
http://127.0.0.1:5173/books/book_0fa830c0-60b2-40bd-b6b0-d0d12d00e509
```

Verify:

```text
1. Two buttons appear: 正常 and 放大.
2. 正常 mode shows the current/default layout.
3. 放大 mode visually enlarges the reader similar to Chrome 150% zoom.
4. Active mode is highlighted.
5. Mode persists after page refresh.
6. PDF remains visible and usable.
7. Chapter outline remains usable.
8. AI panel remains usable.
9. 收合AI / 展開AI still works.
10. Protected PDF still loads from /api/student/.../pdf-view.
11. No backend or DB files were changed.
```

---

## 11. Final Termination Report

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
  - 新增正常 / 放大按鈕：
  - 放大模式視覺效果：
  - 是否近似 Chrome 150%：
  - 是否持久化 localStorage：
  - protected endpoint 是否未改：

- 技術限制說明：
  - 是否有直接改 Chrome browser zoom：否
  - 實作方式：CSS/app-level scale

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

## 12. Acceptance Criteria

Accept only if:

```text
- Normal and large buttons are visible.
- Large mode visibly enlarges the reader UI/PDF experience.
- Normal mode restores the default layout.
- Selection persists after refresh.
- build/typecheck pass.
- No backend/DB changes are included.
```
