# P1 SSH Detector 過程整理

## 1. 任務背景與偏離診斷

本任務旨在處理 `Issue #2: P1 SQLite 與 SSH 偵測垂直切片`，將系統從不一致的 P0/P1 schema 衝突狀態修復並對齊至 P1 標準 canonical schema。先前獨立驗證（AGY）發現了核心架構偏離、Parser 歷史時間衝突、CLI 錯誤引入及測試契約未同步等缺陷。

---

## 2. 修復與開發歷程

為了在不破壞 canonical schema 的前提下收斂系統，我們採取了以下修復歷程：

### 2.1 對齊 SQLite 遷移與 Schema
* 對齊了 `database/migrations/` 底下的 SQL schema，以 `source_type`/`source_path`/`enabled`/`last_event_at`/`detected_at`/`src_ip`/`total_events` 為核心基準。
* 修改了 `LogSourcesService` 及模型定義，修復了在部分欄位更新時 status 被默默變更為 `unknown` 的行為。
* 對 duplicate name 違反唯一約束時正確捕獲並向上拋出 `RuntimeError`，符合 API 規範。

### 2.2 修正收集器去重與 Cursor
* 解決了測試直接依賴 `var/ssh_cursor.position` 原地殘留的問題，並在測試中採用隨機且獨立的暫存 cursor 檔案。
* 重構 `_process_batch` 中的新攻擊者統計邏輯：寫入前使用 `SELECT 1 FROM attackers WHERE src_ip = ?` 進行判斷，唯有真正的新攻擊者才增加 `new_attackers` 計數。
* Cursor precedence 為 constructor `cursor_path`、`SECMON_SSH_CURSOR_PATH`、最後才是 project default；本 collector 使用 auth.log byte offset，不是 journalctl cursor。

### 2.3 修復 Parser 與日誌時間戳記 fallback
* 刪除了 minimum timestamp 的「太舊時間」校驗，完全支援歷史與 Syslog 類型的 SSH 時間戳記。
* 精細化時間戳記 fallback 邏輯：唯有日誌行開頭為 `Failed password` 或 `Invalid user`（或帶有 optional `sshd[1234]: ` 前綴）且完全無法解析時間時，方以目前時間作為 fallback；若本身包含 date-like 特徵卻無法構成合規 ISO 格式時，則正確拋出 `ValueError`。
* 容許使用者名稱開頭與結尾帶有底線 `_`（Linux 系統帳戶常見樣式），並同步修正對應測試案例。

### 2.4 AGY second-repair edge cases
* SSH source port 僅接受 1–65535，並保存至 `attack_events.src_port`。
* Future timestamp policy 為 reference time + 5 分鐘；歷史時間仍接受。
* 先匹配 `Failed password for invalid user`，避免 username 被解析成 `invalid`。

### 2.4 重構測試套件（Test Contract）
* 將所有測試檔案全面遷移至 P1 命名規格。
* 使用 `tmp_path` 與獨立 `sqlite3` 連線來動態呼叫 `migrate_latest`，排除對 `var/secmon.db` 與舊資料的依賴。
* 補齊了多事件 N-increment 的測試校驗。

### 2.5 修正 Ruff & Mypy
* 排除了所有長行（E501，限制 100 字元以內）、未使用變數（F841）與 `B904` 錯誤。
* 修復了 `SSHLogEntry.username` 可為 `None` 的型別不合規問題，Mypy 達成 0 錯誤。

---

## 3. 本地整合驗證

1. **乾淨資料庫遷移測試**：
   - 於 `/tmp/secmon-p1-final.db` 上運行遷移，並透過 `PRAGMA quick_check` 與 `foreign_key_check` 確實驗證完整無異。
2. **入庫與重播**：
   - 使用 fixture 完成 102 筆有效事件寫入；非法 port 行被拒絕。重播時，`attack_events` 及 `attackers` 的事件數均未重複累計。
3. **CLI 報表**：
   - 運行 `scripts/attack_report.py` 成功且格式整齊，且當指定不存在的資料庫路徑時，正確印出找不到資料庫的錯誤並以 exit code 1 結束，無靜默退回之隱憂。

---

## 4. 當前交付狀態

GPT-5.6 的實作修復已全數完成。本地端所有的靜態檢查、編譯與 pytest 均以 exit code 0 執行通過，工作樹的未知修改亦已分次提交，目前正處於「等待 AGY 回歸驗證」的過渡狀態。
