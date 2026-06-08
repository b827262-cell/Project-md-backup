# SQLite Schema Patch — Batch 1 Report

> **Phase 1-C.9b Batch 1 — Import Hardening Only**
> Applied: 2026-06-03 · Branch: `release/vps-lite`

## Summary

| Item | Before | After |
|------|--------|-------|
| Table count | 66 | **66** (unchanged) |
| `index` imported | No | **Yes** |
| `sql` imported | No | **Yes** |
| Timestamp defaults added | 0 | **0** (Batch 2) |
| Index definitions added | 0 | **0** (Batch 3) |

## Import Changes

**File:** `drizzle/schema.sqlite.mvp.ts` line 8–9

```diff
-import { sqliteTable, integer, text, real, blob } from "drizzle-orm/sqlite-core";
+import { sqliteTable, integer, text, real, blob, index } from "drizzle-orm/sqlite-core";
+import { sql } from "drizzle-orm";
```

**Rationale (from SQLITE_PATCH_FEASIBILITY_REVIEW.md):**
- `index` — required for Must-Add index definitions (Batch 3, array form, drizzle-orm 0.44.6)
- `sql` — required for `.default(sql\`(strftime('%s','now'))\`)` timestamp defaults (Batch 2)

## No Timestamp Changes

All 67 `TODO SQLite timestamp default strategy` markers remain unchanged.
Timestamp defaults will be applied in **Batch 2**.

## No Index Changes

`grep -c "index(" schema.sqlite.mvp.ts` → **0**
No index definitions were added.
Index callbacks will be applied in **Batch 3**.

## Verification

```
grep -c "sqliteTable(" drizzle/schema.sqlite.mvp.ts → 66   ✅
grep "^import" drizzle/schema.sqlite.mvp.ts           → 2 lines, no duplicates ✅
grep -c "index(" drizzle/schema.sqlite.mvp.ts         → 0   ✅
grep -c "strftime|unixepoch" drizzle/schema.sqlite.mvp.ts → 0 ✅
```

## Ready For

**Batch 2 — Timestamp Defaults** (42 columns, `strftime('%s','now')`)
