# Gemini Market Flow Analyzer：圖片 / CSV 分流與 Google API Key 用途邊界

> 建立日期：2026-06-22  
> 修正重點：圖片與 CSV 先分流，再分成「基金」與「股市」兩大類。  
> Google API Key 用途：Gemini 僅用於圖片 / CSV 的摘要、分類、欄位辨識與資料歸類。  
> 不使用範圍：不產生完整投資分析報告、不做風險判斷、不輸出操作建議。  
> 適用工具：AGY / Antigravity / Codex CLI。

---

## 1. 最終用途邊界

Google API Key 需要使用，但用途限定在：

1. 判斷輸入檔案是圖片或 CSV。
2. 判斷資料屬於「基金」或「股市」。
3. 對圖片做 Gemini Vision 摘要與欄位辨識。
4. 對 CSV 做欄位摘要與類別判斷。
5. 產生 structured JSON，供 Python / SQLite 使用。

Gemini 不負責：

- 投資風險判斷
- 操作建議
- 買賣建議
- 完整投資分析報告
- 取代 Python 計算
- 取代 SQLite 儲存

---

## 2. 新資料入口分類

資料來源先依檔案型態分成：

```text
input_files
├── images
│   ├── fund_images
│   └── stock_images
└── csv
    ├── fund_csv
    └── stock_csv
```

再依內容分成：

| 類別 | 說明 |
|---|---|
| fund | 基金、ETF、帳戶總覽、申購、持倉、淨值、報酬率 |
| stock | 股市、三大法人、現貨、期貨、台指、券商報表、市場資料 |
| unknown | Gemini 無法可靠判斷時，不硬分類 |

---

## 3. 建議目錄結構

```text
data/
├── raw/
│   ├── inbox/
│   │   ├── images/
│   │   └── csv/
│   ├── funds/
│   │   ├── images/
│   │   └── csv/
│   └── stocks/
│       ├── images/
│       └── csv/
├── processed/
│   ├── classified_files.jsonl
│   └── market_flow.sqlite
└── rejected/
    └── unknown/
```

---

## 4. 新增資料表

```sql
CREATE TABLE IF NOT EXISTS source_file_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_type TEXT NOT NULL,
    domain TEXT NOT NULL,
    source_label TEXT,
    summary TEXT,
    classification_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| file_path | 原始檔案路徑 |
| file_type | image / csv |
| domain | fund / stock / unknown |
| source_label | Gemini 判斷出的資料來源標籤 |
| summary | Gemini 產生的短摘要 |
| classification_json | Gemini 回傳的完整分類 JSON |

---

## 5. Gemini 輸出 JSON 規格

Gemini 只輸出分類 JSON：

```json
{
  "file_type": "image",
  "domain": "fund",
  "source_label": "fund_account_overview",
  "summary": "這是一張基金帳戶總覽圖片，包含基金名稱、持有金額與報酬率欄位。",
  "detected_fields": ["fund_name", "market_value", "return_rate"],
  "confidence": 0.86,
  "needs_manual_review": false
}
```

允許的 `domain`：

```text
fund
stock
unknown
```

允許的 `file_type`：

```text
image
csv
unknown
```

禁止 Gemini 輸出：

- buy
- sell
- hold
- action_suggestion
- risk_score
- risk_notes
- bullish / bearish recommendation
- 操作建議
- 風險判斷

---

## 6. 建議新增模組

```text
src/ai/gemini_file_classifier.py
scripts/classify_input_files.py
scripts/move_classified_files.py
```

### `src/ai/gemini_file_classifier.py`

用途：

- 使用 `GEMINI_API_KEY`。
- 接收圖片或 CSV 的內容摘要。
- 呼叫 Gemini 做檔案分類。
- 回傳固定 JSON。

### `scripts/classify_input_files.py`

用途：

- 掃描 `data/raw/inbox/images` 與 `data/raw/inbox/csv`。
- 圖片送 Gemini Vision 判斷。
- CSV 讀取檔名、表頭、前幾列，再送 Gemini 判斷。
- 將結果寫入 `source_file_registry`。

### `scripts/move_classified_files.py`

用途：

- 依照 `domain` 與 `file_type` 移動檔案。
- fund + image → `data/raw/funds/images/`
- fund + csv → `data/raw/funds/csv/`
- stock + image → `data/raw/stocks/images/`
- stock + csv → `data/raw/stocks/csv/`
- unknown → `data/rejected/unknown/`

---

## 7. CSV 與圖片處理原則

### CSV

CSV 的數值解析仍由 Python 負責。

Gemini 只做：

- 判斷資料類型
- 摘要欄位用途
- 分類為 fund / stock / unknown
- 回傳欄位對應建議

### 圖片

圖片需要使用 Google API Key，因為要用 Gemini Vision 做：

- 畫面文字摘要
- 表格欄位辨識
- 判斷是基金還是股市資料
- 標示是否需要人工複核

若圖片包含敏感資訊，建議先人工遮蔽帳號、身分證、完整交易帳號。

---

## 8. AGY 執行指令

```text
請修正 Gemini Market Flow Analyzer 的資料入口與 Google API Key 用途。

新的原則：
Google API Key 需要使用，但只用於圖片 / CSV 的摘要、分類、欄位辨識與資料歸類。
不使用 Gemini 產生完整投資分析報告，不做風險判斷，不給操作建議。

請執行：

1. 新增資料夾：
   - data/raw/inbox/images
   - data/raw/inbox/csv
   - data/raw/funds/images
   - data/raw/funds/csv
   - data/raw/stocks/images
   - data/raw/stocks/csv
   - data/rejected/unknown

2. 新增或更新 SQLite schema，加入 source_file_registry。

3. 新增 src/ai/gemini_file_classifier.py：
   - 從 .env 讀取 GEMINI_API_KEY
   - 支援 image / csv 分類
   - 輸出固定 JSON
   - domain 僅允許 fund / stock / unknown

4. 新增 scripts/classify_input_files.py：
   - 掃描 inbox images / csv
   - 圖片使用 Gemini Vision
   - CSV 使用檔名、表頭、前幾列做分類
   - 結果寫入 source_file_registry

5. 新增 scripts/move_classified_files.py：
   - 依 classification 結果移動檔案
   - unknown 放入 data/rejected/unknown

6. 移除或停止使用 Gemini 的：
   - action_suggestion
   - risk_notes
   - market_view
   - buy / sell / hold

7. 執行測試：
   python scripts/init_market_flow_db.py
   python scripts/classify_input_files.py
   python scripts/move_classified_files.py

8. 回報：
   - changed files
   - commit SHA
   - commands executed
   - 一筆 fund image 或 fund csv 的 classification_json 範例
   - 一筆 stock image 或 stock csv 的 classification_json 範例
```

---

## 9. 執行流程

```text
圖片 / CSV 放入 inbox
        ↓
classify_input_files.py
        ↓
Gemini 摘要與分類
        ↓
source_file_registry
        ↓
move_classified_files.py
        ↓
funds / stocks / unknown
        ↓
後續 Python 匯入 SQLite
```

---

## 10. 結論

Google API Key 在此專案中需要使用，但只作為 Gemini 分類器：

```text
圖片與 CSV → Gemini 摘要 / 分類 → fund / stock / unknown → Python 後續處理
```

Gemini 不是投資分析器，也不是操作建議器。它只負責把輸入檔案整理成可被程式處理的分類結果。
