# AITools / md

此目錄用於保存 Codex 對 AI Tools 相關工作的 Markdown 回報與審查紀錄。

## Codex 回報規則

- 所有回報寫入此目錄：`AITools/md/`
- 檔案格式：Markdown (`.md`)
- 建議命名：`YYYYMMDD-<topic>-report.md`
- 每份報告至少包含：
  - 任務目標
  - 執行環境 / 版本
  - 實際操作
  - 測試與量測結果
  - 問題 / 風險
  - 結論
  - 最終服務狀態 / rollback 狀態（若適用）
- 僅記錄實測與可驗證結果；推論需明確標示為推論。
- 若任務要求回復原服務或設定，報告中必須附上最終確認結果。

## 目前用途

用於 Muse / llama.cpp RPC / model-switcher / DFlash / Hermes / Codex 等 AI Tools 相關診斷與 production qualification 回報。
