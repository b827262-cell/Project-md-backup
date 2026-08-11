# GLM-4.7-Flash 載入失敗診斷紀錄（RTX 3060 + RPC RTX 5060）

**日期**：2026-08-11
**狀態**：**已解決** — GLM-4.7-Flash 成功載入並於 port 8081 服務中，但 RPC0 側 headroom 偏緊（316 MiB），列為後續觀察項目
**環境**：E500-G9-WS760T（RTX 3060 12GB）+ TUF A16（RTX 5060 Laptop 8GB，經 ggml-rpc）

---

## 摘要

GLM-4.7-Flash IQ4_XS 在 llama.cpp 上無法載入。診斷後確認**兩個獨立、依序出現的失敗點**：

1. **CUDA0（本機 RTX 3060）KV cache OOM** — 已解決（降 context 至 32768）
2. **RPC0（遠端 RTX 5060）compute buffer 配置失敗** — 已解決（降 batch size 至 `-b 512 -ub 128`），
   **且已證實非 VRAM 容量問題**（失敗當下 RPC0 實際有 7490 MiB 空閒）

修復後 GLM-4.7-Flash 已成功載入並通過 `/v1/models` 驗證，唯 RPC0 實際 headroom 僅剩 316 MiB，
低於安全警戒線，列為後續觀察項目（見「載入後的實際 headroom」一節）。

---

## 環境

| 項目 | 值 |
|---|---|
| 本機 | `b827262@b827262-E500-G9-WS760T` |
| 本機 GPU | NVIDIA GeForce RTX 3060，12288 MiB（idle free 約 11896 MiB）|
| 遠端 | `b822726@b822726-NB-TUFA16`（`10.0.3.67` / Tailscale `100.70.207.69`）|
| 遠端 GPU | NVIDIA GeForce RTX 5060 Laptop GPU，8151 MiB |
| RPC endpoint | `10.0.3.67:50053` |
| 模型檔 | `/home/b827262/project/Qwen36llm/GLM-4.7-Flash/zai-org_GLM-4.7-Flash-IQ4_XS.gguf`（16250044288 bytes）|
| 切換工具 | `Qwen36llm/model-switcher/model-switcher.sh` + `profiles/*.conf` |

遠端有**兩個** rpc-server 共用同一張 RTX 5060：

```
b822726  1073403  ggml-rpc-server --host 10.0.3.67 --port 50052 --device CUDA0 --cache
b822726  1073680  ggml-rpc-server -H 0.0.0.0 -p 50053 -c
```

`50052` 供 Qwen36 使用，`50053` 供 Muse / GLM 使用。兩者合計僅佔 258 MiB，未互相排擠。

---

## 問題一：CUDA0 KV cache OOM（已解決）

### 失敗現象

`logs/3-glm47-20260811-214057.log`（21:40）與 `logs/3-glm47-20260811-224957.log`（22:49）失敗模式完全相同：

```
E ggml_backend_cuda_buffer_type_alloc_buffer: allocating 4176.00 MiB on device 0: cudaMalloc failed: out of memory
E alloc_tensor_range: failed to allocate CUDA0 buffer of size 4378853376
E llama_init_from_model: failed to initialize the context: failed to allocate buffer for kv cache
E srv    load_model: failed to create_context with model '.../zai-org_GLM-4.7-Flash-IQ4_XS.gguf'
```

### 根因

從 GGUF metadata 讀出的架構參數：

```
general.architecture              = deepseek2
deepseek2.block_count             = 47
deepseek2.attention.head_count    = 20
deepseek2.attention.head_count_kv = 1
deepseek2.attention.key_length    = 576
deepseek2.attention.value_length  = 512
deepseek2.attention.key_length_mla   = 256
deepseek2.attention.value_length_mla = 256
deepseek2.expert_count            = 64
```

GLM-4.7-Flash 是 **deepseek2 / MLA** 架構。MLA 使用 **k-only** 的統一 KV cache：

```
576 × 2 bytes（f16）× 131072 ctx = 144 MiB / layer
```

在 `TENSOR_SPLIT="59,41"` 下 CUDA0 分到 47 層中的 29 層：

```
144 MiB × 29 layers = 4176.00 MiB   ← 與 log 中失敗值完全吻合
144 × 29 × 1024 × 1024 = 4378853376 bytes  ← 與 log 中 byte 數完全吻合
```

RTX 3060 僅 11896 MiB 可用，還需承載約 59% 的 15.1 GiB 權重（約 8.9 GiB）。
合計約 13.1 GiB > 11.6 GiB，**超出約 1.2 GiB**。

因為在 KV 階段就失敗，log 中完全沒有 weight buffer / compute buffer / layer allocation 的記錄。

### 為何 Muse 相同設定可以，GLM 不行

