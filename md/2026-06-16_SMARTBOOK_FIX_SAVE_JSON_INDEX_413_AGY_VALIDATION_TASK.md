# 2026-06-16 SmartBook AGY Validation Task: Fix Save JSON Index 413

## Validation Target

Feature: FIX_SAVE_JSON_INDEX_413_AND_KEEP_MD_QA_FLOW

Expected code commit: cf8f292

## Summary

Codex reports that Save as QA Reference no longer sends the full generated JSON index from browser to server. The frontend now sends only small metadata such as level and setActive. The server regenerates the JSON index and saves it as a managed artifact.

This should fix 413 Payload Too Large for large PDF JSON indexes.

Manual Markdown Q&A must remain intact and separate from JSON Index QA Reference.

## Checklist

1. Repository state

```bash
cd /home/b827262/project/AI-SmartBook-R1

git branch --show-current
git log --oneline -10
git rev-parse --short HEAD
git status --short
git show --stat --oneline HEAD
git show --name-only --oneline HEAD
```

Expected:

- HEAD is cf8f292 or includes cf8f292.
- Working tree is clean.
- Changes are scoped to save-json-index / API client / Files UI / schema if needed.

2. Validate 413 fix

Check that save-json-index no longer accepts or requires the full JSON payload from frontend.

Expected request body:

```json
{
  "level": "sentence",
  "setActive": true
}
```

Expected server behavior:

- Validate bookId and fileId.
- Validate source PDF.
- Validate level.
- Generate JSON index server-side.
- Save JSON artifact to book upload directory.
- Create book_files row with role=json_index.
- If setActive=true, update qa_reference:<bookId>.
- Return stored summary, not full JSON items payload.

3. Validate code paths

```bash
rg -n "save-json-index|saveJsonIndex|setActive|buildPdfJsonIndex|parsePdfToContents|qa_reference|json_index" apps/AI-adm-D1/src packages/schema/src
```

Expected:

- api.ts saveJsonIndex sends level/setActive only.
- FilesTab calls saveJsonIndex with generatedIndex.level or selected level.
- server/index.ts regenerates JSON server-side.

4. Runtime smoke test

Use the real 943-page PDF if available.

Expected:

- sentence level Save as QA Reference returns HTTP 201 or equivalent success.
- No 413 Payload Too Large.
- Request body is small, not multi-MB.
- Stored JSON itemCount is 15611 or equivalent for the current PDF.
- Stored JSON remains after refresh/list.
- Raw JSON download works.
- Source PDF remains after deleting JSON artifact.

5. Manual Markdown Q&A preservation

Confirm original Q&A flow still works:

- /admin/books/:bookId/qa remains available.
- Q&A list remains visible.
- Manual Markdown upload remains visible.
- Correct Q:/A: markdown import succeeds.
- Imported rows use provider/source manual/markdown.
- JSON Index does not replace or delete manual Markdown Q&A.

6. QA priority / separation

Expected:

- Manual Markdown Q&A remains teacher-curated source.
- JSON Index is structured PDF reference.
- Existing content fallback remains.
- Active JSON can be used by QA when appropriate.
- Deleting JSON reference does not delete manual Q&A.

7. Build and typecheck

```bash
pnpm build
pnpm typecheck
```

Expected: both PASS.

## Final Report Format

Final report must be in Traditional Chinese.

```md
## AGY 驗收回報

- 最終狀態：PASS / PASS_WITH_NOTES / FAIL / BLOCKER
- 驗收對象：FIX_SAVE_JSON_INDEX_413_AND_KEEP_MD_QA_FLOW
- commit SHA：<short SHA>
- 是否修復 413 Payload Too Large：
- Save as QA Reference 是否不再送整包 JSON：
- server 是否自行產生並儲存 JSON：
- Manual Markdown Q&A 是否保留：
- JSON Index 是否與 Markdown Q&A 分離：
- runtime smoke：
  - sentence level Save as QA Reference：
  - no 413：
  - request body 是否小型化：
  - JSON artifact persists：
  - manual markdown upload still works：
  - source PDF remains：
  - QA fallback：
- pnpm build：
- pnpm typecheck：
- 是否需要 DB migration：
- 是否混入 unrelated 變更：
- git status --short：
- 合併 / 部署狀態：NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

## Judgment Rule

PASS if:

- 413 is fixed.
- Save as QA Reference sends only small metadata.
- Server generates and stores JSON.
- Manual Markdown Q&A still works.
- Source PDF remains safe.
- build/typecheck pass.

PASS_WITH_NOTES if:

- Core behavior works but server-side generation may still be slow for very large PDFs.
