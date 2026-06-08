# TutorRouter Patch 1J1E

> **Phase 1-J.1e — JSON + Timestamp batch only**
> Generated: 2026-06-04 · Branch: `release/vps-lite`
> Patched: `server/routers/tutorRouter.ts`

## 1. JSON Fixes

Fixed **3** DB json-mode writes:

- `practiceWrongBook.options` update when re-adding a resolved wrong-book item
- `practiceWrongBook.options` update when refreshing an unresolved wrong-book item
- `practiceWrongBook.options` insert for a new wrong-book item

Changed:

```ts
options: input.options ? JSON.stringify(input.options) : existing.options
options: input.options ? JSON.stringify(input.options) : null
```

to:

```ts
options: input.options ?? existing.options
options: input.options ?? null
```

`practiceWrongBook.options` is `text(..., { mode: "json" })` in SQLite and `json(...)` in MySQL, so raw arrays/objects are the correct Drizzle value convention.

## 2. Timestamp Fixes

Fixed **2** datetime-string writes:

- saved note update `smartBookSavedMessages.updatedAt`
- note image upload `smartBookSavedMessages.updatedAt`

Changed:

```ts
new Date().toISOString().replace('T', ' ').slice(0, 19)
```

to:

```ts
toSqliteTimestamp(new Date())
```

This keeps MySQL forward-compatible through a `Date` value and uses Unix seconds for SQLite.

## 3. Keep-As-Is JSON

Remaining JSON grep count: **20**.

Kept categories:

- LLM response parse
- LLM prompt payload stringify
- API/plain text JSON handling
- guarded DB reads: `typeof x === 'string' ? JSON.parse(x) : x`
- `smartBookSavedMessages.noteImages` plain text JSON string storage

No unguarded DB json-mode parse blocker remains.

## 4. Keep-As-Is Timestamp

Remaining timestamp grep count: **109**.

Kept categories:

- `Date.now()` writes to bigint millisecond columns
- `createdAt` / `updatedAt` read, select, sort, and filter usage
- non-DB timestamp values
- `toSqliteTimestamp(new Date())` patched sites
- local `bookSuggestionCache` table definitions using integer millisecond timestamps

No `new Date().toISOString().replace('T', ' ').slice(0, 19)` DB timestamp write remains.

## 5. Grep Results

JSON:

```text
rg -n "JSON\.stringify|JSON\.parse" server/routers/tutorRouter.ts
```

Result:

```text
20 keep-as-is matches
0 DB JSON blockers
0 JSON.stringify(input.options)
```

Timestamp:

```text
rg -n "toISOString|Date\.now|new Date|createdAt|updatedAt|completedAt|resolvedAt|publishedAt" server/routers/tutorRouter.ts
```

Result:

```text
109 keep-as-is matches
2 toSqliteTimestamp(new Date()) patched sites
0 datetime-string DB writes
```

## 6. Smoke Test

Disposable SQLite smoke:

- Created `/tmp/tutor-router-1j1e-smoke.db`
- Wrote and read JSON object/array values through json-mode columns
- Wrote and read a timestamp-mode Date value
- Verified `getTime()` works
- Deleted DB, WAL, and SHM files

Result:

```text
SQLITE_JSON_TIMESTAMP_SMOKE_PASS objectRead=alpha arrayRead=2 timestampMs=1780576496000 leftovers=0
```

Import check:

```text
IMPORT_OK
```

## 7. SQLite Leftovers Check

No SQLite DB artifacts remain from the smoke test:

- `/tmp/tutor-router-1j1e-smoke.db`: absent
- `/tmp/tutor-router-1j1e-smoke.db-wal`: absent
- `/tmp/tutor-router-1j1e-smoke.db-shm`: absent
- workspace `*.db`, `*.db-wal`, `*.db-shm`: none found

## 8. Modified Files

This phase modified only:

- `server/routers/tutorRouter.ts`
- `TUTOR_ROUTER_PATCH_1J1E_REPORT.md`

The wider working tree already contains prior migration artifacts and previous phase changes.

## 9. Recommendation

Proceed to **Phase 1-J.1f Cleanup / Structural Review**.

The next phase should review remaining structural cleanup candidates, especially portable `db.execute()` result-shape sites, raw `IN (${join})`, and local `sqliteTable(...)` definitions, without mixing schema/runtime wiring unless explicitly scoped.
