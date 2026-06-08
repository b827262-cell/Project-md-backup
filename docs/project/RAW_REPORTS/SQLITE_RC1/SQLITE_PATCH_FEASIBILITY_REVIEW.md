# SQLite Patch Feasibility Review

> **Phase 1-C.9a — Review Only**
> Generated: 2026-06-03 · Branch: `release/vps-lite`
> Patch source: `SQLITE_SCHEMA_HARDENING_PATCH.md`
> **`drizzle/schema.sqlite.mvp.ts` was NOT modified.**

---

## Executive Summary

The patch is **safe to apply** with one amendment: replace `sql\`(unixepoch())\`` with `sql\`(strftime('%s','now'))\`` for VPS SQLite version compatibility.

| Check | Result |
|-------|--------|
| Drizzle index syntax | ✅ Array form correct for v0.44.6 |
| `unixepoch()` syntax | ⚠️ Works locally (SQLite 3.53) — risky on VPS (see below) |
| `strftime('%s','now')` syntax | ✅ Safe on ALL SQLite versions |
| Timestamp column samples (10) | ✅ All correct |
| Index column samples (5) | ✅ All columns exist, no conflicts |
| TODO cleanup rules | ✅ Correct |
| Errors found in patch | 1 minor syntax recommendation |

---

## Drizzle Index Syntax

**Drizzle ORM installed version**: `0.44.6` (declared `^0.44.5` in package.json)

### Verification

```
node_modules/drizzle-orm/sqlite-core/table.d.ts line 22:
(name, columns, extraConfig?: (self) => SQLiteTableExtraConfigValue[])
```

The type signature explicitly accepts `SQLiteTableExtraConfigValue[]` (array form).
The object form `Record<string, SQLiteTableExtraConfigValue>` is still accepted but **marked deprecated** in the same file:

> "The third parameter of sqliteTable is changing and will only accept an array instead of an object"

### Verdict

| Form | Syntax | Status in 0.44.6 |
|------|--------|-----------------|
| **Plan A (object)** | `(t) => ({ idx: index('name').on(t.col) })` | ⚠️ Deprecated |
| **Plan B (array)** | `(t) => [index('name').on(t.col)]` | ✅ **Correct — use this** |

**Use array form (Plan B).** The patch document already specifies this correctly.

---

## SQLite Default Syntax

### Test Results (on dev SQLite 3.53.1)

```
sqlite3 :memory: "CREATE TABLE t (ts INTEGER DEFAULT (unixepoch()));"
→ OK

sqlite3 :memory: "CREATE TABLE t (ts INTEGER DEFAULT (strftime('%s','now')));"
→ OK
```

### Version Compatibility Risk

| Function | Introduced | Dev machine | Ubuntu 20.04 LTS | Ubuntu 22.04 LTS | better-sqlite3 v8+ |
|----------|-----------|-------------|------------------|------------------|--------------------|
| `unixepoch()` | SQLite **3.38.0** (2022-02) | ✅ 3.53 | ❌ 3.31.1 | ❌ 3.37.2 | ✅ bundles ≥3.40 |
| `strftime('%s','now')` | SQLite 3.x (all) | ✅ | ✅ | ✅ | ✅ |

**Risk:** Ubuntu 22.04 LTS (the most common VPS base OS for a fresh 1GB VPS deployment) ships SQLite **3.37.2** — below the 3.38.0 threshold for `unixepoch()`. If `better-sqlite3` uses the system SQLite, this will fail at runtime.

`better-sqlite3` v8.x and above ships a **bundled** SQLite (≥ 3.40), so the system version would be irrelevant once it's installed. However, since `better-sqlite3` is not yet installed, the version used at Phase 1-E wiring is unknown.

### Verdict

| Syntax | Status |
|--------|--------|
| `.default(sql\`(unixepoch())\`)` | ⚠️ **Works locally but risky on Ubuntu 22.04 VPS** |
| `.default(sql\`(strftime('%s','now'))\`)` | ✅ **Safe on ALL SQLite versions — recommended** |

**Amendment to patch**: Change all instances of:
```diff
-.default(sql`(unixepoch())`)
+.default(sql`(strftime('%s','now'))`)
```

Both return identical values (Unix epoch seconds). The only difference is version compatibility.

---

## Timestamp Validation

### Sampled 10 of 42 columns

