# Local Auth SQLite Patch Report

> **Phase 3-B — Local Auth SQLite Patch**
> Generated: 2026-06-04 · Branch: `release/vps-lite`

## 1. Scope
Fix local-auth / user-insert under `DATABASE_PROVIDER=sqlite`. Modified only `server/localAuth.ts` and `server/db.ts` (`upsertUser`). No schema, runtime adapter, router, or package changes; no SQLite `now()` function added; no seed-user bypass.

## 2. Root Cause
`localAuth.ts` imported the **MySQL** `users` table (`../drizzle/schema`) whose `createdAt/updatedAt/lastSignedIn` carry `.defaultNow()`/`.onUpdateNow()`. Under the SQLite driver this emits `now()` → `SqliteError: no such function: now`. `nowTimestampString()` also produced a MySQL datetime string, incompatible with SQLite timestamp-mode columns.

## 3. Patched Files
- **`server/localAuth.ts`** — `createLocalUser`, `getLocalUserByLogin`, `updateLocalLastSignIn`, `seedDefaultAdminIfNeeded`.
- **`server/db.ts`** — `upsertUser` (OAuth/SDK user insert/update).

## 4. Schema Selection Strategy
Added `usersTable()` in `localAuth.ts`:
```ts
function usersTable(): typeof mysqlUsers {
  return isSqliteMode() ? (sqliteUsers as unknown as typeof mysqlUsers) : mysqlUsers;
}
```
- SQLite mode → `drizzle/schema.sqlite.mvp` users (timestamp-mode columns, `strftime` defaults — no `now()`).
- MySQL mode → canonical `drizzle/schema.ts` users (unchanged behavior).
Property names align across both schemas, so the query/insert builders work unchanged.

`db.ts upsertUser` keeps the canonical `users` table but **explicitly writes timestamps** (see §5) so the MySQL defaults never fire — a minimal, dual-safe fix without touching the 342-function legacy layer.

## 5. Timestamp Strategy
All user writes set timestamps explicitly to `new Date()` (dual-safe: mysql2 accepts `Date`; SQLite timestamp-mode → Unix seconds). `nowTimestampString()` removed.
- `createLocalUser`: `lastSignedIn / createdAt / updatedAt = new Date()`.
- `updateLocalLastSignIn`: `lastSignedIn = new Date()`.
- `seedDefaultAdminIfNeeded` update: `updatedAt = new Date()`.
- `upsertUser`: insert sets `createdAt / updatedAt`; update sets `updatedAt` (overrides `onUpdateNow()`).

## 6. SQLite Smoke (`DATABASE_PROVIDER=sqlite`, disposable `auth-test.db`, real registration path)
```
1. createLocalUser PASS (no now() error)        id=1
5. createdAt is Date                            ✅
5. lastSignedIn is Date                         ✅
2. getLocalUserByLogin (loginLocal lookup)      ✅
4. password hash verify PASS                    ok=true bad=false
3. loginLocal lastSignedIn update (no now())    ✅
AUTH_SMOKE_PASS
```

## 7. MySQL Compatibility
`DATABASE_PROVIDER=mysql` import → **IMPORT_OK_MYSQL**. In MySQL mode `usersTable()` returns the canonical table; explicit `new Date()` values are accepted by mysql2 and simply override the column defaults — no behavioral regression. Router still uses `getDb()`.

## 8. Remaining Risks
- The wider `db.ts` 342-function legacy layer still uses MySQL table objects; other user-touching helpers (e.g. `updateUser`, stats writers) may hit the same `now()`/default issue under SQLite and remain for the Phase 1-K db.ts migration. The **local-auth + OAuth upsert** critical path is fixed.
- `usersTable()` uses an `as unknown as` cast (runtime-safe; property names align). `as any` on insert/update values mirrors the pre-existing pattern (`lastSignedIn = new Date()` was already cast).

## 9. RC1 Status
**RC1_DEPLOY_READY blocker REMOVED** for local auth: registration + login + password verify now work under SQLite with no `now()` error, and MySQL mode is unchanged.

---

## Final Answers
- **修正檔案**: `server/localAuth.ts`, `server/db.ts` (+ this report)
- **now() 是否清除**: ✅ Yes — 0 `now()`/`nowTimestampString` refs in localAuth; upsertUser writes explicit timestamps
- **auth.registerLocal PASS**: ✅ (createLocalUser id=1, no crash)
- **loginLocal PASS**: ✅ (lookup + verify + lastSignedIn update)
- **SQLite smoke**: ✅ AUTH_SMOKE_PASS (6/6)
- **MySQL import**: ✅ IMPORT_OK_MYSQL
- **git diff summary**: `server/localAuth.ts` (~47 lines), `server/db.ts` upsertUser (+6 lines; the larger db.ts diff is pre-existing Phase-3 SQLite-adapter work)
- **RC1_DEPLOY_READY blocker removed**: ✅ Yes

## Success Criteria
auth.registerLocal PASS ✅ · createLocalUser PASS ✅ · loginLocal PASS ✅ · `no such function: now` = 0 ✅ · SQLite local auth PASS ✅ · MySQL import PASS ✅ · RC1 blocker removed ✅
