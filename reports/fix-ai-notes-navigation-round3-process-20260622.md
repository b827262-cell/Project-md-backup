# Round 3 Process Handoff: fix-ai-notes-navigation

Date: 2026-06-22

## 1. Purpose

This document is a compact third-round handoff process for Codex CLI using `gpt-5.3-codex-spark` with a 128K context window and Ultra High / Xhigh reasoning.

Round 1 and Round 2 have already produced process reports for:

```text
upstream/codex/question-bank-json-import
upstream/codex/smart-solve-json-import
```

Round 3 must only continue with the `fix-ai-notes-navigation` branch.

Do not reload the full previous conversation. Do not rerun the three-branch audit in one session.

## 2. Mode

Execution language:

```text
GitHub Execution in English.
```

Termination report language:

```text
Termination report in Traditional Chinese.
```

## 3. Target Repository

Local working directory:

```text
/home/b827262/project/temp/smartbook-platform/ai_tutor_helper
```

Remotes:

```text
origin   https://github.com/b827262-cell/ai_tutor_helper.git
upstream https://github.com/iamflashon/ai_tutor_helper.git
```

Baseline branch:

```text
origin/main
```

## 4. Previous Confirmed Context

Known facts from earlier process reports:

- The correct repository is `/home/b827262/project/temp/smartbook-platform/ai_tutor_helper`.
- `origin` does not contain the required `codex/*` branches.
- `upstream` contains the required `codex/*` branches.
- The previous long Codex session failed because the Codex model context window was exhausted.
- The issue was context size, not GitHub, Git, or repository corruption.
- Round 1 was scoped to `upstream/codex/question-bank-json-import`.
- Round 2 was scoped to `upstream/codex/smart-solve-json-import`.
- Round 3 must only process `upstream/codex/fix-ai-notes-navigation`.

## 5. Branches Known From Previous Discovery

The three upstream Codex branches were:

```text
upstream/codex/fix-ai-notes-navigation
upstream/codex/question-bank-json-import
upstream/codex/smart-solve-json-import
```

## 6. Round 3 Target Branch

Only continue with this branch in the third round:

```text
upstream/codex/fix-ai-notes-navigation
```

Do not process the other two branches in this round.

## 7. Round 3 Goal

Create one Markdown report for the `fix-ai-notes-navigation` branch only.

The report should summarize:

1. Repository status.
2. Target branch existence.
3. Baseline comparison against `origin/main`.
4. Main purpose of the branch.
5. Important changed files.
6. Possible merge risks.
7. Whether changes look isolated or risky.
8. Recommended next action.

## 8. Strict Constraints

Do not do any of the following:

- Do not modify source code.
- Do not perform a full three-branch audit.
- Do not inspect huge diffs unless absolutely necessary.
- Do not stage unrelated working tree changes.
- Do not paste or reload the full previous conversation.
- Do not continue if the working directory is wrong.

Only create and stage the new Markdown report file.

## 9. Preferred Lightweight Commands

Use compact commands first:

```bash
cd /home/b827262/project/temp/smartbook-platform/ai_tutor_helper
git status -sb
git fetch origin --prune
git fetch upstream
git branch -r | grep 'upstream/codex/fix-ai-notes-navigation'
git log --oneline --decorate --since='2026-06-01' --until='2026-06-22 23:59:59' origin/main..upstream/codex/fix-ai-notes-navigation | head -n 80
git diff --stat origin/main...upstream/codex/fix-ai-notes-navigation
git diff --name-only origin/main...upstream/codex/fix-ai-notes-navigation | sort -u
```

Use targeted file inspection only if needed:

```bash
git diff --name-only origin/main...upstream/codex/fix-ai-notes-navigation | grep -Ei 'note|notes|navigation|smart|book|reader|tutor|scope|router|schema|admin|page|pdf|highlight|image'
```

If a key file must be inspected, inspect only a limited range with `sed -n`, not the full file.

## 10. Expected Focus From Previous Observation

The previous run suggested that `fix-ai-notes-navigation` is likely related to:

- AI notes navigation changes.
- Smart Book / notes related navigation process.
- Reader or note navigation behavior.
- Page, scope, note window, note list, or smart book navigation correction.
- Documentation under `docs/reports`.

Previously observed related document:

```text
docs/reports/ai-notes-navigation-branch-change-summary.md
```

Previously observed approximate change scale:

```text
Total changed files: about 173
Code files: about 134
Documentation files: about 7
```

These numbers are from an earlier broad scan and should be treated as approximate until verified by the Round 3 lightweight commands.

## 11. Output Report To Create In Target Repository

Create this report in the target repo:

```text
docs/reports/fix-ai-notes-navigation-audit-20260622.md
```

The report should be documentation-only.

Suggested report sections:

```markdown
# Fix AI Notes Navigation Branch Audit

## 1. Scope
## 2. Repository Context
## 3. Branch Confirmation
## 4. Lightweight Commands Used
## 5. Commit Summary
## 6. Changed File Summary
## 7. Key Files Reviewed
## 8. Risk Notes
## 9. Recommendation
## 10. Final Status
```

## 12. Commit and Push Steps

After the report is created:

```bash
git status -sb
git add docs/reports/fix-ai-notes-navigation-audit-20260622.md
git commit -m "docs: audit fix ai notes navigation branch"
git push origin HEAD
git status --short
```

## 13. Required Traditional Chinese Termination Report

The final reply must include:

- 狀態：success / failure / blocker / permission-halt
- 建立檔案路徑
- commit SHA if success
- push result
- `git status --short`
- whether source code was changed

## 14. Context Management Rule

Because this is running on `gpt-5.3-codex-spark` with a 128K context window, use `/compact` after this third-round report is committed and pushed.

Suggested flow:

```text
Round 1: question-bank-json-import completed
/compact
Round 2: smart-solve-json-import completed
/compact
Round 3: fix-ai-notes-navigation
/compact
Round 4: final combined summary
```

## 15. After Round 3

After Round 3 succeeds, the next recommended document is a final combined summary:

```text
reports/codex-three-branches-final-summary-20260622.md
```

The combined summary should compare the three branch reports and list:

- total changed file count by branch,
- code file count by branch,
- documentation file count by branch,
- main feature per branch,
- merge risk per branch,
- recommended merge order.
