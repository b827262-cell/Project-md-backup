# 2026-06-10 SmartBook Lite SQLite / MySQL Sync Handoff

## Purpose

本檔用於換新分頁後快速接續工作。  
目前主線已完成 **SQLite Web Ready**，但 **MySQL true data sync 尚未驗證**。下一步要做的是 PR #15：把 MySQL→SQLite validator 從 dry-run / no-op 升級成真正可 `--apply`、可讀 live MySQL 或 mysqldump、可做 row-count parity 的安全同步工具。

---

## Current Engineering Verdict

```text
Verdict: ACCEPT_SQLITE_WEB_READY_ONLY
```

可宣稱：

```text
SmartBook Lite SQLite Web Ready。
SQLite schema / migration / runtime smoke / web runtime / tRPC DB read 已通過實測。
```

不可宣稱：

```text
MySQL / SQLite full parity PASS
MySQL true data sync PASS
原作者 MySQL 資料已完整同步 SQLite
```

原因：

```text
MySQL env missing
MySQL dump incomplete
validator --apply still no-op / APPLY_NOT_IMPLEMENTED
8 張 active tables row-count parity 尚未驗證
```

---

## Merged PR Status

### PR #12 — Bucket4-A Schema Foundation

Status: MERGED

內容：

- `pdfImageNotes`
- `personaBookBindings`
- SQLite tables: 66 → 68
- build PASS
- SQLite smoke PASS
- schema-only，未接 router / UI

### PR #13 — SQLite Schema Sync + MySQL Validator Foundation

Status: MERGED

Merge commit:

```text
0d02ca12deb138064d623009c828bf25a8a331af
```

Release latest:

```text
0d02ca12 Finish SQLite schema sync and MySQL validator (#13)
```

內容：

- Bucket4-B schema:
  - `pdfHighlights`
  - `aiMsgHighlights`
  - `smartBookQuickButtons`
- SQLite tables: 68 → 71
- 新增:
  - `scripts/sqlite/mysql-to-sqlite-active-tables.ts`
  - `scripts/sqlite/sqlite-runtime-smoke.ts`
  - `docs/project/sqlite/SMARTBOOK_MYSQL_TO_SQLITE_FINISH_REPORT_20260610.md`
  - `docs/project/sqlite/SMARTBOOK_SQLITE_WEB_PARITY_REPORT_20260610.md`

驗證：

- `pnpm build`: PASS
- SQLite schema smoke: PASS
- `migrations=3`
- `tables=71`
- SQLite runtime smoke: PASS
- SQLite web test: PASS
- MySQL web parity: SKIPPED，原因 `MYSQL_WEB_PARITY_SKIPPED_ENV_MISSING`
- true MySQL data sync verified: NO

### PR #14 — Full SQLite Web Parity Report

Status: MERGED or READY TO MERGE depending current GitHub state.

Known PR:

```text
https://github.com/b827262-cell/ai_tutor_helper/pull/14
```

Commit:

```text
dfee0dd7c8d98b4bdcbed32aa98e68d106508352
```

內容：

- docs-only
- 補完整 `SMARTBOOK_SQLITE_WEB_PARITY_REPORT_20260610.md`
- 不碰程式 / schema / migration / router / UI / package

---

## SQLite Web Runtime Evidence

實測網址為 E500 本機：

```text
http://localhost:5013
```

當時啟動環境：

```bash
PORT=5013
NODE_ENV=development
DATABASE_PROVIDER=sqlite
SQLITE_PATH=/tmp/smartbook-web-final-*.db
pnpm dev
```

已測頁面：

```text
/
 /student
/login
/admin
/admin/smart-books
/admin/exam-questions
/not-exist-test
```

結果：

```text
HTTP 200 / SPA shell 正常 / 無 server 500 / 無 table missing
```

已測 API / DB-backed paths：

```text
auth.me → 200
featureToggles.getAll → 200
exam.getCategories → 200
credits.getBalance → 401，protected route 正常
auth.loginLocal → 401，fresh DB 無 admin seed，屬預期
```

Active SQLite tables:

```text
users
smart_books
pdf_categories
pdf_image_notes
persona_book_bindings
pdf_highlights
ai_msg_highlights
smart_book_quick_buttons
```

Row status in fresh SQLite DB:

```text
pdf_categories = 5 seed rows
others = 0
```

---

## Difference From Original Author / Upstream

目前不是 100% 原作者 MySQL 版。

