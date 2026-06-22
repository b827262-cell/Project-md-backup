# Gemini Market Flow Analyzer：AGY 第二階段 Seed 測試與驗收計畫

> 建立日期：2026-06-22  
> 文件用途：軟體功能驗收與測試資料設計。  
> 適用工具：AGY / Antigravity / Codex CLI。  
> 注意：本文件只描述資料管線與 AI 報告產生測試，不構成任何投資建議。

---

## 1. 第一階段測試結果

已執行：

```bash
python scripts/analyze_daily.py --date 2026-06-18
```

測試時，`market_flow.sqlite` 內 2026-06-18 的現貨、期貨與基金資料皆為空。Gemini Analyzer 正確產生「資料不足」報告，沒有自行補出不存在的法人數字或部位資料，信心分數為 0。

這代表第一階段通過：

```text
資料庫為空
    ↓
payload 為 null 或空陣列
    ↓
Gemini 不編造數字
    ↓
報告標示資料不足
    ↓
信心分數 = 0
```

---

## 2. 第二階段目標

第二階段要驗證：當 SQLite 內存在可控的 seed 測試資料時，`scripts/analyze_daily.py` 是否能：

1. 正確讀取 `institutional_spot`。
2. 正確讀取 `institutional_futures`。
3. 正確讀取 `fund_position`。
4. 組成 payload 並送入 Gemini Analyzer。
5. 產生 `reports/daily/2026-06-18.md`。
6. 在報告中標示資料來源為 sample / seed，不把測試資料誤認成正式市場資料。

---

## 3. 建議新增檔案

```text
scripts/seed_market_flow_sample.py
```

用途：寫入一筆可重複執行的 2026-06-18 seed 測試資料。

---

## 4. Seed 測試資料

### institutional_spot

| 欄位 | 測試值 |
|---|---:|
| trade_date | 2026-06-18 |
| foreign_net_buy | -120.5 |
| investment_trust_net_buy | 35.2 |
| dealer_net_buy | -18.7 |
| total_net_buy | -104.0 |

### institutional_futures

| 欄位 | 測試值 |
|---|---:|
| trade_date | 2026-06-18 |
| foreign_net_lot | -8500 |
| investment_trust_net_lot | 1200 |
| dealer_net_lot | 900 |
| foreign_open_interest | -32000 |

### fund_position

| fund_name | category | weight | return_rate |
|---|---|---:|---:|
| 國泰全球品牌50 | 全球科技成長 | 35 | 8.2 |
| 凱基全球菁英55 | 全球半導體科技 | 25 | 6.5 |
| 中信全球高股息 | 高股息防禦 | 15 | 2.1 |

---

## 5. AGY 執行指令

```text
請在目前專案中新增 Gemini Market Flow Analyzer 第二階段 seed 驗收測試。

任務目標：
驗證 scripts/analyze_daily.py 在 SQLite 有測試資料時，是否能成功產出 Markdown 分析報告，並確認 Gemini Analyzer 不會把 sample data 誤判成正式資料來源。

請執行以下工作：

1. 新增 scripts/seed_market_flow_sample.py。

2. seed script 寫入 2026-06-18 測試資料：

institutional_spot：
- trade_date = 2026-06-18
- foreign_net_buy = -120.5
- investment_trust_net_buy = 35.2
- dealer_net_buy = -18.7
- total_net_buy = -104.0
- raw_json 請標示 source=sample_seed, unit=億元

institutional_futures：
- trade_date = 2026-06-18
- foreign_net_lot = -8500
- investment_trust_net_lot = 1200
- dealer_net_lot = 900
- foreign_open_interest = -32000
- raw_json 請標示 source=sample_seed, unit=口

fund_position：
- 國泰全球品牌50，category=全球科技成長，weight=35，return_rate=8.2，source_file=sample_seed
- 凱基全球菁英55，category=全球半導體科技，weight=25，return_rate=6.5，source_file=sample_seed
- 中信全球高股息，category=高股息防禦，weight=15，return_rate=2.1，source_file=sample_seed

3. seed script 必須可重複執行：
   - institutional_spot 使用 INSERT OR REPLACE
   - institutional_futures 使用 INSERT OR REPLACE
   - fund_position 先刪除同 trade_date 的 sample 資料，再重新 insert

4. 執行：
   python scripts/init_market_flow_db.py
   python scripts/seed_market_flow_sample.py
   python scripts/analyze_daily.py --date 2026-06-18

5. 驗證：
   - reports/daily/2026-06-18.md 有產生
   - ai_daily_analysis 有寫入 2026-06-18
   - 報告中有說明此資料來自 sample seed
   - 報告保持風險揭露，不出現保證性語氣

6. 完成後 commit 並 push 到目前分支。

7. 回報：
   - changed files
   - commit SHA
   - 執行過的 commands
   - 測試結果摘要
```

