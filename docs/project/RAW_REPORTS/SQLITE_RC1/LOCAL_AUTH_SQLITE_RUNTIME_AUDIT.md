# Local Auth SQLite Runtime Audit

## 1. Executive Summary

Phase 3-A reproduced the SQLite runtime failure in `auth.registerLocal`.

Result:

```text
RC1_DEPLOY_READY = BLOCKED_BY_LOCAL_AUTH_REGISTER
```

Root cause:

`server/localAuth.ts` imports `users` from the canonical MySQL schema:

```ts
import { users } from "../drizzle/schema";
```

When `DATABASE_PROVIDER=sqlite`, `getDb()` returns the SQLite Drizzle runtime, but `auth.registerLocal` still builds the insert query with the MySQL `users` table metadata. The MySQL schema defines `createdAt` and `updatedAt` with `.defaultNow()`, which Drizzle emits as:

```sql
(now())
```

SQLite does not provide a `now()` SQL function, so registration fails before insert execution.

## 2. Reproduction Result

Environment:

```text
DATABASE_PROVIDER=sqlite
SQLITE_PATH=./data/smartbook.db
```

API reproduction:

```bash
curl -sS -i --max-time 8 \
  -X POST 'http://127.0.0.1:5514/api/trpc/auth.registerLocal?batch=1' \
  -H 'Content-Type: application/json' \
  -d '{"0":{"json":{"username":"phase3audit","password":"Phase3Audit123!","name":"Phase3 Audit","email":"phase3audit@example.com"}}}'
```

Observed response:

```text
HTTP/1.1 500 Internal Server Error
message: no such function: now
path: auth.registerLocal
```

Minimal source reproduction:

```bash
env DATABASE_PROVIDER=sqlite SQLITE_PATH=./data/smartbook.db \
  pnpm exec tsx -e 'import { createLocalUser } from "./server/localAuth.ts"; createLocalUser({ username: `audit-${Date.now()}`, password: "AuditPass123!", name: "Audit User", email: `audit-${Date.now()}@example.com` }).catch((e)=>{ console.error(e?.name); console.error(e?.message); console.error(e?.stack); process.exit(2); });'
```

Observed error:

```text
SqliteError
no such function: now
SqliteError: no such function: now
    at Database.prepare (.../node_modules/.pnpm/better-sqlite3.../better-sqlite3/lib/methods/wrappers.js:5:21)
    at BetterSQLiteSession.prepareQuery (.../node_modules/.pnpm/drizzle-orm.../drizzle-orm/src/better-sqlite3/session.ts:60:28)
    at BetterSQLiteSession.prepareOneTimeQuery (.../node_modules/.pnpm/drizzle-orm.../drizzle-orm/src/sqlite-core/session.ts:250:15)
    at QueryPromise._prepare (.../node_modules/.pnpm/drizzle-orm.../drizzle-orm/src/sqlite-core/query-builders/insert.ts:380:78)
    at QueryPromise.run (.../node_modules/.pnpm/drizzle-orm.../drizzle-orm/src/sqlite-core/query-builders/insert.ts:398:15)
    at QueryPromise.execute (.../node_modules/.pnpm/drizzle-orm.../drizzle-orm/src/sqlite-core/query-builders/insert.ts:414:53)
    at QueryPromise.then (.../node_modules/.pnpm/drizzle-orm.../drizzle-orm/src/query-promise.ts:31:15)
```

Generated SQL from equivalent insert builder:

```sql
insert into "users" (
  "id", "openId", "username", "password_hash", "name", "email",
  "loginMethod", "role", "createdAt", "updatedAt", "lastSignedIn",
  "subscriptionPlan", "subscriptionExpiresAt", "examType", "examTarget",
  "studentStatus", "nickname", "credits", "permanent_credits",
  "daily_credits", "subject_category", "teacher_id", "student_type",
  "teaching_role", "gender", "chat_style", "last_daily_grant_date",
  "daily_earned_credits", "daily_earned_date", "is_first_login",
  "is_banned", "ban_reason", "banned_at", "identity_type",
  "member_account", "trial_reset_date"
) values (
  null, ?, ?, ?, ?, ?, ?, ?, (now()), (now()), ?, ?, null, null,
  null, null, null, ?, ?, ?, null, null, ?, null, null, ?, null,
  ?, null, ?, ?, null, null, ?, null, null
)
```

The failing SQL source is the insert generated for `users.createdAt` and `users.updatedAt`.

## 3. registerLocal Flow

`auth.registerLocal` calls `createLocalUser()` in `server/localAuth.ts`.

Flow:

1. Normalize username and email.
2. Check existing user:

```ts
db.select({ id: users.id }).from(users)
```

3. Build local OpenID:

```ts
local:${username}
```

4. Hash password through `hashPassword()`.
5. Insert user:

```ts
await db.insert(users).values({
  openId,
  username,
  email: email ?? undefined,
  name: input.name,
  passwordHash: await hashPassword(input.password),
  loginMethod: "local",
  role: input.role ?? "user",
  lastSignedIn: nowTimestampString(),
});
```

6. Re-read the user with `getLocalUserByLogin(username)`.

`hashPassword()` is not involved in the SQLite failure. It uses Node crypto `scrypt` and completes before the insert is prepared.

## 4. now() Source

The source is `drizzle/schema.ts`, the canonical MySQL schema:

```ts
export const users = mysqlTable("users", {
  createdAt: timestamp({ mode: "string" }).defaultNow().notNull(),
  updatedAt: timestamp({ mode: "string" }).defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp({ mode: "string" }).defaultNow().notNull(),
});
```

The SQLite MVP schema does not use MySQL `now()`:

```ts
export const users = sqliteTable("users", {
  createdAt: integer("createdAt", { mode: "timestamp" }).default(sql`(strftime('%s','now'))`),
  updatedAt: integer("updatedAt", { mode: "timestamp" }),
  lastSignedIn: integer("lastSignedIn", { mode: "timestamp" }),
});
```

The runtime mismatch is:

```text
SQLite Drizzle runtime + MySQL users table metadata
```

This causes Drizzle to emit MySQL default SQL into a SQLite query.

## 5. Affected Fields

Direct failing fields:

```text
users.createdAt
users.updatedAt
```

Field observed but not the current `now()` source:

```text
users.lastSignedIn
```

`createLocalUser()` explicitly writes `lastSignedIn` using `nowTimestampString()`, so `lastSignedIn` appears as a bound parameter in the generated SQL. It is not the immediate `no such function: now` source for `auth.registerLocal`.

## 6. Schema Mismatch Analysis

`server/db.ts` supports SQLite provider selection:

```ts
if (isSqliteMode()) {
  _db = getSqliteDb() as unknown as ReturnType<typeof drizzleMysql>;
  return _db;
}
```

The SQLite runtime exists, but some auth paths still import MySQL schema tables.

Observed table sources:

```text
server/localAuth.ts                 -> ../drizzle/schema users
server/db.ts upsertUser             -> ../drizzle/schema users
drizzle/schema.sqlite.mvp.ts users  -> valid SQLite table definition
```

`dist/index.js` also contains both generated table definitions:

```text
canonical MySQL users table
SQLite MVP users2 table
```

The register flow uses the canonical MySQL `users` table, not the SQLite MVP `users` table.

## 7. Impact Assessment

### P0

1. `auth.registerLocal` is unavailable in SQLite mode.
2. `seedDefaultAdminIfNeeded()` can fail when it calls `createLocalUser()` in non-production or when dev auto login is enabled.
3. New OAuth/session user creation through `server/db.ts upsertUser()` is likely affected because it also inserts into canonical MySQL `users` while SQLite mode is active.

### P1

1. `loginLocal` for an existing user should be validated after patch. The read and last-login update use the same canonical `users` import. The immediate registration failure blocks creating a fresh local user through the normal API path.

### P2

1. Cleanup opportunity: contain or remove mixed MySQL schema imports in SQLite runtime paths. The current cast in `getDb()` keeps runtime wiring simple, but auth/user code needs provider-aware table selection to avoid dialect defaults.

## 8. Minimal Patch Recommendation

Recommended Phase 3-B patch:

1. Make local auth use provider-aware `users` table metadata.
2. In SQLite mode, use `drizzle/schema.sqlite.mvp.ts` `users`.
3. In MySQL mode, keep `drizzle/schema.ts` `users`.
4. Apply the same provider-aware user insert strategy to `server/db.ts upsertUser()` so OAuth/new-session user creation does not hit the same `now()` source.
5. Write explicit timestamp values for user insert/update fields where needed, using SQLite-compatible `Date` values for SQLite timestamp-mode columns and preserving MySQL path behavior.

Do not add a SQLite user-defined `now()` function as the primary fix. That would mask the schema mismatch and leave MySQL table metadata active in SQLite runtime paths.

Smallest possible workaround:

```text
Provide explicit createdAt and updatedAt values in user inserts.
```

This may avoid the immediate `now()` error, but it does not fully resolve the mixed schema metadata problem. Provider-aware table selection is the safer minimal production patch.

## 9. RC1 Deployment Status

```text
RC1_DEPLOY_READY = BLOCKED_BY_LOCAL_AUTH_REGISTER
```

Proceed to Phase 3-B Local Auth SQLite Patch before VPS Lite RC1 deployment validation can be considered complete.
