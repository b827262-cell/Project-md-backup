# Muse Physical Closure and DFlash Readiness Validation

- 日期：2026-08-13（Asia/Taipei）
- 工作目錄：`/home/b827262/project/Qwen36llm`
- 驗收方式：重算既有 M0/M1/M2 原始量測、讀取本機 GGUF/source、Hub API 查證、下載並驗證 DFlash GGUF、隔離 CPU pairing smoke test。
- Production 變更：無。未切換 production profile、未修改參數或 repo。

## 任務目標

驗證 M0/M2 RPC 流量、token latency 與理論 logits payload 的物理閉合；複核 M1 RX、VRAM/tensor size、M2 byte identity 的解讀；確認 Muse Glimmer DFlash 的發佈狀況、實際大小、b10364 參數相容性與現有 GPU 容量是否足以進行 A/B。

## 執行環境 / 版本

- 主機：`b827262-E500-G9-WS760T`
- GPU：NVIDIA GeForce RTX 3060，12288 MiB；driver `580.178.04`
- 網路介面：`enp6s0`，實讀 `1000 Mb/s`、full duplex
- RPC peer：`10.0.3.67:50053`
- `llama-server`：b10364，version `10364 (153d324bc)`
- Target：Muse Glimmer 30B K-Quant-17GB，vocab 202,048，context 131,072
- 原始量測：`/tmp/muse-perf-placement-results.tsv`，SHA-256 `b8624cecc5da1265d9e64b8b9b80624cce6a9f4db0fe7db45571085556625188`

## 實際操作

1. 從既有 R1–R3 median 重新計算 M0/M2 RX delta、理論 f32 logits bytes、每-token latency 與 1 Gb/s serialization time。
2. 實讀 `enp6s0/speed`、duplex，對 TUF `10.0.3.67` 執行 20 次 ICMP ping。
3. 重算 M1/M2 W/R1/R2/R3/C4 五筆 RX 與不同 sample-selection 的 median。
4. 使用本機 `gguf_dump.py`/`GGUFReader` 讀取 target GGUF 的 tensor shape、quant type、elements 與實際 bytes；對照 b10364 layer placement source。
5. 於 2026-08-13 查詢 Hugging Face API 與 model cards，確認 Meta assistant 與 Unsloth GGUF artifacts。
6. 下載 `dflash-kquant.gguf` 到 `/tmp/muse-dflash-kquant.gguf`，驗證大小、SHA-256 與 GGUF metadata。
7. 先驗證 standalone DFlash 會依設計要求 `ctx_other`；再於獨立 `127.0.0.1:18081` 將 target/draft 強制 CPU、ctx 2048，執行 pairing startup smoke test。測試 server health PASS 後終止，port 已關閉。
8. 全程保持 production PID 469407 不動，最後重新驗證 health、cmdline、單一 server、RPC 與 VRAM。

## 測試與量測結果

### 1. 物理閉合

採用前一輪有效 R1–R3 median：

- M0 RX：`829.92677734375 KiB/token`
- M2 RX：`31.91450439453125 KiB/token`
- M0 tok/s：`17.2612647337301`
- M2 tok/s：`19.570276839668406`

精確重算：

```text
RX delta            = 798.0122729492188 KiB/token
                    = 817,164.5675 bytes/token
theoretical logits  = 202,048 × 4 bytes
                    = 808,192 bytes = 789.25 KiB
payload error       = (817,164.5675 - 808,192) / 808,192
                    = 1.1102024643%

M0 latency          = 1000 / 17.2612647337301 = 57.9331825 ms/token
M2 latency          = 1000 / 19.5702768396684 = 51.0978975 ms/token
measured delta      = 6.8352850 ms/token
1 Gb/s wire time    = 817,164.5675 × 8 / 1e9 = 6.53731654 ms
residual            = 0.29796846 ms
residual / wire     = 4.5587%
```