---

## 6. seed script 範例

```python
from pathlib import Path
import json
import sqlite3

DB_PATH = Path("data/processed/market_flow.sqlite")
TRADE_DATE = "2026-06-18"


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"找不到資料庫：{DB_PATH}，請先執行 scripts/init_market_flow_db.py")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO institutional_spot
            (trade_date, foreign_net_buy, investment_trust_net_buy, dealer_net_buy, total_net_buy, raw_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                TRADE_DATE,
                -120.5,
                35.2,
                -18.7,
                -104.0,
                json.dumps({"source": "sample_seed", "unit": "億元"}, ensure_ascii=False),
            ),
        )

        conn.execute(
            """
            INSERT OR REPLACE INTO institutional_futures
            (trade_date, foreign_net_lot, investment_trust_net_lot, dealer_net_lot, foreign_open_interest, raw_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                TRADE_DATE,
                -8500,
                1200,
                900,
                -32000,
                json.dumps({"source": "sample_seed", "unit": "口"}, ensure_ascii=False),
            ),
        )

        conn.execute(
            "DELETE FROM fund_position WHERE trade_date = ? AND source_file = ?",
            (TRADE_DATE, "sample_seed"),
        )

        funds = [
            (TRADE_DATE, "國泰全球品牌50", "全球科技成長", 35.0, 8.2, "sample_seed"),
            (TRADE_DATE, "凱基全球菁英55", "全球半導體科技", 25.0, 6.5, "sample_seed"),
            (TRADE_DATE, "中信全球高股息", "高股息防禦", 15.0, 2.1, "sample_seed"),
        ]

        conn.executemany(
            """
            INSERT INTO fund_position
            (trade_date, fund_name, category, weight, return_rate, source_file)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            funds,
        )

    print(f"✅ seeded sample market flow data for {TRADE_DATE}")


if __name__ == "__main__":
    main()
```

---

## 7. 驗收指令

```bash
python scripts/init_market_flow_db.py
python scripts/seed_market_flow_sample.py
python scripts/analyze_daily.py --date 2026-06-18
cat reports/daily/2026-06-18.md
```

SQLite 檢查：

```bash
sqlite3 data/processed/market_flow.sqlite \
"SELECT * FROM institutional_spot WHERE trade_date='2026-06-18';"

sqlite3 data/processed/market_flow.sqlite \
"SELECT * FROM institutional_futures WHERE trade_date='2026-06-18';"

sqlite3 data/processed/market_flow.sqlite \
"SELECT fund_name, category, weight, return_rate FROM fund_position WHERE trade_date='2026-06-18';"
```

---

## 8. 第二階段驗收標準

| 驗收項目 | 標準 |
|---|---|
| seed script 可執行 | `python scripts/seed_market_flow_sample.py` 成功 |
| 可重複執行 | 重跑 seed 不會重複污染資料 |
| SQLite 有資料 | 三張表均有 2026-06-18 資料 |
| analyze_daily 可執行 | 成功產生報告 |
| Markdown 報告存在 | `reports/daily/2026-06-18.md` 存在 |
| sample data 標示 | 報告或 payload 明確標示測試資料來源 |
| 無保證性語氣 | 報告保持風險揭露 |
| GitHub 已更新 | commit 並 push 成功 |

---

## 9. 分支命名建議

目前曾 push 到：

```text
codex/tw-legal-flow-dashboard
```

建議後續另開投資資料分析專用分支：

```bash
git checkout -b codex/gemini-market-flow-analysis
```

或：

```bash
git checkout -b codex/market-flow-gemini-analyzer
```

---

## 10. 第三階段方向

第二階段通過後，再接真實資料源：

1. 基金 CSV 匯入。
2. TWSE 三大法人資料匯入。
3. TAIFEX 期貨資料匯入。
4. 加入 5 日、20 日趨勢欄位。
5. 建立每日自動報告。
6. 建立歷史報告留存與回測欄位。

---

## 11. 結論

第一階段已證明：

```text
資料不足時，Gemini Analyzer 不亂猜。
```

第二階段要證明：

```text
有 seed 測試資料時，Gemini Analyzer 能產出穩定、可追蹤、具風險揭露的報告。
```

整體資料管線應維持：

```text
資料 → 計算 → 結構化 payload → AI 解釋 → Markdown 報告 → GitHub 留痕
```
