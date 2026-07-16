# P1 — AGY 正式環境 Runtime Verification 報告

- **角色**：AGY verify-only 驗證者（未修改任何 backend / tests / systemd / 設定模板）
- **判讀依據**：`P1_AGY_TELEGRAM_VERIFICATION_TASK.md`（七、判定規則）

## 0. Runtime Gate 完整性（程式碼未被變更）

Diff `b83c4ea..77c263a` 僅新增下列 3 份文件，**無任何程式碼 / 測試 / systemd / 設定模板變更**：

```
A  docs/P1_AGY_TELEGRAM_FINAL_VERIFICATION.md
A  docs/P1_CLAUDE_GLM52_SECURITY_REVIEW.md
A  docs/P1_CODEX_LUNA_IMPLEMENTATION_REPORT.md
```

Git 確認：

```
git rev-parse HEAD         -> 77c263a2ac89329d2c5a352e5322563dd5d9a6e5
git rev-parse origin/main  -> 77c263a2ac89329d2c5a352e5322563dd5d9a6e5
git status --short         -> (clean，僅本份新報告待提交)
```

Runtime Gate 未被任何程式碼變更觸發停止。

---

## 1. 基本資訊

| 欄位 | 值 |
|---|---|
| Tested repository HEAD | `77c263a2ac89329d2c5a352e5322563dd5d9a6e5` |
| Tested code HEAD | `b83c4ea4f6be0dd9d4c084b736d9f8b9782f1982` |
| Host | `b822726-NB-TUFA16` |
| OS | Linux `7.0.11-arch1-1`（Arch Linux, x86_64, GNU/Linux） |
| Python | `3.14.5` |
| systemd | `260`（`260.2-2-arch`） |
| Verification time | `2026-07-16T19:34:56+08:00` |

> **重要前置事實**：本機 `b822726-NB-TUFA16` 為開發機，**並非**已部署的正式環境主機。已驗證下列項目在本機**不存在**：
>
> - 無 `secmon` 系統使用者（`id: 「secmon」：無此使用者`）
> - 無 `/etc/secmon/`（故無 `/etc/secmon/secmon.env`）
> - 無 `/var/lib/secmon/`（故無 `secmon.db` 與 `ssh.cursor`）
> - 無 `/opt/secmon/`（未安裝部署）
> - 無 `secmon-collector.service`（`systemctl list-unit-files 'secmon*'` → `0 unit files listed`，僅 repo 內 `systemd/` 為模板）
> - 無 `/var/log/auth.log`（Arch 預設走 journald；未配置 syslog → auth.log）
> - 無非互動 sudo（`sudo -n true` 失敗，需密碼；AGY 無 root）
>
> 因此任務之三項 **Runtime Gate（Real Telegram Smoke / Production systemd Runtime / 30-second Gate）無法在本機執行**。以下僅記錄實際可執行的 Static Gate，其餘欄位標註 `NOT EXECUTABLE` 與具體原因，**不偽造任何延遲數據**。

---

## 2. Static Gate（實際執行，本機）

| 檢查 | 指令 | 結果 |
|---|---|---|
| compileall | `.venv/bin/python -m compileall -q backend scripts tests` | exit `0` |
| Ruff | `.venv/bin/ruff check backend tests scripts` | `All checks passed!` — exit `0` |
| mypy | `.venv/bin/mypy backend` | `Success: no issues found in 14 source files` — exit `0` |
| pytest | `.venv/bin/python -m pytest -q` | **115 collected, 115 passed** — exit `0` |
| make check | `PATH="$PWD/.venv/bin:$PATH" make check`（lint+typecheck+test+build） | exit `0`（含 `ruff check backend database tests` / `mypy backend database` 16 files / `npm build` 前端） |

**Static Gate：PASS**

---

## 3. Real Telegram Smoke

| 欄位 | 值 |
|---|---|
| Real Telegram Smoke | **NOT EXECUTABLE** |
| Exit code | N/A |
| Message received | N/A |
| Message ID | N/A |
| Received timestamp | N/A |
| Token exposed in stdout | N/A（未執行；本機無 token） |
| Token exposed in stderr | N/A |
| Token exposed in journal | N/A |

原因：本機無 `/etc/secmon/secmon.env`（無部署），無法安全載入設定；無 Bot Token 可用。
依判定規則「只有 exit code 0 且使用者實際收到訊息，才可判定 PASS」→ **無法判定 PASS**。

---

## 4. Production systemd Runtime

| 欄位 | 值 |
|---|---|
| Systemd active | N/A（無 unit） |
| Runtime duration | N/A |
| auth.log readable | N/A（檔案不存在） |
| Database path | N/A（無 `/var/lib/secmon/secmon.db`） |
| Cursor path | N/A（無 `/var/lib/secmon/ssh.cursor`） |
| Restart loop | N/A |
| Token exposed | N/A |
| **Production Runtime** | **NOT EXECUTABLE** |

