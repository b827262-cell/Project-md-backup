# SQLite Index Patch Report

> **Phase 1-D.3 — Schema Optimization Only**
> Applied: 2026-06-03 · Branch: `release/vps-lite`

## Summary

| Item | Value |
|------|-------|
| Tables | **66** (unchanged) |
| Indexes before | 0 |
| Indexes after | **16** |
| Timestamp defaults | **25** (unchanged) |
| TODO timestamp markers | **42** (unchanged) |
| Runtime changed | No |
| DB created | No |
| Migration executed | No |

## Added Indexes

| # | Index Name | Table | Column(s) | Type |
|---|-----------|-------|-----------|------|
| 1 | `idx_users_openId` | `users` | `openId` | Single |
| 2 | `idx_users_email` | `users` | `email` | Single |
| 3 | `idx_conversations_userId` | `conversations` | `userId` | Single |
| 4 | `idx_conversations_lastMessageAt` | `conversations` | `lastMessageAt` | Single |
| 5 | `idx_messages_conversationId` | `messages` | `conversationId` | Single |
| 6 | `idx_smart_books_public_status` | `smart_books` | `isPublic, processingStatus` | Composite |
| 7 | `idx_sbc_bookId` | `smart_book_chapters` | `bookId` | Single |
| 8 | `idx_sbconv_bookId_userId` | `smart_book_conversations` | `bookId, userId` | Composite |
| 9 | `idx_sbp_bookId_userId` | `smart_book_progress` | `bookId, userId` | Composite |
| 10 | `idx_lp_bookId_chapterId` | `lesson_points` | `bookId, chapterId` | Composite |
| 11 | `idx_lprog_userId_chapterId` | `lesson_progress` | `userId, chapterId` | Composite |
| 12 | `idx_sbrq_bookId_chapterId` | `smart_book_review_questions` | `bookId, chapterId` | Composite |
| 13 | `idx_sbwa_userId_bookId` | `smart_book_wrong_answers` | `userId, bookId` | Composite |
| 14 | `idx_tcs_userId` | `tutor_chat_sessions` | `userId` | Single |
| 15 | `idx_tcs_smartBookId` | `tutor_chat_sessions` | `smartBookId` | Single |
| 16 | `idx_tcm_sessionId` | `tutor_chat_messages` | `sessionId` | Single |

**Tables modified: 13** (users, conversations, messages, smart_books, smart_book_chapters, smart_book_conversations, smart_book_progress, lesson_points, lesson_progress, smart_book_review_questions, smart_book_wrong_answers, tutor_chat_sessions, tutor_chat_messages)

**Index form used:** Drizzle 0.44.x array callback `(table) => [index(...).on(...)]`

## Unchanged

- All column definitions — untouched
- All timestamp defaults — untouched (25 strftime)
- All TODO markers — untouched (42 remaining)
- Zero changes to `server/db.ts`, `server/db.sqlite.ts`, `package.json`, any router

## Verification

```
grep -c "index(" schema.sqlite.mvp.ts                →  16  ✅
grep -c "sqliteTable(" schema.sqlite.mvp.ts           →  66  ✅
grep -c "strftime('%s','now')" schema.sqlite.mvp.ts   →  25  ✅
grep -c "TODO SQLite timestamp" schema.sqlite.mvp.ts  →  42  ✅
git diff --name-only                                  →  (empty) ✅
```

## Schema Hardening Status

| Hardening Area | Target | Current | Status |
|----------------|--------|---------|--------|
| Tables | 66 | 66 | ✅ Complete |
| Timestamp defaults (P0 Critical) | 25 | 25 | ✅ Complete |
| Must-Add indexes | 16 | 16 | ✅ **Complete** |
| TODO timestamp markers (P1/P2/Defer) | 0 | 42 | ⚠️ Not blocking Phase 1-E |
| High-priority indexes | 14 | 0 | Deferred to post-launch |

## Ready For

**Phase 1-E.0 — SQLite Runtime Activation Planning**

All pre-Phase-1-E schema hardening is now complete:
- ✅ 66 tables defined
- ✅ 25 P0/P1 timestamp defaults applied
- ✅ 16 Must-Add indexes defined
- ✅ `server/db.sqlite.ts` design draft exists

Next step: Plan `better-sqlite3` installation and begin runtime wiring.
