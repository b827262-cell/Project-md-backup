# TutorRouter Patch 1J1C

> **Phase 1-J.1c — Upsert batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/tutorRouter.ts`

## 1. Scope

Only `.onDuplicateKeyUpdate()` was changed.

No JSON, boolean, timestamp, `eq(col, 1)`, `eq(col, 0)`, `db.execute` cleanup, raw SQL cleanup, insert return handling, schema, db.ts, package.json, runtime wiring, or other router changes were made in this phase.

## 2. Original Upsert Sites

Original grep:

```text
1890: }).onDuplicateKeyUpdate({ set: { response: aiAnswer, updatedAt: now2, hitCount: sql`hit_count + 1` } });
```

Original count: **1**

Affected table:

- `pageAiResponseCache` / `page_ai_response_cache`

Business logic:

- Cache quick-button AI responses for a book page and question type.
- On repeated `(bookId, page, questionType)`, update `response`, update `updatedAt`, and increment `hitCount`.

Unique-key condition:

- Intended logical key: `(bookId, page, questionType)`.
- Current MySQL schema has `index("parc_bookId_page_type_idx")`, not a `unique(...)` constraint.
- Current SQLite MVP schema does not include `pageAiResponseCache`.

## 3. Migration Strategy

Because the schema does not expose a unique key for `(bookId, page, questionType)`, this batch did **not** use `onConflictDoUpdate`.

Chosen strategy:

```text
SELECT by logical key
  -> exists: UPDATE by id
  -> missing: INSERT
```

This is conservative and works for both MySQL and SQLite without relying on unavailable conflict metadata.

## 4. Patched Sites

Patched **1** site:

- `pageAiResponseCache` quick-button cache write in `tutorChatRouter`

The MySQL-only `.onDuplicateKeyUpdate()` chain was replaced by:

- `select({ id })`
- `update(...).set({ response, updatedAt, hitCount: sql\`hit_count + 1\` })`
- `insert(...).values(...)`

## 5. Grep Results

```text
rg -n "onDuplicateKeyUpdate|onConflictDoUpdate|onConflictDoNothing|upsert|duplicate" server/routers/tutorRouter.ts
```

Result:

```text
no matches
```

Success criterion:

```text
onDuplicateKeyUpdate = 0
```

## 6. Smoke Test

Disposable SQLite smoke:

- Created `/tmp/tutor-router-1j1c-smoke.db`
- Created a minimal `page_ai_response_cache` table
- Performed first insert
- Performed duplicate logical insert through select/update path
- Verified update happened
- Verified `id` did not change
- Verified `hitCount` incremented to 2
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_UPSERT_SMOKE_PASS firstInsertId=1 duplicateId=1 hitCount=2 response=second leftovers=0
```

Import check:

```text
IMPORT_OK
```

## 7. SQLite Leftovers Check

No SQLite DB artifacts remain from the smoke test:

- `/tmp/tutor-router-1j1c-smoke.db`: absent
- `/tmp/tutor-router-1j1c-smoke.db-wal`: absent
- `/tmp/tutor-router-1j1c-smoke.db-shm`: absent
- workspace `*.db`, `*.db-wal`, `*.db-shm`: none found

## 8. Modified Files

This phase modified only:

- `server/routers/tutorRouter.ts`
- `TUTOR_ROUTER_PATCH_1J1C_REPORT.md`

The wider working tree already contains prior migration artifacts and previous phase changes.

## 9. MySQL Compatibility Assessment

MySQL compatibility is preserved:

- The patch uses standard Drizzle `select`, `update`, and `insert` operations.
- The existing `hitCount: sql\`hit_count + 1\`` expression is retained.
- Behavior is at least as explicit as the original path. Since the audited schema shows a non-unique index rather than a unique constraint, the old `onDuplicateKeyUpdate()` depended on conflict metadata that is not visible in the schema.

## 10. Recommendation

Proceed to **Phase 1-J.1d Boolean Batch**.

The remaining tutorRouter work should address boolean writes/comparisons only, without mixing JSON, timestamp, raw SQL cleanup, or schema work.
