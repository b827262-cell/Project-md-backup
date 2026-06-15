# 2026-06-15 SmartBook Codex Task: Fix Save JSON Index 413 and Keep MD Q&A Flow

## Task Name

```text
FIX_SAVE_JSON_INDEX_413_AND_KEEP_MD_QA_FLOW
```

## Background

Manual browser testing shows this request fails:

```text
POST /api/admin/books/:bookId/files/:fileId/save-json-index
Status: 413 Payload Too Large
```

The current implementation appears to send the entire generated JSON index from the browser back to the server. For a large PDF, the generated JSON can be several MB, which exceeds the current Express JSON body limit.

Important product clarification:

```text
The original Knowledge Q&A page uses manually uploaded Markdown Q&A.
That manual Markdown Q&A flow must remain available and must not be replaced by JSON index management.
```

The JSON index should be an additional structured QA reference source, not a replacement for manual Q&A Markdown.

## Goals

1. Fix `save-json-index` 413 Payload Too Large.
2. Avoid sending huge generated JSON through normal JSON request body.
3. Keep manual Markdown Q&A upload and delete functions intact.
4. Keep JSON Index / QA Reference as an additional reference source.
5. Ensure active JSON reference does not break existing manual Q&A display or creation.

## Preferred Fix

Do not increase Express global JSON body limit as the primary fix.

Preferred design:

```text
Frontend sends only small metadata:
- source PDF fileId
- level
- setActive flag

Server regenerates or reuses server-side JSON index and writes it directly to managed storage.
```

Suggested endpoint behavior:

```text
POST /api/admin/books/:bookId/files/:fileId/save-json-index
Body: { level: "page|chapter|clause|line|sentence", setActive: true|false }
```

Server side:

```text
1. Validate bookId and fileId.
2. Validate file is source PDF.
3. Validate level.
4. Generate JSON index on the server using existing buildPdfJsonIndex path.
5. Write JSON file to the book upload directory as managed artifact.
6. Create book_files row with role=json_index.
7. If setActive=true, update app_settings qa_reference:<bookId>.
8. Return stored JSON summary, not the full JSON body unless needed.
```

This avoids browser-to-server large payloads.

## Alternative Acceptable Fix

If the implementation already has a generated server-side cache, it may save from that cache, but do not rely on sending multi-MB JSON from the client.

Raising the body limit may be used only as a short-term safety net, not the primary solution.

## Manual Upload Flow

Manual JSON upload can remain multipart/form-data because it is explicitly a file upload flow.

Validate uploaded JSON as before:

```text
schemaVersion == smartbook-pdf-index-v1
source.pageNumberMode == pdf_physical_page
items array exists
items include pageStart/pageEnd/text/charCount
bookId mismatch is rejected
```

## Knowledge Q&A / Markdown Flow Must Remain

Do not remove or break:

```text
/admin/books/:bookId/qa
Q&A list
新增 Q&A
手動上架 Markdown
manual/markdown source rows
delete existing manual Q&A if delete exists
```

Expected behavior:

```text
- Manual Markdown Q&A remains the teacher-curated Q&A source.
- JSON Index / QA Reference is an additional structured reference source for Knowledge QA matching.
- The QA page should still show existing manual/markdown records.
- Upload Markdown still creates Q&A rows.
- Deleting JSON reference must not delete manual/markdown Q&A.
- Deleting manual/markdown Q&A must not delete JSON index artifacts.
```

## UI Requirements

On Files page:

```text
- Save as QA Reference should not send the full JSON object in request body.
- It should call save endpoint with only level/source metadata.
- After save, refresh the JSON Index / QA Reference list.
- Show a clear success message.
```

On Q&A page:

```text
- Manual Markdown upload remains visible and usable.
- Existing Q&A list remains visible.
- If JSON active reference status is shown, label it separately as Structured JSON QA Reference.
```

## Verification

Run:

```bash
pnpm build
pnpm typecheck
```

Runtime verification:

```text
1. Generate sentence-level JSON index for the 943-page PDF.
2. Click Save as QA Reference.
3. Confirm no 413 Payload Too Large.
4. Confirm stored JSON appears after refresh.
5. Confirm active badge appears if setActive=true.
6. Confirm raw JSON download still works.
7. Open /admin/books/:bookId/qa.
8. Confirm existing manual/markdown Q&A rows remain.
9. Upload manual Markdown Q&A.
10. Confirm manual/markdown Q&A creation still works.
11. Delete JSON reference and confirm source PDF and manual Q&A remain.
12. Confirm Knowledge QA uses JSON when active and falls back when deleted/no match.
```

## Expected Files

Likely files:

```text
apps/AI-adm-D1/src/server/index.ts
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
```

Possibly:

```text
apps/AI-adm-D1/src/pages/BookQaPage.tsx or equivalent QA page component if UI labeling needs clarification
```

Do not modify:

```text
student PDF.js reader
PDF parser physical page logic
chapter builder physical page logic
DB schema/migration unless absolutely necessary
payment/credit/auth
admin account/security
```

## Final Report

Final report must be in Traditional Chinese.

Include:

```text
- final status
- commit SHA
- whether 413 was fixed
- whether full JSON body upload was removed from save-json-index
- whether manual Markdown Q&A still works
- whether JSON QA reference remains separate from manual Q&A
- build/typecheck result
- runtime smoke result
- whether DB migration is required
- merge/deploy status
```