| Area | Original / Upstream | Current SQLite Lite |
|---|---|---|
| DB engine | MySQL | SQLite runtime ready |
| Schema | Full upstream MySQL schema | Selective Lite active tables, currently 71 tables |
| Data sync | MySQL source data | Not truly imported yet |
| Router/UI | Upstream may have more full features | New tables are schema/tool foundation only |
| RAG / legacy | May include more upstream modules | Intentionally excluded from Lite scope |
| Web runtime | MySQL-based | SQLite web test PASS |
| MySQL/SQLite parity | N/A | Not yet full parity |

---

## Current Blocker: MySQL True Data Sync

Latest verification result:

```text
MySQL env found? NO
MySQL dump found? YES
Dump path: /home/b827262/project/temp/smartbook-platform/data/ai_tutor.sql
validator dry-run result: PASS / MYSQL_ENV_MISSING_SKIP
--apply implemented? NO-OP / APPLY_NOT_IMPLEMENTED
row count parity result: HOLD
true data sync verified? NO
```

Dump issue:

```text
pdf_categories dump=0, SQLite seed=5
5 active tables missing from dump
```

Conclusion:

```text
Tool can be improved, but current source is incomplete.
Even after PR #15 tool implementation, final result may be SOURCE_INCOMPLETE unless a complete MySQL source/dump is provided.
```

---

## Next Main Task: PR #15

### Goal

Create PR #15:

```text
sqlite: implement MySQL to SQLite data sync apply path
```

This PR should turn:

```text
scripts/sqlite/mysql-to-sqlite-active-tables.ts
```

from dry-run/no-op validator into a real guarded data sync validator.

### Allowed files

```text
scripts/sqlite/mysql-to-sqlite-active-tables.ts
scripts/sqlite/sqlite-runtime-smoke.ts  # only if needed
scripts/sqlite/mysql-sqlite-sync-lib.ts # optional new helper
docs/project/sqlite/MYSQL_SQLITE_TRUE_DATA_SYNC_IMPLEMENTATION_REPORT_20260610.md
```

### Forbidden files

```text
client/src/*
server/routers/*
server/routers.ts
server/stats.ts
shared/schema.ts
drizzle/schema.ts
drizzle/sqlite/*
package.json
pnpm-lock.yaml
package-lock.json
```

### Strictly forbidden operations

```text
sudo
rm -rf
git reset --hard
git clean -fd
writing production DB
gh pr merge 15
```

---

## PR #15 Required Validator Capabilities

### CLI args

Required:

```text
--dry-run
--apply
--source mysql
--source dump
--dump-path <path>
--sqlite-path <path>
--tables table1,table2
--batch-size <n>
--confirm-write-to-sqlite
--json-report <path>
--help
```

### Defaults and safety

Rules:

```text
No --apply = dry-run.
--apply without --confirm-write-to-sqlite must fail with APPLY_REQUIRES_CONFIRMATION.
MySQL source is read-only.
Dump source is read-only.
Only SQLite target can be written.
Never drop / truncate / delete all.
Never clear seed data.
Never write production DB by default.
```

### Active table whitelist

```text
users
smart_books
pdf_categories
pdf_image_notes
persona_book_bindings
pdf_highlights
ai_msg_highlights
smart_book_quick_buttons
```

### MySQL live adapter

Use existing dependency:

```text
mysql2/promise
```

Supported env:

```text
MYSQL_DATABASE_URL
DATABASE_URL
DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME
MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE
```

Operations:

```text
SELECT only
SHOW TABLES / information_schema read only
COUNT(*)
SELECT * FROM whitelisted tables
No MySQL writes
```

### Dump adapter

Support:

```bash
--source dump --dump-path /home/b827262/project/temp/smartbook-platform/data/ai_tutor.sql
```

Must parse or detect:

```text
CREATE TABLE
INSERT INTO `table` (`a`,`b`) VALUES (...),(...);
INSERT INTO table (...) VALUES (...)
multi-row VALUES
NULL
numbers
single-quoted strings
escaped quote
backslash escape
JSON string as TEXT
```

If unsupported:

```text
DUMP_PARSE_UNSUPPORTED
```

If table missing:

```text
SOURCE_TABLE_MISSING
```

### SQLite writer

Use:

```text
better-sqlite3
```

Rules:

```text
PRAGMA table_info(table)
Only write columns existing in SQLite target
Ignore extra source columns with warning
Skip row if target NOT NULL column missing and no default
Use INSERT OR REPLACE / safe upsert when id exists
No delete / truncate / seed clearing
Per-table transaction
```

