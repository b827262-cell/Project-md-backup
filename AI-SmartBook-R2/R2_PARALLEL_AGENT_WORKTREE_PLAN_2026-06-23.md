# AI-SmartBook-R2 並行 Agent 工作計畫

日期：2026-06-23  
專案：AI-SmartBook-R2  
上游參考目錄：`/project/ai_tutor_helper_upstream_ai_notes`  
上游參考分支：`upstream/codex/fix-ai-notes-navigation`  
上游參考 commit：`c21e02aca7d34ca8e89ae6cab0fb979eee1005ba`  
R2 目前工作分支：`feat/r2-question-bank-json-import`  
R2 目前 commit：`2af9bd4f`

---

## 1. 目前狀態摘要

AI-SmartBook-R2 已完成第一階段上游導入，內容包含：

- 前端路由入口
- CSS / 版面基準
- AI 筆記導覽
- 智能書本入口與閱讀器導向
- 六大模組入口路由
- 390px 行動版 RWD CSS 補強
- `apps/AI-Stu-R1` 直接 Vite build 成功

但目前仍不能視為 production ready，因為仍有下列待修項目：

- workspace 層級 `pnpm build` 仍失敗，錯誤為 `unable to open database file`
- `BookReaderPage.tsx` 仍有 TypeScript 型別問題
- 智能影音、智能題庫、智能手稿、我的題庫仍以入口與版面為主，完整資料流尚未完成
- 管理後台尚未完成完整盤點與功能移植
- 尚未完成實際瀏覽器截圖與視覺回歸驗證

---

## 2. 為什麼要用兩個 Agent 並行

目前任務量大，建議使用兩個 Agent 同時處理，但必須避免兩個 Agent 在同一個資料夾、同一個分支同時改檔。

正確做法是使用 `git worktree` 建立兩個獨立工作目錄：

| Agent | 工作目錄 | 分支 | 任務 |
|---|---|---|---|
| Agent A | `AI-SmartBook-R2-agent-build` | `fix/r2-build-typecheck` | 修 `pnpm build`、DB build error、`BookReaderPage.tsx` 型別錯誤 |
| Agent B | `AI-SmartBook-R2-agent-admin` | `docs/r2-admin-inventory` | 盤點管理後台，不先改功能，只產生對照報告 |

`/project/ai_tutor_helper_upstream_ai_notes` 只作為參考來源，不允許任何 Agent 修改。

---

## 3. 建立兩個 worktree

在主專案執行：

```bash
cd /home/b827262/project/AI-SmartBook-R2

git status --short
git branch --show-current
git rev-parse --short HEAD
git worktree list
```

確認 working tree 乾淨後，建立兩個 Agent 工作目錄：

```bash
git worktree add ../AI-SmartBook-R2-agent-build \
  -b fix/r2-build-typecheck \
  feat/r2-question-bank-json-import

git worktree add ../AI-SmartBook-R2-agent-admin \
  -b docs/r2-admin-inventory \
  feat/r2-question-bank-json-import
```

建立完成後應有：

```bash
/home/b827262/project/AI-SmartBook-R2-agent-build
/home/b827262/project/AI-SmartBook-R2-agent-admin
```

---

## 4. Agent A 任務：修 build / typecheck

工作目錄：

```bash
/home/b827262/project/AI-SmartBook-R2-agent-build
```

分支：

```bash
fix/r2-build-typecheck
```

### Agent A 指令

```text
Repository task for AI-SmartBook-R2 Agent A.

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-build

Branch:
fix/r2-build-typecheck

Reference upstream directory:
/project/ai_tutor_helper_upstream_ai_notes

Do not modify the upstream reference directory.

Goal:
Stabilize the current R2 upstream-sync baseline before adding more features.

Scope:
1. Fix workspace-level pnpm build failure:
   unable to open database file

2. Investigate why build touches database code.

3. Make frontend build safe:
   - frontend build should not require writable DB unless absolutely necessary
   - DB path should be configurable
   - missing DB should not crash static frontend build

4. Fix TypeScript errors in:
   apps/AI-Stu-R1/src/pages/BookReaderPage.tsx

Known issues:
- nullable book/root checks
- pointer/mouse/brush event type mismatch
- ref type mismatch

Rules:
1. Do not add new feature modules.
2. Do not modify .env, secrets, production DB, uploaded files, deployment config, or local runtime data.
3. Do not touch files related to admin inventory unless necessary.
4. Keep changes focused on build/typecheck stability.

Verification:
- git status
- pnpm build
- pnpm --filter AI-Stu-R1 run build if available
- pnpm run typecheck or ./node_modules/.bin/tsc --noEmit
- vite build result

Commit:
Commit changes with a clear message if successful.

Final report in Traditional Chinese:
- success / failure / blocker / permission-halt
- changed files
- commit SHA
- root cause of database build failure
- TypeScript errors fixed
- build result
- typecheck result
- remaining risks
```

---

## 5. Agent B 任務：管理後台盤點

工作目錄：

```bash
/home/b827262/project/AI-SmartBook-R2-agent-admin
```

分支：

```bash
docs/r2-admin-inventory
```

### Agent B 指令

