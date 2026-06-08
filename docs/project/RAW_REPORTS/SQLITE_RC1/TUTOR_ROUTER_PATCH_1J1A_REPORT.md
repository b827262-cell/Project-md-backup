# TutorRouter Patch 1J1A

> **Phase 1-J.1a — Insert Return batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/tutorRouter.ts`

## Scope

Only insert return handling was changed:

- explicit `insertId`
- MySQL-only `$returningId()`
- insert-result array destructuring tied to those sites

No RAND(), INSERT IGNORE, `db.execute()`, `onDuplicateKeyUpdate()`, JSON, boolean, timestamp, raw SQL cleanup, schema, db.ts, package.json, runtime wiring, or other router changes were made.

## Changes

Imported the existing dual-driver helper:

```ts
import { normalizeInsertId } from "../db.sqlite";
```

### explicit `insertId`

Fixed **2** sites:

- `tutorSubjectExamSources` insert
- `tutorSubjectVideoCourses` insert

Pattern:

```ts
const [result] = await db.insert(...).values(...);
return { id: (result as any).insertId };
```

became:

```ts
const result = await db.insert(...).values(...);
return { id: normalizeInsertId(result) };
```

### `$returningId()`

Fixed **4** sites:

- cached-response `tutorChatSessions` insert
- normal chat `tutorChatSessions` insert
- `tutorChatFolders` insert
- `tutorChatLabels` insert

Pattern:

```ts
const [row] = await db.insert(...).values(...).$returningId();
```

became:

```ts
const result = await db.insert(...).values(...);
const id = normalizeInsertId(result);
```

### Destructure Fixes

Fixed **6** insert-return destructures total:

- 2 explicit `insertId` destructures
- 4 `$returningId()` destructures

## Grep Results

Old blocker grep:

```text
rg -n 'insertId|\$returningId|const \[[^\]]+\] = await db\.insert|const \[[^\]]+\] = await db2\.insert' server/routers/tutorRouter.ts
```

Result:

```text
no matches
```

Positive grep:

```text
13:import { normalizeInsertId } from "../db.sqlite";
414:      return { success: true, id: normalizeInsertId(result) };
485:      return { success: true, id: normalizeInsertId(result) };
1271:              const newSessionResult = await db.insert(tutorChatSessions).values({
1275:              sessionId = normalizeInsertId(newSessionResult);
1296:        const newSessionResult = await db
1307:        sessionId = normalizeInsertId(newSessionResult);
2021:      return { id: normalizeInsertId(result) };
2057:      return { id: normalizeInsertId(result) };
```

## Smoke Test

Disposable SQLite smoke:

- Created `/tmp/tutor-router-1j1a-smoke.db`
- Inserted into a simplified affected table (`tutor_subject_exam_sources`)
- Retrieved id via `normalizeInsertId(result)`
- Verified id is a valid `number`
- Read the inserted row by id
- Deleted the inserted row by id
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_INSERT_RETURN_SMOKE_PASS id=1 idType=number create=1 read=1 delete=1 leftovers=0
```

Import check:

```text
IMPORT_OK
```

## SQLite DB Leftovers

No SQLite DB artifacts remain from the smoke test:

- `/tmp/tutor-router-1j1a-smoke.db`: absent
- `/tmp/tutor-router-1j1a-smoke.db-wal`: absent
- `/tmp/tutor-router-1j1a-smoke.db-shm`: absent

## Modified Files

This phase modified only:

- `server/routers/tutorRouter.ts`
- `TUTOR_ROUTER_PATCH_1J1A_REPORT.md`

The wider working tree already contains prior migration artifacts and previous phase changes.

## Recommendation

Proceed to **Phase 1-J.1b Raw SQL MySQL-only Batch**.

Remaining 1-J P0 work should focus on `RAND()`, `INSERT IGNORE`, and `db.execute()` without mixing boolean, JSON, timestamp, or upsert changes.
