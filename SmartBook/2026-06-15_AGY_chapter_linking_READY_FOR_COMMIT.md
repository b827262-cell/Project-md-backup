# SmartBook AGY 驗收整理：章節頁碼、內容連結與章節問答

日期：2026-06-15  
專案：AI-SmartBook-R1 / SmartBook 章節管理與知識問答  
分支：`feat/student-category-cover-reader-chat`  
AGY 驗收 Commit 基準：`c2b117e`，但當時 working tree 仍有 modified 檔案  
測試環境：本地端 `127.0.0.1:4300` / `127.0.0.1:5174`

---

## 1. 最終整理判定

AGY 功能驗收結果可接受，但不建議直接以 `READY` 作為最終合併或部署結論。

較精準狀態應為：

```text
READY_FOR_COMMIT
尚未 READY_FOR_FINAL_MERGE / DEPLOY
```

原因：

1. 驗收時 Git working tree 仍為 modified，尚未形成乾淨 commit。
2. 本次包含 DB / schema 變更，部署環境需要執行 `pnpm db:push` 或等價 migration。
3. 章節功能變更與先前 appearance / header / hero 外觀變更不可混在同一個 commit。
4. 雖然章節功能實測通過，但部分章節仍因 PDF 相對頁碼與絕對頁碼落差而顯示 unlinked，需後續優化全自動頁碼對應。
5. 驗收主要為 build、typecheck、API 實測，未完成完整 GUI 實機瀏覽器點測。

---

## 2. AGY 驗收結果摘要

| 項目 | 結果 | 說明 |
|---|---|---|
| PDF outline 頁碼結構化 | PASS | `chapter-builder.ts` 已加入 `extractPdfOutline` 與 `parsePageRangeFromTitle`，可解析如 `01-1~37` 的書籤格式，並 fallback 尋找 `node.dest` 頁數。 |
| 後台頁碼顯示 | PASS | `ChaptersPage.tsx` 已將頁碼從 title 抽離，透過 `pageStart–pageEnd` 顯示，不再只有 `—`。 |
| 章節內容連結 | PASS | `linkChaptersByPageRange` 會依頁碼範圍遍歷書本內容並建立關聯。 |
| 手動新增章節 | PASS | 後台章節頁新增輸入列，支援 title、pageStart、pageEnd、level 等欄位。 |
| 手動編輯章節 | PASS | 點擊「編輯」後可切換 input，支援修改 title、pageStart、pageEnd、level。 |
| 手動刪除章節 | PASS | 點擊「刪除」會確認並呼叫 DELETE API，後端會先解除 content 連結。 |
| 重新建立章節 | PASS | 後台已有「重新產生章節」按鈕，觸發 `/build` API，會先清空既有章節避免重複。 |
| 重新連結內容 | PASS | 後台已有「重新連結內容」按鈕，可手動觸發頁碼匹配。 |
| 前台章節目錄 | PASS | `BookReaderPage.tsx` 保留章節目錄支援與導航。 |
| 前台章節問答 | PASS | `ChatPanel.tsx` 已將 `chapterId` 帶入 `studentClient.sendBookChat`。 |
| 未連結提示 | PASS | 後端針對有 `chapterId` 但章節未連結內容時，會回覆「此章尚未建立可問答內容，請回後台重新連結內容。」 |
| build / typecheck | PASS | `pnpm build`、`pnpm typecheck` 通過。 |
| 回歸測試 | PASS | 保留 fallback 到全書查詢邏輯，後台與前台既有功能未受阻礙。 |

---

## 3. API 路由確認

| Method | Path | 結果 | 備註 |
|---|---|---|---|
| GET | `/api/admin/books/:bookId/chapters` | PASS | 回傳 enriched chapters，含 `contentLinkStatus`、`linkedContentCount`、`pageStart`、`pageEnd`、`level`、`source`。 |
| POST | `/api/admin/books/:bookId/chapters` | PASS | 支援新增章節與自訂 `pageStart`、`pageEnd`、`level`。 |
| PATCH | `/api/admin/books/:bookId/chapters/:chapterId` | PASS | 支援修改 `title`、`pageStart`、`pageEnd`、`level`、`sortOrder/orderIndex`。 |
| DELETE | `/api/admin/books/:bookId/chapters/:chapterId` | PASS | 刪除前會使用 `repos.contents.linkChapter(c.id, null)` 解除關聯。 |
| POST | `/api/admin/books/:bookId/chapters/build` | PASS | idempotent 重建章節，先清空既有章節，再 outline / fallback / link。 |
| POST | `/api/admin/books/:bookId/chapters/link-content` | PASS | 呼叫 `linkChaptersByPageRange` 重新連結內容。 |
| POST | `/api/admin/books/:bookId/ai/build-chapters` | PASS | 沿用舊路由，現在也會 link。 |
| POST | `/api/student/books/:bookId/chat` | PASS | 新增 `chapterId`，支援章節範圍問答與未連結提示。 |

---

## 4. DB / Schema 確認

| 項目 | 結果 | 備註 |
|---|---|---|
| `pageStart` / `pageEnd` | PASS | `packages/schema/src/chapter.schema.ts` 已有 `z.number().nullable().optional()`。 |
| `sortOrder` | PASS | 實作中名稱為 `orderIndex`。 |
| `level` | PASS | 已支援章節層級欄位。 |
| `contentId` / `contentLinkStatus` | PASS | 狀態即時計算回傳，不硬寫入 sqlite 靜態欄位，避免資料不一致。 |
| migration / db push | 需要 | 因 schema 有變更，部署正式環境時需要執行 `pnpm db:push` 或等價 migration。 |

