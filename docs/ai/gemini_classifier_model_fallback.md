# Gemini Classifier Model Fallback Policy

Created: 2026-06-22

## Scope

Gemini is used only for image and CSV summarization, field recognition, and classification.

Allowed output domains:

- fund
- stock
- unknown

## Preferred model order

1. Gemini 3.1 Flash-Lite
2. Gemma 4 31B
3. Gemma 4 26B
4. Gemini 3.5 Flash
5. Gemini 3 Flash
6. Gemini 2.5 Flash
7. Gemini 2.5 Flash-Lite

## Runtime rule

Do not hard-code one model only. At startup, call the Google Models API and keep only models that support generateContent. The UI dropdown should show available and unavailable status.

## Fallback rule

- 404: switch to the next available model
- 429: switch to the next available model and log rate_limited
- 500, 502, 503: retry once, then switch to the next model
- 400: stop and report request format error
- 401, 403: stop and report key or permission error

## Default behavior

Use Gemini 3.1 Flash-Lite if available. If unavailable, use the next available model in the preferred order.

## Required logs

- selected alias
- attempted model id
- status code
- fallback target
- final model id

## AGY task

Add a model dropdown and automatic fallback mechanism to the Gemini file classifier. Keep Gemini limited to image and CSV classification tasks.