20-ping 實測：0% loss，RTT min/avg/max/mdev = `0.130/0.156/0.192/0.016 ms`。

結論：流量、理論 f32 logits 與 latency 差呈現強物理閉合，足以支持 M0 每 token 傳送完整 logits、M2 避免此 RPC payload 的機制判讀。但嚴格數字不是「三者在 1% 內」：payload error 是 1.1102%；measured latency 與 observed-byte wire time 差 4.56%。0.298 ms residual 與同 LAN 小延遲同量級，但大於本次 ICMP max 0.192 ms，不能等同於實測 TCP ACK RTT。

### 2. M1 RX sample selection

| Phase | M1 RX KiB/token | M2 RX KiB/token |
|---|---:|---:|
| W | 34.929600 | 31.372598 |
| R1 | 72.133647 | 56.049155 |
| R2 | 66.580103 | 31.914504 |
| R3 | 32.610435 | 31.794624 |
| C4 | 29.783709 | 29.190178 |

- M1 all-five median：`34.929600`，不是 66.580103。
- M1 R1–R3-only median：`66.580103`。
- M2 all-five median：`31.794624`；R1–R3-only median：`31.914504`。
- C4：M1 `29.783709` vs M2 `29.190178 KiB/token`，差約 2.03%。

M1 的五筆中只有 W、R3、C4 三筆集中在 29–35；R1/R2 偏高。因計數器涵蓋整張介面，背景流量能污染短樣本。all-five 與 C4 結果強力支持 M1/M2 都消除了 M0 的約 800 KiB/token logits RPC 流量；但 counter 本身不是 tensor allocator trace，故「placement 完全相同」仍是合理推論，不是直接證明。

### 3. Target tensor 實際大小

本機 target GGUF metadata：

| Tensor | Shape | Elements | Quant | Bytes | MiB |
|---|---:|---:|---|---:|---:|
| `token_embd.weight` | 6656 × 202048 | 1,344,831,488 | Q4_K | 756,467,712 | 721.4238 |
| `output.weight` | 6656 × 202048 | 1,344,831,488 | Q5_K | 924,571,648 | 881.7402 |

兩者元素數相同，但 GGUF 實際 ratio 是 `1.2222×`，差 `160.3164 MiB`。因此「embedding 約 492 MiB、output 約 882 MiB、1.8×、output 為 Q6_K」不成立；output 實際是 Q5_K。

b10364 `llama-model.cpp` 顯示 layer split 依 device list/tensor split 重算 repeating/output layers，input layer另行處理。M1 (`RPC0,CUDA0 / 41,59`) 與 M2 (`CUDA0,RPC0 / 59,41` 加 output override) 並非只差 token embedding placement；`10953 - 10461 = 492 MiB` 是整體 allocation 差，不能單獨反推某一 tensor 大小。

### 4. Byte identity 與 VRAM headroom

M0/M2 在既有 short 與 C4 的 `content+reasoning_content` SHA 相同，是本輪配置下的強 regression evidence。它只覆蓋已測 payload/config，不保證 split、ctx、batch、backend 或其他輸入變動後仍 byte-identical。

M2 相對 M0 的 `+13.3768%` 與本輪 byte identity 支持「目前這組設定是低行為風險的嚴格改進」，但不能泛化為所有 production 輸入均零行為變化。R1–R3 僅 n=3；0.0476% range 證明本輪短測穩定，不能排除跨工作負載/日期因素。

llama.cpp context/KV/compute buffers於初始化時配置，因此固定 `-c 131072 -np 1` 的一般文字 decode 不會因 token 數逐步吃掉同一份已配置 KV VRAM。M2 的 958 MiB 是已含 target 131072 context 的靜態觀測 headroom；它仍可能被 drafter、vision/perception、額外 endpoint、driver workspace 或其他 GPU process 消耗。

### 5. DFlash 發佈與 artifact

