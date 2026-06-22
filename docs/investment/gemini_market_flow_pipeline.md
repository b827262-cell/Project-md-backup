# Gemini API Key 整理基金與三大法人現貨／期貨資料執行方案

> 建立日期：2026-06-22  
> 目標：把基金帳戶資料、三大法人現貨、期貨籌碼資料整理成可查詢資料庫，並用 Google Gemini API 產出每日籌碼與資產配置分析。  
> 建議執行角色：AGY / Antigravity / Codex CLI 皆可執行。  
> 重要原則：Gemini 只做「摘要、分類、風險判斷、報告產出」，不要讓 Gemini 直接負責原始數字計算。

---

## 1. 核心結論

這個功能應採用四層架構：

```text
基金 CSV / 三大法人現貨 / 期貨資料
        ↓
Python 清洗與計算
        ↓
SQLite 儲存每日 snapshot
        ↓
Gemini API 做摘要、分類、風險判斷
        ↓
ai_daily_analysis + reports/daily/YYYY-MM-DD.md
```

原因：

1. **數值計算要可重現**：基金市值、成本、損益、法人買賣超、期貨淨口數要由 Python/SQLite 計算。
2. **AI 不應當資料庫**：Gemini 適合整理文字、判斷多空邏輯、產出報告，不適合當唯一的數值來源。
3. **避免幻覺**：所有餵給 Gemini 的資料必須是已整理後的 JSON snapshot。
4. **方便回測與追蹤**：每日輸出都寫入 SQLite，可比對過去 AI 判斷與後續盤勢。

---

## 2. 建議目錄結構

```text
Anti-G-C1/
├── .env
├── .gitignore
├── data/
│   ├── raw/
│   │   ├── funds/
│   │   ├── twse/
│   │   └── taifex/
│   └── processed/
│       └── market_flow.sqlite
├── reports/
│   └── daily/
│       └── 2026-06-17.md
├── scripts/
│   ├── init_market_flow_db.py
│   ├── import_funds.py
│   ├── import_twse_t86.py
│   ├── import_taifex_futures.py
│   └── analyze_daily.py
└── src/
    └── ai/
        └── gemini_analyzer.py
```

---

## 3. 金鑰設定

### `.env`

```bash
GEMINI_API_KEY=你的_google_api_key
GEMINI_MODEL=gemini-3.1-flash-lite
```

### `.gitignore`

```gitignore
.env
*.sqlite
*.db
__pycache__/
.venv/
reports/daily/*.tmp
```

注意：

- `.env` 不可 commit。
- API Key 不要寫死在 Python、Bash、Markdown 或 GitHub issue。
- 若使用 AGY、Codex、Claude Code，請確認執行環境可以讀到 `.env`。

---

## 4. SQLite Schema

建立 `scripts/init_market_flow_db.py`：

```python
from pathlib import Path
import sqlite3

DB_PATH = Path("data/processed/market_flow.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS fund_position (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    category TEXT,
    market_value REAL,
    cost REAL,
    unrealized_pnl REAL,
    return_rate REAL,
    weight REAL,
    source_file TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fund_position_date
ON fund_position(trade_date);

CREATE TABLE IF NOT EXISTS institutional_spot (
    trade_date TEXT PRIMARY KEY,
    foreign_net_buy REAL,
    investment_trust_net_buy REAL,
    dealer_net_buy REAL,
    total_net_buy REAL,
    raw_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS institutional_futures (
    trade_date TEXT PRIMARY KEY,
    foreign_net_lot INTEGER,
    investment_trust_net_lot INTEGER,
    dealer_net_lot INTEGER,
    foreign_open_interest INTEGER,
    raw_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_daily_analysis (
    trade_date TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    input_hash TEXT,
    analysis_json TEXT NOT NULL,
    report_md TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
    print(f"✅ initialized database: {DB_PATH}")


if __name__ == "__main__":
    main()
```

執行：

```bash
python scripts/init_market_flow_db.py
```

---

## 5. Gemini 分析器

建立 `src/ai/gemini_analyzer.py`：

