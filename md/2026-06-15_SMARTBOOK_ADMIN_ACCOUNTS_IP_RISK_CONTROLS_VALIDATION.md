# 2026-06-15 SmartBook 後台帳號 IP 與風險控管驗收紀錄

## 1. 驗收對象

- 專案：AI-SmartBook-R1
- 功能頁面：`http://127.0.0.1:5174/admin/accounts`
- 功能類型：後台帳號安全管理 / Session 風險控管
- 對應 commit：`dfa659b`
- commit message：`feat: add admin account IP tracking and risk controls`

---

## 2. 本次新增功能

### 2.1 後台帳號列表新增欄位

原本欄位：

```text
編號
學生名稱
登入方式
作業系統
裝置類型
瀏覽器
最後上線時間
目前狀態
```

本次新增：

```text
IP 位址
IP 位置
風險標記
封鎖狀態
管理操作
```

### 2.2 IP 位址記錄

後端新增登入 / session 活動 IP 追蹤能力：

- 記錄 `lastIpAddress`
- 支援 localhost / private IP 顯示
- 若部署於 Nginx / Cloudflare 後方，需設定 `TRUST_PROXY=true`
- 本機測試 `127.0.0.1` / 私有網段顯示為 `Localhost / Private IP`
- 公開 IP 尚未接 GeoIP 時顯示 `Unknown`

### 2.3 風險標記

新增帳號 / session 風險等級：

```text
safe      => 安全
risk      => 風險
dangerous => 危險
```

實作內容：

- `riskLevel`，預設 `safe`
- `riskNote`
- 後台 UI 可使用下拉選單即時切換
- badge 顏色：安全=綠、風險=黃、危險=紅

### 2.4 封鎖 / 解除封鎖

新增欄位與操作：

- `isBlocked`
- `blockedAt`
- `blockedReason`
- 後台可封鎖並填寫原因
- 後台可解除封鎖並清除封鎖狀態
- 列表顯示：`已封鎖` / `正常`

---

## 3. 封鎖行為驗證

AGY 回報已完成實測：

```text
前台 /api/student/.../chat 與 chat-sessions 端點已實際回 403。
```

測試結果：

| 測試情境 | 結果 |
|---|---|
| 被封鎖 session 再次請求 | 403 |
| 相同公開 IP 開新 session | 403 |
| 不同 IP | 200 |
| 解除封鎖後 | 200 |

封鎖訊息：

```text
This account/session has been blocked by the administrator.
```

### 3.1 已知限制

目前系統屬於 session / anonymous 模型，尚未有完整持久身分。

因此：

```text
匿名使用者若同時更換 IP 並丟棄舊 sessionId，仍可能建立新 session。
```

完整強制控管需要後續 auth / identity 架構重構。

另外：

```text
last_ip_address 會隨每次請求更新為最新 IP。
```

本機開發時多個 session 共用 `127.0.0.1`，因此私有 IP 不做 IP 比對，避免 localhost 測試時一次擋掉所有本機 session。

---

## 4. DB / Migration 狀態

AGY 回報：

```text
不需 pnpm db:push。
```

原因：

- 專案目前無 `db:push`
- schema 變更透過 `runMigrations()` 於 admin server 啟動時自動以 `addColumnIfMissing` 冪等回填既有 DB
- 亦可手動執行 `pnpm db:migrate`
- 實測 10 個新欄位皆正確建立

部署注意：

```text
雖然不需 pnpm db:push，但正式環境仍必須確認 admin server 啟動時 migrations 已成功執行，或手動執行 pnpm db:migrate。
```

---

## 5. 實際修改檔案

```text
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/pages/AdminAccountsPage.tsx
apps/AI-adm-D1/src/server/index.ts
packages/db/src/migrate.ts
packages/db/src/repositories/chat.repo.ts
packages/db/src/schema.ts
packages/schema/src/chat.schema.ts
```

統計：

```text
7 files changed, 414 insertions(+), 30 deletions(-)
```

---

## 6. 驗證結果

| 項目 | 結果 |
|---|---|
| pnpm build | PASS |
| pnpm typecheck | PASS，11/11 workspace projects |
| git status | working tree clean |
| appearance/header/hero/theme 是否混入 | 否 |
| PDF/chapter 無關變更是否混入 | 否 |
| 是否已 commit | 是 |
| commit SHA | `dfa659b` |

---

## 7. AGY 最終驗證回報

AGY 於後續驗證流程中回報最終狀態為：

```text
PASS
```

驗證對象：

```text
後台帳號 IP 追蹤與風險控管功能
```

### 7.1 後台欄位驗證