| # | Table | Column | MySQL Source | SQLite Draft (current) | Patch Action | Correct? |
|---|-------|--------|-------------|----------------------|--------------|----------|
| 1 | `users` | `createdAt` | `timestamp().defaultNow().notNull()` | `integer("createdAt", { mode: "timestamp" })` | Add `.default(sql\`(unixepoch())\`)` | ✅ |
| 2 | `conversations` | `createdAt` | `timestamp().defaultNow().notNull()` | `integer("createdAt", { mode: "timestamp" })` | Add default | ✅ |
| 3 | `messages` | `createdAt` | `timestamp().defaultNow().notNull()` | `integer("createdAt", { mode: "timestamp" })` | Add default | ✅ |
| 4 | `smart_book_learning_sessions` | `startedAt` | `timestamp().default(sql\`CURRENT_TIMESTAMP\`).notNull()` | `integer("started_at")` (bare) | Add mode + default | ✅ |
| 5 | `smart_book_learning_sessions` | `lastActiveAt` | `timestamp().default(sql\`CURRENT_TIMESTAMP\`).notNull()` | `integer("last_active_at")` (bare) | Add mode + default | ✅ |
| 6 | `smart_book_unit_qa_answers` | `answeredAt` | `timestamp("answered_at").default(sql\`CURRENT_TIMESTAMP\`).notNull()` | `integer("answered_at")` (bare) | Add mode + default | ✅ |
| 7 | `smart_book_chapter_completions` | `completedAt` | `timestamp("completed_at").default(sql\`CURRENT_TIMESTAMP\`).notNull()` | `integer("completed_at")` (bare) | Add mode + default | ✅ ¹ |
| 8 | `exam_questions` | `createdAt` | `timestamp().defaultNow().notNull()` | `integer("createdAt", { mode: "timestamp" })` | Add default | ✅ |
| 9 | `ai_generated_exams` | `createdAt` | `timestamp("created_at").defaultNow().notNull()` | `integer("created_at", { mode: "timestamp" })` | Add default | ✅ |
| 10 | `learning_materials` | `createdAt` | `timestamp().defaultNow()` (nullable in MySQL) | `integer("created_at", { mode: "timestamp" })` | Add default | ✅ |

**¹ Pre-existing issue (NOT introduced by this patch):** `smart_book_chapter_completions.completedAt` is `.notNull()` in the MySQL source but is nullable in the current SQLite draft. The patch does not change nullability — this remains a pre-existing discrepancy to fix in a future pass.

**Convention B columns** (ms timestamps — not patched): Verified that `exam_wrong_book.lastAnsweredAt`, `exam_sets.createdAt`, `video_units.createdAt`, etc. are correctly left as bare `integer().notNull()`. ✅

---

## Index Validation

### Sampled 5 of 16

| # | Index Name | Table Variable | JS Property | DB Column | Exists in Draft? | Naming Conflict? |
|---|-----------|---------------|-------------|-----------|-----------------|-----------------|
| 1 | `idx_users_openId` | `users` | `openId` | `"openId"` (line 19) | ✅ | ✅ No — no existing indexes |
| 2 | `idx_conversations_userId` | `conversations` | `userId` | `"userId"` (line 59) | ✅ | ✅ No |
| 3 | `idx_sbc_bookId` | `smartBookChapters` | `bookId` | `"book_id"` (line 242) | ✅ | ✅ No |
| 4 | `idx_lp_bookId_chapterId` | `lessonPoints` | `bookId, chapterId` | `"book_id"`, `"chapter_id"` (lines 427–428) | ✅ | ✅ No |
| 5 | `idx_tcm_sessionId` | `tutorChatMessages` | `sessionId` | `"session_id"` (line 595) | ✅ | ✅ No |

**Current index count in `schema.sqlite.mvp.ts`**: 0 — no existing index definitions means zero naming conflicts possible.

**Note on `smart_books` composite index**: `idx_smart_books_public_status` is defined on `(table.isPublic, table.processingStatus)`. Both columns are `integer("is_public")` (boolean mode) and `text("processing_status")`. Cross-type composite index is valid in SQLite. ✅

---

## TODO Marker Validation

### Sampled 10 of 67

