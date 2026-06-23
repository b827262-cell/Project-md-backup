# AI-SmartBook-R2 Agent D：GPT-5.4 High 上游 UX / 外觀 / 底圖盤點分支任務

日期：2026-06-23  
目標主線專案：`/home/b827262/project/AI-SmartBook-R2`  
上游參考目錄：`/project/ai_tutor_helper_upstream_ai_notes`  
上游參考分支：`upstream/codex/fix-ai-notes-navigation`  
上游參考 commit：`c21e02aca7d34ca8e89ae6cab0fb979eee1005ba`  
建議模型：`GPT-5.4 High`

---

## 1. 任務定位

這是**第四個 Agent：Agent D** 的獨立分支任務。

Agent D 不直接改 AI-SmartBook-R2 主線功能，也不修改上游參考專案。它的任務是從：

```bash
/project/ai_tutor_helper_upstream_ai_notes
```

找出並整理上游的：

- 網頁外觀設計
- UX 結構
- 背景圖 / 底圖 / 圖片素材
- SVG / icon / logo / favicon
- CSS theme tokens
- layout 規則
- 首頁、學生端、閱讀器、筆記頁、管理後台的視覺樣式

整理完成後，提供給 AI-SmartBook-R2 主線作為後續同步與移植依據。

---

## 2. 四個 Agent 總分工

| Agent | 建議模型 | 工作目錄 | 分支 | 任務 |
|---|---|---|---|---|
| Agent A | GPT-5.3-Codex-Spark Medium / High | `AI-SmartBook-R2-agent-build` | `fix/r2-build-typecheck` | 修 `pnpm build`、DB build error、`BookReaderPage.tsx` 型別錯誤 |
| Agent B | GPT-5.3-Codex-Spark Low / Medium | `AI-SmartBook-R2-agent-admin` | `docs/r2-admin-inventory` | 管理後台功能盤點，不先改功能 |
| Agent C | 依實際既有第三分支任務為準 | 依實際分配 | 依實際分配 | 保留給既有第三個分支任務 |
| Agent D | **GPT-5.4 High** | `AI-SmartBook-R2-agent-d-ux` | `docs/r2-agent-d-upstream-ux-inventory` | 上游 UX / 外觀 / 底圖 / 圖片素材 / CSS 視覺盤點 |

本文件只定義 **Agent D**。

---

## 3. 建議分支與 worktree

在 AI-SmartBook-R2 主專案建立第四個獨立 worktree：

```bash
cd /home/b827262/project/AI-SmartBook-R2

git status --short
git worktree list

git worktree add ../AI-SmartBook-R2-agent-d-ux \
  -b docs/r2-agent-d-upstream-ux-inventory \
  feat/r2-question-bank-json-import
```

建立後工作目錄：

```bash
/home/b827262/project/AI-SmartBook-R2-agent-d-ux
```

分支：

```bash
docs/r2-agent-d-upstream-ux-inventory
```

---

## 4. Agent D 任務範圍

### 工作目錄

```bash
/home/b827262/project/AI-SmartBook-R2-agent-d-ux
```

### 參考來源

```bash
/project/ai_tutor_helper_upstream_ai_notes
```

### 產出文件

```bash
docs/validation/r2-upstream-ux-visual-assets-inventory.md
```

### 任務目標

盤點上游專案的 UI / UX / CSS / 圖片素材，並建立 AI-SmartBook-R2 可移植清單。

---

## 5. Agent D 指令

```text
Repository task for AI-SmartBook-R2 Agent D.

Recommended model:
GPT-5.4 High

Working directory:
/home/b827262/project/AI-SmartBook-R2-agent-d-ux

Branch:
docs/r2-agent-d-upstream-ux-inventory

Reference upstream directory:
/project/ai_tutor_helper_upstream_ai_notes

Do not modify the upstream reference directory.
Do not modify application source code in AI-SmartBook-R2.
This task is documentation and asset/UX inventory only.

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

Search commands to run:
find /project/ai_tutor_helper_upstream_ai_notes -type f | grep -Ei "png|jpg|jpeg|webp|svg|ico|css|scss|sass|less|tailwind|theme|style|layout|header|sidebar|nav|footer|page|component"

rg -n "background|background-image|url\(|hero|banner|cover|logo|icon|theme|gradient|linear-gradient|box-shadow|border-radius|sidebar|nav|header|footer|layout|card|reader|notes|admin|student" /project/ai_tutor_helper_upstream_ai_notes

Also inspect AI-SmartBook-R2 matching paths:
find /home/b827262/project/AI-SmartBook-R2-agent-d-ux -type f | grep -Ei "png|jpg|jpeg|webp|svg|ico|css|scss|sass|less|tailwind|theme|style|layout|header|sidebar|nav|footer|page|component"

rg -n "background|background-image|url\(|hero|banner|cover|logo|icon|theme|gradient|linear-gradient|box-shadow|border-radius|sidebar|nav|header|footer|layout|card|reader|notes|admin|student" /home/b827262/project/AI-SmartBook-R2-agent-d-ux

The report must include:

1. Upstream visual asset inventory
   - asset path
   - asset type
   - likely usage
   - referenced by which CSS/component/page
   - whether equivalent exists in AI-SmartBook-R2
   - recommended action: copy / map / ignore / replace / investigate

2. Upstream CSS/theme inventory
   - CSS file path
   - major selectors or CSS variables
   - layout system
   - color tokens
   - spacing/radius/shadow rules
   - responsive breakpoints
   - matching R2 file
   - recommended action

3. UX/page structure inventory
   - upstream route/page
   - layout composition
   - header/sidebar/footer behavior
   - cards/tables/forms/modals behavior
   - mobile behavior
   - matching R2 route/page
   - status: identical / different / missing / incompatible
   - recommended action

4. Priority porting plan for AI-SmartBook-R2 mainline
   - Phase 1: asset copy/map
   - Phase 2: CSS tokens/theme sync
   - Phase 3: layout/header/sidebar sync
   - Phase 4: page/card/form/table component sync
   - Phase 5: mobile/RWD verification
   - Phase 6: screenshot validation

Rules:
1. Do not edit application source files.
2. Do not copy assets yet unless explicitly asked in a later implementation task.
3. Do not modify .env, secrets, DB files, uploaded files, deployment config, or production settings.
4. Do not run migrations.
5. Do not run destructive commands.
6. Do not modify /project/ai_tutor_helper_upstream_ai_notes.
7. Commit only the documentation report.

Verification:
- git status --short
- confirm only docs/validation/r2-upstream-ux-visual-assets-inventory.md was changed

Commit:
Commit the inventory document only.

Final report in Traditional Chinese:
- success / failure / blocker / permission-halt
- current branch
- commit SHA
- recommended model used: GPT-5.4 High
- upstream reference path
- generated report path
- visual assets found
- CSS/theme files found
- UX/page structures found
- assets missing in AI-SmartBook-R2
- CSS/layout gaps in AI-SmartBook-R2
- recommended sync order
- whether source code was changed
```

