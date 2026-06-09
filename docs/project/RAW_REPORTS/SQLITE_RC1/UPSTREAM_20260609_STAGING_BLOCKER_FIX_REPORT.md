# UPSTREAM 20260609 — Staging Blocker Fix Report

**日期**：2026-06-09
**分支**：release/vps-lite
**HEAD**：cde0f9de
**模式**：SmartBook Lite / SQLite RC1 輕量修補
**範圍來源**：
- `docs/project/upstream/UPSTREAM_20260609_TOC_ASSIST_SMOKE_TEST_PASSED_STAGING_BLOCKED.md`
- `docs/project/sqlite/SQLITE_SCHEMA_COMPAT_MATRIX_20260609.md`

---

## 1. 兩份報告摘要

### 1.1 TOC Assist Smoke Test（已通過事項 — 不重修）

| 項目 | 狀態 |
|------|------|
| `/tutor`、`/admin/smart-books` 頁面 | ✅ 正常 |
| UploadBookDialog 目錄截圖輔助（預設收合） | ✅ |
| AI 偵測大綱 / AI 建立章節按鈕 | ✅ |
| paste zone / Ctrl+V 貼圖 / 縮圖 / 全部清除 | ✅ |
| 章節結構層級選項、AI Vision 圖像分析開關 | ✅ |
| `previewOutline.mutate` count=1 / `showTocAssist` count=4 / AI Vision label count=1 | ✅ |
| TypeScript 無「新增」TOC Assist 相關錯誤 | ✅ |

> **TOC_ASSIST_ALREADY_PASSED = YES**。本輪不觸碰任何已通過的 TOC Assist UI 區塊。

### 1.2 Staging Blocker 直接原因

報告記錄的 blocker 是 **git staging 操作層級**問題（`git add -p AdminSmartBooks.tsx` 兩次 `git apply failed`，diff hunk 混合多 phase），**非程式碼錯誤**。
唯一的程式碼層級風險來自 schema/runtime port 後的型別轉換：`smartBookRouter.ts:1011` 的 SQLite table 物件 cast 缺少 `as unknown` 中間轉換，導致 `TS2352` conversion error（SQLite `SQLiteTableWithColumns` ↔ MySQL `MySqlTableWithColumns` 不重疊）。

### 1.3 Schema Compat Matrix 對照結果

| 欄位 | SQLite schema 現況 | migration | 結論 |
|------|-------------------|-----------|------|
| `smart_books.show_in_tutor_home` | ✅ 已加（schema L239） | ✅ `0001_show_in_tutor_home.sql` | 與 router runtime 一致，無 blocker |
| Batch A 其餘欄位（`*_enabled`、`toc_code`、`subject_focus`、`structure_level` 等） | ❌ 尚未加 | ❌ | router runtime **未引用** → 非本輪 blocker（屬 Batch A 後續 port PR） |

> Matrix Part 5 結論：現有 `isSqliteMode` 架構健全，router 已有分支機制。本輪 runtime patch 只觸及 `show_in_tutor_home` + table 物件切換，與已加的 schema 欄位一致。

---

## 2. 修補計畫與風險

| Blocker / Mismatch | 對應檔案 | 風險 | 處置 |
|--------------------|---------|------|------|
| `smartBookRouter.ts:1011` cast 缺 `unknown`（TS2352） | `server/routers/smartBookRouter.ts` | LOW | **修**（精準字串替換，與檔內既有 9 處 `as unknown as typeof` 模式一致） |
| `smartBookRouter.ts:1014`、`:3032` 同類 cast | `server/routers/smartBookRouter.ts` | LOW | **修**（一併校正，避免下次觸發） |
| Date → string\|SQL（TS2322）等 72 個 | `server/routers/*` | — | **不修**（既有類別，HEAD 已有 14 處 `new Date()`；esbuild build 不檢型別） |
| Batch A 欄位 port | schema + migration | MEDIUM | **不做**（非本輪 blocker，需另立 schema port PR） |
| git staging 混合 hunk | working tree | — | **不自動 staging**（依原報告 Current Decision，保留 working tree） |

---

## 3. 實作的最小 Patch

**檔案**：`server/routers/smartBookRouter.ts`
**方式**：Python 精準字串替換（依既有偏好不使用 Edit tool），各替換 1 次，不改 ternary 結構。

