# VPS Lite Deployment Handoff — SmartBook Lite SQLite RC1

**Version:** RC1 (`v1.0.0-rc1-sqlite`)  
**Branch:** `release/vps-lite`  
**Date:** 2026-06-04  
**Target:** 1 GB RAM VPS — No External MySQL

---

## Quick Start (5 Minutes)

```bash
# 1. Clone & install
git clone -b release/vps-lite <repo-url> /opt/smartbook-lite
cd /opt/smartbook-lite
pnpm install --frozen-lockfile

# 2. Configure environment
cp .env.production.sqlite.example .env
# Edit .env → set SESSION_SECRET, admin credentials, etc.

# 3. Provision database
mkdir -p data
pnpm db:sqlite:push:fresh

# 4. Build & start
pnpm build
pm2 start ecosystem.config.cjs
pm2 save && pm2 startup
```

---

## Environment

### Required Variables

```env
DATABASE_PROVIDER=sqlite
SQLITE_PATH=./data/smartbook.db
NODE_ENV=production
PORT=5000
```

### Key Points

- `DATABASE_PROVIDER=sqlite` → activates SQLite mode (default is MySQL)
- `SQLITE_PATH=./data/smartbook.db` → path to SQLite DB file
- The `mysql2` npm package remains installed but no MySQL server is needed
- Session secret must be generated: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`

### Full Template

See [.env.production.sqlite.example](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/.env.production.sqlite.example)

---

## Provision

### Database Setup

```bash
# Create writable data directory
mkdir -p data

# Push SQLite schema (66 tables + seed data)
pnpm db:sqlite:push:fresh
```

### Expected Output

```text
SQLITE_SCHEMA_PROVISION_PASS
tables = 66
pdfCategories = 5
```

### Verify

```bash
node -e "
  const Database = require('better-sqlite3');
  const db = new Database('./data/smartbook.db');
  const t = db.prepare(\"SELECT count(*) as c FROM sqlite_master WHERE type='table'\").get();
  console.log('Tables:', t.c);
  console.log('WAL:', db.pragma('journal_mode', { simple: true }));
  console.log('FK:', db.pragma('foreign_keys', { simple: true }));
  db.close();
"
```

---

## Start

### Direct (Testing)

```bash
pnpm start
# or
node dist/index.js
```

### PM2 (Production)

```bash
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup  # follow printed sudo command
```

### PM2 Configuration

| Setting | Value |
|---------|-------|
| Process name | `ai-tutor-helper` |
| Exec mode | `fork` |
| Instances | `1` |
| Max memory | `450M` |
| `--max-old-space-size` | `384` |

---

## Validation

After startup, verify each endpoint:

### Home Page

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/
# Expected: 200
```

### Health API

```bash
curl -s http://localhost:5000/api/trpc/system.health?input=%7B%22timestamp%22%3A1%7D
# Expected: {"result":{"data":{"ok":true}}}
```

### TRPC

```bash
# Any TRPC endpoint should respond (not 404/500)
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/trpc
# Expected: non-404 response
```

### Local Auth

```bash
# Register (if default admin not seeded)
curl -s -X POST http://localhost:5000/api/trpc/auth.registerLocal \
  -H "Content-Type: application/json" \
  -d '{"json":{"username":"testuser","password":"Test1234!","name":"Test"}}'

# Login
curl -s -X POST http://localhost:5000/api/trpc/auth.loginLocal \
  -H "Content-Type: application/json" \
  -d '{"json":{"login":"testuser","password":"Test1234!"}}'
```

### SmartBook

```bash
# List smart books (requires auth session)
curl -s http://localhost:5000/api/trpc/smartBookStudent.listBooks
```

### Tutor

```bash
# List tutor subjects (public)
curl -s http://localhost:5000/api/trpc/tutorPublic.listSubjects
```

### Validation Checklist

| # | Check | Expected | Command |
|---|-------|----------|---------|
| 1 | Home Page | HTTP 200 | `curl -o /dev/null -w "%{http_code}" localhost:5000/` |
| 2 | Health API | `{"ok":true}` | `curl localhost:5000/api/trpc/system.health?input=...` |
| 3 | TRPC alive | Non-404 | `curl -o /dev/null -w "%{http_code}" localhost:5000/api/trpc` |
| 4 | Auth register | User created | POST `auth.registerLocal` |
| 5 | Auth login | Session token | POST `auth.loginLocal` |
| 6 | SmartBook list | JSON response | GET `smartBookStudent.listBooks` |
| 7 | Tutor subjects | JSON response | GET `tutorPublic.listSubjects` |
| 8 | PM2 status | `online` | `pm2 status` |
| 9 | Memory usage | < 300 MB | `pm2 describe ai-tutor-helper` |

---

## Rollback

If issues arise, switch back to MySQL in under 1 minute:

```bash
# 1. Stop
pm2 stop ai-tutor-helper

# 2. Switch to MySQL
# Edit .env:
#   DATABASE_PROVIDER=mysql
#   DATABASE_URL=mysql://user:pass@host:3306/smartbook

# 3. Restart
pm2 restart ai-tutor-helper

# 4. Verify
curl -s http://localhost:5000/api/trpc/system.health?input=%7B%22timestamp%22%3A1%7D
```

The SQLite database file is preserved at `data/smartbook.db` — you can switch back to SQLite mode at any time.

---

## Monitoring

```bash
# Real-time logs
pm2 logs ai-tutor-helper --lines 50

# Resource monitoring
pm2 monit

# Process details
pm2 describe ai-tutor-helper

# System resources
free -h && df -h
```

---

## Support Documents

| Document | Purpose |
|----------|---------|
| [VPS_DEPLOYMENT_RUNBOOK.md](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/VPS_DEPLOYMENT_RUNBOOK.md) | Full step-by-step deployment guide |
| [RC1_RELEASE_CHECKLIST.md](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/RC1_RELEASE_CHECKLIST.md) | Pre-deployment validation checklist |
| [RC1_FINAL_VALIDATION_REPORT.md](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/RC1_FINAL_VALIDATION_REPORT.md) | PASS/FAIL matrix for all validation categories |
| [RC1_RELEASE_READINESS.md](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/RC1_RELEASE_READINESS.md) | Release readiness report with file inventory |
| [.env.production.sqlite.example](file:///home/b822726/project/smartbook-lite-sqlite-test/smartbook-lite/.env.production.sqlite.example) | Environment template with comments |
