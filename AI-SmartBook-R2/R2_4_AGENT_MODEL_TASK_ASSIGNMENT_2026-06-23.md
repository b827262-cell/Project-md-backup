# AI-SmartBook-R2 四 Agent 模型任務分配

日期：2026-06-23  
主線專案：`/home/b827262/project/AI-SmartBook-R2`  
上游參考目錄：`/project/ai_tutor_helper_upstream_ai_notes`  
上游參考分支：`upstream/codex/fix-ai-notes-navigation`  
上游參考 commit：`c21e02aca7d34ca8e89ae6cab0fb979eee1005ba`  
R2 目前基準分支：`feat/r2-question-bank-json-import`  
R2 目前基準 commit：`2af9bd4f`

---

## 1. 四 Agent 總分工

| Agent | 指定模型 | 建議強度 | 工作類型 | 分支 | 工作目錄 |
|---|---|---|---|---|---|
| Agent A | `codex-5.3-Spark` | 128K | 實作修復、build/typecheck、程式碼修改 | `fix/r2-build-typecheck` | `/home/b827262/project/AI-SmartBook-R2-agent-a-build` |
| Agent B | `GPT-5.4` | Medium，必要時 High | 六大前台模組盤點、路由/API/資料流設計、移植順序規劃 | `docs/r2-feature-module-inventory` | `/home/b827262/project/AI-SmartBook-R2-agent-b-modules` |
| Agent C | `Claude Sonnet 4.6` | Medium，必要時 High | 管理後台盤點、後台 sidebar/route/page/API/DB 對照、重構建議 | `docs/r2-admin-backend-inventory` | `/home/b827262/project/AI-SmartBook-R2-agent-c-admin` |
| Agent D | `AGY / Gemini 3.1 Pro` | High | UX 視覺、外觀、底圖、圖片素材、瀏覽器截圖驗收 | `docs/r2-ux-visual-validation` | `/home/b827262/project/AI-SmartBook-R2-agent-d-ux` |

---

## 2. 分配原則

### Agent A：codex-5.3-Spark 128K

最適合：

- 改程式
- 跑 build
- 看 log
- 修 TypeScript
- grep / rg / find 大量檔案
- 小型到中型實作修補
- monorepo build pipeline 問題

不建議：

- 大範圍產品決策
- 單獨決定 UX 最終樣式
- 大量跨模組重構而沒有 B/C/D 的盤點依據

### Agent B：GPT-5.4 Medium / High

最適合：

- 前台六大模組的功能架構分析
- route / API / DB / data flow 對照
- 移植優先順序設計
- 將上游功能拆成可執行任務
- 檢查 Agent A 的修復是否符合整體架構

Medium 用於盤點與任務拆解。  
High 用於跨模組決策、資料流設計、合併策略。

### Agent C：Claude Sonnet 4.6 Medium / High

最適合：

- 長文件與大檔案閱讀
- 管理後台功能盤點
- sidebar / layout / route / API / DB schema 對照
- 重構建議
- 複雜 React / TypeScript 程式審視

Medium 用於盤點。  
High 用於後台架構重構建議與高風險差異判斷。

### Agent D：AGY / Gemini 3.1 Pro High

最適合：

- 視覺比對
- UX flow 驗收
- 1440 / 768 / 390 RWD 截圖驗證
- 上游底圖、圖片素材、CSS 外觀盤點
- 管理後台與學生前台實際瀏覽器互動測試

AGY 建議使用 High，因為此任務重視視覺、瀏覽器狀態與跨頁面驗收。

---

## 3. 建立四個 worktree

在主線專案執行：

```bash
cd /home/b827262/project/AI-SmartBook-R2

git status --short
git branch --show-current
git rev-parse --short HEAD
git worktree list
```

確認乾淨後建立四個工作目錄：

```bash
# Agent A：build/typecheck 修復
git worktree add ../AI-SmartBook-R2-agent-a-build \
  -b fix/r2-build-typecheck \
  feat/r2-question-bank-json-import

# Agent B：前台六大模組盤點
git worktree add ../AI-SmartBook-R2-agent-b-modules \
  -b docs/r2-feature-module-inventory \
  feat/r2-question-bank-json-import

# Agent C：管理後台盤點
git worktree add ../AI-SmartBook-R2-agent-c-admin \
  -b docs/r2-admin-backend-inventory \
  feat/r2-question-bank-json-import

# Agent D：UX / 視覺 / 底圖 / 截圖驗收
git worktree add ../AI-SmartBook-R2-agent-d-ux \
  -b docs/r2-ux-visual-validation \
  feat/r2-question-bank-json-import
```

---

## 4. Agent A 任務：build / typecheck 實作修復

### 模型

```text
codex-5.3-Spark 128K
```

### 工作目錄

```bash
/home/b827262/project/AI-SmartBook-R2-agent-a-build
```

### 任務指令