Meta 官方 [`meta-models/Muse-Glimmer-30B-assistant`](https://huggingface.co/meta-models/Muse-Glimmer-30B-assistant) 已於 2026-08 發佈 Muse Glimmer DFlash drafter：5 layers、block size 16、202,048 vocab、131,072 context。官方 BF16 `model.safetensors`：

- bytes：`5,111,976,608`
- size：`4.760899 GiB`
- SHA-256：`fd88d337eb84f8d0e6ba33a7684d7efa6722d4460ba4d6badca9699418392a84`

[`unsloth/Muse-Glimmer-30B-GGUF`](https://huggingface.co/unsloth/Muse-Glimmer-30B-GGUF/tree/main) 已提供量化 `dflash-kquant.gguf`：

- bytes：`1,631,205,312`
- size：`1,555.6386 MiB = 1.519178 GiB`
- SHA-256：`27d9a805fa29b943cfb6ad4843367cd4eaaaf06bd452d8cc3e00a2cd18a677bc`

本機下載 SHA 與 Hub LFS 相同。GGUF parse：version 3、architecture `dflash`、58 tensors、2.6B label、5 blocks、block size 16、target layers `[2,14,26,38,50]`（GGUF 1-based layer representation對應 model card `{1,13,25,37,49}`）、mask token 201818、all-layer SWA 2048、8 KV heads、K/V head dim 128、vocab 202048。實際 tensor bytes 合計 `1,618,131,968`（1543.1709 MiB）。

### 6. b10364 runtime smoke

本機 binary help 與 source 支援：

```text
--spec-type draft-dflash
--spec-draft-model /path/to/dflash-kquant.gguf
--spec-draft-device CUDA0
--spec-draft-ngl all
--spec-draft-n-max 15
```

`block_size=16` 時 DFlash 最大 draft tokens 為 15；本機 source會將超出值 clamp 至 15。draft K/V default 為 f16；不建議在 correctness A/B 前先量化 draft KV。

隔離 CPU pairing smoke 使用相同 target/drafter、ctx 2048、獨立 port 18081，結果：

- health：`{"status":"ok"}`
- `loading draft model '/tmp/muse-dflash-kquant.gguf'`
- `adding speculative implementation 'draft-dflash'`
- `n_max=15, n_min=0, p_min=0.00`
- `block_size=16, mask_token_id=201818, n_extract=5`
- port cleanup：PASS，18081 已關閉

這證明 artifact 與 b10364 loader/metadata/runtime pairing 相容；因強制 CPU 且未發 inference request，不是 correctness/performance A/B。

### 7. DFlash GPU 容量判定

| Profile / 假設 | E500 free | 與 GGUF file 1555.64 MiB 比較 | all-local DFlash |
|---|---:|---:|---|
| M0 | 1840 MiB | +284.36 MiB before runtime overhead | 未證實；headroom 很窄 |
| M1 | 1450 MiB | **-105.64 MiB** | 不可行 |
| M2 | 958 MiB | **-597.64 MiB** | 不可行 |
| M2 split 55/45（原推估） | ~1450 MiB | **~-105.64 MiB** | 仍不可行 |

上述只拿 free VRAM 與檔案 bytes 比，尚未加入 draft KV、compute/output buffers 與 allocator overhead；因此 M1/M2/M2-55/45 的不相容已可在最低界成立。M0 雖在檔案 bytes 上勉強多 284 MiB，但沒有完整 runtime 實測前不能宣稱可行。

根據 drafter config 與 b10364 source，所有 5 層均為 SWA 2048；default f16 draft KV 的純資料理論值約 40 MiB，b10364 SWA cache另有 ubatch/padding，且仍需 compute/output/allocator 空間。實際 GPU footprint 必須由成功啟動 log/nvidia-smi 測得，不能只用 GGUF file size替代。

將 drafter 放 RPC0 可能引入每個 committed/draft block 的 hidden-feature/verify 跨網傳輸；「收益必然完全吃掉」尚未實測，應列為高風險假設而非既成事實。TUF 先前 free minimum 577 MiB 且本輪仍缺 buffer-size/同步 telemetry，不宜在取得新 telemetry 前再把更多 target 或 draft weight 推往 RPC0。

## 問題 / 風險

1. 原「三者 1% 內」是過度精確表述：payload 1.1102%，時間閉合差 4.56%。物理機制仍獲強支持。
2. M1 RX 66.58 是 R1–R3 median，不是五筆 median；五筆只有三筆位於 29–35。
3. 492 MiB VRAM 差不能歸因 embedding，且 target GGUF 的實際 quant/type/bytes直接否定 492 MiB/Q6_K/1.8×說法。
4. M2 byte identity 是已測配置的 regression result，不是長期不變的選型保證。
5. DFlash 供應不再是 blocker；目前 blocker 是 all-local GPU runtime capacity。M1/M2 連 1.519 GiB 檔案下限都不足。
6. CPU pairing smoke只證明 loader/metadata/啟動相容，尚未驗證 GPU OOM、acceptance、correctness、tok/s、長 context 或 peg-native API 行為。
7. M0 看似可能勉強容納，但只剩約 284 MiB（未計 runtime overhead），不應直接在 production 上嘗試。

## 結論

- **物理閉合：PASS（有精度修正）。** M0→M2 RX delta 與 202,048-way f32 logits payload相差 1.1102%；latency delta 與 1 Gb/s serialization同量級，差 0.298 ms / 4.56%。
- **M1/M2 local output 判讀：SUPPORTED，不是 allocator-direct proof。** all-five/C4 流量均接近 30–35 KiB/token。
- **492 MiB embedding 推論：FAIL。** GGUF 實值與 placement source不支持。
- **M2 現況：仍是低風險 production candidate，但本輪未扶正。** 本任務沒有獲授權修改 production default，且 DFlash 容量規劃尚未完成。
- **DFlash artifact/readiness：供應 PASS、b10364 CPU pairing smoke PASS、GPU A/B BLOCKED BY CAPACITY。** 正確 kquant GGUF 已取得並驗證，但 M1/M2/M2-55/45 都不足以 all-local 載入。

建議下一步：先取得同步 TUF VRAM/buffer telemetry，接著設計能在 E500 至少保留 `1555.64 MiB + draft KV/compute/allocator safety margin` 的 target placement；完成成功 startup memory measurement 後，才做 greedy correctness-first DFlash A/B。不要先量化 draft KV或假設 RPC draft 無成本。

## 最終服務狀態

- Production profile：M0 `muse` / `10-muse.conf`
- PID：`469407`（全程未切換）
- health：HTTP 200，`{"status":"ok"}`
- llama-server count：1
- cmdline：`--device CUDA0,RPC0 --tensor-split 59,41`，無 DFlash、無 `-ot`
- RPC：`10.0.3.68:36176 -> 10.0.3.67:50053`，`ESTAB`
- E500：10071 MiB used / 1840 MiB free
- 隔離 smoke port 18081：已關閉

## rollback 狀態

不需 rollback：production 從未離開 M0 baseline。隔離 CPU smoke process 已終止且 port 已關閉；repo、profiles、production 參數均未修改。

## 可驗證證據

- `/tmp/muse-perf-placement-results.tsv`
- `/tmp/muse-dflash-kquant.gguf`
- `/tmp/muse-dflash-kquant-metadata.txt`
- `/tmp/muse-dflash-cpu-init.log`
- `/tmp/muse-dflash-cpu-pair-smoke.log`
- Hub：[`meta-models/Muse-Glimmer-30B-assistant`](https://huggingface.co/meta-models/Muse-Glimmer-30B-assistant)
- Hub：[`unsloth/Muse-Glimmer-30B-GGUF`](https://huggingface.co/unsloth/Muse-Glimmer-30B-GGUF/tree/main)
- llama.cpp speculative documentation：[`docs/speculative.md`](https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md)
