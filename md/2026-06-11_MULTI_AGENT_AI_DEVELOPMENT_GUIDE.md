# 2026-06-11 多 Agent AI 程式開發協作指南

> 適用專案：SmartBook Lite / AI 助教 / SQLite VPS Lite / 多 CLI 自動化開發流程  
> 目標：建立一套可維護、可擴充、可交接、可審查的 AI 協同程式開發標準流程。

---

## 1. 核心結論

2026 年的 AI 程式開發不應只依賴單一模型，而應採用「主控 + 多 Agent 分工 + Git 驗證」架構。

建議配置：

```text
ChatGPT / GPT-5.5 Thinking：主控、需求拆解、架構判斷、任務下達
Codex CLI：主力改碼、跑測試、修 bug、產生 patch、commit
Claude Opus 4.8 / Claude Code：架構審查、風險分析、長上下文重構
AGY / Antigravity / Gemini CLI 類工具：探索、文件整理、Google 生態輔助、多模態輔助
GitHub：版本管理、PR、回滾、交接記錄
Project-md-backup：每日 MD 交接與上下文保存
```

一句話：

> ChatGPT 當 PM，Codex 當工程師，Opus 當架構師，AGY 當研究助理，GitHub 當唯一事實來源。

---

## 2. 推薦總架構

```text
使用者需求
    │
    ▼
ChatGPT 主控聊天室
    │
    ├── 需求分析
    ├── 影響範圍判斷
    ├── 任務拆解
    ├── 產生 MD 指南
    └── 分派給不同 Agent
    │
    ▼
多 Agent 任務層
    │
    ├── Codex CLI
    │   ├── 修改程式
    │   ├── 跑 pnpm build
    │   ├── 跑 SQLite smoke
    │   ├── 產生 diff report
    │   └── commit / push
    │
    ├── Claude Opus 4.8
    │   ├── 架構審查
    │   ├── 風險分析
    │   ├── migration 檢查
    │   ├── hidden coupling 檢查
    │   └── PR final review
    │
    └── AGY / Antigravity
        ├── 探索 repo
        ├── 整理文件
        ├── 查找 UI / API 關聯
        ├── 輔助研究 Google 生態
        └── 產生只讀報告
    │
    ▼
Git Worktree / Branch / PR
    │
    ▼
Build / Smoke / Review / Merge
```

---

## 3. Agent 角色分工

| Agent | 主要角色 | 適合任務 | 不適合任務 |
|---|---|---|---|
| ChatGPT / GPT-5.5 Thinking | 主控 PM / 架構總控 | 任務拆解、流程設計、MD 文件、指派 Codex/Claude/AGY | 直接長時間操作本機 terminal |
| Codex CLI | 主力工程師 | 改碼、除錯、跑測試、產生 patch、commit | 沒有範圍限制的大改版 |
| Claude Opus 4.8 | 高階架構審查 | 大型重構、長上下文、PR 審查、風險分析 | 小 bug 全丟給它，成本較高 |
| AGY / Antigravity | 探索與研究助理 | 文件整理、Google 生態、快速分析、多模態輔助 | 作為唯一主力工程工具 |
| GitHub | 版本事實來源 | branch、tag、PR、rollback、history | 不應存放密鑰 |

---

## 4. 專案維護核心原則

未來新增需求或修改功能時，必須遵守以下規則：

```text
1. 舊前台 UX 儘量不動。
2. 後台功能採模組化新增。
3. API 統一入口，不在頁面亂接多套邏輯。
4. DB 變更一律 migration，不手改正式資料表。
5. AI provider / prompt / RAG 必須拆開，不寫死在業務功能中。
6. 每次修改先 git status，再改檔。
7. 每次修改只處理一個明確任務。
8. 每次改完必須 build + smoke test。
9. 每次 commit 必須附報告。
10. PR merge 前至少做一次架構審查。
```

---

## 5. 建議程式目錄架構

