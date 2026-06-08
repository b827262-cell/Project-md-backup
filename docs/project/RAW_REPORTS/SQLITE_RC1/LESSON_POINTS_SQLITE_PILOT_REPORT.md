# LessonPoints SQLite Pilot Report

> **Phase 1-F.1 — Router Pilot Patch**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Only `server/routers/lessonPointsRouter.ts` patched. Disposable DB created + deleted. MySQL untouched.

---

## Result: ✅ PASS

All P0 + P1 issues from `LESSON_POINTS_SQLITE_AUDIT.md` are fixed; the patched value conventions round-trip correctly through the SQLite adapter (11/11 smoke checks PASS).

---

## Changes Applied

| Class | Fix | Sites |
|-------|-----|-------|
| **P0-A** datetime string → `new Date()` | `publishedAt` / `completedAt` / `classroomQuizGeneratedAt` (`nowUtc`/`nowUtc2`) now pass a `Date`; Drizzle `mode:"timestamp"` → Unix seconds | 9 |
| **P0-B** drop `JSON.stringify(options)` | json-mode column gets the array directly | 4 |
| **P0-C** drop `JSON.parse(options)` | json-mode column returns an array already (getById, list, getPublished) | 3 logical (4 lines) |
| **P1-A** boolean `1/0` → `true/false/!!x` | `needsImage`, `isPublished`, `completed` | 12 |
| **P1-B** `eq(col, 1)` → `eq(col, true)` | `isPublished` ×2, `completed` ×1 | 3 |

**Lines changed:** ~32 logic lines across 12 edit sites. Router shrank 1050 → 1043 lines (getPublished double-decode block collapsed to a single `options: p.options`).

### Deliberately NOT changed (correctness over vanity grep)
- **5 `JSON.parse` calls remain** (lines 224, 564, 748, 840, 900). These parse **LLM response content** (`response.choices[0].message.content`), NOT DB columns. Removing them would break AI generation. The audit explicitly flagged these as keep-as-is.
- `Date.now()` + `Math.random()` (S3 object key) — DB-agnostic, kept.
- insert→re-select and select→update/insert upsert patterns — already portable, kept.

### Behavioral note (response shape)
`getPublished` previously returned `options` as a re-stringified **string** (inconsistent with `getById`/`list` which returned arrays). It now returns an **array**, consistent with the other read endpoints. The frontend consuming `getPublished` should expect an array (same as `list`). Flagged for Phase 1-F.2 frontend check.

---

## Verification

```
grep -c "JSON.stringify("  lessonPointsRouter.ts → 0   ✅
grep -c "toISOString()"    lessonPointsRouter.ts → 0   ✅
grep "isPublished, 1)|completed, 1)"             → 0   ✅ (boolean compares fixed)
grep "? 1 : 0 | isPublished: 1 | completed: ...1" → none ✅ (boolean writes fixed)
grep "JSON.parse("         lessonPointsRouter.ts → 5   ⚠️ ALL are LLM-response parses (NOT options) — intentionally kept
```

The literal "JSON.parse = 0" target from the task is **not met by design**: the only remaining `JSON.parse` calls operate on AI/LLM JSON responses, which must be parsed. Breaking them to hit a grep count would break the router. Zero `JSON.parse` remains on any **DB column**.

---

## Smoke Test (disposable `./data/pilot-test.db`, `DATABASE_PROVIDER=sqlite`)

Mirrors the patched router's data operations against the SQLite adapter:

| Operation | Check | Result |
|-----------|-------|--------|
| **Create** | insert with array options + boolean flags + Date | ✅ id=1 |
| **Read** | options is array; isPublished `true`; publishedAt is `Date` | ✅ |
| **Update** | options array replace; isPublished=false | ✅ |
| **GetPublished** | filter `eq(isPublished, true)` returns row with array options | ✅ rows=1 |
| **RecordAnswer (insert)** | completed `true`, completedAt is `Date` | ✅ |
| **RecordAnswer (update)** | attempts increment | ✅ attempts=2 |
| **All-completed filter** | `eq(completed, true)` | ✅ rows=1 |
| **Delete** | row removed | ✅ rows=0 |

`PILOT_SMOKE_PASS` — 11/11 checks passed.

> Scope note: the smoke validates the **patched value conventions** against the SQLite adapter. Full in-process router invocation against SQLite requires the `getActiveDb()` switch (Phase 1-F.2 Dual Mode) — the router still calls `getDb()` (MySQL) today.

---

## Safety

| File | Status |
|------|--------|
| `server/db.ts` | ✅ untouched (`getDb()` intact) |
| `server/db.sqlite.ts` | ✅ untouched |
| `server/db.runtime.ts` | ✅ untouched |
| `drizzle/schema.sqlite.mvp.ts` | ✅ untouched (66 tables) |
| `package.json` | ✅ untouched |
| `smartBookRouter` / `tutorRouter` / `smartBookLearningRouter` | ✅ untouched |
| `DATABASE_PROVIDER` default | ✅ mysql (sqlite only transient in test subprocess) |
| SQLite DB files | ✅ none remain (`pilot-test.db*` deleted) |
| Temp smoke script | ✅ deleted |
| MySQL source of truth | ✅ unchanged |

The router still imports `getDb` from `../db` and tables from `../../drizzle/schema` (MySQL) — so **production behaviour is unchanged**. The value-convention fixes are forward-compatible: `new Date()`, boolean values, and array JSON all work identically on MySQL+Drizzle, so this patch does **not** regress the live MySQL path.

---

## Result

**PASS** — lessonPointsRouter is SQLite-ready at the value-convention level; MySQL path preserved.

## Recommendation

✅ **Proceed to Phase 1-F.2 Dual Mode Pilot** — switch lessonPointsRouter's `getDb()` → `getActiveDb()` (and its schema import to mode-aware), then run the full router end-to-end under `DATABASE_PROVIDER=sqlite`. Verify the `getPublished` array response shape against the frontend.

*Pilot patch only. One router, ~32 lines. No dual-mode switch, no other router, MySQL default preserved.*
