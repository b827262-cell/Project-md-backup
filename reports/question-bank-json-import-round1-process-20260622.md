# Question Bank JSON Import Branch Audit

## 1. Scope
第一輪僅處理分支 `upstream/codex/question-bank-json-import`，不處理其他兩個 `codex` 分支。

## 2. Repository Context
- 本地倉庫：`/home/b827262/project/temp/smartbook-platform/ai_tutor_helper`
- 當前分支：`release/vps-lite`
- `git status -sb`：工作樹潔淨，分支與 `origin/release/vps-lite` 落後 19 個提交
- Remotes：`origin`（`b827262-cell/ai_tutor_helper`）、`upstream`（`iamflashon/ai_tutor_helper`）

## 3. Branch Confirmation
- `upstream/codex/question-bank-json-import` 存在於遠端分支清單。
- 與 `origin/main` 比較的 commit range 可取得。
- 與 `origin/main` 的共同祖先（merge-base）：`cca345530dff28fe033cc5eee5a81fe797f1ca97`

## 4. Lightweight Commands Used
```bash
git status -sb
git remote -v
git fetch origin --prune
git fetch upstream
git branch -r | grep 'upstream/codex/question-bank-json-import'
git log --oneline --decorate --since='2026-06-01' --until='2026-06-22 23:59:59' origin/main..upstream/codex/question-bank-json-import | head -n 80
git diff --stat origin/main...upstream/codex/question-bank-json-import
git diff --name-only origin/main...upstream/codex/question-bank-json-import | sort -u
git rev-list --count origin/main..upstream/codex/question-bank-json-import
git log --oneline --reverse origin/main..upstream/codex/question-bank-json-import | head -n 12
git log --oneline origin/main..upstream/codex/question-bank-json-import | head -n 12
git log --oneline --reverse origin/main..upstream/codex/question-bank-json-import -- client/src/pages/AdminQuestionBankImport.tsx server/routers/questionBankRouter.ts
git show --name-status --stat 77e8d7af
git diff --numstat origin/main...upstream/codex/question-bank-json-import | sort -t $'\t' -k1,1nr -k2,2nr | head -n 30
```

## 5. Commit Summary
- 分支相較於 `origin/main` 新增提交數：`772`
- 最新提交（分支目標）：`77e8d7af`（Add question bank JSON import page）
- 開始提交（從 `origin/main` 往前）中可見為功能性堆疊，且最末端才加入本次 JSON 匯入功能。
- 尾段關聯的重要提交包括：
  - `86f7e6e9`（題庫辨識流程/覆蓋邏輯修正）
  - `6b27450a`（建立題庫中心基礎功能：題庫集、題庫題目與練習流程）
  - `fb0b3e86`（題型與含表格欄位）
  - `77e8d7af`（新增 JSON 匯入頁與後端 API）

## 6. Changed File Summary
- `origin/main...upstream/codex/question-bank-json-import` 的總差異：`140 files changed, 65458 insertions(+), 15484 deletions(-)`
- 主要高變更檔（依新增/刪除較多行）上位：
  - `package-lock.json` (+18103)
  - `server/routers/smartBookRouter.ts`
  - `client/src/pages/AdminSmartBooks.tsx`
  - `client/src/pages/TutorChat.tsx`
  - `client/src/pages/AdminSmartSolve.tsx`
  - `server/routers/smartSolveRouter.ts`
  - `client/src/pages/SmartBooks.tsx`
  - `client/src/components/PdfViewer.tsx`
  - `client/src/components/DrawingCanvas.tsx`
  - `server/routers/examSourceRouter.ts`
  - `server/routers/questionBankRouter.ts`
  - `client/src/pages/AdminQuestionBankCenter.tsx`
- 直接與本輪目標最相關的新增/變更：
  - `client/src/pages/AdminQuestionBankImport.tsx`（新增）
  - `client/src/pages/AdminQuestionBankCenter.tsx`（新增「匯入 JSON」導入口）
  - `server/routers/questionBankRouter.ts`（新增 `importLocalQuestions`）
  - `client/src/App.tsx`（新增 `/admin/question-bank-import` 路由）

## 7. Key Files Reviewed
- `client/src/pages/AdminQuestionBankImport.tsx`（新增頁面）：
  - 實作本地 `questions.json` 匯入、題目預覽、驗證摘要、匯入到新題庫或既有題庫
- `client/src/pages/AdminQuestionBankCenter.tsx`：
  - 新增導向 `AdminQuestionBankImport` 的按鈕（列表與題庫詳情）
- `server/routers/questionBankRouter.ts`：
  - 新增 `localQuestionImportSchema`、題目正規化（選項、答案、頁碼、題型）
  - 新增 `importLocalQuestions` mutation，支援 dryRun、可選覆蓋既有題目
- `client/src/App.tsx`：
  - 註冊新頁面元件與路由

## 8. Risk Notes
1. 分支跨度很大：與 `origin/main` 比較到 `772` 個提交、`140` 個檔案，包含大量既有功能變更，非「單一 JSON 匯入」改動。
2. 風險集中點：
   - `importLocalQuestions` 支援自動補齊欄位與預設 `correctIndex`，有少量資料品質風險；缺少題目的題目會被標記 warning，但匯入流程仍可進行。
   - `replaceExisting` 為破壞性操作，會清空目標題庫既有題目。
   - `questions.json` 欄位採彈性解析，需注意來源欄位命名差異與類型不一致。
3. Branch 內包含 `.git_broken/`、`.manus/checkpoint_zip/` 等大量檔案與附件，需確認是否為必要提交。

## 9. Recommendation
- 第一輪建議先完成這三項：
  - 只對 `client/src/pages/AdminQuestionBankImport.tsx`、`server/routers/questionBankRouter.ts` 做深度審核。
  - 明確驗證 `importLocalQuestions` 在缺值/錯值資料時的回傳與是否會造成錯誤匯入。
  - 在下一輪前與 `origin/main` 做一次最小化重放差異萃取（只保留題庫 JSON 匯入主線）。

## 10. Final Status
- 目標分支已確認存在，且第一輪調查已完成。
- 報告已建立：`docs/reports/question-bank-json-import-audit-20260622.md`
- source code 未修改（僅新增文件報告）。
- 推薦結果：`proceed-with-caution`（高量差異，需在第二輪限定範圍）。
