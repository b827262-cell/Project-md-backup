# PEG-500 ATTRIBUTION TEST

## 開場自檢

時間：2026-08-12 22:14:19 CST

依指定原命令：

- date: 2026-08-12 22:14:19 CST
- pgrep -c -f llama-server: 2
- health: {"status":"ok"}
- 原命令的 pgrep -n -f 被自檢 shell 自身匹配，未取得有效 cmdline

立即以 exact process matching 複核：

- exact process count: 1
- PID: 445638
- device: CUDA0,RPC0
- tensor-split: 59,41
- health: PASS, HTTP 200
- PPID/SID: 1/445638

## RESULTS

這三個 request 已於本任務前一輪實際執行，本次沒有重跑。

| test | max_tokens | HTTP | finish_reason | completion_tokens | tok/s |
|---|---:|---:|---|---:|---:|
| T1 | 400 | 200 | length | 400 | 17.2042 |
| T2 | 2048 | 200 | length | 2048 | 17.0318 |
| T3 | 4096 | 200 | length | 4096 | 17.0306 |

每次 request 後 PID 445638 均為 ALIVE。

## CROSS-ARM COMPARISON

| test | reversed（上一輪） | baseline（本輪） | 一致？ |
|---|---:|---:|---|
| 2K | 500 | 200 | NO |
| 4K | 500 | 200 | NO |

上一輪 reversed 的 2K/4K request 已完成指定 decode 後才返回 invalid peg-native output HTTP 500。

注意：上一輪 reversed 使用 synthetic checklist prompt；本輪 baseline 使用本任務指定的 count prompt，因此不是 byte-identical workload。

## VERDICT: (B)

reversed-specific — baseline 在 T2/T3 均回 HTTP 200。

支持證據：

- baseline T1/T2/T3 全部 HTTP 200。
- baseline T2/T3 均完整完成 2048/4096 tokens，finish_reason=length。
- baseline log 有完整 eval timing 與 slot release。
- baseline log 沒有 peg、peg_parse 或 expected-format error。
- reversed 上一輪 2K/4K 則在 decode 完成後回 HTTP 500。

這否定了「500 是 baseline 與 reversed 共通的純 parser 缺陷」這個較窄的假設；但尚不能單獨證明根因一定是 device order，也可能涉及輸出內容、reasoning-format 或 template 行為差異。

## AVAILABLE BYPASS FLAGS

僅查詢，未套用：

- --reasoning-format FORMAT
- --reasoning [on|off|auto]
- --reasoning-budget N
- --reasoning-preserve / --no-reasoning-preserve
- --jinja / --no-jinja
- --chat-template
- --chat-template-file
- --skip-chat-parsing / --no-skip-chat-parsing

## SERVER LOG CONTEXT

Baseline log：

/home/b827262/project/Qwen36llm/model-switcher/logs/1-muse-20260812-212721.log

- T1 eval: 23250.19 ms / 400 tokens, 17.20 tok/s
- T2 eval: 120245.59 ms / 2048 tokens, 17.03 tok/s
- T3 eval: 240508.73 ms / 4096 tokens, 17.03 tok/s
- 三次均正常 slot release。
- peg/peg_parse/expected-format grep 無匹配。

## FINAL STATE

- health: PASS, HTTP 200
- PID: 445638
- device/split: CUDA0,RPC0 / 59,41
- exact llama-server process count: 1
- 未切換 profile、未停止或重啟 server。
