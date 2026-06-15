# 2026-06-15 SmartBook Codex Task: Persistent JSON Index as QA Reference

## 1. Task Name

```text
PERSISTENT_JSON_INDEX_QA_REFERENCE_AND_MANUAL_FILE_MANAGEMENT
```

## 2. Background

The Admin Files page can now generate a 5-level PDF JSON index on demand.

Current limitation:

```text
Generated JSON exists only in browser memory unless downloaded.
After refresh, the generated result is not persisted.
```

New requirement:

```text
After JSON index is generated, it should be usable directly as the Knowledge QA reference template.
The page should also provide manual JSON file upload and delete actions.
```

## 3. Goals

1. Persist generated JSON index as a managed file/artifact.
2. Allow one persisted JSON index to be selected as the active Knowledge QA reference.
3. Allow manual upload of an existing JSON index file.
4. Allow deleting stored JSON index files.
5. Keep existing PDF upload, Parse Content, Parse Outline, and Generate JSON Index workflow.

## 4. Recommended Admin UI

On `/admin/books/:bookId/files`, add a new section:

```text
JSON Index / QA Reference
```

Actions:

```text
- Save Generated JSON as QA Reference
- Upload JSON Index
- Set as QA Reference
- View JSON
- Download JSON
- Delete JSON
```

The generated JSON result area should show:

```text
- Save as QA Reference
```

The stored JSON list should show:

```text
File name
Level / levelLabel
Item count
Generated or uploaded timestamp
Active QA Reference badge
Actions: Set as QA Reference / View / Download / Delete
```

## 5. Storage Design

Preferred first implementation:

```text
Store JSON index as a managed book file or generated artifact without DB migration if existing book_files metadata is sufficient.
```

If using `book_files`, use a role or metadata classification that can distinguish JSON index files from PDF source files.

Possible role/name:

```text
json_index
qa_reference_index
```

If schema does not currently support this role, use the smallest safe schema/migration change and report it clearly.

Do not overwrite the source PDF.

## 6. API Requirements

Add or implement equivalent endpoints:

```text
POST /api/admin/books/:bookId/files/:fileId/save-json-index
POST /api/admin/books/:bookId/json-indexes/upload
GET  /api/admin/books/:bookId/json-indexes
POST /api/admin/books/:bookId/json-indexes/:indexFileId/set-active-qa-reference
GET  /api/admin/books/:bookId/json-indexes/:indexFileId/raw
DELETE /api/admin/books/:bookId/json-indexes/:indexFileId
```

Exact names may differ if they fit the current code style better.

## 7. QA Reference Behavior

When a JSON index is set as active QA reference:

```text
- Knowledge QA should prefer this JSON index as its structured reference source.
- If no active JSON index exists, fallback to existing content-based QA behavior.
```

First implementation can use the JSON index as a deterministic reference template and does not need embeddings yet.

Do not implement vector DB or embedding in this task.

## 8. JSON Validation

Manual upload should validate:

```text
schemaVersion === smartbook-pdf-index-v1
bookId matches current book or can be explicitly accepted with warning
fileId exists or can be treated as external uploaded JSON
level is one of page/chapter/clause/line/sentence
items is an array
items include pageStart/pageEnd/text/charCount
source.pageNumberMode === pdf_physical_page
```

Reject invalid JSON with clear error.

## 9. Delete Behavior

Delete should:

```text
- Delete only the stored JSON index artifact.
- Never delete the source PDF.
- If deleting the active QA reference, clear active reference and fallback to existing QA behavior.
- Ask for UI confirmation before delete.
```

## 10. Non-goals

Do not implement:

```text
vector DB
embedding pipeline
background jobs
OCR
LLM-based segmentation
payment or credit changes
student reader PDF.js changes
admin account/security changes
```

## 11. Expected Files

Likely files:

```text
apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/server/index.ts
packages/db/src/schema.ts if role/storage schema is needed
packages/db/src/migrate.ts if schema change is needed
packages/db/src/repositories/bookFile.repo.ts or new repo if needed
packages/schema/src/pdfIndex.schema.ts if upload validation schema is extended
```

Keep changes narrowly scoped.

## 12. Verification

Run:

```bash
pnpm build
pnpm typecheck
git diff --name-only
git diff --stat
```

Manual verification:

```text
1. Generate JSON index.
2. Click Save as QA Reference.
3. Confirm stored JSON appears in JSON Index / QA Reference list.
4. Confirm active badge appears.
5. Refresh page; stored JSON remains.
6. Upload a valid JSON index manually.
7. Set uploaded JSON as active QA reference.
8. View and download stored JSON.
9. Delete stored JSON.
10. Confirm source PDF remains intact.
11. Confirm QA fallback works if active JSON is deleted.
```

## 13. Final Report

Final report must be in Traditional Chinese.

Include:

```text
- final status
- commit SHA
- whether DB/migration changed
- generated JSON persistence behavior
- manual upload behavior
- delete behavior
- active QA reference behavior
- build/typecheck result
- git status
- merge/deploy status
```
