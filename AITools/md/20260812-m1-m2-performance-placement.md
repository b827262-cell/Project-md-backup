# M1/M2 PERFORMANCE & PLACEMENT VERIFICATION

- 日期：2026-08-12（Asia/Taipei）
- 工作目錄：`/home/b827262/project/Qwen36llm`
- 報告性質：實測驗收；未修改 repo、模型、參數、systemd、網路或 TUF。

## 任務目標

以固定 payload 與順序實測 M0、M1、M2 的 correctness、tensor placement、decode performance 與 E500 VRAM，結束後以 model-switcher 恢復 `10-muse.conf` baseline。

## 執行環境 / 版本

- 主機：`b827262-E500-G9-WS760T`
- OS kernel：Linux `7.0.0-28-generic` x86_64（Ubuntu 24.04 系列 kernel）
- GPU：NVIDIA GeForce RTX 3060，12288 MiB
- NVIDIA driver：`580.178.04`
- `llama-server`：version `10364 (153d324bc)`，GNU 13.3.0，Linux x86_64
- API：`http://127.0.0.1:8081/v1/chat/completions`
- RPC：`10.0.3.67:50053`
- 網路計數器：`/sys/class/net/enp6s0/statistics/{rx_bytes,tx_bytes}`
- 模型 alias：`muse-glimmer-30B`

測試 profiles（檔案僅讀取，未修改）：

| Profile | model-switcher | 實際關鍵 cmdline | profile SHA-256 |
|---|---|---|---|
| M0 | menu 1 / `10-muse.conf` | `--device CUDA0,RPC0 --tensor-split 59,41`，無 `--main-gpu` | `ab3274f74f56229d392a2a7093460ebf8afb5f0ccb30998c42b092267bfe6504` |
| M1 | menu 5 / `12-muse-reversed-no-main.conf` | `--device RPC0,CUDA0 --tensor-split 41,59`，無 `--main-gpu` | `417eee6f1b8f8d9533c52257d751369d004af3d7c233c7a81afbe9c278436072` |
| M2 | menu 6 / `13-muse-output-cuda.conf` | `--device CUDA0,RPC0 --tensor-split 59,41 -ot ^output\\.weight$=CUDA0` | `6e69fea2fc0559cf07386007be3fe438bae73664c5f426317c1706982e97ee8a` |

## 實際操作

1. 驗證既有 `/tmp/peg-req-4k.json` 存在，SHA-256 為 `ec4f04ebad23167a28c05850e7b76b02adffd779a340621b570d1dbccd7826ff`。
2. 依 correction 建立 `/tmp/perf-req-400.json`：user content 精確為 `Count from 1 to 400. Output one number per line, nothing else.`；`model=muse-glimmer-30B`、`temperature=0`、`seed=42`、`max_tokens=400`、`stream=false`；以 `jq` 精確驗證。SHA-256：`1e2a1c8076a1f65d6f4e73e79a2a40ee9a9b49736229d973dc68e9c16035adbf`。
3. 每個 profile 均以 model-switcher 切換；依序執行 W（discard）、R1、R2、R3（400 max tokens）與 C4（既有 4K payload）。
4. 每筆擷取 curl rc、HTTP、finish reason、completion tokens、`timings.predicted_per_second`、enp6s0 RX/TX counter delta、每 completion token KiB、content+reasoning_content 最大連續相同字元數與 content 前 120 字元。
5. 每次切換擷取實際 cmdline、E500 VRAM 與 launch log；測試 log 掃描 OOM/CUDA/RPC/allocation/assert 類錯誤。
6. 執行唯讀 DFlash `--help` grep 與 local `find`；未下載、未啟用。
7. 完成 M2 C4 後立即以 model-switcher menu 1 恢復 baseline，未繼續 optimization。

## CORRECTNESS