```text
Repository task for AI-SmartBook-R2 Agent A.

Model:
codex-5.3-Spark 128K

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-a-build

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
3. Do not touch admin inventory or UX inventory docs unless necessary.
4. Keep changes focused on build/typecheck stability.
5. Commit only focused source/config changes needed for build/typecheck stability.

Verification:
- git status --short
- pnpm build
- pnpm --filter AI-Stu-R1 run build if available
- pnpm run typecheck or ./node_modules/.bin/tsc --noEmit
- direct vite build result

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

## 5. Agent B 任務：前台六大模組盤點與移植策略

### 模型

```text
GPT-5.4 Medium
必要時切 High
```

### 工作目錄

```bash
/home/b827262/project/AI-SmartBook-R2-agent-b-modules
```

### 產出文件

```bash
docs/validation/r2-feature-module-inventory.md
```

### 任務指令

```text
Repository task for AI-SmartBook-R2 Agent B.

Model:
GPT-5.4 Medium, switch to High for cross-module architecture decisions.

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-b-modules

Branch:
docs/r2-feature-module-inventory

Reference upstream directory:
/project/ai_tutor_helper_upstream_ai_notes

Do not modify the upstream reference directory.
Do not modify application source code.
This task is frontend module inventory and implementation planning only.

Goal:
Create a complete inventory and migration plan for the six student-facing modules in AI-SmartBook-R2 compared with the upstream reference.

Modules:
1. 智能書本
2. 智能影音
3. 智能題庫
4. 智能筆記
5. 智能手稿
6. 我的題庫

Required report:
docs/validation/r2-feature-module-inventory.md

The report must include:
- module name
- upstream route
- upstream page/component files
- upstream API endpoint if found
- upstream DB/model/table if found
- AI-SmartBook-R2 route
- AI-SmartBook-R2 page/component files
- AI-SmartBook-R2 API endpoint if found
- AI-SmartBook-R2 DB/model/table if found
- current status: identical / different / partial / missing / incompatible
- implementation priority
- recommended owner agent for next phase

Search keywords:
student, book, books, reader, video, course, quiz, question, question bank, notes, ai notes, handwriting, manuscript, canvas, OCR, favorite, wrong questions, saved questions,
智能書本, 智能影音, 智能題庫, 智能筆記, 智能手稿, 我的題庫, 收藏, 錯題, 自建題庫

Rules:
1. Do not edit source files.
2. Do not modify .env, DB, secrets, uploaded files, or deployment config.
3. Do not implement modules yet.
4. Commit only the documentation report.

Verification:
- git status --short
- confirm only docs/validation/r2-feature-module-inventory.md was changed

Final report in Traditional Chinese:
- success / failure / blocker / permission-halt
- current branch
- commit SHA
- modules fully matched
- modules partial
- modules missing
- API/data-flow gaps
- recommended implementation order
```

---

## 6. Agent C 任務：管理後台盤點與後台架構建議

### 模型

```text
Claude Sonnet 4.6 Medium
必要時切 High
```

### 工作目錄

```bash
/home/b827262/project/AI-SmartBook-R2-agent-c-admin
```

### 產出文件

```bash
docs/validation/r2-admin-backend-inventory.md
```

### 任務指令

```text
Repository task for AI-SmartBook-R2 Agent C.

Model:
Claude Sonnet 4.6 Medium, switch to High for backend architecture and high-risk refactor decisions.

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-c-admin

Branch:
docs/r2-admin-backend-inventory

Reference upstream directory:
/project/ai_tutor_helper_upstream_ai_notes

Do not modify the upstream reference directory.
Do not modify application source code.
This task is admin backend inventory and architecture planning only.

Goal:
Inventory the 管理後台 interface and functionality compared with the upstream reference.

Admin features:
1. 考古題下載
2. 測試回饋記錄
3. AI助教科目管理
4. AI助教問答記錄
5. AI助教書本綁定
6. AI課堂知識點管理
7. 建議問題快取管理
8. 學生內容總覽
9. 題庫中心（PDF辨識）

Required report:
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
- implementation risk level

Search keywords:
admin, sidebar, nav, layout, route, menu, exam, feedback, tutor, assistant, subject, binding, knowledge, cache, student, PDF, OCR,
考古題, 測試回饋, AI助教, 科目管理, 問答記錄, 書本綁定, 知識點, 建議問題, 快取, 學生內容, 題庫中心, PDF辨識

Rules:
1. Do not edit source files.
2. Do not modify .env, DB, secrets, uploaded files, or deployment config.
3. Do not run migrations.
4. Do not implement admin pages yet.
5. Commit only the documentation report.

Verification:
- git status --short
- confirm only docs/validation/r2-admin-backend-inventory.md was changed

Final report in Traditional Chinese:
- success / failure / blocker / permission-halt
- current branch
- commit SHA
- admin mapping summary
- missing admin routes
- missing admin pages
- missing API endpoints
- missing DB/model support
- recommended sync order
```

---

## 7. Agent D 任務：AGY / Gemini 3.1 Pro High UX 視覺驗收

### 模型

```text
AGY / Gemini 3.1 Pro High
```

### 工作目錄

```bash
/home/b827262/project/AI-SmartBook-R2-agent-d-ux
```

### 產出文件

```bash
docs/validation/r2-upstream-ux-visual-assets-inventory.md
```

### 任務指令

```text
Repository task for AI-SmartBook-R2 Agent D.