兩者 GGUF 檔案大小極為接近（Muse 16756681056 vs GLM 16250044288 bytes），
導致 GLM profile 直接沿用了 Muse 已驗證的 `CONTEXT="131072"` 與 `TENSOR_SPLIT="59,41"`。
但兩者 KV 結構完全不同 —— GLM 的 MLA cache 在 131K 下總量達 6.61 GiB，
Muse（dense 架構）遠低於此。**檔案大小相近不代表 KV 需求相近**，這是本次的主要教訓。

### 修正

僅修改 `profiles/30-glm47-flash.conf` 一行：

```diff
18c18
< CONTEXT="131072"
---
> CONTEXT="32768"
```

備份：`30-glm47-flash.conf.bak.20260811-230133`

KV 需求：`4176 MiB → 約 1044 MiB`。
`--flash-attn off`、`TENSOR_SPLIT=59,41`、KV f16 精度均**未改動**。

### 結果

**CUDA0 這一關通過。** 載入過程中觀測到 GPU 一度達 9317 MiB used / 2594 MiB free，
遠超先前失敗點，證實 KV OOM 已排除。

---

## 問題二：RPC0 compute buffer 配置失敗（已解決）

### 失敗現象

`logs/3-glm47-20260811-230324.log`（23:03）——**失敗點已移動到另一個裝置與另一個階段**：

```
E ggml_gallocr_reserve_n_impl: failed to allocate RPC0[10.0.3.67:50053] buffer of size 1517164672
E graph_reserve: failed to allocate compute buffers
E llama_init_from_model: failed to initialize the context: failed to allocate compute pp buffers
E srv    load_model: failed to create_context with model '.../zai-org_GLM-4.7-Flash-IQ4_XS.gguf'
```

失敗配置：**1517164672 bytes = 1447.0 MiB**，位於 **RPC0**，屬於 **compute buffer**（非 KV、非權重）。

### 失敗點比較

| | 修改前（21:40 / 22:49） | 修改後（23:03） |
|---|---|---|
| 失敗裝置 | CUDA0（RTX 3060，本機） | **RPC0（RTX 5060，遠端）** |
| 失敗階段 | KV cache | **compute buffer** |
| 失敗大小 | 4378853376 B（4176.00 MiB） | **1517164672 B（1447.0 MiB）** |
| 錯誤訊息 | `failed to allocate buffer for kv cache` | `failed to allocate compute pp buffers` |

### 關鍵發現：這不是 VRAM 容量問題

於 TUF A16 本機直接查詢 RPC0 實際 VRAM：

```
NVIDIA GeForce RTX 5060 Laptop GPU
memory.total: 8151 MiB
memory.used:   258 MiB
memory.free:  7490 MiB
```

**RPC0 有 7490 MiB 空閒，卻配不出 1447 MiB。** 空閒量超過需求 5 倍以上。

因此**降 context 或調整 split 都不會有幫助** —— 阻擋這次配置的不是容量，是別的機制。
（此點修正了先前「RPC0 餘量不足」的錯誤推測。）

### 待查方向

1. **版本歪斜** — 遠端 `50053` rpc-server 由 `/home/b822726/project/llama-muse/build-muse-rpc-cuda/` 建置；
   本機 client 為 `/home/b827262/project/Qwen36llm/llama-muse/build-muse-rpc-cuda/bin/llama-server`。
   RPC 協定或 ggml 版本不一致可能導致遠端拒絕配置，與可用記憶體無關。
2. **rpc-server 啟動旗標** — `50053` 僅帶裸 `-c`，未指定 cache 大小上限。
3. **單次配置上限** — 約 1.5 GB 的單一 buffer 可能撞到 RPC 協定或整數型別上限。
4. **Muse 能過而 GLM 不能** — 同一個 RPC0 endpoint，Muse 在 131072 context 下正常運行。
   兩者 compute graph 需求的差異是最強線索。

### 修正：調整 batch size（已解決）

compute buffer 主要隨 **batch size** 而非 context 變動，故授權調整。

**嘗試 1**：`-b 1024 -ub 256`（備份 `30-glm47-flash.conf.bak.20260811-231918`）
→ 仍失敗，`logs/3-glm47-20260811-231943-b1024-ub256.log`。

**嘗試 2**：`-b 512 -ub 128`（備份 `30-glm47-flash.conf.bak.20260811-232023`）
→ **成功**，`logs/3-glm47-20260811-232041-b512-ub128.log`。

最終 `EXTRA_ARGS`（僅 `-b` / `-ub` 為新增，其餘未變）：

```
"-ngl" "99"
"-b" "512"
"-ub" "128"
"--fit" "off"
"--flash-attn" "off"
"--jinja"
"--temp" "0.7"
"--top-p" "1.0"
"--metrics"
```

### 驗證

