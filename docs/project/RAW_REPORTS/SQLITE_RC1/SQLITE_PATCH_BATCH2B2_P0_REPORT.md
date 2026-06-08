# SQLite Schema Patch — Batch 2B-2 P0 Report

> **Phase 1-C.9b Batch 2B-2 — P0 Critical Timestamp Defaults**
> Applied: 2026-06-03 · Branch: `release/vps-lite`

## Summary

| Item | Value |
|------|-------|
| Tables remain | **66** |
| Timestamp defaults before | 15 |
| Timestamp defaults after | **25** (+10) |
| Indexes added | **0** |
| TODO timestamp markers | 52 → **42** (−10) |
| Runtime changed | No |
| DB created | No |
| Migration executed | No |

## Modified Columns

### Diff Type A — Add `.default(sql`(strftime('%s','now'))`)` only (3 columns)

These already had `{ mode: "timestamp" }`. Only the default was added.

| # | Table | Variable | Column | Line |
|---|-------|----------|--------|------|
| 1 | `credit_transactions` | `creditTransactions` | `createdAt` | 143 |
| 2 | `user_usage_stats` | `userUsageStats` | `createdAt` | 171 |
| 3 | `saved_qa` | `savedQa` | `created_at` | 1006 |

Each change:
```diff
- createdAt: integer("createdAt", { mode: "timestamp" }), // TODO SQLite timestamp default strategy
+ createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(strftime('%s','now'))`), // Phase 1-C.9b Batch 2B-2 — Unix seconds, DEFAULT(strftime('%s','now'))
```

### Diff Type B — Add `{ mode: "timestamp" }` + `.default(sql`(strftime('%s','now'))`)` (7 columns)

These were bare `integer()` — both mode and default were added.

| # | Table | Variable | Column | Line | Router |
|---|-------|----------|--------|------|--------|
| 4 | `smart_book_unit_qa_answers` | `smartBookUnitQAAnswers` | `answered_at` | 368 | smartBookLearningRouter |
| 5 | `smart_book_learning_sessions` | `smartBookLearningSessions` | `started_at` | 376 | smartBookLearningRouter |
| 6 | `smart_book_chapter_daily_verifications` | `smartBookChapterDailyVerifications` | `verified_at` | 390 | smartBookRouter, smartBookLearningRouter |
| 7 | `smart_book_chapter_completions` | `smartBookChapterCompletions` | `completed_at` | 401 | smartBookLearningRouter |
| 8 | `smart_book_review_questions` | `smartBookReviewQuestions` | `created_at` | 482 | smartBookRouter, smartBookLearningRouter, tutorRouter |
| 9 | `smart_book_wrong_answers` | `smartBookWrongAnswers` | `created_at` | 499 | smartBookRouter |
| 10 | `smart_book_qa_viewed` | `smartBookQAViewed` | `created_at` | 531 | smartBookRouter |

Each change:
```diff
- createdAt: integer("created_at"), // TODO SQLite timestamp default strategy (was sql`CURRENT_TIMESTAMP`)
+ createdAt: integer("created_at", { mode: "timestamp" }).default(sql`(strftime('%s','now'))`), // Phase 1-C.9b Batch 2B-2 — Unix seconds, DEFAULT(strftime('%s','now'))
```

## Unchanged

- All `updatedAt`, `lastMessageAt`, `lastActiveAt`, `lastSignedIn`, `flaggedAt`, `reviewedAt` — untouched
- All Convention B ms-timestamp columns — untouched
- All P1 / P2 / Defer columns — untouched
- Zero index definitions added
- Zero changes to `server/db.ts`, `drizzle/schema.ts`, runtime

## Verification

```
grep -c "sqliteTable(" schema.sqlite.mvp.ts          → 66   ✅
grep -c "strftime('%s','now')" schema.sqlite.mvp.ts  → 25   ✅ (15 + 10)
grep -c "index(" schema.sqlite.mvp.ts                →  0   ✅
grep -c "TODO SQLite timestamp" schema.sqlite.mvp.ts → 42   ✅ (52 − 10)
grep -c "Batch 2B-2" schema.sqlite.mvp.ts            → 10   ✅ (all P0)
```

## Cumulative Progress

| Batch | Columns Patched | Total strftime | TODO Remaining |
|-------|-----------------|----------------|----------------|
| Batch 2A | 5 (core createdAt) | 5 | 62 |
| Batch 2B-1 | 10 (SmartBook + Lesson createdAt) | 15 | 52 |
| **Batch 2B-2** | **10 (P0 Critical)** | **25** | **42** |

## Remaining 42 TODO Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| P1 createdAt (need default) | 12 | Write-once columns in optional/admin tables |
| P1 mode-only (no default) | 3 | `lastActiveAt`, `savedMessages.updatedAt`, `questionShown.updatedAt` |
| P1/P2 updatedAt (comment only) | 21 | App-side columns, need TODO → comment cleanup |
| Defer | 6 | Dormant tables, no router references |
| **Total** | **42** | |

## Ready For

**Phase 1-D — Runtime Wiring Preparation**

All P0 Critical timestamp defaults are now in place. The 42 remaining TODOs are:
- **Not blocking Phase 1-E** — they are updatedAt (app-side), optional, admin, or dormant
- Can be addressed in a P1 cleanup pass or deferred to production hardening
