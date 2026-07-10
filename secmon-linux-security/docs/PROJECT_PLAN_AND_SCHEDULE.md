# SecMon 專案規劃與交付排程

## 1. 文件目的

本文件將 SecMon Linux 資安監控 MVP 拆成可執行的工作階段，並分派給兩個 AI 角色：

- **GPT-5.6**：架構主責、後端與安全核心實作者、整合修復者。
- **AGY（Gemini 3.5 Flash）**：PM／QA／前端整合驗證者、Release Gate 管理者。

AI 名稱是工作角色，不是 GitHub 帳號，因此 GitHub Issue 以標題前綴及文件欄位標示責任人，不直接加入 assignee。

## 2. 專案目標

在 Ubuntu 24.04 單機環境完成以下閉環：

```text
SSH/Nginx/Suricata 日誌
        ↓
Collector 與 Parser
        ↓
SQLite WAL
        ↓
攻擊者彙總、告警與威脅分數
        ↓
React 管理前台
        ↓
人工限時封鎖、白名單與稽核
```

## 3. 執行原則

1. **安全優先**：先偵測、再人工封鎖，最後才評估自動封鎖。
2. **小批次交付**：每個 Phase 都必須可以單獨驗證、回退及交接。
3. **單一寫入責任**：同一時間只允許一個 AI 修改同一組核心檔案。
4. **驗證與實作分離**：GPT-5.6 實作；AGY 優先負責驗證、證據整理與 Release Gate。
5. **禁止虛構完成**：沒有命令輸出、測試結果、截圖或 Git diff，不得宣稱完成。
6. **敏感資料隔離**：不得提交 `.env`、Token、真實密碼、公司固定 IP 或內部網段。

## 4. 里程碑排程

排程以 2026-07-10 為起點；實際開始日變動時，保持 Phase 順序與驗收門檻不變。

| 階段 | 日期 | 主責 | 主要交付 |
|---|---|---|---|
| P0 規格凍結與骨架 | 2026-07-10～07-12 | GPT-5.6 + AGY | Repo 骨架、ADR、設定範本、驗收矩陣 |
| P1 SQLite 與 SSH 垂直切片 | 2026-07-13～07-19 | GPT-5.6 | Schema、migration、SSH collector、事件去重、CLI 查詢 |
| P2 Nginx／Suricata 與查詢 API | 2026-07-20～07-26 | GPT-5.6 | Parser、來源健康狀態、Dashboard/Events API |
| P3 前台 Dashboard 與管理頁 | 2026-07-27～08-02 | AGY 主驗證、GPT-5.6 修復 | React UI、攻擊者、事件、告警、封鎖與白名單頁 |
| P4 nftables、RBAC 與稽核 | 2026-08-03～08-09 | GPT-5.6 | 人工限時封鎖、解除、權限、audit log、systemd |
| P5 整合測試與試營運 | 2026-08-10～08-16 | AGY Release Gate | E2E、效能、安全測試、部署與回復 SOP |

## 5. Phase 詳細內容

### P0：規格凍結與專案骨架

**GPT-5.6**

- 建立後端、前端、database、systemd、tests 目錄。
- 建立 `pyproject.toml`、前端 package、lint/type-check/test 指令。
- 將資料庫 schema 放入可執行 migration。
- 建立設定資料結構與 `.env.example`，不得包含秘密資料。
- 建立 ADR：時間格式、SQLite、API 框架、驗證方式、nftables 邊界。

**AGY**

- 將需求整理成驗收矩陣。
- 驗證 README、架構、資料庫與 MVP 文件互相一致。
- 列出 Blocker、風險與待決策事項。
- 確認所有開發命令可在乾淨環境執行。

**Gate P0**

- 目錄與指令存在。
- 沒有秘密資料。
- 文件與程式骨架一致。
- CI 至少能執行 lint、type check 與空測試框架。

### P1：SQLite 與 SSH 垂直切片

**GPT-5.6**

- 建立 SQLite 連線管理、PRAGMA 與 migration。
- 實作 `attack_events`、`attackers`、`log_sources`。
- 實作 SSH Journal Collector 與 cursor 保存。
- 實作 SSH Parser、IPv4/IPv6 驗證、事件去重。
- 以單一 transaction 寫事件並 UPSERT attackers。
- 提供 CLI：最近 24 小時攻擊 IP 排名。

**AGY**

- 使用 fixture 驗證 `Failed password`、`Invalid user`、格式異常與 IPv6。
- 驗證 Collector 重啟不大量重複。
- 比對事件明細與 attackers 統計。
- 產出測試證據與缺陷清單，不直接重構核心寫入流程。

**Gate P1**

- SSH 事件可於 30 秒內入庫。
- 重播相同 fixture 不增加重複事件。
- `PRAGMA quick_check` 回傳 `ok`。
- 單元測試涵蓋正常、異常、IPv4、IPv6 與去重。

### P2：Nginx、Suricata 與 API

**GPT-5.6**