| # | Line | Current TODO | Column Role | Correct Replacement |
|---|------|-------------|-------------|---------------------|
| 1 | 26 | `// TODO SQLite timestamp default strategy` | `users.createdAt` — write-once | `// Phase 1-C.9 — Unix seconds, DEFAULT(strftime('%s','now'))` |
| 2 | 27 | `// TODO SQLite timestamp default strategy` | `users.updatedAt` — app-side | `// Application-side — set on update` |
| 3 | 63 | `// TODO SQLite timestamp default strategy` | `conversations.createdAt` — write-once | Default comment ✅ |
| 4 | 65 | `// TODO SQLite timestamp default strategy` | `conversations.lastMessageAt` — app-side | `// Application-side — set when message created` ✅ |
| 5 | 103 | `// TODO SQLite timestamp default strategy` | `conversation_files.uploadedAt` — write-once | Default comment ✅ |
| 6 | 200 | `// TODO SQLite timestamp default strategy (was sql\`CURRENT_TIMESTAMP\`)` | `smart_book_categories.createdAt` — write-once | Default comment ✅ |
| 7 | 270 | `// TODO SQLite timestamp default strategy (was sql\`CURRENT_TIMESTAMP\`)` | `smart_book_conversations.createdAt` — write-once | Default comment ✅ |
| 8 | 375 | `// TODO SQLite timestamp default strategy (was sql\`CURRENT_TIMESTAMP\`)` | `smart_book_learning_sessions.startedAt` — write-once | Default comment ✅ |
| 9 | 553 | `// TODO SQLite timestamp default strategy (was sql\`CURRENT_TIMESTAMP\`)` | `smart_book_verifications.createdAt` — write-once | Default comment ✅ |
| 10 | 617 | `// TODO SQLite timestamp default strategy (was sql\`CURRENT_TIMESTAMP\`)` | `tutor_subject_exam_sources.createdAt` — write-once | Default comment ✅ |

All 10 sampled replacements are correct per the patch's Part 5 rules. ✅

---

## Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | `unixepoch()` not available on Ubuntu 22.04 VPS system SQLite (3.37) | **High** | Replace with `strftime('%s','now')` — same output, all versions |
| 2 | `better-sqlite3` version unknown — if it uses system SQLite on VPS, `unixepoch()` fails | **High** | Same mitigation: use `strftime('%s','now')` |
| 3 | 21 bare `integer()` columns get `{ mode: "timestamp" }` added — changes Drizzle type from `number\|null` to `Date\|null` | **Medium** | This is intentional; these were Convention A columns missing their mode. Callers that treated them as numbers will need to adapt when Phase 1-E wiring begins (not a problem in the draft). |
| 4 | `smart_book_chapter_completions.completedAt` — `.notNull()` lost in original draft (pre-existing, not from this patch) | **Low** | Note for Phase 1-E: add `.notNull()` to this column when wiring. |
| 5 | Line numbers in patch document may shift slightly after import line change | **Low** | Use column name + table name to locate — not line numbers alone. |

---

## Recommendation

### ✅ Patch is safe to apply with one amendment

**Required amendment before applying:**

```diff
- .default(sql`(unixepoch())`)
+ .default(sql`(strftime('%s','now'))`)
```

Apply this substitution to all 42 timestamp column changes in the patch. The output is identical (Unix epoch seconds), but `strftime('%s','now')` is guaranteed to work on SQLite 3.x regardless of VPS OS age.

### Suggested Phase 1-C.9b Apply Order

To minimize risk, apply the patch in three small batches rather than one large write:

1. **Batch 1 — Import line only** (1 line change, zero schema impact)
2. **Batch 2 — Timestamp defaults** (42 column changes, no structural change to tables)
3. **Batch 3 — Indexes** (13 table structural changes, adds callback function)

After each batch: verify `grep -c "sqliteTable(" schema.sqlite.mvp.ts` still returns **66**.

### Phase 1-E Prerequisite Check

After patch applied:
- [ ] `grep -c "sqliteTable(" drizzle/schema.sqlite.mvp.ts` → 66
- [ ] `grep -c "strftime\|unixepoch" drizzle/schema.sqlite.mvp.ts` → 42
- [ ] `grep -c "index(" drizzle/schema.sqlite.mvp.ts` → 16
- [ ] `grep -c "TODO SQLite timestamp" drizzle/schema.sqlite.mvp.ts` → 0

---

*Review Only. `drizzle/schema.sqlite.mvp.ts` was NOT modified.*
