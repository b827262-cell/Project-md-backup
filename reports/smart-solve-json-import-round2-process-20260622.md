# Smart Solve JSON Import Branch Audit (Round 2)

## 1. Scope
第二輪針對 `upstream/codex/smart-solve-json-import` 做第一輪審核記錄，仍為 documentation-only。

本報告聚焦 `Smart Solve` JSON 匯入、Smart Book 匯入工具整合與 `preflight` 工具鏈，不重做第三方程式碼修改。

## 2. Repository Context
- 本地倉庫：`/home/b827262/project/temp/smartbook-platform/ai_tutor_helper`
- 遠端：
  - `origin`：`https://github.com/b827262-cell/ai_tutor_helper.git`
  - `upstream`：`https://github.com/iamflashon/ai_tutor_helper.git`
- 當前比較分支：`upstream/codex/smart-solve-json-import`
- 目標基準：`origin/main`
- 作業分支（本次上傳）：`codex/smart-solve-json-import-round2-upload`

## 3. User-supplied SHA
使用者提供的提交 SHA：`51f66887d02861d88d3bedc0d85d85165866c303`

查核結果：在上述本地與來源 repo 中未找到該物件；本次報告改以分支 HEAD `upstream/codex/smart-solve-json-import`（`fff66c0f23c012f50a3a41869bb10718d130a04f`）與可追溯 commit 範圍為依據。

## 4. Commands Used
```bash
cd /home/b827262/project/temp/smartbook-platform/ai_tutor_helper
git status -sb
git remote -v
git fetch upstream
git branch -r | grep 'upstream/codex/smart-solve-json-import'
git rev-parse upstream/codex/smart-solve-json-import
git rev-list --count origin/main..upstream/codex/smart-solve-json-import
git log --oneline --reverse origin/main..upstream/codex/smart-solve-json-import > /tmp/smart-solve-log.txt
grep -E 'Smart Solve JSON import|SmartSolveJsonImportDialog|smart book JSON import|Smart Books local content package import|Show TOC page codes for smart book imports|preflight' /tmp/smart-solve-log.txt

git diff --name-only --diff-filter=AMR origin/main...upstream/codex/smart-solve-json-import | rg -i 'smart.?solve|smart.?book|preflight|adminsmart|smartsolve|solve'

git show --name-only --pretty=format: 31e4239a 9dd4b4df 57a6ccf5 4bb3897b 4c61897e 00975419 3fb83116 16b5f6c1 e1a947c6 284dc2be 5731865f
```

## 5. Commit Overview
- 與 `origin/main` 比較：`862` commits (總比對範圍)
- 針對 Smart Solve/Smart Book import 與 preflight 核心線索的關鍵提交（共 11 筆）：
  1. `31e4239a` Add Smart Solve JSON import
  2. `9dd4b4df` SmartSolveJsonImportDialog useMemo 修正
  3. `57a6ccf5` Improve Smart Solve JSON import grouping
  4. `4bb3897b` Add Smart Books chapter JSON import
  5. `4c61897e` Add Smart Books local content package import
  6. `00975419` Make Smart Book package exporter interactive
  7. `3fb83116` Add Smart Book package export GUI
  8. `16b5f6c1` Add no-AI smart book PDF upload
  9. `e1a947c6` Show smart book JSON import in editor
  10. `284dc2be` Support nested smart book chapter imports
  11. `5731865f` Add deployment preflight checks
  12. `fff66c0f` docs: summarize codex branch change overview

## 6. Core File Changes (From Commit Filtering)
- `client/src/pages/AdminSmartSolve.tsx`
- `server/routers/smartSolveRouter.ts`
- `client/src/pages/AdminSmartBooks.tsx`
- `server/routers/smartBookRouter.ts`
- `ai_tutor_gui/export_smart_book_package.bat`
- `ai_tutor_gui/export_smart_book_package.py`
- `ai_tutor_gui/smart_book_package_gui.py`
- `ai_tutor_gui/start_smart_book_package_gui.bat`
- `ai_tutor_gui/smart_book_preprocess_gui.py`
- `ai_tutor_gui/start_smart_book_preprocess_gui.bat`
- `ai_tutor_gui/smart_book_chapter_analysis_gui.py`
- `scripts/preflight.mjs`
- `package.json`
- `.gitignore`
- `.prettierignore`
- `todo.md`

## 7. Commit-level Notes
### 7.1 31e4239a
`client/src/pages/AdminSmartSolve.tsx` 與 `server/routers/smartSolveRouter.ts` 建立 Smart Solve JSON 匯入主幹。

### 7.2 9dd4b4df
修復 `SmartSolveJsonImportDialog` 的 `useMemo` 引用錯誤（補 `React import`），避免頁面渲染中斷。

### 7.3 57a6ccf5
修正 / 改善 Smart Solve JSON 匯入分組邏輯。

### 7.4 4bb3897b / 4c61897e / 00975419 / 3fb83116
擴展 Smart Book 匯入流程：章節 JSON 匯入、local content package 匯入、GUI 互動與導出工具。

### 7.5 16b5f6c1 / e1a947c6 / 284dc2be
加入無 AI 上傳路徑、在 UI 顯示 JSON 匯入編輯器、支援巢狀章節匯入。

### 7.6 5731865f
新增 `scripts/preflight.mjs`，並在 `package.json` 補 `preflight` / `preflight:full`，同時更新 ignore 與 `todo.md`。

## 8. Key Functional Files for Round-2 Deep Review
建議第二輪重點只聚焦：
- `client/src/pages/AdminSmartSolve.tsx`
- `server/routers/smartSolveRouter.ts`
- `client/src/pages/AdminSmartBooks.tsx`
- `server/routers/smartBookRouter.ts`
- `scripts/preflight.mjs`

前述 5 檔可覆蓋前端匯入 UX、後端 import 驗證、預處理腳本與部署前檢查。

## 9. Risks (Round-2 Preview)
1. 分支差異仍然龐大：與 `origin/main` 比較有 `862` 個提交，需留意重複修補與歷史回歸。
2. `preflight` 提交名稱與實際內容可能偏離 `smart-solve-json-import` 名稱直覺，建議明確確認功能邊界。
3. Smart Book/Smart Solve 相關匯入流程在 `AdminSmartBooks.tsx`、`smartBookRouter.ts` 及 `smartSolveRouter.ts` 有跨檔交互，需確認 schema 一致性。
4. 歷史上有多個 `Checkpoint` commit，需確認是否留有未整理的過渡邏輯。

## 10. Process Status
- 來源調研完成
- 文件檔案已生成：`reports/smart-solve-json-import-round2-process-20260622.md`
- Source code 未修改
- 本次提交僅新增文件（documentation-only）