```text
Repository task for AI-SmartBook-R2 Agent B.

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-admin

Branch:
docs/r2-admin-inventory

Reference upstream directory:
/project/ai_tutor_helper_upstream_ai_notes

Do not modify the upstream reference directory.

Goal:
Inventory the 管理後台 interface and functionality compared with the upstream reference.

First pass only:
Do not modify application source code.
Only create or update documentation under:
docs/validation/

Admin features to locate:
1. 考古題下載
2. 測試回饋記錄
3. AI助教科目管理
4. AI助教問答記錄
5. AI助教書本綁定
6. AI課堂知識點管理
7. 建議問題快取管理
8. 學生內容總覽
9. 題庫中心（PDF辨識）

Also keep these student modules in mind:
1. 智能書本
2. 智能影音
3. 智能題庫
4. 智能筆記
5. 智能手稿
6. 我的題庫

Required output:
Create:
docs/validation/r2-admin-backend-inventory.md

The report must include:
- feature name
- upstream route
- upstream page/component file
- upstream API endpoint
- upstream DB/model/table if found
- AI-SmartBook-R2 route
- AI-SmartBook-R2 page/component file
- AI-SmartBook-R2 API endpoint
- AI-SmartBook-R2 DB/model/table if found
- status: identical / different / missing / incompatible
- recommended action

Search keywords:
admin, sidebar, nav, layout, route, menu, exam, feedback, tutor, assistant, subject, binding, knowledge, cache, student, PDF, OCR,
考古題, 測試回饋, AI助教, 科目管理, 問答記錄, 書本綁定, 知識點, 建議問題, 快取, 學生內容, 題庫中心, PDF辨識

Rules:
1. Do not edit source files.
2. Do not modify .env, DB, secrets, uploaded files, or deployment config.
3. Do not run migrations.
4. Do not implement admin pages yet.
5. This task is documentation and inventory only.

Verification:
- git status
- confirm only docs/validation/r2-admin-backend-inventory.md was changed

Commit:
Commit the inventory document only.

Final report in Traditional Chinese:
- success / failure / blocker / permission-halt
- changed files
- commit SHA
- admin mapping summary
- missing admin routes
- missing admin pages
- missing API endpoints
- missing DB/model support
- recommended sync order
```

---

## 6. 兩個 Agent 同時執行的規則

最重要的規則如下：

```text
1. Agent A 可以改 source code，但只修 build/typecheck。
2. Agent B 不改 source code，只寫 docs/validation 報告。
3. 兩個 Agent 不要同時 push 到同一個分支。
4. 兩個 Agent 都不得修改 /project/ai_tutor_helper_upstream_ai_notes。
5. 兩個 Agent 都不得修改 .env、機密、DB、uploaded files、部署設定。
```

不建議做法：

```text
兩個 Agent 都進 /home/b827262/project/AI-SmartBook-R2
兩個 Agent 都在 feat/r2-question-bank-json-import
兩個 Agent 都可以改 src/
```

原因：

```text
容易發生檔案互蓋、git index lock、build 結果互相干擾、commit 混在一起、rollback 困難。
```

---

## 7. 完成後整合流程

如果兩個 Agent 只在本機完成 commit，回到主專案整合：

```bash
cd /home/b827262/project/AI-SmartBook-R2

git status --short
git merge fix/r2-build-typecheck
git merge docs/r2-admin-inventory
```

如果兩個 Agent 都已 push 到 GitHub：

```bash
git push -u origin fix/r2-build-typecheck
git push -u origin docs/r2-admin-inventory
```

主分支整合前建議：

```bash
git fetch origin --prune
git log --oneline --graph --decorate --all -20
```

---

## 8. 後續建議順序

目前最佳順序：

```text
1. Agent A 修 pnpm build DB 問題
2. Agent A 修 BookReaderPage.tsx TypeScript 問題
3. Agent B 完成管理後台盤點文件
4. 合併兩個分支
5. 再開下一輪：管理後台 Sidebar / Route / Page 移植
6. 再補：智能影音、智能題庫、智能手稿、我的題庫完整資料流
7. 最後做瀏覽器截圖與 RWD 視覺驗收
```

---

## 9. 驗收標準

### Agent A 驗收

- `pnpm build` 不再因 DB 檔案無法開啟而失敗
- 前端 build 不依賴本機可寫 DB
- `BookReaderPage.tsx` 型別錯誤已修正
- `apps/AI-Stu-R1` Vite build 保持成功
- 沒有修改 .env、DB、uploaded files、部署設定

### Agent B 驗收

- 產出 `docs/validation/r2-admin-backend-inventory.md`
- 報告列出 9 個管理後台功能對照
- 明確標示 route / page / API / DB 的 existing、missing、different、incompatible 狀態
- 沒有修改 source code
- 沒有修改 .env、DB、uploaded files、部署設定

---

## 10. 結論

可以同時開兩個 Agent。

目前最安全分工是：

```text
Agent A：修 build/typecheck，可改 source code。
Agent B：管理後台盤點，只寫 docs，不改 source code。
```

等 Agent A 把基礎穩定、Agent B 完成後台盤點後，再進入下一輪管理後台實作移植。