| 項目 | 結果 |
|---|---|
| IP 位址 | PASS，正確取得並顯示 |
| IP 位置 | PASS，透過 `describeIpLocation` 顯示 |
| 風險標記 | PASS，提供下拉選單對應狀態 |
| 封鎖狀態 | PASS，顯示為「正常」或「已封鎖」 |
| 管理操作 | PASS，提供風險等級切換與封鎖 / 解除封鎖按鈕 |

### 7.2 風險標記驗證

| 風險狀態 | 顯示 | 結果 |
|---|---|---|
| `safe` | 安全 | PASS |
| `risk` | 風險 | PASS |
| `dangerous` | 危險 | PASS |

重新整理後是否保留：PASS。修改後前端會呼叫 `load()` 從資料庫重新取得狀態，確認變更持久化。

### 7.3 封鎖 / 解除封鎖驗證

| 項目 | 結果 |
|---|---|
| 封鎖是否成功 | PASS |
| 解除封鎖是否成功 | PASS |
| `blockedReason` 是否保存 | PASS，可透過 prompt 輸入並傳給後端寫入 |
| `blockedAt` 是否保存 | PASS，封鎖時會寫入時間戳記 |

### 7.4 學生端阻擋驗證

| 項目 | 結果 |
|---|---|
| blocked session 是否回 403 | PASS，透過 `rejectIfBlocked` 檢查 `session?.isBlocked` |
| 相同公開 IP 是否回 403 | PASS，透過 `repos.chat.isIpBlocked(ip)` 跨 session 阻擋 |
| 不同 IP 是否可通過 | PASS |
| 解除封鎖後是否恢復 200 | PASS |
| 封鎖訊息是否正確 | PASS，回應 `This account/session has been blocked by the administrator.` |

### 7.5 IP 偵測驗證

| 項目 | 結果 |
|---|---|
| `TRUST_PROXY=false` 時是否只使用 socket IP | PASS |
| `TRUST_PROXY=true` 時是否支援 `CF-Connecting-IP` / `X-Forwarded-For` / `X-Real-IP` | PASS，並依照優先順序解析 |
| localhost/private IP 是否顯示 `Localhost / Private IP` | PASS，已實作 `isPrivateIp` 過濾與特殊標示 |
| public IP 無 GeoIP 時是否顯示 `Unknown` | PASS |

### 7.6 DB / Migration 驗證

| 項目 | 結果 |
|---|---|
| 是否新增欄位 | PASS，在 `chat_sessions` 中新增 IP 記錄與風控相關欄位 |
| migration 是否 idempotent | PASS，使用 `addColumnIfMissing` 避免重複修改或破壞 |
| 是否需要 `pnpm db:push` | 否 |
| 是否需要 `pnpm db:migrate` 或 `runMigrations` | 是，`server/index.ts` 啟動時會自動執行 `runMigrations(sqlite)` 完成綱要升級 |

### 7.7 最終驗證結論

AGY 結論：

```text
dfa659b 實作邏輯完整清晰、防禦到位且無夾帶無關變更，可以接受 (PASS)。
```

---

## 8. 驗收判定

本次功能可判定為：

```text
ADMIN_ACCOUNTS_IP_RISK_CONTROLS_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
DEPLOYMENT_MIGRATION_CHECK_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

### 8.1 可接受項目

- 後台帳號列表已新增 IP 欄位
- 後台帳號列表已新增 IP 位置顯示
- 風險標記：安全 / 風險 / 危險已完成
- 封鎖 / 解除封鎖 UI 已完成
- 學生端 chat / session endpoint 已有 403 阻擋
- 相同公開 IP 跨 session 封鎖已驗證
- TRUST_PROXY 行為已驗證
- build/typecheck 通過
- working tree clean
- 未混入 unrelated UI / PDF / chapter 變更

### 8.2 部署前注意事項

正式部署前仍需確認：

1. Admin server 啟動時 `runMigrations()` 是否確實成功執行。
2. 若正式環境位於 Nginx / Cloudflare 後方，需設定：

```env
TRUST_PROXY=true
```

3. 若後續需要精準國家 / 城市定位，需另行規劃 GeoIP provider 或 Cloudflare header，不應混入本次 commit。
4. 因系統目前仍為 session / anonymous 模型，封鎖不是完整身份級封鎖；完整身份封鎖需另開 auth/identity 任務。

---

## 9. 下一步建議

目前不建議直接 final merge / deploy。

建議下一步：

```text
1. 執行只讀確認：git log / git status / git show
2. 確認正式部署環境 migration 策略
3. 確認正式環境是否經過 Nginx / Cloudflare，並設定 TRUST_PROXY=true
4. 再決定 push / PR / merge / deploy
```

---

## 10. 最終結論

`dfa659b` 可接受為後台帳號 IP 與風險控管功能 commit。

AGY 已完成驗證並回報：

```text
PASS
```

但此功能涉及 schema/migration 與代理 IP 判定，因此目前狀態仍應維持：

```text
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```
