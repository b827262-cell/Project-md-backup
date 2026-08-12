# PEG-500 ATTRIBUTION RETEST (byte-identical)

Date: 2026-08-12

## BASELINE STATE

- PID: 445638
- PPID/SID: 1/445638
- health: PASS, HTTP 200
- device: CUDA0,RPC0
- tensor-split: 59,41
- profile was not switched
- no stop/restart performed
- exact llama-server count: 1

## REQUEST PROVENANCE

The previous reversed qualification used the preserved payload files
/tmp/muse-qual-longgen-2k.json and
/tmp/muse-qual-longgen-4k.json directly with curl -d @payload.
Those files were copied byte-for-byte, without JSON reserialization:

- 2K source: /tmp/muse-qual-longgen-2k.json
- 2K replay: /tmp/peg-req-2k.json
- 2K SHA256: d17dc9adfd644c421e2edb5b81da954f9dccf65f63475c0cca927ee33222dadc
- 4K source: /tmp/muse-qual-longgen-4k.json
- 4K replay: /tmp/peg-req-4k.json
- 4K SHA256: ec4f04ebad23167a28c05850e7b76b02adffd779a340621b570d1dbccd7826ff
- byte comparison: both source/replay pairs cmp=identical
- confirmed same as reversed: YES, based on the exact preserved request files used by the previous reversed run

Body prefix for both files (first 300 bytes):

{"model": "muse-glimmer-30B", "messages": [{"role": "system", "content": "Reasoning strength: low"}, {"role": "user", "content": "Generate a long numbered synthetic technical checklist. Each item should contain a unique short diagnostic statement. Continue until the token limit."}], "temperature": 0

The 2K and 4K files differ only in their original max_tokens value, as in the previous reversed requests.

## RESULTS

Requests were sent to the unchanged baseline with 5 seconds between them.

| test | HTTP | finish | tokens | content empty? | reasoning_content | tok/s |
|---|---:|---|---:|---|---:|---:|
| 2K | 200 | length | 2048 | NO | present, 902 chars | 17.0882 |
| 4K | 200 | stop | 3900 | NO | present, 902 chars | 17.0059 |

Additional observed output:

- 2K baseline content length: 9739 chars
- 4K baseline content length: 19425 chars
- 2K response prefix is a structured checklist beginning: 1. Verify power supply voltage within specified tolerance.
- 4K response prefix is the same structured checklist format
- PID 445638 was ALIVE after both requests

## CROSS-ARM (byte-identical)

| test | reversed | baseline | consistent? |
|---|---:|---|---|
| 2K | HTTP 500 after 2048 decoded tokens | HTTP 200, 2048 tokens, finish=length | NO |
| 4K | HTTP 500 after 4096 decoded tokens | HTTP 200, 3900 tokens, finish=stop | NO |

## OBSERVABLE OUTPUT DIFFERENCES

The difference is not only the status code:

- Reversed 2K and 4K server logs contain common_chat_peg_parse: unparsed peg-native output: followed by a long run of repeated R characters, then HTTP 500.
- Baseline with the same request bytes returned a normal JSON completion with non-empty structured checklist content.
- Baseline exposed reasoning_content of 902 chars and parsed content; reversed exposed no usable completion body because response packaging failed.
- Baseline 4K naturally stopped at 3900 tokens; reversed decoded the full 4096 tokens before the peg-native failure.

Device order is theoretically a tensor-placement change and should not intentionally alter token distribution. The observed divergence therefore requires investigation at the arm/runtime level. This result supports a reversed-arm-specific failure, but does not isolate which coupled runtime difference is causal: the reversed arm also used --device RPC0,CUDA0, --tensor-split 41,59, and --main-gpu 1.

## VERDICT

**(B) reversed-specific — baseline returned HTTP 200 for both byte-identical requests.**

The previous (B) result is confirmed after removing the prompt mismatch. The 500 is not a baseline-common parser failure for these exact request bodies.

This is an arm-level attribution only. It is not proof that device order alone, rather than the complete reversed runtime configuration, causes the output divergence.

## SERVER LOG COMPARISON

Baseline log:

/home/b827262/project/Qwen36llm/model-switcher/logs/1-muse-20260812-212721.log

- 2K: eval 119848.662 ms / 2048 tokens, 17.0882 tok/s; normal completion response
- 4K: eval 229332.652 ms / 3900 tokens, 17.0059 tok/s; normal completion response
- requested peg|peg_parse|does not match the expected grep: no matches

Previous reversed log:

/home/b827262/project/Qwen36llm/model-switcher/logs/4-muse-reversed-20260812-211444.log

- 2K: eval 104512.96 ms / 2048 tokens, 19.60 tok/s; repeated-R invalid peg-native output and HTTP 500
- 4K: eval 210272.84 ms / 4096 tokens, 19.48 tok/s; repeated-R invalid peg-native output and HTTP 500

## FINAL STATE

- health: PASS, HTTP 200
- PID: 445638
- device/split: CUDA0,RPC0 / 59,41
- exact llama-server count: 1
- no profile switch, stop, restart, bypass flag, or configuration change