```python
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError("找不到 GEMINI_API_KEY，請確認 .env 是否存在")

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_market_flow(payload: dict) -> dict:
    prompt = f"""
你是台股法人籌碼與基金配置分析助理。

請根據以下資料，輸出 JSON，不要輸出 Markdown。

請輸出欄位：
- market_view: 今日整體多空判斷
- spot_summary: 三大法人現貨方向
- futures_summary: 期貨多空方向
- divergence: 現貨與期貨是否背離
- fund_allocation_view: 基金配置是否偏科技、偏成長、偏防禦
- action_suggestion: 今日操作建議
- risk_notes: 風險提醒；資料不足也要說明
- confidence_score: 0 到 100 的信心分數

規則：
1. 不得編造不存在的數字。
2. 若資料為 null 或缺漏，請明確說明。
3. 操作建議應分成「保守、一般、積極」三種情境。
4. 不做保證獲利語氣。

資料：
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    return json.loads(response.text)
```

安裝套件：

```bash
pip install google-genai python-dotenv
```

---

## 6. 每日分析腳本

建立 `scripts/analyze_daily.py`：

```python
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from src.ai.gemini_analyzer import GEMINI_MODEL, analyze_market_flow

DB_PATH = Path("data/processed/market_flow.sqlite")
REPORT_DIR = Path("reports/daily")


def fetch_daily_payload(conn: sqlite3.Connection, trade_date: str) -> dict:
    conn.row_factory = sqlite3.Row

    spot = conn.execute(
        "SELECT * FROM institutional_spot WHERE trade_date = ?",
        (trade_date,),
    ).fetchone()

    futures = conn.execute(
        "SELECT * FROM institutional_futures WHERE trade_date = ?",
        (trade_date,),
    ).fetchone()

    funds = conn.execute(
        """
        SELECT fund_name, category, market_value, cost, unrealized_pnl, return_rate, weight
        FROM fund_position
        WHERE trade_date = ?
        ORDER BY weight DESC
        """,
        (trade_date,),
    ).fetchall()

    return {
        "trade_date": trade_date,
        "spot": dict(spot) if spot else None,
        "futures": dict(futures) if futures else None,
        "funds": [dict(row) for row in funds],
    }


def render_markdown(trade_date: str, analysis: dict) -> str:
    return f"""# {trade_date} 三大法人與基金配置分析

## 市場方向

{analysis.get("market_view", "無資料")}

## 現貨籌碼

{analysis.get("spot_summary", "無資料")}

## 期貨籌碼

{analysis.get("futures_summary", "無資料")}

## 現貨／期貨背離

{analysis.get("divergence", "無資料")}

## 基金配置判斷

{analysis.get("fund_allocation_view", "無資料")}

## 操作建議

{analysis.get("action_suggestion", "無資料")}

## 風險提醒

{analysis.get("risk_notes", "無資料")}

## 信心分數

{analysis.get("confidence_score", "無資料")}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="交易日，例如 2026-06-17")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        payload = fetch_daily_payload(conn, args.date)
        input_text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        input_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()

        analysis = analyze_market_flow(payload)
        report_md = render_markdown(args.date, analysis)

        conn.execute(
            """
            INSERT OR REPLACE INTO ai_daily_analysis
            (trade_date, model, input_hash, analysis_json, report_md)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                args.date,
                GEMINI_MODEL,
                input_hash,
                json.dumps(analysis, ensure_ascii=False),
                report_md,
            ),
        )

    report_path = REPORT_DIR / f"{args.date}.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"✅ 已產生分析報告：{report_path}")


if __name__ == "__main__":
    main()
```

執行：

```bash
python scripts/analyze_daily.py --date 2026-06-17
```

---

## 7. Bash Gemini CLI 接入 `/analyze` 指令

可在現有 Gemini CLI 主循環中加入：

```bash
if [[ "$USER_INPUT" =~ ^/analyze[[:space:]]+([0-9]{4}-[0-9]{2}-[0-9]{2})$ ]]; then
    TARGET_DATE="${BASH_REMATCH[1]}"
    echo -e "\033[1;33mi\033[0m 正在分析 $TARGET_DATE 的基金與三大法人資料..."
    python scripts/analyze_daily.py --date "$TARGET_DATE"
    continue
fi
```

使用：

```bash
/analyze 2026-06-17
```

---

## 8. 建議資料匯入順序

### Step 1：初始化資料庫

```bash
python scripts/init_market_flow_db.py
```

### Step 2：匯入基金資料

