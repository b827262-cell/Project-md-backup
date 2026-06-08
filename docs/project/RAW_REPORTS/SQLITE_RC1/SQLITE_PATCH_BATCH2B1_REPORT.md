# SQLite Schema Patch — Batch 2B-1 Report

> **Phase 1-C.9b Batch 2B-1 — Core Timestamp Expansion**
> Applied: 2026-06-03 · Branch: `release/vps-lite`

## Summary

| Item | Value |
|------|-------|
| Tables remain | **66** |
| Timestamp defaults before | 5 |
| Timestamp defaults after | **15** |
| Indexes added | **0** |
| TODO timestamp markers | 62 → **52** (−10) |
| Runtime changed | No |
| DB created | No |
| Migration executed | No |

## Modified Columns

All 10 are core SmartBook + Lesson `createdAt` columns. Each was a bare `integer("created_at")` (Convention A, originally `sql\`CURRENT_TIMESTAMP\``); per approved patch Part 2b, both `{ mode: "timestamp" }` and the default were applied.

| # | Table | Variable | Column | Category |
|---|-------|----------|--------|----------|
| 1 | `smart_book_categories` | `smartBookCategories` | `created_at` | A. SmartBook |
| 2 | `smart_books` | `smartBooks` | `created_at` | A. SmartBook |
| 3 | `smart_book_chapters` | `smartBookChapters` | `created_at` | A. SmartBook |
| 4 | `smart_book_conversations` | `smartBookConversations` | `created_at` | A. SmartBook |
| 5 | `smart_book_chapter_qa` | `smartBookChapterQA` | `created_at` | A. SmartBook |
| 6 | `smart_book_credit_transactions` | `smartBookCreditTransactions` | `created_at` | A. SmartBook |
| 7 | `smart_book_unit_qa` | `smartBookUnitQA` | `created_at` | A. SmartBook |
| 8 | `smart_book_saved_messages` | `smartBookSavedMessages` | `created_at` | A. SmartBook |
| 9 | `lesson_points` | `lessonPoints` | `created_at` | D. Lesson |
| 10 | `lesson_progress` | `lessonProgress` | `created_at` | D. Lesson |

Each change:
```
- createdAt: integer("created_at"), // TODO SQLite timestamp default strategy (was sql`CURRENT_TIMESTAMP`)
+ createdAt: integer("created_at", { mode: "timestamp" }).default(sql`(strftime('%s','now'))`), // Phase 1-C.9b Batch 2B-1 — Unix seconds, DEFAULT(strftime('%s','now'))
```

## Unchanged

- All `updatedAt`, `completedAt`, `publishedAt`, `reviewedAt`, `lastMessageAt`, etc. — untouched
- All Convention B ms-timestamp columns — untouched
- Zero index definitions added
- Zero changes to `server/db.ts`, `drizzle/schema.ts`, runtime

## Verification

```
grep -c "sqliteTable(" schema.sqlite.mvp.ts          → 66   ✅
grep -c "strftime('%s','now')" schema.sqlite.mvp.ts  → 15   ✅ (5 + 10)
grep -c "index(" schema.sqlite.mvp.ts                →  0   ✅
grep -c "TODO SQLite timestamp" schema.sqlite.mvp.ts → 52   ✅ (62 − 10)
grep -c "Batch 2B-1" schema.sqlite.mvp.ts            → 10   ✅ (all createdAt)
```

## Ready For

**Batch 2B-2 — Remaining Timestamp Defaults** (27 Convention A createdAt/equivalent columns remaining toward the 42-column target; balance are app-side `updatedAt`/conditional timestamps that keep their comments only)
