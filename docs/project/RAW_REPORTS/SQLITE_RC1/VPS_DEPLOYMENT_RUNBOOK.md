# VPS Deployment Runbook — SmartBook Lite SQLite RC1

**Version:** RC1  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-04  
**Target:** 1 GB RAM VPS with SQLite (no external MySQL)

---

## 1. VPS Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| OS | Ubuntu 24.04 LTS | Ubuntu 24.04 LTS |
| Node.js | v22+ (LTS) | v22.x |
| RAM | 1 GB | 1 GB |
| Swap | 2 GB | 2 GB |
| Disk | 10 GB+ | 20 GB |
| CPU | 1 vCPU | 2 vCPU |

### System Packages

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools (required for better-sqlite3 native compilation)
sudo apt install -y build-essential python3 git

# Install Node.js 22 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Install pnpm
corepack enable
corepack prepare pnpm@latest --activate

# Verify
node --version    # v22.x.x
pnpm --version    # 9.x+
```

### Swap Configuration (1 GB VPS)

```bash
# Create 2 GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Persist across reboots
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h
```

---

## 2. Installation

### Clone Repository

```bash
# Clone the release branch
git clone -b release/vps-lite <your-repo-url> /opt/smartbook-lite
cd /opt/smartbook-lite
```

### Install Dependencies

```bash
pnpm install --frozen-lockfile
```

### Verify better-sqlite3

```bash
# Test native module loads
node -e "require('better-sqlite3'); console.log('better-sqlite3 OK')"
```

Expected output:

```text
better-sqlite3 OK
```

If this fails, rebuild native modules:

```bash
pnpm rebuild better-sqlite3
```

### Build Production Bundle

```bash
pnpm build
```

Verify the build output:

```bash
ls -la dist/index.js
```

---

## 3. Environment Configuration

### Create .env

```bash
cp .env.production.sqlite.example .env
```

### Required Variables

Edit `.env` and configure:

```env
# Database — SQLite mode
DATABASE_PROVIDER=sqlite
SQLITE_PATH=./data/smartbook.db

# Runtime
NODE_ENV=production
PORT=5000
ENABLE_TRPC_REQUEST_LOGS=false

# Auth — set your own values
JWT_SECRET=<generate-a-random-64-char-hex-string>
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=<your-strong-password>
OWNER_OPEN_ID=local:admin
```

### Generate JWT_SECRET

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Important Notes

- `DATABASE_PROVIDER=sqlite` activates SQLite mode. Without this, the app defaults to MySQL.
- `SQLITE_PATH` must point to a writable location. The directory must exist before first run.
- The `mysql2` npm package must remain installed (static import dependency) even though no MySQL server is used.

---

## 4. Database Provision

### Create Data Directory

```bash
mkdir -p data
```

### Run SQLite Schema Push

```bash
pnpm db:sqlite:push:fresh
```

### Expected Output

```text
SQLITE_SCHEMA_PROVISION_PASS
tables = 66
pdfCategories = 5
```

### Verify Database File

```bash
ls -la data/smartbook.db

