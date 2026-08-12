# Muse-Reversed Production Qualification Report

- 日期：2026-08-12（Asia/Taipei）
- 結果：**FAIL**
- 建議預設：**保留 Muse baseline（`10-muse.conf`）**
- 報告性質：production qualification 實測與獨立審查彙整

## 任務目標

驗證 `muse-reversed` 是否具備取代 Muse baseline 成為正式預設的條件，範圍包括：

- reversed profile 啟動、health 與短輸出 sanity。
- 約 32K、62K prompt 的長上下文行為。
- 2,048 與 4,096 token sustained decode。
- E500 與 TUF GPU telemetry。
- 共用 model switcher 對 Qwen、GLM 的 lifecycle regression。
- 測試後透過 switcher rollback 至 `10-muse.conf` baseline。

本輪不進行模型或參數調整；production qualification 以 API 能否正常交付結果為必要條件。

## 執行環境 / 版本

### E500 主機

- Host：`b827262-E500-G9-WS760T`
- OS：Zorin OS 18.1
- Kernel：Linux `7.0.0-28-generic` x86-64
- GPU：NVIDIA GeForce RTX 3060，12,288 MiB
- NVIDIA driver：`580.178.04`
- Bash：`5.2.21(1)-release`
- llama-server：version `10364`，commit `153d324bc`
- llama-server compiler：GNU 13.3.0 for Linux x86-64
- API：`http://127.0.0.1:8081/v1`
- RPC endpoint：`10.0.3.67:50053`

### TUF 遠端 GPU

- 實際 pane：`w1:p4`
- GPU：NVIDIA GeForce RTX 5060 Laptop GPU
- Telemetry 來源：既有 TUFA16 terminal pane 上的唯讀 `nvidia-smi` monitor
- 未開啟 SSH、未修改 TUF RPC process 或遠端設定

## 測試配置

### Baseline

```text
profile: 10-muse.conf
device: CUDA0,RPC0
tensor split: 59,41
context: 131072
parallel: 1
```

### Reversed

```text
profile: 11-muse-reversed.conf
device: RPC0,CUDA0
tensor split: 41,59
main GPU: 1
context: 131072
parallel: 1
```

Reversed server PID 為 `440801`，PPID 與 SID 分別為 `1`、`440801`；health 回應 HTTP 200。

## 實際操作

1. 驗證 baseline health、PID、cmdline、device order、tensor split 與 switcher syntax。
2. 透過 model switcher 從 baseline 切換至 `muse-reversed`。
3. 執行固定短輸出 sanity request。
4. 執行約 32K prompt long-context request。
5. 執行約 62K prompt long-context request。
6. 執行 `max_tokens=2048` sustained-decode request。
7. 執行 `max_tokens=4096` sustained-decode request。
8. 使用 E500 `nvidia-smi` CSV monitor 記錄本機 telemetry。
9. 透過既有 `w1:p4` pane 在 TUF 上記錄唯讀 telemetry。
10. 透過 switcher 依序啟動 Qwen、GLM，檢查 health、detach 及切換後 cleanup。
11. 透過 switcher 恢復 `10-muse.conf` baseline，核對 health、RPC、process 數量與 runtime state。

## 測試與量測結果

### API 與 decode

| 測試 | Prompt tokens | 實際 decoded tokens | HTTP | Finish | Decode | 結果 |
|---|---:|---:|---:|---|---:|---|
| Short sanity | 50 | 400 | 200 | `length` | 19.7635 tok/s | PASS |
| Long context 32K | 33,042 | 317 | 200 | `stop` | 18.6308 tok/s | PASS |
| Long context 62K | 約 62,441 prompt/cache tokens | 400 | 500 | API error | 約 17.79 tok/s | FAIL |
| Long completion 2K | 短 prompt | 2,048 | 500 | API error | 19.60 tok/s | FAIL |
| Long completion 4K | 短 prompt | 4,096 | 500 | API error | 19.48 tok/s | FAIL |

32K prompt evaluation：

- 33,016 uncached prompt tokens
- 58,466.86 ms
- 564.70 tok/s

62K prompt evaluation：

- Payload tokenization：62,009 content tokens
- Server release：約 62,441 prompt/cache tokens
- 29,133 uncached prompt tokens（cache reused）
- 72,630.10 ms
- 401.11 tok/s

### HTTP 500 證據

62K、2K、4K 三次 response body 均為：

```json
{
  "error": {
    "code": 500,
    "message": "The model produced output that does not match the expected peg-native format",
    "type": "server_error"
  }
}
```

Server log 顯示三次請求均完成指定 token 數的 decode，之後由 `common_chat_peg_parse` 記錄未解析的 peg-native output，API 才回傳 HTTP 500。各次錯誤後 server 仍存活；最後由 switcher 正常停止。

### Network counters

Network counter 取自整張 `enp6s0`，包含 HTTP request、prompt upload、RPC 及同介面其他可能流量，並非 RPC-port 專屬統計。

| 測試 | RX bytes | TX bytes | 備註 |
|---|---:|---:|---|
| Short | 14,258,211 | 18,113,572 | 34.8101 / 44.2226 kB per completion token |
| 32K | 1,020,588,967 | 2,357,955,726 | 包含大型 prompt 傳輸 |
| 62K | 906,039,412 | 4,028,814,004 | HTTP 500，未以 API usage 作 denominator |
| 2K | 433,875,486 | 85,850,386 | 以 server decoded 2,048 tokens 計算 |
| 4K | 169,079,465 | 178,369,182 | 以 server decoded 4,096 tokens 計算 |

Reversed RX 先前觀察到約 33–34 與 58–59 kB/token 的雙峰，本輪未釐清原因。

### E500 telemetry

Reversed 實際時間窗內：

