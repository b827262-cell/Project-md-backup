# P1 Telegram → Codex 執行任務

## 1. 任務目的

透過 Telegram 對專案代理下達任務，由 **Codex CLI 作為唯一程式修改執行者**，完成 SecMon P1 的 Production SSH Collector 常駐輪詢、Telegram SSH 攻擊告警、安全的環境變數與 systemd 部署，以及完整測試、commit 與 push。

> 本文件可直接貼入 Telegram Bot。不得在 Telegram、Git、程式碼、測試或文件中填入真實 Bot Token。

## 2. 角色分工

- **Codex**：唯一 write executor，負責修改、測試、commit、push。
- **Telegram Agent**：負責協調、監督、驗證結果與回報。
- **AGY**：後續獨立驗證者，不參與本次實作修改。

限制：

- Telegram Agent 不得直接修改程式。
- 不得修改任何 AGY 原始驗證報告。
- 不得提前宣告 P1 Release Gate PASS。

## 3. Repository 基準

- Repository：`b827262-cell/Project-md-backup`
- Project：`secmon-linux-security`
- 工作目錄：`/home/b822726/project/get-rg/secmon-linux-security`
- Branch：`main`
- Expected base HEAD：`645388ea56943ca9213d8ceac4cc647f7b429ad9`
- Issue：`#2`
- Telegram Chat ID：`8350114645`

開始前執行：

```bash
cd /home/b822726/project/get-rg/secmon-linux-security

git fetch origin
git pull --ff-only origin main
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git status --short
```

回報：

```text
Repository：
Branch：
Local HEAD：
origin/main：
Expected base HEAD：
Working tree：
Unknown existing changes：
```

若 HEAD 不是 `645388ea56943ca9213d8ceac4cc647f7b429ad9`，停止修改並回報實際 HEAD，不得強制 reset。

## 4. Production Collector Loop

目前 systemd 預期使用：

```bash
python -m backend.collectors.main
```

確認並建立：

```text
backend/collectors/main.py
```

需求：

1. 建立 `SSHCollector` production polling loop。
2. 每輪呼叫 `collect_from_file()`。
3. 支援：
   - `SECMON_DATABASE_PATH`
   - `SECMON_SSH_CURSOR_PATH`
   - `SECMON_SSH_LOG_PATH`
   - `SECMON_COLLECT_INTERVAL_SECONDS`
4. 預設輪詢間隔為 5 秒。
5. 設定合理最小間隔，避免 busy loop。
6. 正確處理 `SIGTERM`、`SIGINT`。
7. systemd stop 時可正常結束。
8. 單輪可恢復錯誤：記錄後繼續下一輪。
9. 初始化、schema 或設定等不可恢復錯誤：明確記錄並以非零 code 結束。
10. 每輪記錄 start time、new events、new attackers、duration、next poll interval。
11. Production DB 與 cursor 不得寫入 repository 的 `./var`。

## 5. Telegram Notifier

新增：

```text
backend/notifiers/__init__.py
backend/notifiers/telegram.py
```

介面：

```python
class TelegramNotifier:
    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        ...

    def send_message(self, text: str) -> bool:
        ...
```

設定來源：

```text
SECMON_TELEGRAM_ENABLED
SECMON_TELEGRAM_BOT_TOKEN
SECMON_TELEGRAM_CHAT_ID
SECMON_TELEGRAM_TIMEOUT_SECONDS
SECMON_TELEGRAM_MIN_SEVERITY
SECMON_TELEGRAM_COOLDOWN_SECONDS
```

預設：

```dotenv
SECMON_TELEGRAM_ENABLED=false
SECMON_TELEGRAM_TIMEOUT_SECONDS=5
SECMON_TELEGRAM_MIN_SEVERITY=3
SECMON_TELEGRAM_COOLDOWN_SECONDS=60
```

Telegram Chat ID：`8350114645`

### Telegram Client 要求

1. 呼叫 Telegram Bot API `sendMessage`。
2. 僅使用 HTTPS。
3. 設定 request timeout。
4. 處理 HTTP error、timeout、DNS/network error、Telegram `ok=false`、malformed JSON，以及 HTTP 400／401／429／500。
5. 失敗回傳 `False` 或明確 exception，但不得 rollback 已完成的 DB transaction。
6. log 不得包含 Token 或完整 Bot API URL。
7. 訊息限制在 3500 字元內。
8. 優先使用純文字，避免未處理的 HTML／Markdown 特殊字元。
9. Telegram disabled 時不得發生任何網路請求。