Model:
AGY / Gemini 3.1 Pro High

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-d-ux

Branch:
docs/r2-ux-visual-validation

Reference upstream directory:
/project/ai_tutor_helper_upstream_ai_notes

Do not modify the upstream reference directory.
Do not modify application source code unless explicitly asked in a later implementation task.
This task is UX, visual asset, CSS appearance, and browser validation inventory only.

Goal:
Find and document the upstream webpage appearance, background images, visual assets, CSS/theme design, layout rules, and UX structure from /project/ai_tutor_helper_upstream_ai_notes, then provide a clear implementation guide for the AI-SmartBook-R2 mainline.

Required output file:
docs/validation/r2-upstream-ux-visual-assets-inventory.md

Scope to inspect in upstream:
1. public assets
2. images, svg, png, jpg, webp, icons, logos, backgrounds
3. global CSS / SCSS
4. component CSS
5. Tailwind config if present
6. theme tokens / CSS variables
7. layout components
8. page components
9. navigation / sidebar / header / footer
10. mobile responsive rules
11. student frontend pages
12. admin backend pages
13. AI notes navigation UI
14. book reader UI
15. card/list/table/button/form styles

Required visual validation:
- desktop 1440px
- tablet 768px
- mobile 390px

Report must include:
1. Upstream visual asset inventory
2. Upstream CSS/theme inventory
3. UX/page structure inventory
4. AI-SmartBook-R2 visual gaps
5. Screenshot or manual visual observations if browser is available
6. Priority porting plan

Rules:
1. Do not edit source files.
2. Do not copy assets yet unless explicitly asked later.
3. Do not modify .env, secrets, DB files, uploaded files, deployment config, or production settings.
4. Do not run migrations.
5. Do not run destructive commands.
6. Do not modify /project/ai_tutor_helper_upstream_ai_notes.
7. Commit only the documentation report.

Verification:
- git status --short
- confirm only docs/validation/r2-upstream-ux-visual-assets-inventory.md was changed

Final report in Traditional Chinese:
- success / failure / blocker / permission-halt
- current branch
- commit SHA
- recommended model used: AGY / Gemini 3.1 Pro High
- upstream reference path
- generated report path
- visual assets found
- CSS/theme files found
- UX/page structures found
- assets missing in AI-SmartBook-R2
- CSS/layout gaps in AI-SmartBook-R2
- viewport validation result
- recommended sync order
- whether source code was changed
```

---

## 8. 四 Agent 互不干擾規則

```text
1. Agent A 可改 source code，但只修 build/typecheck。
2. Agent B 不改 source code，只寫六大前台模組盤點文件。
3. Agent C 不改 source code，只寫管理後台盤點文件。
4. Agent D 不改 source code，只寫 UX/視覺/底圖/截圖驗收文件。
5. 四個 Agent 不得同時 push 到同一個分支。
6. 四個 Agent 不得修改 /project/ai_tutor_helper_upstream_ai_notes。
7. 四個 Agent 不得修改 .env、secrets、DB、uploaded files、部署設定。
```

---

## 9. 完成後整合順序

建議依序整合：

```bash
cd /home/b827262/project/AI-SmartBook-R2

git status --short

git merge docs/r2-feature-module-inventory
git merge docs/r2-admin-backend-inventory
git merge docs/r2-ux-visual-validation
git merge fix/r2-build-typecheck
```

原因：

```text
1. B/C/D 多半只改 docs，衝突風險低。
2. A 會改 source code，最後合併較容易確認是否影響文件與主線。
3. 若 A build 修復影響路由或檔案結構，再回頭更新 B/C/D 文件即可。
```

若全部都 push 到 GitHub：

```bash
git push -u origin fix/r2-build-typecheck
git push -u origin docs/r2-feature-module-inventory
git push -u origin docs/r2-admin-backend-inventory
git push -u origin docs/r2-ux-visual-validation
```

---

## 10. 下一輪實作建議

等四個 Agent 完成後，下一輪再開實作分支：

```bash
git checkout -b feat/r2-upstream-sync-implementation
```

實作順序：

```text
1. 先合併 Agent A 的 build/typecheck 修復
2. 根據 Agent D 報告同步必要 CSS tokens / 圖片 / 底圖 / layout
3. 根據 Agent B 報告補齊前台六大模組完整資料流
4. 根據 Agent C 報告移植管理後台 sidebar / route / page / API
5. 最後做 1440 / 768 / 390 視覺驗收
6. pnpm build / typecheck / frontend build 全部通過後才考慮 main merge
```

---

## 11. 結論

正式四 Agent 分配如下：

```text
Agent A：codex-5.3-Spark 128K
任務：build/typecheck 實作修復。

Agent B：GPT-5.4 Medium，必要時 High
任務：前台六大模組盤點與移植策略。

Agent C：Claude Sonnet 4.6 Medium，必要時 High
任務：管理後台盤點與後台架構建議。

Agent D：AGY / Gemini 3.1 Pro High
任務：UX 視覺、底圖、素材、RWD、截圖驗收。
```