原因：無 `secmon-collector.service`（`0 unit files listed`），未安裝部署，無 sudo/root，故無法 `daemon-reload` / `restart` / 檢查 journal。

---

## 5. 三次 30-second End-to-End Gate

| 欄位 | 值 |
|---|---|
| Run 1 DB latency | NOT EXECUTABLE |
| Run 1 Telegram latency | NOT EXECUTABLE |
| Run 2 DB latency | NOT EXECUTABLE |
| Run 2 Telegram latency | NOT EXECUTABLE |
| Run 3 DB latency | NOT EXECUTABLE |
| Run 3 Telegram latency | NOT EXECUTABLE |
| Duplicate counts | N/A（無 DB） |
| quick_check | N/A（無 `/var/lib/secmon/secmon.db`） |
| foreign_key_check | N/A（無 DB） |

原因：三項必要條件均不具備——(a) 無 `secmon.db`；(b) 無 `/var/log/auth.log` 可觸發；(c) AGY 無法從「另一台已授權測試主機」產生真實 SSH 失敗登入（無該授權主機可達、無 sudo）。**未以任何模擬 / 假資料替代**。
依規則「三次 DB latency 都 <= 30 秒」→ **無法驗證，無法判定 PASS**。

---

## 6. Token exposure check

- 本機**無** `/etc/secmon/secmon.env`，未載入、未輸出任何 Bot Token。
- Static Gate 全部輸出（compileall / ruff / mypy / pytest / make check）已檢視，無任何 secret / URL / token。
- 本次提交**僅**本份報告 `docs/P1_AGY_PRODUCTION_RUNTIME_VERIFICATION.md`，未提交 env、DB、cursor、journal log、Telegram response dump。
- **Token exposure check：PASS（因未涉及真實 token，無洩漏可能）**

---

## 7. 發現分級

- **Blocker**
  - **Runtime Gate 無法執行**：驗證主機非正式環境，缺 `secmon` 使用者、`/etc/secmon`、`/var/lib/secmon`、`/opt/secmon`、`secmon-collector.service`，且 AGY 無 sudo/root。三項 Runtime Gate 全部無法於本機驗證。
- **High**
  - 無（因 Runtime Gate 未能執行，未觀察到任何運行期缺陷）。
- **Medium**
  - 本 Arch 主機預設無 `/var/log/auth.log`（journald）。正式部署須確認已配置 rsyslog/syslog-ng → `/var/log/auth.log`，且 `secmon` 使用者具讀取權，否則 SSH 偵測器無事件來源。
  - Diff 範圍正確（僅 3 份文件），但部署「安裝到正式主機」此一動作目前無對應 commit/證據可稽核（非本次 AGY 變更，屬部署流程）。
- **Low**
  - 無。

---

## 8. 三項 Gate 判定

| Gate | 判定 |
|---|---|
| Real Telegram Smoke | **NOT EXECUTABLE**（無法 PASS） |
| Production systemd Runtime | **NOT EXECUTABLE**（無法 PASS） |
| 30-second Gate | **NOT EXECUTABLE**（無法 PASS） |

> 本案為「無法執行」，**非 FAIL**：產品程式碼未呈現任何運行期失敗，Static Gate 全綠；問題在於 Runtime Gate 驗證環境（正式主機）不在本機。

---

## 9. Final recommendation

- **Static Gate：PASS**
- **Real Telegram Smoke：NOT EXECUTABLE → 無法 PASS**
- **Production systemd Runtime：NOT EXECUTABLE → 無法 PASS**
- **30-second Gate：NOT EXECUTABLE → 無法 PASS**

### P1 Recommendation：**NOT READY**

依任務規則「若任何一項無法執行 → P1 Recommendation：NOT READY」。

- **Issue #2：保持 OPEN**
- **不可宣告 Release Gate PASS**（三項 Runtime Gate 全部未通過實證）
- **Required next step（非 FAIL，不需 Codex Luna 維修）**：將本 AGY Runtime Verification 移至**真正的正式主機**執行——該主機需具備：已安裝部署（`/opt/secmon` + `secmon-collector.service` active）、`secmon` 使用者、`/etc/secmon/secmon.env`（權限 ≤ 600、含真實 token）、`/var/lib/secmon/{secmon.db,ssh.cursor}`、`/var/log/auth.log`（secmon 可讀）、可達的已授權 SSH 測試主機，以及 AGY 可用之 sudo/root。
- **Required repair owner**：N/A（非 FAIL；為驗證環境/部署到位問題，由部署負責人將 Runtime 驗證移至正式主機後重跑本份 AGY 程序）。