# Check table count
node -e "
  const Database = require('better-sqlite3');
  const db = new Database('./data/smartbook.db');
  const tables = db.prepare(\"SELECT count(*) as c FROM sqlite_master WHERE type='table'\").get();
  console.log('Tables:', tables.c);
  db.close();
"
```

Expected: `Tables: 66` (or more if indices are counted)

### Verify PRAGMAs

```bash
node -e "
  const Database = require('better-sqlite3');
  const db = new Database('./data/smartbook.db');
  console.log('journal_mode:', db.pragma('journal_mode', { simple: true }));
  console.log('foreign_keys:', db.pragma('foreign_keys', { simple: true }));
  db.close();
"
```

Expected:

```text
journal_mode: wal
foreign_keys: 1
```

---

## 5. Runtime Validation

### Start the Application

```bash
# Direct start (for initial testing)
node dist/index.js
```

Or using pnpm:

```bash
pnpm start
```

### Verify Endpoints

Open a new terminal and test:

```bash
# Health API
curl -s http://localhost:5000/api/trpc/system.health?input=%7B%22timestamp%22%3A1%7D

# Expected: {"result":{"data":{"ok":true}}}

# Home Page
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/

# Expected: 200
```

### Console Verification

The startup log should show:

- No MySQL connection errors
- No `MODULE_NOT_FOUND` errors
- Server listening on PORT 5000

### Stop Test Server

```bash
# Ctrl+C or
kill $(lsof -t -i:5000)
```

---

## 6. PM2 Setup

### Install PM2

```bash
npm install -g pm2
```

### Start with PM2

```bash
cd /opt/smartbook-lite
pm2 start ecosystem.config.cjs
```

### Verify PM2 Status

```bash
pm2 status
```

Expected:

```text
┌─────────────────┬────┬──────┬───────┬────────┬─────────┐
│ App name        │ id │ mode │ status│ restart│ memory  │
├─────────────────┼────┼──────┼───────┼────────┼─────────┤
│ ai-tutor-helper │ 0  │ fork │ online│ 0      │ < 300MB │
└─────────────────┴────┴──────┴───────┴────────┴─────────┘
```

### Persist PM2 Process

```bash
# Save current process list
pm2 save

# Generate startup script (auto-start on reboot)
pm2 startup
# Follow the printed sudo command
```

### PM2 Monitoring

```bash
# Real-time logs
pm2 logs ai-tutor-helper

# Monitoring dashboard
pm2 monit

# Memory check
pm2 describe ai-tutor-helper | grep memory
```

### PM2 Environment Notes

The `ecosystem.config.cjs` sets:

| Variable | Value |
|----------|-------|
| `NODE_ENV` | `production` |
| `PORT` | `5000` (from env) |
| `NODE_OPTIONS` | `--max-old-space-size=384` |
| `max_memory_restart` | `450M` |

**Important:** `DATABASE_PROVIDER` and `SQLITE_PATH` are read from `.env` by the application, not from `ecosystem.config.cjs`. Ensure your `.env` file is correctly configured.

---

## 7. Rollback to MySQL

If you need to revert to MySQL mode:

### Step 1 — Stop the Application

```bash
pm2 stop ai-tutor-helper
```

### Step 2 — Update Environment

Edit `.env`:

```env
DATABASE_PROVIDER=mysql
DATABASE_URL=mysql://user:password@host:3306/smartbook
```

Or remove `DATABASE_PROVIDER` entirely (defaults to MySQL).

### Step 3 — Restart

```bash
pm2 restart ai-tutor-helper
```

### Step 4 — Verify

```bash
curl -s http://localhost:5000/api/trpc/system.health?input=%7B%22timestamp%22%3A1%7D
# Expected: {"result":{"data":{"ok":true}}}
```

### Notes

- The SQLite database file (`data/smartbook.db`) is preserved. You can switch back to SQLite mode later.
- No data migration between MySQL and SQLite is automated. Each database is independent.
- The `drizzle/schema.ts` (MySQL) and `drizzle/schema.sqlite.mvp.ts` (SQLite) are separate schema definitions.

---

## 8. Troubleshooting

### Problem: `better-sqlite3` module not found

**Symptom:**

```text
Error: Cannot find module 'better-sqlite3'
```

**Solution:**

```bash
pnpm install
pnpm rebuild better-sqlite3
node -e "require('better-sqlite3'); console.log('OK')"
```

If on Alpine Linux (Docker):

```bash
apk add --no-cache python3 make g++
pnpm rebuild better-sqlite3
```

---

### Problem: `SQLITE_PATH` permission denied

**Symptom:**

```text
SqliteError: unable to open database file
```

**Solution:**

```bash
# Ensure directory exists
mkdir -p data

# Check permissions
ls -la data/

# Fix ownership (if running as non-root user)
sudo chown -R $(whoami):$(whoami) data/

# Fix permissions
chmod 755 data/
```

---

### Problem: Database locked (SQLITE_BUSY)

**Symptom:**

```text
SqliteError: database is locked
```

**Cause:** Another process has an exclusive lock on the database file.

**Solution:**

```bash
# Check for other processes using the DB
lsof data/smartbook.db

# Kill stale processes
pm2 stop ai-tutor-helper
pm2 delete ai-tutor-helper

# Remove stale WAL/SHM files (only when NO process is using the DB)
rm -f data/smartbook.db-wal data/smartbook.db-shm

# Restart
pm2 start ecosystem.config.cjs
```

**Prevention:** The adapter sets `busy_timeout = 5000` (wait 5 seconds before failing). Under normal single-process operation, this should not occur.

---

### Problem: `mysql2` import dependency error

**Symptom:**

```text
Error: Cannot find module 'mysql2'
```

**Cause:** `mysql2` was removed from `node_modules`, but `server/db.ts` has a static import of `drizzle-orm/mysql2`.

**Solution:**

```bash
# mysql2 must remain installed even in SQLite-only mode
pnpm install

# Verify
node -e "require('mysql2'); console.log('mysql2 OK')"
```

**Why:** `server/db.ts` line 2 contains `import { drizzle as drizzleMysql } from "drizzle-orm/mysql2"` — this is a static top-level import that executes regardless of `DATABASE_PROVIDER`. The mysql2 npm package must be present, but no MySQL server connection is attempted.

---

### Problem: Server crashes on startup with OOM

**Symptom:**

```text
FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory
```

**Solution:**

```bash
# Check current memory limit
node -e "console.log(process.memoryUsage())"

# Ensure swap is enabled
free -h

# Ensure ecosystem.config.cjs has correct NODE_OPTIONS
# NODE_OPTIONS: "--max-old-space-size=384"
```

---

### Problem: Port 5000 already in use

**Symptom:**

```text
Error: listen EADDRINUSE: address already in use :::5000
```

**Solution:**

```bash
# Find the process using port 5000
lsof -i :5000

# Kill it
kill -9 $(lsof -t -i:5000)

# Or change the port in .env
# PORT=5001
```

---

## Appendix A: File Layout (Production)

```text
/opt/smartbook-lite/
├── .env                          ← Production environment (from template)
├── data/
│   ├── smartbook.db              ← SQLite database file
│   ├── smartbook.db-wal          ← WAL file (auto-managed)
│   └── smartbook.db-shm          ← SHM file (auto-managed)
├── dist/
│   └── index.js                  ← Production bundle
├── ecosystem.config.cjs          ← PM2 configuration
├── node_modules/                 ← Dependencies (includes mysql2 + better-sqlite3)
├── drizzle/
│   ├── schema.ts                 ← MySQL schema (kept for dual-mode)
│   └── schema.sqlite.mvp.ts     ← SQLite schema (66 tables)
└── package.json
```

## Appendix B: Quick Commands

| Action | Command |
|--------|---------|
| Start | `pm2 start ecosystem.config.cjs` |
| Stop | `pm2 stop ai-tutor-helper` |
| Restart | `pm2 restart ai-tutor-helper` |
| Logs | `pm2 logs ai-tutor-helper --lines 100` |
| Status | `pm2 status` |
| Monitor | `pm2 monit` |
| Health Check | `curl http://localhost:5000/api/trpc/system.health?input=%7B%22timestamp%22%3A1%7D` |
| DB Table Count | `node -e "const d=require('better-sqlite3')('./data/smartbook.db');console.log(d.prepare(\"SELECT count(*) as c FROM sqlite_master WHERE type='table'\").get());d.close()"` |
| Rebuild Native | `pnpm rebuild better-sqlite3` |
