# GLM-4.7-Flash 32K 穩定性、40960 OOM 與 KV 量化可行性追蹤報告

**日期**：2026-08-12

**環境**：RTX 3060 12 GB（CUDA0）+ RTX 5060 Laptop 8 GB（RPC0）

**模型**：GLM-4.7-Flash IQ4_XS，deepseek2 / MLA，47 layers

**結論**：目前已確認的穩定配置為 `ctx=32768`、`split=59,41`、`-b 512 -ub 128`、f16 KV、Flash Attention off。40960 在 59:41 與 60:40 下都於 RPC0 compute buffer 配置失敗。

---

## 摘要

本報告延續 [2026-08-11 初始 OOM 診斷](glm47-flash-vram-oom-process-20260811.md)，記錄 2026-08-12 完成的實際載入、推論、context、tensor split 與 KV 量化原始碼審驗。

今日確認：

1. `32768 / 59,41 / -b 512 -ub 128` 可載入並完成推論。
2. `40960 / 59,41` 失敗，RPC0 無法配置 500,926,080 bytes 的 compute buffer。
3. `32768 / 60,40` 可載入，但兩張 GPU 的 VRAM 數字完全不變，表示 1% split 調整未搬動完整 layer。
4. `40960 / 60,40` 仍以相同的 500,926,080-byte RPC0 allocation 失敗。
5. 失敗後已把 profile 完整還原為 `32768 / 59,41`；profile 與備份 `20260812-001649` byte-for-byte 相同。
6. q8_0 KV 理論上可節省記憶體，但 GLM MLA 要求 K/V 同型，而且量化 V 強制要求 Flash Attention；RPC + Flash Attention 尚未實測。

---

## 對 8/11 報告的更正

8/11 報告曾依「載入前 RPC0 有 7490 MiB free」推論 1447 MiB compute buffer 失敗不是容量問題。這個推論不成立：

- 7490 MiB 是模型權重與 KV 尚未完整配置前的空閒量。
- GLM 成功載入 32K 後，RPC0 實測只剩 316 MiB；今日重測更只有 248 MiB。
- 今日 40960 失敗發生在權重與 KV 已佔用 RPC0 後，新的 477.72 MiB compute buffer 無法配置，與緊迫的實際 headroom 一致。

因此目前應採用的結論是：**RPC0 的 8 GB VRAM 是 40960 的實際瓶頸；不能用載入前的 idle VRAM 排除容量問題。**

---

## 穩定基準：32768 / 59,41

最終 profile：

```text
TENSOR_SPLIT="59,41"
CONTEXT="32768"
PARALLEL="1"
-b 512
-ub 128
--fit off
--flash-attn off
```

成功載入時的量測：

| 裝置 | used | free | total |
|---|---:|---:|---:|
| CUDA0 — RTX 3060 | 10775 MiB | 1136 MiB | 12288 MiB |
| RPC0 — RTX 5060 Laptop | 7500 MiB | **248 MiB** | 8151 MiB |

驗證項目：

- `/v1/models` 回傳 `id=glm-4.7-flash`、`n_ctx=32768`
- `/health` 回傳 `{"status":"ok"}`
- 簡短 chat completion 回傳 HTTP 200
- 先前的短／長 request smoke test 均未令 server crash

RPC0 free 低於 500 MiB，應視為警告；32K 可用不代表仍有足夠空間提高 context 或增加並發。

---

## Probe 1：40960 / 59,41

只修改 `CONTEXT=32768 -> 40960`，其餘參數不變。

結果：**載入失敗**。

```text
ggml_gallocr_reserve_n_impl: failed to allocate RPC0[10.0.3.67:50053] buffer of size 500926080
graph_reserve: failed to allocate compute buffers
llama_init_from_model: failed to initialize the context: failed to allocate compute pp buffers
```

- 裝置：RPC0
- allocation：500,926,080 bytes，約 477.72 MiB
- 類型：compute pp buffer
- log：`logs/3-glm47-20260812-000400.log`
- 依 stop condition 未測 45056、47104、49152 或 65536
- 失敗後恢復 32768 並重新啟動成功

---

## Probe 2：60,40 tensor split

### 32768 / 60,40

先只修改：

```diff
-TENSOR_SPLIT="59,41"
+TENSOR_SPLIT="60,40"
```

結果：載入成功、HTTP 200 推論成功，單次短 request 約 0.44 秒；server 持續存活。

但量測與 59:41 完全相同：