```bash
python scripts/import_funds.py --date 2026-06-17 --file "data/raw/funds/account.csv"
```

### Step 3：匯入三大法人現貨資料

```bash
python scripts/import_twse_t86.py --date 2026-06-17 --file "data/raw/twse/t86_20260617.csv"
```

### Step 4：匯入期貨資料

```bash
python scripts/import_taifex_futures.py --date 2026-06-17 --file "data/raw/taifex/futures_20260617.csv"
```

### Step 5：產出 AI 分析

```bash
python scripts/analyze_daily.py --date 2026-06-17
```

---

## 9. AGY 執行指令

可直接貼給 AGY / Antigravity：

```text
請在目前專案中新增「Gemini API 整理基金與三大法人現貨／期貨資料」功能。

請依照以下規格執行：

1. 建立目錄：
   - data/raw/funds
   - data/raw/twse
   - data/raw/taifex
   - data/processed
   - reports/daily
   - scripts
   - src/ai

2. 新增 .gitignore 規則：
   - .env
   - *.sqlite
   - *.db
   - __pycache__/
   - .venv/

3. 新增 scripts/init_market_flow_db.py：
   - 建立 SQLite：data/processed/market_flow.sqlite
   - 建立 fund_position、institutional_spot、institutional_futures、ai_daily_analysis 四張表

4. 新增 src/ai/gemini_analyzer.py：
   - 從 .env 載入 GEMINI_API_KEY
   - GEMINI_MODEL 預設 gemini-3.1-flash-lite
   - 使用 google-genai
   - analyze_market_flow(payload: dict) 回傳 JSON dict
   - Gemini 只做摘要、分類、風險判斷，不負責原始數字計算

5. 新增 scripts/analyze_daily.py：
   - 讀取 SQLite 中指定 trade_date 的基金、現貨、期貨資料
   - 組成 payload
   - 呼叫 analyze_market_flow
   - 將結果寫入 ai_daily_analysis
   - 產生 reports/daily/YYYY-MM-DD.md

6. 若專案已有 Bash Gemini CLI，請加入 /analyze YYYY-MM-DD 指令，呼叫：
   python scripts/analyze_daily.py --date YYYY-MM-DD

7. 請不要把 .env 或 API Key commit。

8. 完成後請執行：
   python scripts/init_market_flow_db.py
   python scripts/analyze_daily.py --date 2026-06-17

9. 若沒有資料，analyze_daily.py 應該仍可產生「資料不足」報告，不可崩潰。

10. 完成後請輸出：
    - changed files
    - commit SHA
    - 測試結果
```

---

## 10. 驗收標準

完成後應符合：

- [ ] `.env` 不在 Git 追蹤內。
- [ ] `python scripts/init_market_flow_db.py` 可成功建立 SQLite。
- [ ] `python scripts/analyze_daily.py --date YYYY-MM-DD` 可成功執行。
- [ ] 若資料不足，仍會產出 Markdown 報告。
- [ ] `ai_daily_analysis` 會保存 Gemini JSON 與 Markdown 報告。
- [ ] `reports/daily/YYYY-MM-DD.md` 會產出可閱讀報告。
- [ ] Gemini 不直接負責原始數值計算。
- [ ] 所有投資結論都有風險提醒，不使用保證獲利語氣。

---

## 11. 後續可擴充方向

1. **三大法人趨勢分數**  
   加入近 5 日、20 日累積買賣超。

2. **期貨多空轉折偵測**  
   外資期貨淨空單快速增加時標記風險。

3. **基金集中度偵測**  
   自動判斷科技、AI、半導體、美股集中度。

4. **每日 Telegram 通知**  
   將 `reports/daily/YYYY-MM-DD.md` 摘要推送到 Telegram。

5. **回測 AI 判斷**  
   比對 Gemini 每日多空判斷與後續台指／加權指數表現。

---

## 12. 最重要的設計邊界

這套功能不是要讓 Gemini 變成投資神諭，而是讓它成為：

```text
已驗證數據 → 結構化判斷 → 風險提醒 → 可追蹤日報
```

因此，正確分工是：

- Python：抓資料、清洗、計算、驗證。
- SQLite：保存每日狀態與分析紀錄。
- Gemini：摘要、解釋、分類、產出報告。
- AGY/Codex：落地檔案、執行測試、commit/push。