---

## 5. 實測證據摘要

### 後台章節頁

- URL：`/admin/books/:bookId/chapters`
- 頁碼欄結果：可看到形如 `1-37` 的獨立頁碼欄位，不再只跟 title 黏在一起。
- 對應內容欄結果：可顯示 `已連結`、`未連結`、`無可用內容`、`頁碼範圍錯誤` 等狀態 badge。
- 手動編修：可切換 input，能成功送出 PATCH，reload 後資料保留。
- 重新產生章節：會先清空既有章節，再重建，避免重複章節。
- 重新連結內容：可手動觸發頁碼範圍與內容重新匹配。

### 前台知識問答

- URL：`/student/books/:bookId`
- ChatPanel 會帶入目前章節 `chapterId`。
- 測試未連結章節時，回應：

```text
此章尚未建立可問答內容，請回後台重新連結內容。
```

- 已連結章節會依章節範圍檢索。
- 未指定章節時仍可 fallback 到 book-level search。

---

## 6. 已知風險與後續優化

### 6.1 相對頁碼與絕對頁碼落差

本次實測真實 PDF 書時，章節 outline 標題使用「每章相對頁」，例如：

```text
第1章 1-37
第2章 1-62
```

但 `book_contents.pageNumber` 是 PDF 絕對頁碼，因此依頁碼自動連結時會有重疊或落差，導致部分章節仍顯示 unlinked。

目前狀態欄能如實反映 linked / unlinked，且管理者可透過手動編輯頁碼與「重新連結內容」修正。

若要全自動精準，後續需要：

1. 優先解析 PDF outline destination 絕對頁碼。
2. 若 pdf-parse 無法回傳數值 dest，需改用更完整的 PDF outline parser。
3. 或建立「章節相對頁 → PDF 絕對頁」校正機制。

### 6.2 多層目錄尚待擴充

目前 outline 主要取 top-level，實測顯示多為 L1。`level` 欄位已保留，未來可支援多層章節目錄。

### 6.3 未完整 GUI 實機點測

本次驗收主要依據：

- `pnpm build`
- `pnpm typecheck`
- API 實測
- 本地端服務驗證

尚未完成完整瀏覽器 GUI 點測，因此合併或部署前仍建議再做一次人工瀏覽器回歸。

### 6.4 系統提示可能被寫入對話紀錄

AGY 發現：

若使用者在未連結章節提問，系統回覆「此章尚未建立可問答內容」後，這段可能仍會透過 `repos.chat.addMessage` 寫入 DB。雖不影響核心功能，但使用者切回全書問答時可能看到阻擋訊息。此項列為 P2 優化。

---

## 7. Commit 策略

本次只應提交「章節資料鏈結 / chapter-content linking / chapter-aware chat」相關檔案。

不要混入：

- appearance 設定
- Header 外觀
- Hero 外觀
- 其他 UI 外觀調整

禁止使用：

```bash
git add .
```

建議流程：

```bash
git diff --name-only
```

人工分類：

```text
chapter / content / chat / schema 相關：納入本次 commit
appearance / header / hero / 外觀設定相關：不要納入本次 commit
```

建議 commit message：

```bash
git commit -m "feat: add editable chapter page ranges and chapter-aware chat linking"
```

commit 後驗證：

```bash
git rev-parse --short HEAD
git status --short
git show --stat --oneline HEAD
```

---

## 8. 給 AGY 的下一步指令

```md
驗收結果接受，但請將最終狀態從 READY 修正為 READY_FOR_COMMIT。

請不要直接合併，也不要把 appearance 相關變更一起提交。

下一步請執行：

1. 列出目前變更檔案：

```bash
git diff --name-only
```

2. 人工分類：
   - chapter / content / chat / schema 相關：納入本次 commit
   - appearance / header / hero / 外觀設定相關：不要納入本次 commit

3. 僅 add 本次章節功能相關檔案，不要使用：

```bash
git add .
```

4. 建立 commit：

```bash
git commit -m "feat: add editable chapter page ranges and chapter-aware chat linking"
```

5. commit 後回報：

```bash
git rev-parse --short HEAD
git status --short
git show --stat --oneline HEAD
```

6. 另外請明確標示部署注意事項：

```text
本次包含 schema/db 變更，部署後需要執行 pnpm db:push 或等價 migration。
```

最後回報：

- 本次 commit SHA
- 實際提交檔案列表
- 是否還有未提交 appearance 變更
- schema/db 是否需要部署更新
- pnpm build / typecheck 是否仍通過
```

---

## 9. 換分頁銜接摘要

若要換新分頁，請在新分頁貼上以下摘要即可接續：

```text
SmartBook 目前章節資料鏈結已由 AGY 驗收通過，功能面包含：PDF outline 頁碼結構化、後台章節手動新增/編輯/刪除、重新產生章節、重新連結內容、前台 ChatPanel 帶 chapterId 進行章節問答，以及未連結章節提示。

但最終狀態應定為 READY_FOR_COMMIT，不是 READY_FOR_FINAL_MERGE，因為 working tree 仍有 modified、schema/db 需 db:push 或 migration、且 appearance 變更不可混入本次 commit。

下一步請 AGY 只提交 chapter/content/chat/schema 相關檔案，不要 git add .，不要混入 appearance/header/hero 外觀變更。commit message 建議：feat: add editable chapter page ranges and chapter-aware chat linking。

commit 後需回報 commit SHA、實際提交檔案、git status、是否仍有 appearance 未提交變更、schema/db 部署注意事項，以及 build/typecheck 是否通過。
```
