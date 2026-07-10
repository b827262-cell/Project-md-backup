# P1 SSH Detector 過程整理

## 1. 任務背景

本次處理的主題是 `Issue #2: P1 SQLite 與 SSH 偵測垂直切片`，目標包含：

- SQLite migration、WAL、busy timeout、transaction 管理
- `attack_events`、`attackers`、`log_sources` 表設計
- SSH Journal Collector 與 cursor 保存
- `Failed password` / `Invalid user` parser
- IPv4、IPv6、Port、時間與欄位長度驗證
- event_key 去重與 attackers UPSERT
- 最近 24 小時攻擊 IP CLI 報表
- fixture、unit test 與 handoff 文件

## 2. 已完成內容

依既有狀態報告與 handoff 文件，P1 的主要功能已實作完成：

- SQLite schema / migration
- SSH collector
- SSH parser
- CLI 攻擊報表
- 測試 fixtures
- handoff 與狀態報告文件

## 3. 本次實際檢查與驗證

我先確認了目前工作樹與執行環境：

- `git status` 顯示有多個已修改檔案與未追蹤檔案
- 目前分支為 `main`
- remote 指向 `origin`（GitHub）
- 先前環境缺少 `ruff` / `pytest`，因此建立並啟用 `venv`，再安裝 `.[dev]`

接著做了實際檢查：

- `ruff check backend/ tests/`：顯示仍有 lint 錯誤
- `pytest tests/test_ssh_parser.py -v`：顯示 `test_ssh_parser.py` 仍有多個失敗

## 4. 主要發現的問題

### 4.1 lint / style 問題

檢查結果顯示主要是：

- `E501` 長行
- `F841` 未使用變數
- `F821` 未定義名稱
- `UP045` 型別註記格式
- `B904` exception chaining 問題
- `E402` import 順序問題

### 4.2 測試失敗

`tests/test_ssh_parser.py` 仍有多個失敗，包含：

- `SSHLogEntry.is_valid()` 的驗證結果與預期不一致
- timestamp / IP 驗證失敗數量與測試預期不同
- 部分測試寫法與目前實作不相容

## 5. 本次已做的調整

在檢查過程中，先做了幾個明確可修正的整理：

- `backend/models/__init__.py`
  - 移除不需要的 `Optional` 匯入
- `backend/parsers/ssh_parser.py`
  - 拆分過長字串
  - 移除無用的 `fallback` 變數
- `backend/services/log_sources.py`
  - 拆分過長 SQL 字串
- `tests/test_log_sources.py`
  - 補上缺少的 `Path` 匯入
- `tests/test_replay_deduplication.py`
  - 修正檔頭 docstring
- `tests/test_ssh_collector.py`
  - 修正匯入與 class 命名問題
- `tests/test_ssh_parser.py`
  - 移除部分未使用變數與長行

## 6. 目前狀態

### 已確認

- venv 已建立
- 開發依賴已安裝
- 能夠實際執行 `ruff` 與 `pytest`
- 已確認 lint / test 仍有剩餘問題需要後續修正

### 尚未完成

- 仍有未修完的 `ruff` 錯誤
- `tests/test_ssh_parser.py` 尚未全部修復
- 尚未進行 commit / push

## 7. 後續建議

若要繼續往可上線狀態推進，建議依序處理：

1. 先收斂 `ruff` 錯誤
2. 再對齊 `tests/test_ssh_parser.py` 與目前實作行為
3. 跑完整測試套件
4. 確認工作樹僅包含預期變更
5. 再 commit / push 到 GitHub

## 8. 本次使用的關鍵工具結果

- `git status`：確認目前工作樹與未追蹤檔案
- `ruff check`：確認 lint 錯誤仍存在
- `pytest tests/test_ssh_parser.py -v`：確認測試仍失敗
- `venv + pip install -e .[dev]`：補齊本地開發工具

## 9. 結論

這份整理記錄了本次 P1 SSH Detector 的實際排查流程、已確認問題與當前進度。功能面已具備基礎完成度，但 lint 與 parser 測試仍需後續收尾，才能算是完整通過驗證。