有效測試共 15 筆：curl rc 全為 0、HTTP 全為 200；所有 short 均 `finish_reason=length`、400 completion tokens；所有 C4 均 `finish_reason=stop`；所有 max char run 均為 3，未超過 stop threshold 30。三份測試 launch log 均未找到 OOM/CUDA/RPC/allocation/assert stop-condition 訊息。

| Profile | Phase | HTTP | finish | completion | tok/s | RX bytes | TX bytes | RX KiB/token | TX KiB/token | max run | content/reasoning chars | content prefix 120 |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| M0 | W | 200 | length | 400 | 17.244310 | 339691311 | 19119020 | 829.324490 | 46.677295 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M0 | R1 | 200 | length | 400 | 17.273940 | 350018748 | 17936644 | 854.537959 | 43.790635 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M0 | R2 | 200 | length | 400 | 17.261265 | 339907795 | 17870377 | 829.853015 | 43.628850 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M0 | R3 | 200 | length | 400 | 17.205453 | 339938008 | 17703246 | 829.926777 | 43.220815 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M0 | C4 | 200 | stop | 2512 | 17.106621 | 2128326262 | 112449090 | 827.405898 | 43.715591 | 3 | 12011/854 | `1. Verify power supply voltage within nominal tolerance.\\n2. Confirm ground continuity across chassis points.\\n3. Check fi` |
| M1 | W | 200 | length | 400 | 19.739690 | 14307164 | 18217474 | 34.929600 | 44.476255 | 3 | 548/248 | `1\\n2\\n3...42\\n43\\n` |
| M1 | R1 | 200 | length | 400 | 19.733908 | 29545942 | 17499561 | 72.133647 | 42.723538 | 3 | 524/314 | `1\\n2\\n3...42\\n43\\n` |
| M1 | R2 | 200 | length | 400 | 19.731420 | 27271210 | 17392798 | 66.580103 | 42.462886 | 3 | 524/314 | `1\\n2\\n3...42\\n43\\n` |
| M1 | R3 | 200 | length | 400 | 19.748059 | 13357234 | 17033142 | 32.610435 | 41.584819 | 3 | 524/314 | `1\\n2\\n3...42\\n43\\n` |
| M1 | C4 | 200 | stop | 1771 | 19.604049 | 54012876 | 72916381 | 29.783709 | 40.207455 | 3 | 7789/1118 | `1. Verify power supply voltage within tolerance.\\n2. Confirm input power cable securely seated.\\n3. Check system fan opera` |
| M2 | W | 200 | length | 400 | 19.560609 | 12850216 | 18062422 | 31.372598 | 44.097710 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M2 | R1 | 200 | length | 400 | 19.570277 | 22957734 | 16764739 | 56.049155 | 40.929539 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M2 | R2 | 200 | length | 400 | 19.577093 | 13072181 | 16711224 | 31.914504 | 40.798887 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M2 | R3 | 200 | length | 400 | 19.567784 | 13023078 | 16775706 | 31.794624 | 40.956313 | 3 | 516/324 | `1\\n2\\n3...42\\n43\\n` |
| M2 | C4 | 200 | stop | 2512 | 19.363937 | 75085545 | 105709195 | 29.190178 | 41.095396 | 3 | 12011/854 | `1. Verify power supply voltage within nominal tolerance.\\n2. Confirm ground continuity across chassis points.\\n3. Check fi` |

M0 與 M2 的 R1/R2/R3 `content+reasoning_content` SHA-256 均為 `04c982227ea4ed033e590d55311fecd8a30496b86f997bba834a97bb3da26f8c`；兩者 C4 combined SHA-256 均為 `b91a9f342c2a3548a2b675d8970b70fd29882519fbac78bd341cf59d3c25bc1d`。因此 M2 對本輪有效 payload 與 M0 的輸出文字 byte-identical。M1 輸出 SHA 與 completion tokens 不同；這不是 corruption，但不可宣稱與 M0 byte-identical。

## PLACEMENT

