# 2026-06-15 SmartBook AGY Validation Task: Persistent JSON Index QA Reference

## 0. Language Rule

```text
All execution-facing inspection, command notes, code review notes, and verification reasoning must be in English.

Only the final termination report must be written in Traditional Chinese.
```

---

## 1. Validation Target

```text
PERSISTENT_JSON_INDEX_QA_REFERENCE_AND_MANUAL_FILE_MANAGEMENT
```

Validate current HEAD.

Codex reported implementation summary:

```text
- bookFileRoleSchema added json_index.
- pdfIndex schema added saveJsonIndexInputSchema and storedJsonIndexSummarySchema/types.
- Server added JSON artifact persistence, active QA reference via app_settings, and Knowledge QA integration.
- Admin API client methods were added.
- FilesTab now has Save as QA Reference and JSON Index / QA Reference management UI.
- JSON artifacts are stored under the book upload directory using book_files role=json_index.
- Active QA reference key uses qa_reference:<bookId> in app_settings.
- Manual JSON upload validates schema and rejects wrong bookId.
- Delete removes only JSON artifact; source PDF remains intact.
- QA uses active JSON index first, then falls back to existing content-based QA.
- pnpm build PASS.
- pnpm typecheck PASS.
- runtime smoke test passed with temp DB.
```

---

## 2. Repository / Commit Inspection

Run first:

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

```text
- If Codex already committed, working tree should be clean and HEAD should be the persistent JSON QA reference commit.
- If changes are uncommitted, validate first and commit only scoped files after PASS.
```

If uncommitted changes exist:

```text
- Do not use git add .
- Stage only scoped files from this feature.
- Commit only after build/typecheck and runtime validation pass.
```

Suggested commit message if commit is still needed:

```bash
git commit -m "feat: persist PDF JSON index as QA reference"
```

---

## 3. Expected Modified Scope

Likely files:

```text
packages/schema/src/bookFile.schema.ts
packages/schema/src/pdfIndex.schema.ts
apps/AI-adm-D1/src/server/index.ts
apps/AI-adm-D1/src/api.ts
apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx
```

Optional if implementation required:

```text
packages/db/src/repositories/bookFile.repo.ts
packages/db/src/repositories/settings.repo.ts
apps/AI-adm-D1/src/styles.css
```

Must not modify unrelated areas:

```text
student PDF.js reader
admin accounts/security
payment/credit/auth
PDF parser physical page logic
chapter builder physical page logic
vector DB / embeddings
OCR
```

---

## 4. Validate Schema and Role

Run:

```bash
rg -n "json_index|bookFileRoleSchema|saveJsonIndexInputSchema|storedJsonIndexSummarySchema|PdfJsonIndex|pdf_physical_page" packages/schema apps packages
```

Expected:

```text
- bookFileRoleSchema supports json_index.
- PDF JSON index schema validates smartbook-pdf-index-v1.
- source.pageNumberMode must remain pdf_physical_page.
- Stored JSON index summary type exists.
```

DB migration expectation:

```text
- No DB migration if role is stored in existing free-text role field and active reference uses app_settings.
- If DB schema/migration was changed, report it clearly.
```

---

## 5. Validate API Endpoints

Run:

```bash
rg -n "save-json-index|json-indexes|set-active-qa-reference|qa_reference|json_index|active.*reference|storedJsonIndex|raw" apps/AI-adm-D1/src/server/index.ts apps/AI-adm-D1/src/api.ts
```

Expected endpoints or equivalent:

```text
POST /api/admin/books/:bookId/files/:fileId/save-json-index
POST /api/admin/books/:bookId/json-indexes/upload
GET  /api/admin/books/:bookId/json-indexes
POST /api/admin/books/:bookId/json-indexes/:indexFileId/set-active-qa-reference
GET  /api/admin/books/:bookId/json-indexes/:indexFileId/raw
DELETE /api/admin/books/:bookId/json-indexes/:indexFileId
```