```text
smartbook-lite/
├── AGENTS.md
├── README.md
├── docs/
│   ├── AI_DISPATCH/
│   │   ├── 2026-06-11_MASTER_PLAN.md
│   │   ├── 2026-06-11_CODEX_TASKS.md
│   │   ├── 2026-06-11_AGY_TASKS.md
│   │   └── 2026-06-11_OPUS_REVIEW.md
│   │
│   ├── architecture/
│   │   ├── SMARTBOOK_LITE_MODULAR_ARCH.md
│   │   └── MULTI_AGENT_DEV_GUIDE.md
│   │
│   ├── verification/
│   │   ├── BUILD_REPORT.md
│   │   ├── SQLITE_SMOKE_REPORT.md
│   │   └── FINAL_DIFF_REPORT.md
│   │
│   └── changelog/
│       └── 2026-06-11_CHANGELOG.md
│
├── scripts/
│   ├── pre-pr-check.sh
│   ├── smoke-sqlite.sh
│   ├── backup-final-diff.sh
│   └── ai-dispatch.sh
│
├── server/
│   ├── modules/
│   │   ├── books/
│   │   ├── chapters/
│   │   ├── pdf-parser/
│   │   ├── rag/
│   │   ├── questions/
│   │   ├── users/
│   │   └── credits/
│   │
│   ├── ai/
│   │   ├── providers/
│   │   │   ├── gemini.ts
│   │   │   ├── openai.ts
│   │   │   └── local.ts
│   │   ├── prompts/
│   │   │   ├── splitBook.ts
│   │   │   ├── askBook.ts
│   │   │   └── generateQuestions.ts
│   │   └── aiService.ts
│   │
│   └── db/
│       ├── runtime.ts
│       ├── sqlite.ts
│       └── mysql.ts
│
├── drizzle/
│   ├── schema.ts
│   └── migrations/
│       ├── 0001_init.sql
│       ├── 0002_books.sql
│       ├── 0003_chapters.sql
│       └── 0004_rag_chunks.sql
│
├── client/
├── shared/
└── package.json
```

---

## 6. 後台模組化標準

每個後台模組固定使用同一種分層：

```text
server/modules/<module-name>/
├── router.ts       # API / tRPC / Express route
├── service.ts      # 商業邏輯
├── repository.ts   # SQLite / MySQL 資料存取
├── schema.ts       # Zod 驗證與 TypeScript 型別
├── prompt.ts       # 若此模組有 AI 功能才需要
└── README.md       # 模組用途與維護說明
```

範例：書本模組

```text
server/modules/books/
├── router.ts
├── service.ts
├── repository.ts
├── schema.ts
└── README.md
```

範例：AI 問書模組

```text
server/modules/rag/
├── router.ts
├── service.ts
├── repository.ts
├── schema.ts
├── retriever.ts
├── reranker.ts
├── prompt.ts
└── README.md
```

---

## 7. 新需求標準流程

每次新增需求都必須走以下流程：

```text
Step 1：建立需求 MD
Step 2：判斷影響範圍
Step 3：建立 branch / worktree
Step 4：指派 Codex 實作
Step 5：跑 pnpm build
Step 6：跑 SQLite smoke test
Step 7：產生 FINAL_DIFF_REPORT.md
Step 8：交給 Opus / ChatGPT review
Step 9：只 commit 指定檔案
Step 10：push GitHub
Step 11：建立 PR
Step 12：merge 後更新 Project-md-backup
```

---

## 8. Git 分支與 Worktree 規範

建議命名：

```text
feature/<date>-<feature-name>
fix/<date>-<bug-name>
review/<date>-<review-scope>
spike/<date>-<research-topic>
```

範例：

```text
feature/2026-06-11-admin-modules
fix/2026-06-11-sqlite-study-minutes
review/2026-06-11-opus-pr15-final
spike/2026-06-11-agy-ui-route-map
```

Worktree 範例：