### 嚴禁

- 真實 Bot Token 寫入程式碼、Git、測試或文件。
- log、stdout、stderr 顯示 Token。
- 將完整 raw SSH log 傳到 Telegram。
- 在 SQLite transaction 內呼叫 Telegram。
- Telegram 失敗時 rollback 已成功入庫事件。

## 6. Collector 整合

修改：

```text
backend/collectors/ssh_collector.py
```

需求：

1. 只對實際成功 INSERT 的新事件發送通知。
2. DB commit 完成、connection 關閉後才發送 Telegram。
3. `new_events=0` 時不得通知。
4. replay 或 duplicate 不得重複通知。
5. Telegram 失敗只記錄 warning，不影響 DB commit、`attackers.total_events`、cursor 或 Collector 回傳值。
6. 多筆事件聚合成單一 batch alert，不得逐筆洗版。
7. 支援 cooldown。
8. notifier 可由 constructor 注入，方便測試。
9. 通知內容只能來自本批次真正新增事件。

建議 constructor：

```python
def __init__(
    self,
    database_path: Path | None = None,
    cursor_path: Path | None = None,
    notifier: TelegramNotifier | None = None,
) -> None:
    ...
```

### 告警訊息格式

```text
🚨 SecMon SSH Attack Alert

Host: <hostname>
New events: <count>
New attackers: <count>
Detected: <time range>

Top sources:
1. <ip> — <count> attempts

Users:
<user list>

Database: healthy
```

訊息不得包含 Token、密碼、完整 raw log、`.env` 或內部敏感路徑。

## 7. Telegram 測試命令

支援：

```bash
.venv/bin/python -m backend.notifiers.telegram --test
```

規則：

- 從環境變數讀取 Token 與 Chat ID。
- 成功 exit code 0。
- 失敗 exit code 非 0。
- stdout、stderr 不得顯示 Token。

測試訊息：

```text
✅ SecMon Telegram notification test
Host: <hostname>
Status: connected
```

## 8. Systemd

檢查並修正：

```text
systemd/secmon-collector.service
```

必須使用：

```ini
EnvironmentFile=/etc/secmon/secmon.env
ExecStart=/opt/secmon/.venv/bin/python -m backend.collectors.main
Restart=on-failure
RestartSec=5s
```

確認 writable paths：

```text
/var/lib/secmon
/var/log/secmon
```

不得在 unit 內直接寫 Token。

正式主機先檢查：

```bash
stat -c '%U %G %a %n' /var/log/auth.log
id secmon
```

只有確認 `/var/log/auth.log` 所屬群組為 `adm`，而 `secmon` 無讀取權限時，才加入：

```ini
SupplementaryGroups=adm
```

不得盲目假設群組名稱。

## 9. 環境範例

更新 `.env.example`，只能放 placeholder：

```dotenv
SECMON_DATABASE_PATH=/var/lib/secmon/secmon.db
SECMON_SSH_CURSOR_PATH=/var/lib/secmon/ssh.cursor
SECMON_SSH_LOG_PATH=/var/log/auth.log
SECMON_COLLECT_INTERVAL_SECONDS=5

SECMON_TELEGRAM_ENABLED=false
SECMON_TELEGRAM_BOT_TOKEN=
SECMON_TELEGRAM_CHAT_ID=
SECMON_TELEGRAM_TIMEOUT_SECONDS=5
SECMON_TELEGRAM_MIN_SEVERITY=3
SECMON_TELEGRAM_COOLDOWN_SECONDS=60
```

真實 Token 只能放在：

```text
/etc/secmon/secmon.env
```

檔案權限建議：

```bash
sudo install -d -m 0750 /etc/secmon
sudo touch /etc/secmon/secmon.env
sudo chmod 600 /etc/secmon/secmon.env
```

## 10. 自動化測試

新增至少：

```text
tests/test_collector_main.py
tests/test_telegram_notifier.py
tests/test_collector_telegram.py
```

測試不得連線至真正 Telegram。

必須驗證：

### Production Loop

- 多輪執行。
- interval env parsing。
- invalid interval。
- minimum interval。
- log path env。
- SIGTERM／SIGINT。
- stop event。
- 可恢復錯誤後繼續。
- 初始化失敗非零退出。
- 不會 busy spin。

