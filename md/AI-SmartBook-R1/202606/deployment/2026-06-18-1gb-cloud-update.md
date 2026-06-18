# 1GB Cloud Update Handoff - AI-SmartBook-R1

## Date
2026-06-18

## Status
user-accepted / ready-for-1gb-cloud-update

## Main Code Repo
`b827262-cell/AI-SmartBook-R1`

## Target Branch
`feat/student-category-cover-reader-chat`

## Release Commit
`a04232f3037f3751c7a26e81a29de735875d88fb`

## Markdown Backup Repo
`b827262-cell/Project-md-backup`

## AGY Acceptance Report
`md/AI-SmartBook-R1/202606/agy-acceptance/a04232f3037f3751c7a26e81a29de735875d88fb.md`

## User Acceptance
User confirmed the mobile reader control task is complete and approved moving to the 1GB cloud computer update.

## Release Scope

This release includes the Android Chrome mobile reader controls fix:

1. Two-row mobile bottom action bar.
2. Visible page controls row:
   - previous page button,
   - current page / total page display,
   - page input,
   - jump button,
   - next page button.
3. Existing mobile action buttons remain available:
   - 返回,
   - 目錄,
   - 問AI,
   - 筆記.
4. Touch-zone test IDs added for mobile verification.
5. Bottom offsets for page-jump bar and toast use dynamic `--mobile-reader-bottom` measurement.

## 1GB Cloud Update Commands

> Run these commands on the 1GB cloud computer. Adjust project path if needed.

### 1. SSH into the 1GB cloud machine

```bash
ssh <user>@<1gb-cloud-ip>
```

### 2. Go to the deployed project folder

```bash
cd /opt/AI-SmartBook-R1 2>/dev/null || cd ~/project/AI-SmartBook-R1
```

### 3. Confirm current branch and clean status

```bash
git status --short
git branch --show-current
```

If the working tree is not clean, back up before pulling:

```bash
mkdir -p ~/backup/AI-SmartBook-R1-$(date +%Y%m%d-%H%M%S)
git status --short > ~/backup/AI-SmartBook-R1-$(date +%Y%m%d-%H%M%S)/git-status.txt
```

### 4. Fetch and checkout target branch

```bash
git fetch origin
git checkout feat/student-category-cover-reader-chat
git pull --ff-only origin feat/student-category-cover-reader-chat
```

### 5. Verify release commit

```bash
git rev-parse HEAD
git log --oneline -3
```

Expected HEAD:

```text
a04232f3037f3751c7a26e81a29de735875d88fb
```

If HEAD is not the expected commit, stop and report blocker.

### 6. Install dependencies carefully for 1GB RAM

Prefer frozen lockfile if dependencies are already installed:

```bash
pnpm install --frozen-lockfile --prefer-offline
```

If memory is tight, use swap first:

```bash
free -h
swapon --show
```

Optional 2GB swap creation if no swap exists:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -h
```

### 7. Build frontend/admin if required

```bash
pnpm build
```

If full monorepo build is too heavy on 1GB RAM, build only the deployed app package if the workspace supports it:

```bash
pnpm --filter AI-Stu-R1 build
pnpm --filter AI-adm-D1 build
```

### 8. Restart service

Use the actual service manager on the 1GB machine.

If systemd:

```bash
sudo systemctl restart smartbook || sudo systemctl restart ai-smartbook || true
sudo systemctl status smartbook --no-pager || sudo systemctl status ai-smartbook --no-pager || true
```

If PM2:

```bash
pm2 list
pm2 restart all
pm2 save
```

If Vite/Node dev service is manually running, restart the terminal process or its tmux/screen session.

### 9. Nginx check if used

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 10. Health check

Replace host and port as needed:

```bash
curl -I --max-time 5 http://127.0.0.1/
curl -I --max-time 5 http://127.0.0.1:5173/ || true
curl -I --max-time 5 http://127.0.0.1:4300/ || true
```

### 11. Manual mobile verification

Open Android Chrome and verify:

1. Reader page loads without white screen.
2. Bottom two-row control bar is visible.
3. Page input and jump button work.
4. Previous / next page buttons work.
5. 返回 / 目錄 / 問AI / 筆記 still work.
6. Console has no runtime error.

## Rollback Plan

If deployment fails:

```bash
git log --oneline -5
git checkout <previous-good-commit>
pnpm build
sudo systemctl restart smartbook || pm2 restart all
```

Previous known baseline before this fix:

```text
5480378a04dde6641a49e95e23bd48c9b3b04c16
```

## Known Risks

1. 1GB RAM may be insufficient for full monorepo dependency installation or full build without swap.
2. Codex report noted pre-existing TypeScript typecheck errors that are not part of this mobile-reader fix.
3. If the cloud machine uses a different branch or old service process, the UI may still show the old build until the service is restarted.

## ChatGPT Sync Summary
使用者已完成驗收，Android Chrome 手機版 Reader 控制列修正可結案。請將 1GB 雲端電腦更新到 `AI-SmartBook-R1` commit `a04232f3037f3751c7a26e81a29de735875d88fb`，分支 `feat/student-category-cover-reader-chat`。更新後需重新 build/restart，並用手機確認底部兩列控制列、頁碼跳轉、上一頁/下一頁與 PDF 顯示正常。