```bash
git worktree add ~/project/smartbook-lite-feature-admin-modules feature/2026-06-11-admin-modules
```

---

## 9. Codex CLI 任務模板

```text
[TO:CODEX]

任務名稱：<任務名稱>

工作目錄：
~/project/<worktree-name>

目標：
1. <目標一>
2. <目標二>
3. <目標三>

限制：
- 先執行 git status --short
- 不得修改 .env
- 不得修改 node_modules
- 不得修改 data/*.db
- 不得碰未指定檔案
- 不得混入其他 bug 修補

允許修改檔案：
- server/modules/<module>/router.ts
- server/modules/<module>/service.ts
- server/modules/<module>/repository.ts

驗證：
- pnpm build
- bash scripts/smoke-sqlite.sh
- git diff --stat

輸出：
- docs/verification/BUILD_REPORT.md
- docs/verification/SQLITE_SMOKE_REPORT.md
- docs/verification/FINAL_DIFF_REPORT.md

提交規則：
- build 通過才 commit
- smoke 通過才 commit
- commit message 使用：feat: <summary> 或 fix: <summary>
```

---

## 10. Claude Opus 4.8 審查模板

```text
[TO:OPUS]

請審查以下 PR / diff。

審查重點：
1. 是否破壞舊前台 UX
2. 是否造成 SQLite / MySQL 雙路徑混亂
3. 是否有 hidden coupling
4. 是否有不必要的大改版
5. 是否有 1GB VPS 不適合的重依賴
6. 是否有 migration 風險
7. 是否有 API key / prompt / provider 寫死
8. 是否有安全性問題
9. 是否有 rollback 困難
10. 是否可 merge

請輸出：
- BLOCKER
- HIGH RISK
- MEDIUM RISK
- LOW RISK
- 建議修正
- 是否可 merge
```

---

## 11. AGY / Antigravity 任務模板

```text
[TO:AGY]

任務名稱：只讀探索與文件整理

限制：
- 不要改檔
- 不要 commit
- 不要刪檔
- 只讀 repo

目標：
1. 掃描 README / docs / client / server
2. 整理目前功能地圖
3. 標出前台 UX 路由
4. 標出後台模組化候選區
5. 標出 API / DB / AI provider 關聯

輸出：
- docs/AI_DISPATCH/AGY_RESEARCH_REPORT.md
```

---

## 12. SQLite 維護規範

SQLite 是 VPS Lite 的核心，必須穩定維護。

規則：

```text
1. 不直接手動改正式 DB。
2. 不修改已套用的舊 migration。
3. 新增欄位一律新增 migration。
4. repository 層負責 DB 存取。
5. service 層不可直接寫 SQL。
6. router 層不可直接碰 DB。
7. 每次 DB 修改必須有 smoke test。
```

新增欄位範例：

```sql
ALTER TABLE books ADD COLUMN content_type TEXT DEFAULT 'pdf';
```

禁止：

```text
直接在 router 裡 db.update(...)
直接改 production sqlite 檔
直接修改 0001_init.sql
```

---

## 13. AI Provider 維護規範

AI 功能必須可替換 provider。

建議結構：

```text
server/ai/
├── providers/
│   ├── gemini.ts
│   ├── openai.ts
│   ├── anthropic.ts
│   └── local.ts
├── prompts/
│   ├── splitBook.ts
│   ├── askBook.ts
│   └── generateQuestions.ts
├── types.ts
└── aiService.ts
```

規則：

```text
1. 不在業務 service 裡直接呼叫 Gemini / OpenAI SDK。
2. prompt 必須獨立存放。
3. provider 由 env 控制。
4. API key 僅讀取 env。
5. 錯誤要有 fallback。
6. AI 回傳資料必須經 schema 驗證。
```

---

## 14. 1GB VPS 維護原則

目標部署：

```text
Nginx
Node.js 22
SQLite
systemd
少量背景任務
外部 AI API
```

避免：