### Type conversion

```text
bigint / epoch / timestamp number → INTEGER
tinyint boolean → 0/1
boolean → 0/1
JSON object/array/string → TEXT
null → null
undefined → null
varchar/text/longtext → string
created_at / updated_at date-like string → epoch ms if possible
```

### Table summary output

Per table:

```text
source type
source table exists
source rows
target table exists
target rows before
inserted
replaced
skipped
failed
target rows after
parity status
warnings
```

### Final verdicts

Allowed final verdicts:

```text
MYSQL_SQLITE_TRUE_DATA_SYNC_PASS
MYSQL_SQLITE_SYNC_TOOL_READY_SOURCE_INCOMPLETE
MYSQL_SQLITE_SYNC_APPLY_PASS_PARITY_PARTIAL
HOLD
```

Rules:

```text
8/8 active tables source exists + apply successful + target rows after = source rows
→ MYSQL_SQLITE_TRUE_DATA_SYNC_PASS

Tool works but source/dump missing tables
→ MYSQL_SQLITE_SYNC_TOOL_READY_SOURCE_INCOMPLETE

Some tables imported but not 8/8 parity
→ MYSQL_SQLITE_SYNC_APPLY_PASS_PARITY_PARTIAL

Crash / smoke fail / unsafe behavior
→ HOLD
```

---

## Direct Prompt for Codex / Opus

Use this when opening the next tab:

```text
請停止 codebase overview，直接建立 PR #15。

任務：sqlite: implement MySQL to SQLite data sync apply path

從最新 origin/release/vps-lite 建立 worktree：

~/project/smartbook-lite-rc1-pr15-mysql-sqlite-true-sync

branch:

sync/mysql-sqlite-true-data-sync-20260610

只允許修改：
- scripts/sqlite/mysql-to-sqlite-active-tables.ts
- scripts/sqlite/sqlite-runtime-smoke.ts，如需要
- scripts/sqlite/mysql-sqlite-sync-lib.ts，如需要
- docs/project/sqlite/MYSQL_SQLITE_TRUE_DATA_SYNC_IMPLEMENTATION_REPORT_20260610.md

禁止修改：
- router/UI/package/shared schema/drizzle schema/migrations

實作：
- guarded --apply
- --confirm-write-to-sqlite
- live MySQL read-only adapter
- mysqldump adapter
- SQLite writer
- active table whitelist
- type conversion
- row-count parity
- JSON report
- source incomplete honest verdict

驗證：
- pnpm build
- SQLite schema smoke migrations=3 tables=71
- runtime smoke PASS
- dry-run PASS
- dump dry-run PASS or SOURCE_INCOMPLETE
- dump apply to /tmp SQLite PASS or SOURCE_INCOMPLETE
- post-apply runtime smoke PASS

若 report verdict 非 HOLD：
commit / push / create PR #15
不要 merge PR #15。
```

---

## GPT-5.5 Acceptance Prompt After PR #15 Exists

Use after Codex/Opus returns PR #15 URL:

```text
請以 GPT-5.5 擔任 PR #15 engineering acceptance reviewer。

檢查：
- PR #15 scope
- changed files
- no router/UI/package/schema/migration changes
- validator no longer no-op
- --apply requires --confirm-write-to-sqlite
- MySQL source read-only
- no drop/delete/truncate
- dump adapter handles source incomplete honestly
- row-count parity not faked
- pnpm build PASS
- SQLite smoke PASS
- runtime smoke PASS
- dump dry-run/apply-to-temp-db PASS or SOURCE_INCOMPLETE

判定只能是：
- READY_TO_MERGE_PR15_TOOL_READY_SOURCE_INCOMPLETE
- READY_TO_MERGE_PR15_TRUE_SYNC_VERIFIED
- HOLD_PR15
```

---

## Current Safe Wording

Use this for reports or handoff:

```text
SQLite Web Ready: schema(71 tables), runtime smoke, web runtime, tRPC/DB read all passed.

MySQL → SQLite true data sync is not yet verified.
Current validator supports dry-run only / apply path is not complete.
A MySQL dump exists but is incomplete for the active table set.
Full data sync requires a complete MySQL source or dump and row-count parity across all 8 active tables.
```

---

## Next Status to Expect

Likely successful PR #15 outcome:

```text
READY_TO_MERGE_PR15_TOOL_READY_SOURCE_INCOMPLETE
```

Not expected unless complete source is available:

```text
READY_TO_MERGE_PR15_TRUE_SYNC_VERIFIED
```