---

## 6. 建議盤點目錄

### 上游參考專案

```bash
/project/ai_tutor_helper_upstream_ai_notes
```

優先檢查：

```bash
public/
src/
app/
apps/
components/
pages/
styles/
assets/
```

### AI-SmartBook-R2

```bash
/home/b827262/project/AI-SmartBook-R2-agent-d-ux
```

優先檢查：

```bash
apps/AI-Stu-R1/src/
apps/AI-Stu-R1/public/
apps/AI-Stu-R1/src/styles.css
apps/AI-adm-D1/src/
packages/
docs/validation/
```

---

## 7. 視覺資產盤點表格式

| 類型 | 上游路徑 | 用途推定 | 被引用位置 | R2 對應路徑 | 狀態 | 建議動作 |
|---|---|---|---|---|---|---|
| background | `...` | 首頁底圖 | `styles.css` | `...` | missing/different | copy/map |
| logo | `...` | Header logo | `StudentHeader.tsx` | `...` | identical/different | keep/replace |
| icon | `...` | Sidebar icon | `AdminSidebar.tsx` | `...` | missing | copy |
| CSS | `...` | 全域樣式 | app root | `...` | different | merge carefully |

---

## 8. CSS / UX 盤點表格式

| 類別 | 上游檔案 | 主要內容 | R2 對應檔案 | 差異 | 建議動作 |
|---|---|---|---|---|---|
| theme tokens | `styles.css` | color, radius, shadow | `apps/AI-Stu-R1/src/styles.css` | partial | sync tokens |
| layout | `Layout.tsx` | header/sidebar/page shell | `App.tsx` | different | port structure |
| reader UX | `BookReaderPage.tsx` | reader + notes panel | `BookReaderPage.tsx` | partial | verify interaction |
| notes UX | `NotesDirectoryPage.tsx` | folder/date grouping | `NotesDirectoryPage.tsx` | partial | sync behavior |
| admin UX | `AdminLayout.tsx` | sidebar menu | admin app | unknown | inventory first |

---

## 9. 交付給主線 AI-SmartBook-R2 的方式

Agent D 完成後，不直接 merge source code。先只 merge 文件：

```bash
cd /home/b827262/project/AI-SmartBook-R2

git merge docs/r2-agent-d-upstream-ux-inventory
```

接著主線依據報告再開實作分支：

```bash
git checkout -b feat/r2-upstream-visual-sync
```

後續實作順序：

```text
1. 複製/對應必要圖片與底圖
2. 同步 CSS variables / theme tokens
3. 同步 layout shell
4. 同步 header/sidebar/navigation
5. 同步卡片、按鈕、表單、表格樣式
6. 同步 reader / notes / admin 視覺細節
7. 做 1440 / 768 / 390 截圖驗證
```

---

## 10. 驗收標準

Agent D 驗收：

- 已產出 `docs/validation/r2-upstream-ux-visual-assets-inventory.md`
- 使用建議模型：`GPT-5.4 High`
- 有列出上游圖片、SVG、Logo、底圖、背景樣式
- 有列出 CSS/theme/layout 檔案
- 有列出學生端與管理後台 UX 結構
- 有標示 AI-SmartBook-R2 缺漏項
- 有建議同步順序
- 沒有修改 source code
- 沒有修改 `.env`、DB、uploaded files、部署設定

---

## 11. 結論

這個任務是**第四個 Agent：Agent D**。

建議角色命名：

```text
Agent D：GPT-5.4 High UX / Visual Asset Inventory Agent
```

任務重點不是立即移植，而是先把上游的「網頁外觀、底圖、UX 組成、CSS 規則」完整找出，整理成 AI-SmartBook-R2 主線可執行的同步清單。

完成後再由主線或下一個實作分支根據清單進行移植。
