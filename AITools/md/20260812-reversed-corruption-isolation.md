# REVERSED CORRUPTION ISOLATION

Date: 2026-08-12

Correctness was the only acceptance criterion. No performance tuning was performed. No bypass flags were used.

## MATRIX

| profile | device | split | main-gpu | -ot | HTTP short/2K | max char run short/2K | CORRUPTED? | VRAM E500 used/free |
|---|---|---|---|---|---|---|---|---|
| M0 | CUDA0,RPC0 | 59,41 | none | none | 200 / 200 | 3 / 3 | NO / NO | 10071 / 1840 MiB |
| M1 | RPC0,CUDA0 | 41,59 | none | none | 200 / 200 | 2 / 3 | NO / NO | 10461 / 1450 MiB |
| M2 | CUDA0,RPC0 | 59,41 | none | ^output\.weight$=CUDA0 | 200 / 200 | 3 / 3 | NO / NO | 10953 / 958 MiB |

Corruption rule: max char run > 30. Every tested response was below the threshold.

### Per-request observations

- M0 short: HTTP 200, finish=length, 400 tokens, content length 1134, reasoning length 902, max repeated token group 3.
- M0 2K: HTTP 200, finish=length, 2048 tokens, content length 9642, reasoning length 902, max repeated token group 3.
- M1 short: HTTP 200, finish=length, 400 tokens, content length 904, reasoning length 1123, max repeated token group 1.
- M1 2K: HTTP 200, finish=stop, 2030 tokens, content length 9817, reasoning length 1115, max repeated token group 1.
- M2 short: HTTP 200, finish=length, 400 tokens, content length 1134, reasoning length 902, max repeated token group 3.
- M2 2K: HTTP 200, finish=length, 2048 tokens, content length 9642, reasoning length 902, max repeated token group 3.

All profiles used the existing byte-identical 2K payload:

/tmp/peg-req-2k.json

The short payload changed only max_tokens from 2048 to 400:

/tmp/peg-req-400.json

## PROFILE AND LOG EVIDENCE

- M0 log: /home/b827262/project/Qwen36llm/model-switcher/logs/1-muse-20260812-231015.log
- M1 log: /home/b827262/project/Qwen36llm/model-switcher/logs/5-muse-reversed-no-main-20260812-231404.log
- M2 log: /home/b827262/project/Qwen36llm/model-switcher/logs/6-muse-output-cuda-20260812-231657.log

No profile log contained OOM, CUDA error, allocation failure, RPC error, or assertion failure.

No profile log contained a peg-native parse error for these requests.

M2 process cmdline contained the exact anchored override:

-ot ^output\.weight$=CUDA0

M2 override/buffer/output log message count was 0, not multiple lines. Therefore the requested log message did not provide direct confirmation; this is recorded as a telemetry gap. M2 nevertheless loaded with 10953 MiB used versus M0 10071 MiB, and completed both correctness tests cleanly.

## ATTRIBUTION

M1 is clean while retaining both reversed device order and reversed tensor split, but removing only --main-gpu 1.

Per the requested isolation rule, this points to variable C, --main-gpu 1, as the corruption root-cause candidate. Variables A/B were not sufficient to reproduce corruption in this matrix.

M2 is also clean: baseline order/split plus anchored output.weight placement completed both tests without corruption. This demonstrates a correctness-clean path that does not require reversing the device order.

This is a correctness attribution only. It is not a performance result, and it does not prove that main-gpu is the only lower-level implementation cause.

## RECOMMENDED PATH

Do not adopt the previous reversed profile with --main-gpu 1.

The correctness-clean candidates are:

1. M1 if reversed placement is required without --main-gpu.
2. M2 as the preferred surgical path for keeping baseline order/split while placing only output.weight on CUDA0.

M2 should remain a candidate until its missing buffer-override log confirmation is resolved in a separate task. No performance recommendation is made here.

## RESTORE

- restored through model-switcher: YES
- final profile: 10-muse.conf
- final PID: 460478
- final health: PASS, HTTP 200
- final device: CUDA0,RPC0
- final tensor split: 59,41
- final RPC: established to 10.0.3.67:50053
- exact llama-server process count: 1
- final E500 VRAM: 10071 MiB used / 1840 MiB free

No bypass flag, source, GGUF, systemd, network, or TUF RPC change was made.