R1-R3 median RX KiB/token：M0 `829.926777`、M1 `66.580103`、M2 `31.914504`。C4 RX KiB/token：M0 `827.405898`、M1 `29.783709`、M2 `29.190178`。

**明確標示為推論：** M0 的每-token 高 RX 與 M1/M2 的低 RX 差距，和 M1 的 device order 變更及 M2 明確將 `output.weight` 放到 CUDA0 一致，支持 M0 output path 跨 RPC、M1/M2 output path 位於本地 CUDA0 的判讀。網卡計數器是整張介面的總量，可能包含背景流量，因此它是 placement 的強佐證，不是 tensor allocator 的直接內部追蹤。

三份 launch log 都未出現可識別的 RPC0 buffer-size 行；依規格記為「無證據」，未填造 TUF buffer/VRAM 數值。

## PERFORMANCE

W 僅暖機並丟棄；以下只用 R1-R3：

| Profile | R1/R2/R3 tok/s | median tok/s | range | range / median | 相對 M0 |
|---|---|---:|---:|---:|---:|
| M0 | 17.273940 / 17.261265 / 17.205453 | 17.261265 | 0.068487 | 0.3968% | baseline |
| M1 | 19.733908 / 19.731420 / 19.748059 | 19.733908 | 0.016639 | 0.0843% | +14.3248% |
| M2 | 19.570277 / 19.577093 / 19.567784 | 19.570277 | 0.009309 | 0.0476% | +13.3768% |

M1 比 M2 median 快 `0.163631 tok/s`（`+0.8361%`）。

## VALIDITY

採用 criterion：pairwise median 差異必須大於兩 profile 的 observed range 總和。

| Pair | median 差異 | range 總和 | criterion |
|---|---:|---:|---|
| M1 vs M0 | 2.472643 | 0.085127 | PASS |
| M2 vs M0 | 2.309012 | 0.077796 | PASS |
| M1 vs M2 | 0.163631 | 0.025948 | PASS |

本輪三組差異均通過該 validity criterion。這只描述本輪三次重測的內部可分辨性，不等同跨日期、跨負載的統計信賴區間。

## VRAM

| Profile | E500 used MiB | E500 free MiB |
|---|---:|---:|
| M0 | 10071 | 1840 |
| M1 | 10461 | 1450 |
| M2 | 10953 | 958 |
| restore M0 | 10071 | 1840 |

M2 僅餘 958 MiB free，為三者最低；這是容量風險，尤其對其他同 GPU 工作負載或未測 context/prompt 形狀。此輪未發生 OOM。

## DFLASH READINESS

唯讀 `llama-server --help | grep -Ei 'model-draft|draft|spec|dflash'` 證實 binary 提供 `--spec-draft-model`、draft cache/thread/device/ngl/override 選項，以及 `--spec-type ...draft-dflash...`。local `find` 找到 `llama-muse/src/models/dflash.cpp`、相應 build object，以及其他名稱含 draft 的來源/UI 檔案。

未找到檔名含 dflash/draft 的 `.gguf` drafter model。結論：binary/source 支援存在，但本機尚無已驗證 drafter GGUF；本輪未下載、未套用、未測 DFlash，不能宣稱 production ready。

## 問題 / 風險

1. Correction 到達時，先前錯誤的 synthetic-checklist short payload 已有 curl 在途；現場後續確認它在終止前完成 W 與 R1。這與 correction 文字中的「no request was sent」不一致。兩筆錯誤結果已明確作廢、從有效 TSV 移除；之後以正確 payload 重新啟動全新 M0，再執行完整 M0→M1→M2。錯誤請求不列入任何結論。
2. Correction 指定的 count prompt 覆寫了原始任務「short body 與 PEG request 相同」的要求；因此 `/tmp/perf-req-400.json` 與 `/tmp/peg-req-2k.json` 不是 byte-identical。這是依後到且更精確的 correction 執行，不宣稱兩者相同。
3. M1 雖無 corruption 且速度最高，但固定 seed/temperature 下的輸出 bytes 與 M0/M2 不同，C4 completion tokens 亦為 1771（M0/M2 為 2512）。若 production 要求 baseline 輸出一致，M1 有行為差異風險。
4. RX/TX 是介面總 counter delta，包含可能的背景流量；R1-R3 中 M1/M2 有明顯 RX 離群，但 C4 與 median placement 結論仍一致。
5. 沒有 TUF telemetry 或 launch-log RPC buffer-size 證據；不得從 E500 counter 推導遠端 VRAM/buffer 大小。