```
$ curl -s http://127.0.0.1:8081/v1/models
{"models":[{"name":"glm-4.7-flash", ...}],
 "data":[{"id":"glm-4.7-flash","aliases":["glm-4.7-flash"],
   "meta":{"n_ctx":32768,"n_ctx_train":202752,"n_embd":2048,
   "n_params":29943393920,"size":16240568832,
   "ftype":"IQ4_XS - 4.25 bpw"}}]}
```

`glm-4.7-flash` 已在 port 8081 正常服務，`n_ctx=32768` 與 profile 設定一致。

### 載入後的實際 headroom（GLM 存活狀態下量測）

| 裝置 | used | free | 備註 |
|---|---|---|---|
| 本機 RTX 3060（CUDA0） | 10775 MiB | 1136 MiB | 尚有餘裕 |
| 遠端 RTX 5060（RPC0） | 7432 MiB | **316 MiB** | 直接於 TUF A16 用 `nvidia-smi` 量測，餘量偏緊 |

**RPC0 餘量僅 316 MiB，低於 500 MiB 警戒線。** GLM 目前雖成功運行，但 RPC0 側幾乎沒有安全邊際 ——
任何額外請求（例如更長輸出、並發請求、或 `50052` 上 Qwen36 若同時啟動）都可能再次觸發 OOM。
**此為警告，非阻斷性問題**：服務目前正常，但不建議在此狀態下嘗試拉高 context 或啟動第二個模型。

---

## 未取得的數值

llama.cpp 的 verbosity 設定下，即使成功載入也不會逐項印出以下明細；
失敗時的 log 更是在 context 建立前就中止，這些數值**從未寫入任何一次 log**：

```
KV_TOTAL              NOT LOGGED
KV_CUDA0              NOT LOGGED
KV_RPC0               NOT LOGGED
COMPUTE_BUFFER_CUDA0  NOT LOGGED
COMPUTE_BUFFER_RPC0   1447.0 MiB（僅以「配置失敗」形式出現，非正常配置記錄；成功後的實際值仍未知）
WEIGHTS_CUDA0         NOT LOGGED
WEIGHTS_RPC0          NOT LOGGED
LAYERS_CUDA0          NOT LOGGED
LAYERS_RPC0           NOT LOGGED
```

這些數值改以**外部量測**（`nvidia-smi` 前後差值）取代，見上一節「載入後的實際 headroom」。

---

## 附帶發現

### 1. switcher 失敗後不會自動回復舊模型

22:49 的切換嘗試中，switcher 先停掉 Muse，GLM 起不來後停在：

```
ERROR: 新模型啟動失敗；目前沒有自動回復舊模型
ERROR: 切換失敗，已回到選單
按 Enter 繼續...
```

結果是**兩個模型都沒有服務**，port 8081 無 listener，Hermes 完全無法使用。
`profiles/10-muse.conf` 與 `30-glm47-flash.conf` 共用 port 8081 與同一個 RPC endpoint `50053`，
兩者互斥，切換必然先停舊的。建議未來加入失敗自動回滾。

### 2. SSH config 帳號不一致

`~/.ssh/config` 中：

```
Host tuf-a16
    HostName 10.0.3.67
    User b827262
```

但 TUF A16 上實際帳號為 **`b822726`**（數字順序不同）。
這可能就是 `REMOTE_VRAM_CHECK_CMD=""` 一直未啟用的原因。
若要啟用自動遠端 VRAM 檢查，需先修正此帳號。

### 3. 量化格式辨識

磁碟上的檔案是 **IQ4_XS**（`zai-org_GLM-4.7-Flash-IQ4_XS.gguf`），
與 Q4_K_M 為不同格式，該目錄下沒有 Q4_K_M 版本。

---

## 目前系統狀態

- **GLM-4.7-Flash 執行中**，PID 181760，port 8081 服務正常，`/v1/models` 回傳 `glm-4.7-flash`
- 本機 RTX 3060：10775 MiB used / 1136 MiB free
- 遠端 RTX 5060（RPC0）：7432 MiB used / **316 MiB free**（偏緊，見上方警告）
- `CONTEXT=32768`、`-b 512 -ub 128` 為最終生效設定
- 遠端兩個 rpc-server 均未重啟、未終止
- **Muse 目前未運行**（8081 由 GLM 佔用，兩者互斥，如前述附帶發現一節）

---

## 教訓

1. **GGUF 檔案大小相近 ≠ 資源需求相近。** 架構（MLA vs dense）決定 KV 結構，
   直接沿用另一個模型的已驗證 profile 是本次的根源錯誤。
2. **失敗點移動代表有進展。** 從 CUDA0/KV 移到 RPC0/compute buffer，
   證明第一個修正有效，而非原地打轉。
3. **先量測再推論。** 「RPC0 餘量不足」的推測被實測 7490 MiB free 直接推翻；
   若未實際查詢遠端，會往錯誤方向繼續調 context。
4. **從 log 缺漏本身也能得到資訊。** 大量 `NOT LOGGED` 說明失敗發生在 context 建立前，
   這本身就縮小了問題範圍。