```diff
- ? (sqliteSmartBooks as typeof smartBooks)
+ ? (sqliteSmartBooks as unknown as typeof smartBooks)

- ? (sqliteSmartBookChapters as typeof smartBookChapters)
+ ? (sqliteSmartBookChapters as unknown as typeof smartBookChapters)

- ? (sqliteSmartBookCategories as typeof smartBookCategories)
+ ? (sqliteSmartBookCategories as unknown as typeof smartBookCategories)
```

**理由**：SQLite drizzle table 物件型別與 MySQL schema 型別不重疊，TypeScript 要求經 `unknown` 中間轉換。檔內其餘 9 處同類 cast 已正確使用此模式，本次 3 處為遺漏，校正後一致。runtime 行為不變（`isSqliteMode()` 分支與插入值皆未動）。

**未改動**：package.json、schema、migration、TOC Assist UI、UploadWithOutline、BookSettingsDialog、Home catalog 邏輯。

---

## 4. 驗證

| 命令 | 結果 |
|------|------|
| `pnpm build`（vite + esbuild，實際 build 路徑） | ✅ **PASS**（`dist/index.js 2.9mb`，僅既有 duplicate-key warnings） |
| `pnpm tsc --noEmit`（風險定位用，非 build gate） | `smartBookRouter.ts` 72 errors，**TS2352@1011 已消失** |
| 殘留舊 cast grep | `NO_STALE_CAST`，`as unknown as typeof` 共 9 處 |

> esbuild 不做型別檢查，剩餘 72 個 tsc 錯誤屬既有類別（Date/SQL、TextContent 陣列），不阻塞 build，與本 staging blocker 無關。

---

## 5. 尚未解決 / 後續事項

- **Batch A schema port**（7 個 `*_enabled`、`toc_code`、`subject_focus`、`structure_level`、`teacher_bio`、`md_shared_search` 等）：需另立 schema port PR（ALTER COLUMN + 更新 `schema.sqlite.mvp.ts` + 新 migration），本輪不做。
- **git staging 混合 hunk**：working tree 仍混多 phase（TOC Assist + categories + showInTutorHome）。建議依原報告 Next Safe Option，於乾淨 branch 分批 commit。
- **既有 72 個 tsc 型別錯誤**：屬 SQLite port 的 `new Date()` vs MySQL schema 型別既有成本，全專案 1360 錯誤的子集，非本輪範圍。

## Arbitration Update

Later hunk analysis confirmed the cast changes cannot be staged as a standalone minimal commit.

- CAST_FIX_SAFE = YES
- CAST_ONLY_COMMIT_SAFE = NO
- HUNK_MIXED = YES
- CAN_STAGE_CAST_ONLY = NO

Reason:
The `as unknown as typeof ...` corrections are embedded inside the larger `smartBookRouter.ts` SQLite runtime port hunks. They are not independent committed-line edits. A cast-only commit would require manual patch splitting and risks recreating the earlier git apply failure.

Commit strategy changed:
Do not commit this report alone. Do not commit cast-only. Treat `server/routers/smartBookRouter.ts` SQLite runtime port as one reviewable phase, or recreate it cleanly on a fresh branch.

---

## 6. 完成條件

```text
TOC_ASSIST_ALREADY_PASSED = YES
STAGING_BLOCKER_IDENTIFIED = YES  (git staging 層級 + 1011 cast 型別錯誤)
SCHEMA_MATRIX_CHECKED = YES
PATCH_SCOPE_MINIMAL = YES  (僅 3 行 cast 校正)
PACKAGE_JSON_CHANGED = NO
PNPM_BUILD_RESULT = PASS
SMOKE_TEST_RESULT = PARTIAL_WITH_REASON
  (TOC Assist 瀏覽器 smoke 已於前報告通過；本輪僅做 build 驗證，未重啟 dev server 重跑 UI smoke)
READY_FOR_REVIEW = YES
```

> **READY_FOR_REVIEW = YES**：可進入下一輪 Sonnet review / GPT-5.5 arbitration。
> 建議 review 聚焦：① 3 處 cast 校正是否需一併處理 Batch A schema port；② working tree 分批 commit 策略。