## RECOMMENDATION

建議以 **M2** 作為後續 production candidate，而非直接採用 M1：M2 對 M0 的 R1-R3 median 提升 `13.3768%`、placement 網路量顯著下降，且本輪 short/C4 輸出文字與 M0 byte-identical。代價是 E500 VRAM used 增至 10953 MiB、free 僅 958 MiB，導入前需另做目標 context/併發下的容量驗證。

M1 為純速度最高候選（比 M0 `+14.3248%`、比 M2 `+0.8361%`），且 VRAM 壓力低於 M2；但只有在接受其固定 payload 輸出與 baseline 不同後才可考慮。**本輪未套用任何 optimization；最終仍保持 M0 baseline。**

## 結論

- CORRECTNESS：M0/M1/M2 本輪有效請求均 PASS；無 max-run corruption、HTTP/RPC/CUDA/OOM/server failure。
- PLACEMENT：M1/M2 RX/token 相較 M0 大幅下降；推論支持 output path 已移至本地 CUDA0，其中 M2 有明確 anchored override cmdline 證據。
- PERFORMANCE：M1 最快，M2 次之；兩者對 M0 的提升及 M1/M2 彼此差異均通過本輪 range criterion。
- Production recommendation：M2（條件是另行完成 VRAM headroom 驗證）；本輪不變更 production baseline。

## 最終服務狀態

- Profile：`muse` / `10-muse.conf`
- PID：`469407`
- health：HTTP 200，`{"status":"ok"}`
- 唯一 llama-server：1 個（PID 469407）
- cmdline：`--device CUDA0,RPC0 --tensor-split 59,41`，無 `--main-gpu`、無 `-ot`
- RPC：`10.0.3.68:36176 -> 10.0.3.67:50053`，TCP `ESTAB`，owner `llama-server` PID 469407
- E500：10071 MiB used / 1840 MiB free
- final log：`model-switcher/logs/1-muse-20260812-235422.log`

## RESTORE

Rollback/restore：**PASS**。M2 完成後已由 model-switcher menu 1 恢復 `10-muse.conf`；health、device/split、RPC、單一 server 與 final cmdline 均已實測驗證。未手動 start/stop llama-server，未修改任何 profile 或 repo 參數。

## 可驗證證據

- `/tmp/muse-perf-placement-results.tsv`
- `/tmp/muse-perf-<M0|M1|M2>-<W|R1|R2|R3|C4>-meta.txt`
- `/tmp/muse-perf-<M0|M1|M2>-<W|R1|R2|R3|C4>-response.json`
- `/tmp/muse-perf-M0-cmdline.txt`、`/tmp/muse-perf-M1-cmdline.txt`、`/tmp/muse-perf-M2-cmdline.txt`
- `/tmp/muse-perf-switch-m0-corrected.txt`、`/tmp/muse-perf-switch-m1.txt`、`/tmp/muse-perf-switch-m2.txt`、`/tmp/muse-perf-switch-restore.txt`
- `/tmp/muse-perf-dflash-help.txt`、`/tmp/muse-perf-dflash-find.txt`
- `model-switcher/logs/1-muse-20260812-234052.log`
- `model-switcher/logs/5-muse-reversed-no-main-20260812-234602.log`
- `model-switcher/logs/6-muse-output-cuda-20260812-234952.log`
- `model-switcher/logs/1-muse-20260812-235422.log`
