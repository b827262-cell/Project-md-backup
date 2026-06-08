# SmartBookRouter Patch 1E

> **Phase 1-I.1e — Boolean batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/smartBookRouter.ts`

## Scope

Only DB boolean-mode column writes and comparisons were handled.

No DATE(), INSERT IGNORE, JSON, insertId, datetime, tutorRouter, db.ts, schema, package.json, runtime wiring, or other router changes were made in this phase.

## Changes

### Boolean Writes

Fixed **10** DB boolean-mode writes:

- `smartBooks.isPublic`
- `smartBooks.requireVerification`
- `smartBooks.hasPageNumbers`
- `smartBookChapters.isEnabled`
- `smartBookVerifications.unlockedByAdmin`
- `lessonPoints.needsImage`
- `lessonPoints.isPublished`
- `smartBookConversations.chatAnswered`
- `smartBookWrongAnswers.isLearned` insert
- `smartBookWrongAnswers.isLearned` update

Patterns changed:

- `condition ? 1 : 0` -> `!!condition`
- literal `1` -> `true`
- literal `0` -> `false`

### Boolean Compares

Fixed **16** DB boolean-mode comparisons:

- `eq(..., 1)` -> `eq(..., true)`
- `eq(..., 0)` -> `eq(..., false)`

Covered columns include:

- `smartBookWrongAnswers.isLearned`
- `aiQuestionSources.isPublished`
- `aiGeneratedExams.isPublic`
- `smartBooks.isPublic`
- `smartBookChapters.isEnabled`
- `lessonPoints.isPublished`
- `lessonProgress.completed`

## Grep Results

Remaining DB boolean blocker grep:

```text
rg "\?\s*1\s*:\s*0|eq\([^\n]+,\s*1\)|eq\([^\n]+,\s*0\)|isLearned:\s*[01]\b|isPublished:\s*1\b|needsImage:\s*.*\?\s*1\s*:\s*0|chatAnswered:.*\?\s*1\s*:\s*0|unlockedByAdmin:\s*1\b" server/routers/smartBookRouter.ts
```

Remaining matches:

```text
5395: return { alreadyViewed: false, creditsDeducted: deductSuccess ? 1 : 0, deductSuccess };
5774: return { alreadyViewed: false, success, creditsDeducted: success ? 1 : 0 };
5787: return { success, creditsDeducted: success ? 1 : 0 };
```

These are non-DB numeric API return values and were intentionally left unchanged.

Positive boolean grep shows the patched DB sites:

```text
!!updates.* / !!isEnabled / !!input.chatAnswered
eq(..., true) / eq(..., false)
isLearned: false / isLearned: true
isPublished: true
unlockedByAdmin: true
```

## Smoke Test

Disposable SQLite smoke:

- Created `/tmp/smartbook-router-1e-smoke.db`
- Verified boolean write round-trip
- Verified `eq(..., true)` filter
- Verified `eq(..., false)` filter
- Verified wrong answers `isLearned=false` query
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_BOOLEAN_SMOKE_PASS writes=2 trueFilter=1 falseFilter=1 wrongAnswersFalse=1 leftovers=0
```

Import check:

```text
IMPORT_OK
```

## SQLite DB Leftovers

No SQLite DB artifacts remain from the smoke test:

- `/tmp/smartbook-router-1e-smoke.db`: absent
- `/tmp/smartbook-router-1e-smoke.db-wal`: absent
- `/tmp/smartbook-router-1e-smoke.db-shm`: absent
- workspace `*.db`, `*.db-wal`, `*.db-shm`: none found

## Modified Files

This phase modified only:

- `server/routers/smartBookRouter.ts`
- `SMARTBOOK_ROUTER_PATCH_1E_REPORT.md`

The wider working tree already contains earlier migration artifacts and prior phase changes.

## Recommendation

Proceed to **Phase 1-J tutorRouter Audit**.

The SmartBookRouter Phase 1-I.1 batches are now complete through boolean handling.
