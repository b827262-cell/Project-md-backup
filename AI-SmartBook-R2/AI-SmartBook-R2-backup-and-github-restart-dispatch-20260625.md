# AI-SmartBook-R2 Backup and GitHub Restart Dispatch

Date: 2026-06-25
Repository for this note: `b827262-cell/Project-md-backup`
Target project: `project/AI-SmartBook-R2`
Status: `ready-for-local-execution`

## 1. User request

Move the current local `project/AI-SmartBook-R2` project into a backup area, then restart the project workflow from GitHub with a clean baseline.

This note is a dispatch document for local agents and GitHub-side coordination.

## 2. Important boundary

GitHub can store this runbook and project records, but GitHub cannot directly move a local directory such as:

```text
~/project/AI-SmartBook-R2
/project/AI-SmartBook-R2
```

The actual folder move must be executed on the local machine or server where the directory exists.

## 3. Goal

Keep the current local work safe as a timestamped backup, then restart from GitHub using the protected canonical branch.

Recommended source of truth for restart:

```text
Repository: b827262-cell/AI-SmartBook-R1
Branch: master
```

## 4. Local backup commands

Run on the machine that currently contains `AI-SmartBook-R2`.

### 4.1 Detect current project path

```bash
ls -la ~/project
ls -la /project 2>/dev/null || true
```

Find the actual folder. Common paths:

```text
~/project/AI-SmartBook-R2
/project/AI-SmartBook-R2
```

### 4.2 Create backup folder

```bash
mkdir -p ~/project/_backup
```

### 4.3 Move current project into backup area

If the project is under `~/project`:

```bash
cd ~/project
mv AI-SmartBook-R2 _backup/AI-SmartBook-R2-backup-20260625
```

If the project is under `/project`:

```bash
mkdir -p /project/_backup
cd /project
mv AI-SmartBook-R2 _backup/AI-SmartBook-R2-backup-20260625
```

### 4.4 Confirm backup exists

```bash
ls -la ~/project/_backup/AI-SmartBook-R2-backup-20260625 2>/dev/null || true
ls -la /project/_backup/AI-SmartBook-R2-backup-20260625 2>/dev/null || true
```

Do not delete the backup folder.

## 5. Fresh restart from GitHub

After the old local folder is safely moved, clone from GitHub again.

Recommended location:

```bash
mkdir -p ~/project
cd ~/project

git clone https://github.com/b827262-cell/AI-SmartBook-R1.git AI-SmartBook-R2
cd AI-SmartBook-R2

git checkout master
git pull --ff-only origin master
```

## 6. Baseline verification after clone

```bash
corepack enable
pnpm install --frozen-lockfile

pnpm --filter AI-adm-D1 typecheck
pnpm --filter AI-adm-D1 build

pnpm --filter AI-Stu-R1 typecheck
pnpm --filter AI-Stu-R1 build
```

Expected result:

```text
AI-adm-D1 typecheck: PASS
AI-adm-D1 build: PASS
AI-Stu-R1 typecheck: PASS
AI-Stu-R1 build: PASS
```

A Vite chunk-size warning is acceptable if the build succeeds.

## 7. Restart development branch

After baseline verification, start the next development phase from the latest `master`.

```bash
git checkout master
git pull --ff-only origin master
git checkout -b feat/r2-one-click-solve-followup
```

## 8. Rules for the restart

1. Do not continue development directly from old local `AI-SmartBook-R2`.
2. Do not merge PR #4.
3. Do not integrate `85152bbd` now.
4. Use old branches only as read-only references.
5. Start new source-code work from latest protected `master`.
6. Keep One-click Solve as the next primary milestone.

## 9. Current GitHub closure status

| Item | Result |
| --- | --- |
| PR #5 | R2 main integration merged |
| PR #6 | post-merge cleanup report merged |
| PR #7 | governance / handoff docs merged |
| PR #11 | final cleanup docs merged |
| PR #12 | cleanup complete next-phase docs merged |
| PR #13 | PR4 / AntiG defer docs merged |
| PR #4 | closed, not merged |
| AntiG commit `85152bbd` | deferred |
| Current next phase | One-click Solve |

## 10. Multi-agent dispatch

## Agent 1 — Local executor / Codex

Mission:

```text
Move the current local AI-SmartBook-R2 folder into a timestamped backup directory and clone a fresh copy from GitHub master.
```

Rules:

1. Do not delete the old project.
2. Move it into `_backup` only.
3. Clone from `b827262-cell/AI-SmartBook-R1` into a new `AI-SmartBook-R2` folder.
4. Run baseline verification.
5. Report exact local path and commands executed.

Required termination report:

```md
## 終止回報

- status: success / failure / blocker / permission-halt
- old project path:
- backup path:
- fresh clone path:
- current branch:
- current commit SHA:
- typecheck/build result:
- failure:
- blocker:
- permission-halt:
```

## Agent 2 — AGY / Gemini

Mission:

```text
Read-only verification of fresh clone and branch hygiene.
```

Check:

```text
fresh clone uses master
PR #4 remains closed
AntiG commit 85152bbd remains deferred
no old topic branch is used as new base
```

## Agent 3 — Codex-5.3 Spark

Mission:

```text
Run typecheck/build on the fresh clone.
```

Commands:

```bash
pnpm --filter AI-adm-D1 typecheck
pnpm --filter AI-adm-D1 build
pnpm --filter AI-Stu-R1 typecheck
pnpm --filter AI-Stu-R1 build
```

## Agent 4 — GPT-5.5 final coordinator

Mission:

```text
After backup and fresh clone verification, authorize the next branch for One-click Solve.
```

Expected branch:

```text
feat/r2-one-click-solve-followup
```

## 11. Final expected state

```text
local old AI-SmartBook-R2: moved to backup
new AI-SmartBook-R2: fresh clone from GitHub master
next development branch: feat/r2-one-click-solve-followup
source code changed during backup: no
GitHub master remains protected and canonical
```
