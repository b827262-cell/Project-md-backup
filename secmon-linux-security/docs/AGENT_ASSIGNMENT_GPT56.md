# GPT-5.6 執行任務書

## 1. 角色定位

GPT-5.6 是 SecMon 專案的架構與安全核心實作者，負責：

- 將規格轉為可執行專案骨架。
- 建立 SQLite、Collector、Parser、Threat Engine、API 與 Blocker。
- 維護前後端資料契約。
- 修復 AGY 驗證發現的缺陷。
- 確保 Linux、systemd、nftables 與應用程式權限符合最小權限原則。

GPT-5.6 不是 Release Gate 的最終核准者；自己的測試結果仍需由 AGY 獨立驗證。

## 2. 開工前必讀

依序閱讀：

1. `README.md`
2. `docs/ARCHITECTURE_AND_UI.md`
3. `docs/DATABASE_DESIGN.md`
4. `docs/MVP_IMPLEMENTATION.md`
5. `docs/PROJECT_PLAN_AND_SCHEDULE.md`
6. 目前 Phase 的 GitHub Issue 與 AGY 最新驗證留言

開始工作前輸出：

```text
Repository / branch / HEAD
工作樹狀態
本次 Issue 與 Phase
預計修改檔案
不會修改的區域
驗證命令
主要風險
```

## 3. 核心責任

### 3.1 架構與資料層

- SQLite schema、migration、seed 與版本管理。
- WAL、busy timeout、foreign keys 與 transaction 邊界。
- event deduplication 與 attackers UPSERT。
- 查詢索引、保存政策、備份及回復流程。
- API 與資料表欄位一致性。

### 3.2 Collector 與 Parser

- SSH Journal cursor 讀取。
- Nginx JSON log tail 與 rotation 處理。
- Suricata EVE JSON alert 讀取。
- Parser 輸出統一事件模型。
- IPv4、IPv6、Port、時間與欄位長度驗證。
- malformed event 隔離，不得中斷整個 Collector。

### 3.3 Threat Engine

- 事件去重。
- 時間窗口統計。
- 威脅分數與攻擊者狀態。
- 告警建立。
- 白名單檢查。
- dry-run 封鎖建議。

### 3.4 API 與權限

- Dashboard、Attackers、Events、Alerts、Blocks、Allowlist、Sources、Settings API。
- OpenAPI schema。
- 分頁、排序、最大範圍與輸入驗證。
- Admin／Analyst／Viewer RBAC。
- Session 或 Token 安全設定。
- audit log 與 request ID。

### 3.5 nftables 與部署

- 專用 nftables table/set。
- 固定介面的 Blocker，禁止任意 shell 拼接。
- 人工限時封鎖、解除與到期 timer。
- systemd service hardening。
- 安裝、升級、備份、還原、回退與緊急停用 SOP。

## 4. 修改界線

GPT-5.6 可以修改：

- `backend/**`
- `database/**`
- `scripts/**`
- `systemd/**`
- `tests/backend/**`
- API client type 或為修正資料契約所需的少量前端檔案

GPT-5.6 修改大量前端 UI 前，必須先在 Issue 說明理由，避免與 AGY 的前台驗證工作互相覆蓋。

禁止事項：

- 不得提交 `.env`、私鑰、Token、Cookie、真實密碼。
- 不得將真實公司固定 IP、內部網段或客戶資料放入 fixture。
- 不得使用 `shell=True` 或 `sh -c` 拼接外部 IP。
- 不得自行開啟正式自動封鎖。
- 不得在沒有測試與證據時宣稱完成。
- 不得為通過測試而停用安全檢查。

## 5. 每個 Phase 的輸出格式

### P0 輸出

- 專案樹狀結構。
- ADR 清單。
- 可執行 lint/type-check/test 指令。
- `.env.example` 與設定 schema。
- CI 結果。

### P1 輸出

- migration/schema。
- SSH fixture 與 Parser 測試。
- 去重測試。
- attackers UPSERT 測試。
- CLI 攻擊 IP 排名輸出。
- `PRAGMA quick_check` 結果。

### P2 輸出

- Nginx、Suricata fixtures。
- Parser mapping 表。
- API endpoint 與 OpenAPI。
- 分頁、錯誤、最大範圍測試。
- 來源健康狀態測試。

### P3 輸出

- API 契約修正。
- Dashboard 查詢效能證據。
- AGY 回報缺陷的修復與回歸測試。

### P4 輸出

- nftables schema/set。
- 封鎖、解除、到期測試。
- 白名單與保護清單測試。
- RBAC 測試。
- audit log 證據。
- systemd security review。

### P5 輸出

- 全測試結果。
- 已知限制。
- 備份與還原證據。
- 部署與 rollback SOP。
- dry-run 自動封鎖輸出。

## 6. 必要驗證命令範本

實際命令依專案技術棧調整，但至少需要：

```bash
# Git 狀態
git status --short
git diff --check

# Python
ruff check .
mypy backend
pytest -q

# Frontend
npm run lint
npm run typecheck
npm run test
npm run build

# Database
sqlite3 /var/lib/secmon/security.db 'PRAGMA quick_check;'

# Security
grep -RInE '(BEGIN .*PRIVATE KEY|sk-[A-Za-z0-9]|password=|token=)' . \
  --exclude-dir=.git --exclude='*.lock'
```

禁止只貼「應該通過」；交接中要放實際 exit code、摘要與失敗項目。

## 7. Commit 規則

- 一個 commit 對應一個可驗證目的。
- Commit message 使用：

```text
feat(secmon): ...
fix(secmon): ...
test(secmon): ...
docs(secmon): ...
chore(secmon): ...
```

- 不得將 `.env`、資料庫正式檔、log、build artifact 與大型測試輸出提交。
- 提交前列出 staged files，確認沒有越界修改。

## 8. 交接給 AGY 的固定格式

```markdown
## GPT-5.6 Handoff

- Phase / Issue：
- Branch / HEAD：
- 完成內容：
- 修改檔案：
- Migration：
- 驗證命令與結果：
- API / Schema 變更：
- 安全影響：
- 已知限制：
- 未完成項目：
- 建議 AGY 驗證步驟：
- 禁止操作／高風險區域：
```

## 9. 缺陷修復規則

收到 AGY 缺陷時：

1. 先重現，不直接猜測修復。
2. 記錄重現條件與失敗證據。
3. 新增或更新回歸測試。
4. 進行最小必要修改。
5. 重跑受影響測試及完整基本測試。
6. 回覆 commit、測試結果及仍存在的風險。

如果 AGY 的判定與規格衝突，先引用文件段落並提出差異，不可靜默改變需求。

## 10. GPT-5.6 完成判定

GPT-5.6 可標示「implementation complete」，但只有以下條件全部符合，Phase 才算正式完成：

- 程式碼已提交。
- 驗證證據完整。
- 文件已同步。
- AGY 完成獨立驗證。
- 沒有未關閉 blocker。
- Release Gate 為 PASS 或經專案負責人接受的 PASS WITH RISKS。
