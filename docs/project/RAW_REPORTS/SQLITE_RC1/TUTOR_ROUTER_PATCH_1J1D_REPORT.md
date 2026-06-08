# TutorRouter Patch 1J1D

> **Phase 1-J.1d — Boolean batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/tutorRouter.ts`

## Scope

Only DB boolean convention issues were handled:

- boolean `1/0` DB writes
- `eq(col, 1)`
- `eq(col, 0)`

No JSON, timestamp, raw SQL cleanup, db.execute cleanup, schema, db.ts, package.json, runtime wiring, or other router changes were made.

## Boolean Write Fixes

Fixed **15** DB boolean writes:

- `tutorSubjects.isEnabled` x3
- `bookCustomSuggestions.isActive` x2 raw insert values
- `tutorChatSessions.isHiddenByUser` x3
- `practiceWrongBook.isResolved` x3
- `aiClassroomRecords.isCompleted` x1
- `aiClassroomLessons.isEdited` x4

Patterns changed:

- `1` -> `true`
- `0` -> `false`
- `condition ? 1 : 0` -> `!!condition`

## Boolean Compare Fixes

Fixed **19** DB boolean comparisons:

- `tutorSubjects.isEnabled`
- `smartBookChapterQA.isRecommended`
- `smartBookUnitQA.isActive`
- `bookCustomSuggestions.isActive`
- `smartBooks.isPublic`
- `smartBookChapters.isEnabled`
- `tutorChatSessions.isHiddenByUser`
- `lessonPoints.isPublished`
- `practiceWrongBook.isResolved`

Patterns changed:

- `eq(col, 1)` -> `eq(col, true)`
- `eq(col, 0)` -> `eq(col, false)`

## Kept Non-DB 1/0

Remaining `1/0` grep matches are not DB boolean convention blockers. They are numeric values such as:

- `sortOrder`
- `questionCount`
- `fetchCount`
- `messageCount`
- `page`
- `hitCount`
- `wrongCount`
- `knowledgePointIndex`
- `totalQuestions`
- `correctCount`
- response counts / empty result counts / delete counts

These were intentionally kept.

## Grep Results

Command:

```text
rg -n "\?\s*1\s*:\s*0|eq\([^\n]+,\s*1\)|eq\([^\n]+,\s*0\)|:\s*1\b|:\s*0\b" server/routers/tutorRouter.ts
```

Result:

```text
Remaining matches are all non-DB numeric usage.
No eq(col, 1), eq(col, 0), or DB boolean writes remain.
```

Positive patched examples:

```text
isEnabled: true
eq(tutorSubjects.isEnabled, true)
eq(smartBookChapterQA.isRecommended, true)
eq(smartBookChapterQA.isRecommended, false)
eq(tutorChatSessions.isHiddenByUser, false)
.set({ isHiddenByUser: true })
isResolved: false
.set({ isResolved: true, ... })
isCompleted: !!input.isCompleted
isEdited: true / false
```

## Smoke Test

Disposable SQLite smoke:

- Created `/tmp/tutor-router-1j1d-smoke.db`
- Verified boolean write true round-trip
- Verified boolean write false round-trip
- Verified `eq(..., true)` filter
- Verified `eq(..., false)` filter
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_BOOLEAN_SMOKE_PASS trueRoundTrip=1 falseRoundTrip=1 trueFilter=1 falseFilter=1 leftovers=0
```

Import check:

```text
IMPORT_OK
```

## SQLite Leftovers Check

No SQLite DB artifacts remain from the smoke test:

- `/tmp/tutor-router-1j1d-smoke.db`: absent
- `/tmp/tutor-router-1j1d-smoke.db-wal`: absent
- `/tmp/tutor-router-1j1d-smoke.db-shm`: absent
- workspace `*.db`, `*.db-wal`, `*.db-shm`: none found

## Modified Files

This phase modified only:

- `server/routers/tutorRouter.ts`
- `TUTOR_ROUTER_PATCH_1J1D_REPORT.md`

The wider working tree already contains prior migration artifacts and previous phase changes.

## Recommendation

Proceed to **Phase 1-J.1e JSON + Timestamp Batch**.

The next batch should only handle JSON convention and timestamp convention issues, without mixing raw SQL cleanup, db.execute cleanup, schema work, or runtime wiring.
