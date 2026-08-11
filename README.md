# Project-md-backup

專用紀錄 repo，只放 MD；各專案程式碼與設計文件分開保存，降低互相覆蓋風險。

## 專案文件索引

### LLM 本地部署 / 除錯紀錄

llama.cpp 多 GPU（本機 CUDA + 遠端 RPC）部署問題的診斷過程。

- [GLM-4.7-Flash 載入失敗診斷（RTX 3060 + RPC RTX 5060）](reports/glm47-flash-vram-oom-process-20260811.md) — MLA 架構 KV cache OOM 與 RPC compute buffer 配置失敗
- [GLM-4.7-Flash 32K／40960／60:40 與 KV 量化追蹤測試](reports/glm47-flash-followup-tests-20260812.md) — 更正 RPC0 容量判讀，記錄 context 與 split probes，審驗 q8_0 + Flash Attention 路徑

### SecMon Linux Security Monitor

Linux 資安偵測、攻擊 IP 彙整、SQLite、Suricata、CrowdSec 與 nftables 的公司落地 MVP 設計。

- [SecMon 專案 README](secmon-linux-security/README.md)
- [系統架構與前後台功能設計](secmon-linux-security/docs/ARCHITECTURE_AND_UI.md)
- [SQLite 資料庫設計](secmon-linux-security/docs/DATABASE_DESIGN.md)
- [MVP 實作與部署計畫](secmon-linux-security/docs/MVP_IMPLEMENTATION.md)
