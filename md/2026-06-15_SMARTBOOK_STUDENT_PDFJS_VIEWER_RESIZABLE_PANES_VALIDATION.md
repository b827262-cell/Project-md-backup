# 2026-06-15 SmartBook Student PDF.js Viewer / Resizable Panes 驗收紀錄

## 1. 驗收對象

- 專案：AI-SmartBook-R1
- 功能名稱：STUDENT_PDF_READER_RESIZABLE_PANES_AND_RELIABLE_NAV_ZOOM
- commit SHA：`40814f8`
- 技術選擇：PDF.js
- 驗收結果：AGY PASS

---

## 2. AGY 最終驗收判定

```text
PASS
```

整體狀態：

```text
STUDENT_PDFJS_VIEWER_RESIZABLE_PANES_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
PDFJS_DEPENDENCY_ADDED
DEPLOYMENT_PNPM_INSTALL_REQUIRED
DIST_ASSETS_WORKER_DEPLOY_REQUIRED
NO_DB_MIGRATION_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```

---

## 3. 核心結論

AGY 驗收確認：

```text
此 commit 已將學生端 PDF 閱讀器從 native iframe 遷移到 PDF.js canvas rendering。
```

因此已解決前一版 native iframe 的主要問題：

```text
- #page= 章節跳頁不可靠
- #zoom= 縮放不可靠
- React state 改了但 PDF 可視畫面不一定真的變化
```

---

## 4. PDF.js 驗證

| 項目 | 結果 |
|---|---|
| 是否使用 PDF.js | PASS，透過 `ProtectedPdfViewer` 呼叫 PDF.js 渲染 |
| 是否移除 iframe 作為主要閱讀器 | PASS，已由 `<canvas>` 取代舊 iframe |
| pdfjs-dist 版本 | `5.4.296` |
| worker asset 是否正常 | PASS，透過 `?url` 匯入 `pdf.worker.min.mjs`，可被 Vite 正確打包 |

---

## 5. Protected PDF 行為

| 項目 | 結果 |
|---|---|
| 是否仍使用 `/api/student/.../pdf-view` | PASS |
| 是否仍使用 `X-Student-Session-Id` | PASS |
| 是否未使用 `/api/admin/.../raw` | PASS |
| protected endpoint 是否未改 | PASS，後端完全未變動 |

---

## 6. PDF Page Navigation 驗證

| 項目 | 結果 |
|---|---|
| 是否使用 `chapter.pageStart` | PASS |
| 是否以 PDF physical page 為 canonical | PASS |
| 是否由 PDF.js 實際 render 目標頁 | PASS |

AGY 說明：

```text
左側章節列表驅動 pdfPage 的切換，呼叫 doc.getPage(targetPage) 後清除舊任務並精準 render。
```

---

## 7. Zoom 驗證

| 項目 | 結果 |
|---|---|
| 是否支援 50~200% | PASS |
| 是否由 PDF.js scale 控制 | PASS |
| 75/100/125/150/200 實測結果 | PASS |

AGY 說明：

```text
ZOOM_OPTIONS 提供從 50 到 200 的多個級距，並直接控制 getViewport({ scale: zoom / 100 })。
```

這代表縮放已不再依賴 native iframe 的 `#zoom=` fragment。

---

## 8. Resize Panes 驗證

| 項目 | 結果 |
|---|---|
| Chapter/PDF divider | PASS |
| PDF/AI divider | PASS |
| 是否 live resize | PASS |
| 是否 localStorage 持久化 | PASS |
| 是否兼具內部與外側空白分隔線 | PASS |

AGY 確認已使用：

```text
TOC_WIDTH_KEY
AI_WIDTH_KEY
OUTER_LAYOUT_KEY
```

並判定：

```text
兼具內部分隔線（章節/AI）與外側空白分隔線（leftOuter / rightOuter 寬度調整）。
```

因此不需再另開 outer-space resize task。

---

## 9. Collapse Behavior 驗證

| 項目 | 結果 |
|---|---|
| 收合章節 | PASS |
| 展開章節 | PASS |
| 收合AI | PASS |
| 展開AI | PASS |
| PDF 是否展開 | PASS |

AGY 說明：

```text
採用 CSS Grid 及彈性空間設定，不論收合哪側，中央 PDF 畫布區塊均能自動向外展開填滿。
```

---

## 10. Watermark / Notes 驗證

| 項目 | 結果 |
|---|---|
| watermark 是否保留 | PASS |
| 是否不阻擋操作 | PASS，具備 `pointer-events: none` |
| 貼圖筆記狀態 | PASS_WITH_CONTEXT |

貼圖筆記目前狀態：

```text
仍維持提供實體頁資訊草稿功能。
目前尚未直接使用 canvas 截圖，但因已遷移到 PDF.js 生態，後續實作真截圖已具備良好基礎。
```

---

## 11. Build / Typecheck

| 項目 | 結果 |
|---|---|
| pnpm build | PASS |
| pnpm typecheck | PASS |
| git status | working tree clean |
| unrelated 變更 | 無 |

---

## 12. 後端與 DB 狀態

| 項目 | 結果 |
|---|---|
| 是否修改後端 | 否 |
| 是否修改 DB / migration | 否 |
| 是否需要 DB migration | 否 |

---

## 13. 部署備註

此 commit 新增前端依賴：

```text
pdfjs-dist@5.4.296
```

部署前需注意：

1. 部署環境需執行 `pnpm install` 或確保 lockfile 對應依賴已安裝。
2. Vite build 已將 PDF worker asset 獨立打包。
3. 靜態部署時必須一併部署 `dist/assets/pdf.worker...` 相關檔案。
4. 本 commit 不需要 DB migration。

---

## 14. 最終結論

`40814f8` 可接受為 SmartBook 學生端 PDF.js 閱讀器與可拖拉版面正式 commit。

AGY 驗收結果：

```text
PASS
```

目前狀態：

```text
STUDENT_PDFJS_VIEWER_RESIZABLE_PANES_ACCEPTED
COMMIT_ACCEPTED
WORKTREE_CLEAN
AGY_VALIDATION_PASS
PDFJS_DEPENDENCY_ADDED
DEPLOYMENT_PNPM_INSTALL_REQUIRED
DIST_ASSETS_WORKER_DEPLOY_REQUIRED
NO_DB_MIGRATION_REQUIRED
NOT_READY_FOR_FINAL_MERGE_OR_DEPLOY
```
