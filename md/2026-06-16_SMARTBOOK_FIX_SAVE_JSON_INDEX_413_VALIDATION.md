# 2026-06-16 SmartBook Save JSON Index 413 修復驗收紀錄

## 驗收對象

- Feature: FIX_SAVE_JSON_INDEX_413_AND_KEEP_MD_QA_FLOW
- Code commit: cf8f292
- Result: SUCCESS / AGY PASS

## 狀態碼

```text
SAVE_JSON_INDEX_413_FIX_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
NO_DB_MIGRATION_REQUIRED
MANUAL_MARKDOWN_QA_PRESERVED
SERVER_SIDE_JSON_GENERATION_ENABLED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

## 問題背景

手動瀏覽器驗證曾出現：

```text
POST /api/admin/books/:bookId/files/:fileId/save-json-index
413 Payload Too Large
```

根因是前端把整包 JSON index 傳回後端。sentence level JSON 可達 15611 筆，約 3 MB，超過 Express body limit。

## 修復方式

修正後 Save as QA Reference 不再傳整包 JSON，只傳小型 metadata：

```json
{
  "level": "sentence",
  "setActive": true
}
```

後端自行完成：

1. 驗證 bookId / fileId。
2. 驗證檔案是 PDF source document。
3. 驗證 level。
4. 重新產生 JSON index。
5. 寫入書本 upload 目錄。
6. 建立 book_files role=json_index。
7. setActive=true 時更新 app_settings qa_reference:<bookId>。
8. 回傳 stored summary，不回傳整包 items。

## 驗收結果

| 項目 | 結果 |
|---|---|
| 是否修復 413 Payload Too Large | PASS |
| Save as QA Reference 是否不再送整包 JSON | PASS |
| request body 是否小型化 | PASS，約數十 bytes |
| server 是否自行產生並儲存 JSON | PASS |
| 是否回傳 stored summary 而非 full JSON | PASS |
| Manual Markdown Q&A 是否保留 | PASS |
| Q:/A: Markdown 匯入是否成功 | PASS |
| JSON Index 是否與 Markdown Q&A 分離 | PASS |
| pnpm build | PASS |
| pnpm typecheck | PASS |
| DB migration | 不需要 |
| working tree | clean |

## Runtime Smoke

```text
sentence level Save as QA Reference: PASS
no 413: PASS
JSON artifact persists: PASS
raw JSON download: PASS
manual markdown upload still works: PASS
source PDF remains: PASS
QA fallback: PASS
```

curl 驗證結果：

```text
HTTP/1.1 201 Created
```

回傳摘要包含：

```text
fileSize: 3686217
isActive: true
valid: true
level: sentence
levelLabel: 頂級
itemCount: 15611
pageCount: 943
```

## Manual Markdown Q&A 保留

AGY 確認原本 /qa 頁面的手動 Markdown Q&A 流程未被破壞。

兩者定位如下：

```text
Manual Markdown Q&A = 老師人工整理的標準問答
JSON Index = PDF 自動拆解後的結構化參考資料
```

聊天優先序維持：

```text
手動 Markdown Q&A → 結構化 JSON 索引 → 內容回退
```

## 部署注意事項

- 不需要 DB migration。
- 不需要 pnpm install。
- UPLOAD_DIR 必須可寫。
- JSON 工件應與 PDF 原始檔一併納入備份。
- 大型 PDF 的 server-side JSON generation 仍可能耗時，後續可改成 background job。

## 最終結論

```text
SUCCESS
```

commit cf8f292 可接受為 Save JSON Index 413 修復正式 commit。

目前仍維持：

```text
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

原因是尚未進入正式 merge / deploy 流程。