- 實作 Nginx JSON access log parser。
- 實作 Suricata `event_type=alert` parser。
- 建立來源健康狀態與解析錯誤統計。
- 實作 Dashboard、Attackers、Events、Health REST API。
- 所有列表支援伺服器端分頁、排序與時間範圍限制。

**AGY**

- 驗證敏感路徑、Path Traversal、SQLi 樣本與正常 404 的區分。
- 驗證 Suricata severity mapping。
- 驗證 API 欄位、分頁、空資料、錯誤與權限狀態。
- 檢查輸入是否可能造成 SQL Injection、XSS 或超大查詢。

**Gate P2**

- 三種來源可轉為統一事件格式。
- API schema 穩定且有 OpenAPI。
- 大範圍查詢會被限制。
- raw log 顯示資料經 escaping。

### P3：前台 Dashboard 與管理頁

**GPT-5.6**

- 建立 API client、型別與必要後端修復。
- 修正 AGY 驗證發現的資料契約與效能問題。
- 保持後端查詢與 UI 需求一致。

**AGY**

- 實作或協調實作 React Dashboard UI。
- 完成 Dashboard、Attackers、Attacker Detail、Events、Alerts、Blocks、Allowlist、Sources。
- 建立 Loading、Empty、Error、Permission denied 狀態。
- 使用 Playwright 驗證 desktop 與 mobile。
- 確認色彩不是唯一風險辨識方式。

**Gate P3**

- 主要頁面可從真實 API 顯示資料。
- 篩選條件可由圖表導向詳細頁。
- 所有時間顯示 Asia/Taipei，API 資料維持 UTC。
- 前端無未處理 console error。

### P4：封鎖、RBAC 與稽核

**GPT-5.6**

- 建立 nftables 專用 set 與受控 blocker service。
- 實作人工限時封鎖、解除及到期 timer。
- 實作白名單與保護清單。
- 實作 Admin／Analyst／Viewer RBAC。
- 實作 audit log，記錄舊值、新值、操作者與 request ID。
- 建立 systemd hardening 與最小權限設定。

**AGY**

- 驗證 Viewer 無法封鎖。
- 驗證白名單、本機、管理來源與代理不會被封鎖。
- 驗證 shell injection、XSS、CSRF/session 設定。
- 驗證 SQLite 與 nftables 狀態一致。

**Gate P4**

- Web API 不以 root 身分執行。
- 不使用任意 `sh -c` 拼接 IP。
- 封鎖、解除與到期皆有 audit log。
- 失敗同步會保留可追蹤狀態並告警。

### P5：整合測試與試營運

**GPT-5.6**

- 修復整合測試缺陷。
- 補齊安裝、升級、備份、回復、解除誤封 SOP。
- 建立 dry-run 自動封鎖模式，但預設關閉正式自動封鎖。

**AGY**

- 執行完整 Release Gate。
- 產出測試摘要、截圖、命令輸出、已知限制與 Go/No-Go 判定。
- 驗證服務重啟、資料庫備份還原、磁碟滿載與來源中斷情境。
- 確認文件與實際程式版本一致。

**Gate P5**

- 所有 P0～P4 阻斷項目關閉。
- 備份可還原並通過 `quick_check`。
- 服務重啟後 Collector 可從 cursor 繼續。
- 自動封鎖維持 dry-run，除非管理者書面核准。

## 6. 每日工作節奏

| 時段 | 動作 |
|---|---|
| 開始前 | 讀取目前分支、最新 commit、Issue、工作樹狀態與上次交接 |
| 實作中 | 小批次修改；每完成一個可驗證單位即執行測試 |
| 提交前 | lint、type check、unit/integration test、git diff、秘密資料掃描 |
| 交接時 | 更新 Issue checklist、證據、風險、下一步與禁止修改區 |
| Release Gate | AGY 依驗收矩陣判定 PASS／PASS WITH RISKS／FAIL |

## 7. Definition of Done

一項工作只有同時符合以下條件才可標記完成：

- 程式碼或文件已提交到指定 branch。
- 有可重現的驗證命令與實際結果。
- 新增行為有測試；修復缺陷有回歸測試。
- 沒有新增秘密資料、明文密碼或真實內部 IP。
- 相關 README、API、schema 或操作文件已更新。
- AGY Release Gate 沒有未處理 blocker。

## 8. 風險與緩解

| 風險 | 緩解方式 |
|---|---|
| SQLite 鎖競爭 | WAL、小 transaction、查詢範圍限制、單一寫入服務 |
| 錯誤 Real IP | 只信任明確代理網段，驗證 X-Forwarded-For |
| 誤封管理端 | 白名單、保護清單、人工封鎖、dry-run |
| 日誌造成 XSS | escaping、CSP、原始日誌預設收合 |
| nftables 指令注入 | `ipaddress` 驗證、netlink/固定 helper、禁止 shell 拼接 |
| AI 同時改同檔 | 明確 owner、交接鎖、一次一個 writer |
| 文件與實作漂移 | 每個 Phase Gate 由 AGY 比對文件與程式 |
