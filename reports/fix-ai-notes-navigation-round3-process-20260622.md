# AI Notes Navigation Branch Audit (Round 3)

## 1. Scope
第一輪僅處理 `upstream/codex/fix-ai-notes-navigation`，不做額外程式修正，只生成審核報告。

## 2. Repository Context
- 本地倉庫：`/home/b827262/project/temp/smartbook-platform/ai_tutor_helper`
- 目標比較基準：`origin/main`
- 遠端：
  - `origin`: `https://github.com/b827262-cell/ai_tutor_helper.git`
  - `upstream`: `https://github.com/iamflashon/ai_tutor_helper.git`
- 目標分支：`upstream/codex/fix-ai-notes-navigation`

## 3. User-supplied SHA
使用者提供：`6623e6a4505d7550c19f7c9dadb9e0fb0aeac5f4`

查核結果：本地與上游歷史中未能定位該 SHA。

最接近且與主題相關的提交如下（含分支尾段）：
- `663f630b` fix AI notes navigation
- `2e6832b0` fix AI notes folder hierarchy
- `dcc4c029` group AI notes by date
- `aaf23aeb` docs: add AI notes navigation revision process
- `c21e02ac` docs: summarize AI notes navigation branch changes

## 4. Commands Used
```bash
cd /home/b827262/project/temp/smartbook-platform/ai_tutor_helper
git status -sb
git remote -v
git fetch origin
git fetch upstream
git branch -r | rg 'upstream/codex/fix-ai-notes-navigation'
git rev-list --count origin/main..upstream/codex/fix-ai-notes-navigation
git log --oneline --reverse origin/main..upstream/codex/fix-ai-notes-navigation > /tmp/fix-ai-notes-log.txt
rg -n 'note|notes|folder|navigation|MyNotes|chapterName|tutorChat' /tmp/fix-ai-notes-log.txt
git log --oneline --no-color --reverse origin/main..upstream/codex/fix-ai-notes-navigation | tail -n 40

git show --stat --oneline 663f630b 2e6832b0 dcc4c029 aaf23aeb c21e02ac
git show --name-only --oneline 29a6df67 dc87f691

git diff --name-only origin/main...upstream/codex/fix-ai-notes-navigation | rg -i 'note|tutorchat|notes|my|floating|router'
```

## 5. Branch Overview
- 與 `origin/main` 比較新增提交數：`820`
- 分支目標提交（HEAD）：`c21e02ac`

## 6. Commit Snapshot（與本輪主題高度關聯）
1. `29a6df67`（早期檢查）：重寫 `renderNoteGroup`，改為「日期 > 頁碼」雙層分組。
2. `dc87f691`（早期檢查）：`drizzle/schema.ts` 加 `chapterName` 欄位；`pdfImageNotesRouter.save` 支援 `chapterName`，前端同步帶入選取章節。
3. `663f630b`：修正 AI notes 導航邏輯。
4. `2e6832b0`：修正 AI notes 資料夾階層。
5. `dcc4c029`：按日期分組 notes。
6. `aaf23aeb`：補入 `docs/requirements/ai-notes-navigation-revision-process.md`。
7. `c21e02ac`：補入 `docs/reports/ai-notes-navigation-branch-change-summary.md`。

## 7. Key Files for Round-3 Review
### 7.1 `client/src/pages/MyNotes.tsx`
- 處理 AI notes 導航時可能的目錄/列表行為與跳轉邏輯（與 `663f630b` 相關）。

### 7.2 `client/src/pages/TutorChat.tsx`
- 筆記顯示、分組（日期、頁碼）、與 notes 的 UI 導覽與選取流程為核心。

### 7.3 `server/routers/tutorRouter.ts`
- 支援 notes 資料查詢與保存流程，與篩選/資料夾行為有關。

### 7.4 `server/routers/videoCourseRouter.ts`
- 在 `663f630b` 中一併調整，確認 notes 流程與影音/筆記資料寫入時不影響導覽。

### 7.5 `drizzle/schema.ts`, `server/routers/pdfImageNotesRouter.ts`, `client/public/__manus__/version.json`
- 牽涉到 notes 的欄位與版本快照/格式演進，需在第二輪深入驗證。

### 7.6 Docs (`docs/requirements/ai-notes-navigation-revision-process.md`, `docs/reports/ai-notes-navigation-branch-change-summary.md`)
- 紀錄這輪變更軌跡，符合第一輪輸出要求。

## 8. Functional Notes and Risks
1. 這支分支範圍巨大（820 commits），但本次聚焦點在「AI notes 導航/目錄」的最後幾個提交，仍建議第二輪再縮窄到只含上述核心檔。
2. `MyNotes` 與 `TutorChat` 共享 notes 資料管道，folder/grouping UI 變更容易影響既有資料夾樹狀假設，需要用有舊/有新筆記資料進行回歸。
3. `pdfImageNotes` 的欄位演進（如 `chapterName`）需檢查舊筆記舊資料的向下相容；第一輪未核對資料庫 migration 與生產 SQL 實際落地。

## 9. Process Status
- 本輪調查完成（第一輪，documentation-only）。
- 報告已建立：`reports/fix-ai-notes-navigation-round3-process-20260622.md`
- 未修改任何來源程式。
- 本地上傳分支：`codex/fix-ai-notes-navigation-round3-upload`