- VRAM used max：10,465 MiB
- VRAM free min：1,446 MiB
- GPU utilization max：100%
- Memory utilization max：77%
- Temperature max：68°C
- Power max：136.88 W
- SM clock max：1,942 MHz
- Memory clock max：7,501 MHz

### TUF telemetry

`w1:p4` 上的 telemetry 檔共有 643 筆，時間為 `21:14:20.954–21:25:18.550`，完整覆蓋 reversed qualification。

按 reversed 實際啟動後的時間窗 `21:15:08–21:25:18` 重新切片：

- Samples：597
- VRAM used max：7,171 MiB
- VRAM free min：577 MiB
- GPU utilization max：100%
- Memory utilization max：55%
- Temperature max：72°C
- Power max：50.22 W

監控全時段曾出現 `7,561 MiB used / 187 MiB free / 85% memory utilization`，但該極值發生在 reversed 正式啟動前，因此不可標示為 reversed peak。

### Switcher regression

| Profile | PID | Start/health | Detached | Switch-away cleanup |
|---|---:|---|---|---|
| Qwen3.6 35B-A3B | 444514 | PASS / HTTP 200 | PASS，PPID/SID=1 | PASS |
| GLM-4.7-Flash IQ4_XS | 445128 | PASS / HTTP 200 | PASS，PPID/SID=1 | PASS |

恢復 baseline 後只剩一個受 switcher 管理的 `llama-server`。

## 問題 / 風險

### Production blocker：API 無法交付長測試結果

62K、2K、4K 雖完成 decode，但 API 均回 HTTP 500。Production qualification 應以可用 API response 為準，因此必須判定 FAIL，不能因 GPU 計算完成而視為通過。

### 根因尚未隔離

可驗證事實是：模型輸出大量不符合 peg-native 格式的內容，`common_chat_peg_parse` 隨後回傳 HTTP 500。

**推論（未證實）：** 根因可能位於模型長輸出退化、chat template、格式生成或 parser 相容性。現有證據不足以將問題單獨歸因於 parser。

### 尚未證明是 reversed 特有問題

本輪未用 baseline 對 62K、2K、4K 執行完全相同的對照請求。因此只能確認 reversed qualification 失敗，不能確認錯誤由 device order 或 reversed profile 所造成。

### 62K payload 代表性有限

62K payload 主要由重複的 `diagnostic` 文字構成，可驗證 context/resource stability，但不等同自然語言長上下文。

### TUF VRAM headroom

Reversed 時間窗內最低 free VRAM 為 577 MiB，headroom 偏低。雖未觀察到 OOM，仍應在長時間與多工作負載下持續觀察。

### Network 數據限制

`enp6s0` counter 是整張介面的差值，無法排除同介面背景流量，也無法單獨歸因於 RPC endpoint。

## 錯誤與穩定性核對

- OOM：未發現
- CUDA allocation/runtime fatal error：未發現
- RPC fatal error：未發現
- `llama-server` crash：未發現
- Kernel OOM/NVRM/segfault/killed-process：qualification 時間窗內未發現
- Application/API error：有，62K、2K、4K 重複出現 peg-native format HTTP 500
- Orphan `llama-server`：未發現

## 結論

`muse-reversed` 的 production qualification 結果為 **FAIL**。

Short sanity 與 32K long-context 均通過，且 62K、2K、4K 在計算層完成 decode，顯示本輪失敗不是由 OOM、CUDA、RPC、kernel error 或 server crash 所造成。然而三個重要長測試均無法取得成功的 API response，已構成 production blocker。

建議：

- 正式預設維持 Muse baseline。
- 保留 `muse-reversed` profile 供獨立的 peg-native 格式生成／解析鏈路調查。
- 後續以 baseline 執行同一批 62K、2K、4K request，隔離問題是否為 reversed 特有。
- 調查時不得把「parser 問題」當作已證實根因。

## 最終服務狀態

報告同步前再次唯讀確認：

- Profile：`10-muse.conf`
- Model：Muse Glimmer 30B
- PID：`445638`
- PPID / SID：`1 / 445638`
- Process state：`Ssl`
- API：`127.0.0.1:8081` listening
- Health：HTTP 200，`{"status":"ok"}`
- Device：`CUDA0,RPC0`
- Tensor split：`59,41`
- RPC：至 `10.0.3.67:50053` 的 TCP connection 為 `ESTABLISHED`
- 其他 `llama-server` process：無

## Rollback 狀態

- Rollback：**PASS**
- 執行方式：透過 model switcher 從 GLM 切回 profile `1 / muse`
- GLM PID `445128` 已停止
- E500 VRAM 回收檢查：PASS
- RPC preflight：PASS
- Baseline PID `445638` 啟動並 health PASS
- Runtime state、PID file 與實際 cmdline 一致
- 未進行 commit、DFlash、模型調參、GGUF 修改或 TUF RPC 修改

## 證據索引

- `/tmp/MUSE_REVERSED_PRODUCTION_QUALIFICATION_REPORT.md`
- `/tmp/muse-qual-short.tsv`
- `/tmp/muse-qual-long32k.tsv`
- `/tmp/muse-qual-long60k.tsv`
- `/tmp/muse-qual-long2k.tsv`
- `/tmp/muse-qual-long4k.tsv`
- `/tmp/muse-qual-e500-2114.csv`
- TUF：`w1:p4:/tmp/muse-qual-tuf.csv`
- `model-switcher/logs/4-muse-reversed-20260812-211444.log`
- `/tmp/muse-qual-switch-qwen.txt`
- `/tmp/muse-qual-switch-glm.txt`
- `/tmp/muse-qual-switch-restore.txt`

以上結論只採用實測或可重複核對的證據；推論已明確標示。
