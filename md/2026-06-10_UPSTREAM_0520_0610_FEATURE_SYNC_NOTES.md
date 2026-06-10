# 2026-06-10 Upstream 0520-0610 Feature Sync Notes

## 1. Purpose

This document summarizes upstream feature changes from 2026-05-20 to 2026-06-10 for later SmartBook Lite sync planning.

It is an analysis note only. It does not mean these upstream changes have already been synced into `release/vps-lite`, and it must not be mixed into PR #15.

Checkpoint: 新增兩大功能：

1. 考古題跨書關聯：
   - 後台可設定考古題書本關聯到哪些教科書。
   - 整本關聯，可排除特定題目。
   - 前台智能練題加入「考古題練習」分頁。
   - 可挑選來源書本。
   - 分頁作答。
   - 即時顯示答案解析。

2. 富文本編輯器 OCR 辨識：
   - 工具列加入 ScanText 按鈕。
   - 點擊後彈出 OcrImageDialog。
   - 支援貼上截圖或上傳圖片。
   - 後端用 Vision LLM 辨識文字。
   - 可編輯後插入到編輯器。

## 2. Upstream Reference

- repo: `iamflashon/ai_tutor_helper`
- target commit: `9b7741f37a59c4cd397d210e6870d05088f58911`
- date range: 2026-05-20 to 2026-06-10

## 3. High Value Feature Candidates

- 考古題跨書關聯：high-value learning workflow, but likely touches DB schema, admin UI, student UI, and smart practice routing.
- 富文本編輯器 OCR 辨識：high-value authoring workflow, likely touches rich text editor UI, image paste/upload handling, and a Vision LLM endpoint.
- quiz progress / autoGenerateQuiz polling：improves long-running quiz generation feedback and may reduce user uncertainty.
- FloatingNotepad / video toolbar：improves study workflow around video/PDF learning, but likely touches UI state and content persistence.
- PDF / OCR / screenshot paste：strong productivity feature, but requires careful upload/storage, OCR cost, and content sanitation review.
- smart book quick buttons / applyToBooks：useful classroom workflow, likely needs schema and admin UX review.
- cleanMarkdown 強化：lower-risk utility candidate if isolated and covered by regression tests.
- preview job async endpoint：useful for long-running preview generation, but requires server-side job lifecycle and error handling review.
- lesson_points / batchAutoProcess 修正：potentially important data correctness fix; should be separated from feature sync.

## 4. Feature Risk Table

| Feature | Value | Touches UI | Touches Server | Touches DB | SQLite Risk | Suggested Sync Method | Suggested Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 考古題跨書關聯 | High | Yes | Yes | Yes | High | Manual port after schema review | `sync/upstream-0520-0610-exam-cross-book-relation` |
| 富文本編輯器 OCR 辨識 | High | Yes | Yes | Maybe | Medium-High | Isolated PR with OCR endpoint review | `sync/upstream-0520-0610-richtext-ocr-editor` |
| quiz progress / autoGenerateQuiz polling | Medium-High | Yes | Yes | No/Maybe | Medium | Cherry-pick small slices with smoke tests | `sync/upstream-0520-0610-quiz-notepad` |
| FloatingNotepad / video toolbar | Medium-High | Yes | Yes | Maybe | Medium | Manual UI port, then runtime smoke | `sync/upstream-0520-0610-quiz-notepad` |
| PDF / OCR / screenshot paste | High | Yes | Yes | Maybe | Medium-High | Separate PR, storage/OCR safety review | `sync/upstream-0520-0610-pdf-ocr-preview` |
| smart book quick buttons / applyToBooks | Medium-High | Yes | Yes | Yes | High | Schema-first review, then UI/server port | `sync/upstream-0520-0610-db-schema-review` |
| cleanMarkdown 強化 | Medium | No | Maybe | No | Low | Cherry-pick utility + tests | `sync/upstream-0520-0610-docs-utils` |
| preview job async endpoint | Medium | Yes | Yes | Maybe | Medium | Manual port with job lifecycle review | `sync/upstream-0520-0610-pdf-ocr-preview` |
| lesson_points / batchAutoProcess 修正 | Medium-High | Maybe | Yes | Maybe | Medium-High | Separate bugfix PR, no feature mixing | `sync/upstream-0520-0610-docs-utils` |

## 5. Do Not Auto Sync

- DB schema / drizzle / migrations.
- `package.json` / `pnpm-lock.yaml` / `package-lock.json`.
- auth / credits / payment.
- production DB scripts.
- large UI rewrite.
- Manus-specific code.
- anything conflicting with PR #15 SQLite validator.

## 6. Recommended Sync Order

1. docs / pure utility
2. shared cleanMarkdown
3. server low-risk bugfix
4. richtext OCR editor
5. quiz progress / FloatingNotepad
6. exam cross-book relation
7. DB schema / migrations 最後處理

## 7. Branch Plan

- `sync/upstream-0520-0610-docs-utils`
- `sync/upstream-0520-0610-richtext-ocr-editor`
- `sync/upstream-0520-0610-exam-cross-book-relation`
- `sync/upstream-0520-0610-quiz-notepad`
- `sync/upstream-0520-0610-pdf-ocr-preview`
- `sync/upstream-0520-0610-db-schema-review`

## 8. Final Verdict

- UPSTREAM_MD_SYNC_READY
- 不建議直接 merge upstream。
- 建議分批 cherry-pick / manual port。
- PR #15 不應混入 upstream feature sync。
- 考古題跨書關聯屬高價值高風險，需獨立 PR。
- 富文本 OCR 屬高價值中高風險，需獨立 PR。
- 目前只是整理 MD，不代表功能已同步完成。