```text
Docker Compose 多服務常駐
MySQL
Redis
Qdrant
大型本地模型
重型 OCR
長時間背景 worker
```

保留彈性：

```text
PDF 解析可模組化
RAG 可先 SQLite / simple chunks
未來再升級到 Qdrant / Chroma
AI provider 可先 Gemini API，未來再換 OpenAI / local
```

---

## 15. SWOT 分析

### Strengths 優勢

- 多 Agent 分工清楚，降低單一模型失誤風險。
- Codex 擅長實作與測試，適合主力改碼。
- Opus 擅長長上下文與複雜架構審查。
- AGY / Antigravity 適合探索、文件與 Google 生態輔助。
- GitHub + MD 文件可保留完整決策紀錄。
- 適合低資源 VPS Lite 長期維護。

### Weaknesses 弱點

- 多 Agent 容易產生上下文不一致。
- 沒有嚴格檔案範圍時，容易互相覆蓋修改。
- 若沒有 smoke test，DB 問題容易延後爆發。
- Prompt、provider、DB 若耦合太深，未來維護成本會升高。

### Opportunities 機會

- 可形成個人 AI 工程隊流程。
- 可把 SmartBook 拆成長期可擴充平台。
- 可支援不同 AI provider，降低成本風險。
- 可透過 GitHub PR 建立標準開發紀錄。
- 可將 Project-md-backup 作為跨分頁、跨工具交接中心。

### Threats 威脅

- Agent 可能做超出授權範圍的改動。
- API / CLI 工具版本變動快。
- 1GB VPS 資源很有限，架構過重會造成維護困難。
- 沒有 migration 規範時，SQLite 容易產生不可回復錯誤。
- 若直接在主分支修改，回滾成本高。

---

## 16. PR 前檢查清單

```text
[ ] git status 已確認
[ ] diff 只包含本任務檔案
[ ] 未修改 .env
[ ] 未提交 DB 檔案
[ ] 未提交 node_modules
[ ] pnpm build 通過
[ ] SQLite smoke 通過
[ ] migration 合理
[ ] 沒有破壞舊前台 UX
[ ] 沒有引入重型依賴
[ ] 已產生 FINAL_DIFF_REPORT.md
[ ] 已請 Opus / ChatGPT review
[ ] commit message 清楚
[ ] PR description 完整
```

---

## 17. 每日交接 MD 格式

```markdown
# YYYY-MM-DD AI Development Handoff

## 今日目標
- 

## 已完成
- 

## 未完成
- 

## 目前分支
- repo:
- branch:
- worktree:
- HEAD:

## 本次修改檔案
- 

## 驗證結果
- pnpm build:
- SQLite smoke:
- final diff:

## 已知問題
- 

## 下一步
- 

## 給 Codex 的任務
- 

## 給 Opus 的審查重點
- 

## 給 AGY 的探索任務
- 
```

---

## 18. 最終建議執行模式

最穩定的長期模式：

```text
ChatGPT：需求與任務分派
Project-md-backup：保存上下文與每日交接
Codex CLI：實作與測試
Claude Opus 4.8：架構審查
AGY / Antigravity：探索與文件輔助
GitHub PR：唯一合併入口
E500：測試環境
1GB VPS：正式精簡部署
```

---

## 19. 簡化版口訣

```text
需求先寫 MD。
改碼交 Codex。
架構問 Opus。
探索交 AGY。
驗證靠 build / smoke。
紀錄進 GitHub。
部署走 systemd。
資料庫只走 migration。
```

---

## 20. 結論

未來需求的新增與修改，不要用一次大改版處理，而要採用：

```text
一個需求
一個模組
一個 branch
一個 migration
一份 smoke report
一份 final diff
一個 PR
一份 MD 交接
```

這樣 SmartBook Lite / AI 助教專案才能在 1GB VPS、SQLite、低成本 AI API、多 Agent 協同開發的限制下，長期維護與穩定擴充。