Validate each endpoint:

```text
- Validates bookId.
- Validates file/index belongs to book.
- Validates role=json_index for JSON index operations.
- Does not delete source PDF.
- Raw endpoint returns application/json or JSON-compatible output.
- Delete active JSON clears active reference.
```

---

## 6. Validate Generated JSON Persistence

Expected:

```text
- After Generate JSON Index, admin can click Save as QA Reference.
- The JSON index is saved as a managed artifact under the book upload directory.
- The managed artifact uses book_files role=json_index.
- Page refresh still shows the saved JSON in JSON Index / QA Reference list.
- Source PDF remains untouched.
```

Manual verification:

```text
1. Open /admin/books/:bookId/files.
2. Generate a JSON index.
3. Click Save as QA Reference.
4. Confirm stored JSON appears in JSON Index / QA Reference section.
5. Refresh page.
6. Confirm stored JSON remains.
7. Confirm active QA Reference badge appears if setActive=true.
```

---

## 7. Validate Manual JSON Upload

Expected validation:

```text
- schemaVersion must be smartbook-pdf-index-v1.
- level must be page/chapter/clause/line/sentence.
- items must be an array.
- items must include pageStart/pageEnd/text/charCount.
- source.pageNumberMode must be pdf_physical_page.
- bookId mismatch must be rejected with 400 or a clear error.
```

Manual verification:

```text
1. Upload a valid JSON index for the current book.
2. Confirm upload succeeds and appears in the list.
3. Upload JSON with wrong bookId.
4. Confirm server rejects with 400.
5. Upload invalid JSON.
6. Confirm server rejects with clear error.
```

---

## 8. Validate Active QA Reference Behavior

Run:

```bash
rg -n "qa_reference|active.*json|json_index|Knowledge QA|structured index|content fallback|fallback|chapterTitle|pageStart|pageEnd" apps/AI-adm-D1/src/server/index.ts
```

Expected:

```text
- Each book can have one active JSON index reference.
- Active reference is stored in app_settings key qa_reference:<bookId> or equivalent.
- Knowledge QA prefers active JSON index items as structured reference.
- If active JSON index has no match, fallback to existing content-based QA.
- If active JSON is deleted, active reference is cleared and QA falls back.
- Response includes PDF physical page references such as P1 or P1-3 when using JSON index.
```

Manual/runtime validation:

```text
1. Set a JSON index as active QA reference.
2. Ask a Knowledge QA question that should match JSON index text.
3. Confirm response uses structured JSON index and includes physical PDF page reference.
4. Delete active JSON index.
5. Ask again.
6. Confirm fallback to existing content-based QA.
```

---

## 9. Validate Delete Behavior

Expected:

```text
- Delete removes only JSON index artifact.
- Delete never removes the source PDF file or source_document row.
- If the deleted JSON is active, active reference becomes null.
- UI asks for confirmation before delete.
```

Manual/runtime validation:

```text
1. Save or upload JSON index.
2. Set as active QA reference.
3. Delete it.
4. Confirm activeId becomes null.
5. Confirm source PDF row remains.
6. Confirm PDF parse/content/outline actions still exist.
```

---

## 10. Validate Files Page UI

Run:

```bash
rg -n "Save as QA Reference|JSON Index / QA Reference|Upload JSON|Set as QA Reference|Active QA Reference|View JSON|Download JSON|Delete JSON|json-index" apps/AI-adm-D1/src/pages/tabs/FilesTab.tsx apps/AI-adm-D1/src/styles.css
```

Expected:

```text
- Save as QA Reference appears in generated JSON result area.
- JSON Index / QA Reference management section exists.
- Manual upload UI exists.
- Stored JSON list exists.
- Set/View/Download/Delete actions exist.
- Active badge is visible for active index.
```

---

## 11. Build / Typecheck

Run:

```bash
pnpm build
pnpm typecheck
```

Expected:

```text
pnpm build: PASS
pnpm typecheck: PASS
```

---

## 12. Runtime Smoke Test

If local server is available, validate at least:

```text
- save-json-index with setActive=true creates a JSON artifact and activeId.
- list json-indexes returns the new artifact and activeId.
- wrong-book upload returns 400.
- valid upload returns 201 or equivalent success.
- raw returns JSON.
- delete active returns success and clears activeId.
- source PDF row remains.
- QA with active JSON uses structured index.
- QA after delete falls back to content-based QA.
```

---

## 13. Final Termination Report

Final report must be in Traditional Chinese only.

Use this format:

```md
## AGY 驗收回報

- 最終狀態：
  - PASS / PASS_WITH_NOTES / PARTIAL_SUCCESS / FAIL / BLOCKER / PERMISSION-HALT

- 驗收對象：
  - PERSISTENT_JSON_INDEX_QA_REFERENCE_AND_MANUAL_FILE_MANAGEMENT

- commit SHA：
  - <short SHA>

- 實際修改檔案：
  - <file list>

- git status --short：
  ```text
  <paste output>
  ```

- 是否 working tree clean：
  - 是 / 否

- JSON index 持久化：
  - 產生後是否可 Save as QA Reference：
  - 是否寫入受管工件：
  - 是否 refresh 後保留：
  - 是否未覆寫 source PDF：

- 手動上傳 JSON：
  - Upload JSON 是否存在：
  - schemaVersion 驗證：
  - bookId mismatch 是否拒絕：
  - invalid JSON 是否拒絕：

- JSON Index / QA Reference 管理：
  - list 是否存在：
  - active badge：
  - Set as QA Reference：
  - View JSON：
  - Download JSON：
  - Delete JSON：

- QA reference 行為：
  - active JSON 是否優先於 content-based QA：
  - 回覆是否包含 PDF physical page：
  - 刪除 active 後是否 fallback：

- Delete 行為：
  - 是否只刪 JSON 工件：
  - 是否不刪 source PDF：
  - active 被刪時是否清除 activeId：

- Storage / schema：
  - book_files role=json_index：
  - active reference storage：
  - 是否使用 app_settings：
  - 是否需要 DB migration：

- 是否有修改後端：
  - 是 / 否

- 是否有修改 DB / migration：
  - 是 / 否

- 是否混入 unrelated 變更：
  - 否；若有請列出

- build/typecheck：
  - pnpm build：
  - pnpm typecheck：

- runtime smoke：
  - save-json-index：
  - list activeId：
  - wrong-book upload 400：
  - valid upload：
  - raw JSON：
  - delete active：
  - source PDF remains：
  - QA active JSON：
  - QA fallback：

- 部署注意事項：
  - 是否需 DB migration：
  - 是否需 pnpm install：
  - UPLOAD_DIR 是否需可寫：
  - JSON 工件是否需納入備份：

- commit 狀態：
  - 若本次尚未 commit，PASS 後是否已 commit：
  - commit message：

- 合併 / 部署狀態：
  - NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY

- 結論：
  - <一句話說明此 commit 是否可接受，以及 embedding/vector pipeline 是否仍需另開任務>
```

---

## 14. Judgment Rule

Use:

```text
PASS
```

if:

```text
- JSON can be saved as persistent artifact.
- Manual upload works and validates schema.
- Active QA reference works and fallback works.
- Delete is safe and does not delete source PDF.
- build/typecheck pass.
- scoped commit exists or is created after validation.
```

Use:

```text
PASS_WITH_NOTES
```

if:

```text
- Core works, but QA matching is deterministic/basic and not embedding-based.
- JSON artifacts are file-based and require UPLOAD_DIR backup.
```

Use:

```text
FAIL
```

if:

```text
- JSON is not persisted after refresh.
- Wrong-book upload is accepted silently.
- Deleting JSON deletes source PDF.
- Active QA reference is not used by Knowledge QA.
- build/typecheck fails.
```
