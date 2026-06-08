# RC1 Deployment Checklist

Project: `AI Tutor Helper / SmartBook Lite`  
Branch: `release/vps-lite`

## Pre-Deployment

- `runtime bundle`: verify `smartbook-lite-runtime.tar.gz` exists and checksum matches `DEPLOYMENT_MANIFEST.md`
- `sqlite db`: prepare target path `./data/smartbook.db` and confirm schema push will be run
- `env`: copy `.env.production.sqlite.example` to `.env` and set `DATABASE_PROVIDER=sqlite`
- `backup`: create pre-deploy backup for runtime bundle and DB file
- `pm2`: verify PM2 is installed and the service command is known

## Deployment

- `upload`: upload runtime bundle and required env/config files to the VPS
- `extract`: extract bundle into the target runtime directory
- `permissions`: create `data/` and verify the app user can write to it
- `smoke test`: run `pnpm db:sqlite:push:fresh`, start the app, then verify health and home page

## SQLite Connectivity Gate (MANDATORY)

> **Blocking gate.** Run this **after** `pnpm db:sqlite:push:fresh` and **after** the app has started,
> and **before** deployment sign-off. Run it from the application directory (e.g. `/opt/smartbook-lite`)
> where `.env` and `node_modules/better-sqlite3` live. The gate opens the DB **read-only**, so it is safe
> to run while the app is live (WAL allows concurrent readers).
>
> **If ANY check reports `[FAIL]`, STOP. Do not proceed to sign-off. Report the exact failing check.**

### One-shot gate (runs all checks, exits non-zero on failure)

```bash
node <<'GATE'
const fs = require('fs');
const envTxt = fs.existsSync('.env') ? fs.readFileSync('.env', 'utf8') : '';
const provider = ((envTxt.match(/^DATABASE_PROVIDER=(.*)$/m) || [, '<unset>'])[1] || '').trim();
const pathSet  = ((envTxt.match(/^SQLITE_PATH=(.*)$/m) || [, ''])[1] || '').trim();
const p = process.env.SQLITE_PATH || pathSet || './data/smartbook.db';
let fail = false;

console.log('1. DATABASE_PROVIDER =', provider, provider === 'sqlite' ? '[OK]' : '[FAIL]');
if (provider !== 'sqlite') fail = true;

console.log('2. SQLITE_PATH       =', pathSet || '<unset>', pathSet ? '[OK]' : '[FAIL]');
if (!pathSet) fail = true;

const exists = fs.existsSync(p);
console.log('3. DB file exists    =', exists ? '[OK] ' + p : '[FAIL] ' + p);
if (!exists) { console.log('GATE: FAIL (DB file missing — schema push not run?)'); process.exit(1); }

const d = require('better-sqlite3')(p, { readonly: true });
const integ = d.pragma('integrity_check', { simple: true });
const n = d.prepare("select count(*) c from sqlite_master where type='table' and name not like 'sqlite_%'").get().c;
d.close();

console.log('4. integrity_check   =', integ, integ === 'ok' ? '[OK]' : '[FAIL]');
if (integ !== 'ok') fail = true;

console.log('5. sqlite_master tables =', n);
console.log('6. non-zero / expect 66 =', n >= 1 ? (n === 66 ? '[OK] 66' : '[WARN] expected 66, got ' + n) : '[FAIL] 0 tables');
if (n < 1) fail = true;

console.log('7. NOTE: /api/trpc/system.health is liveness-only ({ ok: true }, no DB query) — NOT a DB validation signal.');
console.log('GATE:', fail ? 'FAIL' : 'PASS');
process.exit(fail ? 1 : 0);
GATE
```

### Required checks (all must pass)

| # | Check | Pass condition | Fail action |
|---|-------|----------------|-------------|
| 1 | `DATABASE_PROVIDER=sqlite` | `.env` resolves to `sqlite`; confirm the **running** process agrees: `pm2 env 0 \| grep '^DATABASE_PROVIDER='` | `<unset>`/`mysql` → app is in the wrong mode; STOP |
| 2 | `SQLITE_PATH` is set | non-empty value (e.g. `./data/smartbook.db`) | empty → STOP |
| 3 | SQLite DB file exists | file at `SQLITE_PATH` is present | missing → schema push was skipped; STOP |
| 4 | `PRAGMA integrity_check` | returns exactly `ok` | any other value → DB corrupt; STOP |
| 5 | `sqlite_master` table count | counts `type='table' AND name NOT LIKE 'sqlite_%'` | — |
| 6 | Table count non-zero (expect 66) | `>= 1` required; **66** expected for the MVP schema (matches `scripts/sqlite-provision.ts`) | `0` → empty/unprovisioned DB, STOP; `!= 66` → investigate schema drift before sign-off |
| 7 | Health check is **not** DB validation | `/api/trpc/system.health` is liveness-only (`{ ok: true }`, no DB query — `server/_core/systemRouter.ts`); DB readiness is established ONLY by checks 1–6 | treating health as DB-OK → STOP and run checks 1–6 |

## Post-Deployment

- `health check`: call `/api/trpc/system.health` — **liveness only**. Returns `{ ok: true }` with NO database query; this MUST NOT be treated as DB validation (see the SQLite Connectivity Gate above).
- `login test`: verify admin login succeeds (requires a non-empty `JWT_SECRET` in `.env` — see runbook §3)
- `student page`: open the student-facing SmartBook / Tutor path
- `admin page`: open the admin dashboard and verify key pages load
- `sqlite validation`: **MANDATORY — run the SQLite Connectivity Gate above.** All six DB checks (provider, path, file, `integrity_check`, table count, non-zero/66) must pass before sign-off. WAL mode is verified separately in the runbook PRAGMA step.

## Rollback

- `restore db`: restore the previous SQLite DB backup or switch back to MySQL configuration
- `restore runtime`: restore the previous runtime bundle if the release artifact is faulty
- `restart service`: restart PM2 and verify health after rollback

## Release Gates

- `RC1 core routers`: PASS in final validation
- `SQLite schema provision`: required before first runtime boot
- `mysql2 package`: must remain installed
- `non-core SQLite gaps`: accepted for Lite RC1 scope

## Final Gate

```text
Deploy only if:
  - runtime bundle checksum matches
  - .env is complete (including a non-empty JWT_SECRET)
  - SQLite schema is provisioned
  - SQLite Connectivity Gate passes (provider, path, file, integrity_check, table count = 66)
  - better-sqlite3 validated on the target VPS (Node 22 / Ubuntu 24.04)
  - PM2 runtime is healthy
  - target-host smoke checks pass
```