### Telegram Client

- disabled 不發送。
- Telegram `ok=true`／`ok=false`。
- HTTP 400／401／429／500。
- timeout。
- malformed JSON。
- Token 不出現在 log。
- Chat ID 負數可用。
- 超長訊息截斷。

### Collector Integration

- 新事件成功後通知。
- replay 不重複通知。
- Telegram 失敗不 rollback DB。
- Telegram 失敗不影響 cursor。
- IPv4／IPv6 顯示。
- batch aggregation。
- cooldown。
- raw log 不出現在訊息。

允許注入 HTTP transport、sleep function、clock、stop event、collector factory、notifier。不得在 unit tests 中真正 sleep 或呼叫 Telegram。

## 11. 驗證命令

```bash
python -m compileall -q backend scripts tests
ruff check backend tests scripts
mypy backend
pytest -q
PATH="$PWD/.venv/bin:$PATH" make check
```

### Fake Production Smoke

```bash
export SECMON_DATABASE_PATH=/tmp/secmon-tg.db
export SECMON_SSH_CURSOR_PATH=/tmp/secmon-tg.cursor
export SECMON_SSH_LOG_PATH=tests/fixtures/ssh_failure.log
export SECMON_COLLECT_INTERVAL_SECONDS=2
export SECMON_TELEGRAM_ENABLED=false

rm -f "$SECMON_DATABASE_PATH" "$SECMON_SSH_CURSOR_PATH"

python database/migrate.py --database "$SECMON_DATABASE_PATH"

timeout 8s .venv/bin/python -m backend.collectors.main
```

必須看到多輪執行，第二輪應為：

```text
new_events=0
new_attackers=0
```

### 真實 Telegram Smoke

只有在 `/etc/secmon/secmon.env` 已由使用者安全填入 Token 後才可執行：

```bash
set -a
source /etc/secmon/secmon.env
set +a

.venv/bin/python -m backend.notifiers.telegram --test
```

輸出不得包含 Token。

## 12. Git 與安全規則

禁止：

```bash
git add .
git reset --hard
git clean -fd
```

不得提交：

- 真實 Token
- `.env`
- SQLite DB
- cursor
- logs
- Telegram API response dump
- sandbox state
- AGY 原始報告修改
- 原本未知工作樹檔案

每次 commit 前執行：

```bash
git diff --check
git diff --cached --name-only
git status --short
```

## 13. 建議 Commit 拆分

```text
feat(p1): add production SSH collector loop
feat(p1): add Telegram notification client
feat(p1): send aggregated SSH attack alerts
test(p1): cover collector and Telegram behavior
docs(p1): document secure Telegram configuration
```

完成後：

```bash
git diff --check
git status --short
git log --oneline 645388e..HEAD
git push origin main
```

## 14. 最終回報格式

```text
Base HEAD：
New HEAD：
Commits：
Changed files：

Production loop：
Signal handling：
Polling interval：
Systemd：

Telegram client：
Telegram Chat ID：8350114645
Token protection：
Aggregation：
Cooldown：
Failure behavior：
Replay notification：

compileall：
Ruff：
mypy：
pytest：
make check：
Fake production smoke：
Real Telegram smoke：
Telegram message ID：

AGY reports unchanged：
Unknown files excluded：
Push status：

Ready for AGY Telegram verification：YES / NO
30-second ingestion：PASS / NOT VERIFIED
P1 Release Gate：NOT PASSED
```

## 15. 驗收原則

只有符合以下條件，才可回報 Ready for AGY Telegram verification：

```text
[ ] Production loop 可常駐執行
[ ] systemd entry point 存在
[ ] Telegram disabled 無網路請求
[ ] Telegram Token 未進入 Git 或 log
[ ] 新事件聚合通知
[ ] replay 不重發
[ ] Telegram 失敗不影響 DB 與 cursor
[ ] compileall PASS
[ ] Ruff PASS
[ ] mypy PASS
[ ] pytest PASS
[ ] make check PASS
[ ] Fake production smoke PASS
[ ] commits 已拆分並 push
[ ] AGY 報告未修改
```

即使 Telegram 功能與程式回歸通過，只要真實主機 30 秒端到端入庫尚未驗證，狀態仍為：

```text
Telegram Gate：待 AGY 驗證
30-second Ingestion：NOT VERIFIED
P1 Release Gate：NOT PASSED
Issue #2：OPEN
```