| split | CUDA0 used/free | RPC0 used/free |
|---|---|---|
| 59:41 | 10775 / 1136 MiB | 7500 / 248 MiB |
| 60:40 | 10775 / 1136 MiB | 7500 / 248 MiB |

結論：layer split 是離散配置，60:40 沒有跨過下一個完整 layer 的分配界線，因此沒有釋放 RPC0 VRAM。

### 40960 / 60,40

結果：**再次失敗**，錯誤與 59:41 相同：

```text
ggml_gallocr_reserve_n_impl: failed to allocate RPC0[10.0.3.67:50053] buffer of size 500926080
graph_reserve: failed to allocate compute buffers
llama_init_from_model: failed to initialize the context: failed to allocate compute pp buffers
```

- log：`logs/3-glm47-20260812-002650.log`
- 60:40 不值得保留
- 已還原 `59,41 / 32768`

---

## Profile 備份與變更鏈

| 備份時間 | 下一步變更 |
|---|---|
| 20260811-230133 | context 131072 → 32768 |
| 20260811-231918 | 新增 `-b 1024 -ub 256` |
| 20260811-232023 | batch 改為 `-b 512 -ub 128` |
| 20260812-000304 | context 32768 → 40960 |
| 20260812-000503 | context 40960 → 32768 |
| 20260812-001649 | split 59,41 → 60,40 |
| 20260812-002337 | context 32768 → 40960 |
| 20260812-002808 | split 與 context 還原 |

最終 profile 與 `30-glm47-flash.conf.bak.20260812-001649` 完全一致。

`10-muse.conf` 與 `20-qwen36.conf` 未被修改。

---

## KV cache 計算

GGUF metadata：

```text
general.architecture = deepseek2
deepseek2.block_count = 47
deepseek2.attention.head_count_kv = 1
deepseek2.attention.key_length = 576
deepseek2.attention.value_length = 512
deepseek2.attention.key_length_mla = 256
deepseek2.attention.value_length_mla = 256
```

MLA 採 k-only cache。f16、32K 時：

```text
576 × 2 bytes × 32768 = 36 MiB/layer
36 MiB × 47 = 1692 MiB total
```

在 29/18 layer 分配下：

- CUDA0 KV：約 1044 MiB
- RPC0 KV：約 648 MiB

---

## q8_0 KV 可行性審驗

本機 llama.cpp build 支援 `q8_0`、`q4_0` 等 KV cache type，但 GLM MLA 有以下 gate：

1. MLA 模型的 K/V cache type 必須相同，不能只設定 `--cache-type-k`。
2. quantized V cache 必須啟用 Flash Attention。
3. q8_0/q4_0 block size 為 32；GLM 的 576/512 與 MLA 256/256 都可被 32 整除，因此通過 divisibility gate。
4. Flash Attention 透過 RPC 時有額外的 remote allocation-size 查詢路徑；目前這套 RPC0 從未在 `--flash-attn on` 下驗證。

q8_0 在 32K 約可把 1692 MiB 的總 KV 降至約 899 MiB，總節省約 793 MiB。但這些節省會分散到兩張 GPU：

- CUDA0 約節省 489 MiB
- RPC0 約節省 **304 MiB**

因此 q8_0 值得測試，但不能宣稱一定能讓 40960 載入。

### 建議的受控測試順序

1. 維持 `32768 / 59,41 / f16 KV`，只把 `--flash-attn off` 改為 `on`，驗證 RPC + Flash Attention。
2. 第一步成功後，仍維持 32768，再同時加入 `--cache-type-k q8_0 --cache-type-v q8_0`。
3. 驗證啟動、短／長推論、輸出品質與兩卡 VRAM。
4. 只有 q8_0 在 32K 穩定後，才另行授權測試 40960。

每一步都應獨立備份、只引入一組變數；首次 OOM、crash 或品質異常即停止並回復上一個穩定配置。

---

## 報告完成時的系統狀態

- Profile：`59,41 / 32768 / -b 512 -ub 128 / f16 KV / --flash-attn off`
- Profile 已驗證可成功載入及推論
- 驗證完成後透過 model-switcher 正常停止 GLM
- Port 8081：無 listener
- RTX 3060：15 MiB used / 11896 MiB free
- RTX 5060 RPC server 保持運行，未重啟或修改
- 尚未執行 Flash Attention on 或 q8_0 KV 實測

---

## 最終決策

目前 production-safe 上限維持 **32768**。

`60,40` 不會改變 layer 分配；`40960` 在兩種 split 下都失敗。

下一個合理實驗不是繼續提高 context，而是先獨立驗證 RPC + Flash Attention，再測 q8_0 K/V。
