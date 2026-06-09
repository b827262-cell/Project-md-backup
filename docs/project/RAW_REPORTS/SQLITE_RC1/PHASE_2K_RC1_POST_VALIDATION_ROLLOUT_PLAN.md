# Phase 2K: RC1 Post-validation Rollout Planning

## Status

- `PHASE_2K_DONE = YES`
- `REPORT_CREATED = YES`
- `RC1_VPS_DEPLOYMENT_VALIDATION = PASS`
- `PRODUCTION_DEPLOYMENT_DONE = NO`
- `FORMAL_DB_TOUCHED = NO`

## Source Snapshot

- Branch: `release/vps-lite`
- Local HEAD: `36e02e21cc82661a8ec9ac5635bfd3ec2126ec35`
- Current remote HEAD: `36e02e21cc82661a8ec9ac5635bfd3ec2126ec35`
- Code gate commit SHA: `3927d74b32593968a94aca8b8d668700bcfc49c7`
- Validation report commit SHA: `36e02e21cc82661a8ec9ac5635bfd3ec2126ec35`

## What Has Been Validated

- Clean checkout validation completed from an isolated working directory.
- `pnpm install --frozen-lockfile` passed in the isolated checkout.
- `pnpm build` passed.
- SQLite schema import / push smoke test passed against a disposable DB.
- Required RC1 runtime tables were verified present in the disposable SQLite database.
- Remote HEAD matched the validated commit.
- The validation report was persisted as a markdown report only.
- `FORMAL_DB_TOUCHED = NO`.
- `PRODUCTION_DEPLOYMENT_DONE = NO`.

## What Has Not Been Validated

- Production deployment on the real VPS.
- Startup and runtime behavior on the actual production host after release.
- Production SQLite database creation.
- Production migration execution.
- PM2 start / restart on the real production instance.
- Backup restore from the real production backup.
- End-to-end traffic validation against a live production environment.
- Any changes still present only in the dirty local working tree.
- Separate review of `.env.production.sqlite.example` and `VPS_DEPLOYMENT_RUNBOOK.md` unless they are independently committed.

## Dirty Worktree Warning

The current local repository is not clean. `git status --short` shows modified files and untracked files, including:

- Modified:
  - `.env.production.sqlite.example`
  - `VPS_DEPLOYMENT_RUNBOOK.md`
- Untracked examples:
  - `DEPLOYMENT_BLOCKER_REMEDIATION_REPORT.md`
  - `NODE22_SQLITE_VALIDATION_REPORT.md`
  - `PHASE_3_PROTECTION_FINAL_REPORT.md`
  - `POST_REMEDIATION_DEPLOYMENT_REVIEW.md`
  - `RC1_DEPLOYMENT_BLOCKER_ARBITRATION.md`
  - `RC1_DEPLOYMENT_CHECKLIST.md`
  - `RC1_RELEASE_ARTIFACT_INVENTORY.md`
  - `RC1_RELEASE_BUNDLE_REPORT.md`
  - `RC1_RELEASE_BUNDLE_REVIEW.md`
  - `SQLITE_SCHEMA_COVERAGE_GAP_REPORT.md`
  - `docs/project/sqlite/PHASE_2I_PUSH_RC1_SQLITE_GATE_AND_VPS_PREP.md`
  - `storage/`
  - several stray files such as `Ensure`, `configuration`, `exists.`, `file`, and `install_project_md_autopack.sh`

Deployment must not use this dirty working tree. Formal rollout input must come from a GitHub clean checkout or a verified release artifact only.

## Safe Deployment Source Recommendation

Use one of these sources only:

1. A fresh clean checkout from `origin/release/vps-lite` at `36e02e21cc82661a8ec9ac5635bfd3ec2126ec35`.
2. A release artifact built from that same clean commit, with manifest verification before use.

Do not deploy from the current dirty working tree. Do not mix uncommitted local edits with production rollout input.

## Deployment Manifest Reference

`DEPLOYMENT_MANIFEST.md` exists and should be treated as the release artifact reference.

- Bundle: `smartbook-lite-runtime.tar.gz`
- Bundle size: `6.4M`
- Bundle SHA256: `2ad4bfa1034c473db503af7db3dbb865f9c15a3405d37541c62084031e31fd22`
- Backup: `backup_ai_tutor_20260603.sql`
- Backup size: `5.1M`
- Backup SHA256: `64aa6c8b7aad413fcb71c8ec823d5f83907ff3006da128ec6a9811dec7964d16`
- Tag: `vps-lite-prod-20260601`

This manifest is useful for provenance checks, but it is not a substitute for a clean source checkout.

## Recommended Deployment Method

Recommended method is a release-first rollout:

1. Start from a GitHub clean checkout of `release/vps-lite`, or use a verified release artifact.
2. Confirm the commit matches `36e02e21cc82661a8ec9ac5635bfd3ec2126ec35`.
3. Copy the production SQLite env template into a deployment `.env` file.
4. Create the SQLite data directory on the target host.
5. Run the SQLite schema push for the production database path.
6. Build the app on the target host or verify the release artifact already contains the built runtime.
7. Start via the normal process manager flow only after database and environment verification passes.

## SQLite DB Path Recommendation

Recommended production path:

- `./data/smartbook.db` in app-relative config
- resolved on host as `/opt/smartbook-lite/data/smartbook.db`

Reasoning:

- It keeps the database under the application root.
- It matches the runbook's relative-path model.
- It is easy to back up, restore, and inspect.

## Required Environment Variables

Minimum required variables for SQLite production rollout:

```env
DATABASE_PROVIDER=sqlite
SQLITE_PATH=./data/smartbook.db
NODE_ENV=production
PORT=5000
ENABLE_TRPC_REQUEST_LOGS=false
JWT_SECRET=<generate-a-random-64-char-hex-string>
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=<your-strong-password>
OWNER_OPEN_ID=local:admin
```

Notes:

- `JWT_SECRET` is required for production session token signing.
- `.env.production.sqlite.example` still needs separate review before use unless it has been independently committed.
- `VPS_DEPLOYMENT_RUNBOOK.md` also needs separate review unless it has been independently committed.

## Required Pre-deploy Checklist

- Confirm you are on a clean checkout or verified release artifact.
- Confirm the checked-out commit is `36e02e21cc82661a8ec9ac5635bfd3ec2126ec35`.
- Confirm the worktree is clean on the target deployment source.
- Confirm the target host has Node.js 22+, pnpm, and build prerequisites.
- Confirm `DATABASE_PROVIDER=sqlite` is set in the deployment environment.
- Confirm `SQLITE_PATH` points to the intended production file.
- Confirm the deployment directory exists and is writable.
- Confirm the application build passes on the target source.
- Confirm the process manager configuration is present and reviewed.
- Confirm the production backup is available before any database write.

## Required Backup Checklist

- Verify the production database backup exists before migration or first-run schema push.
- Verify backup integrity against the recorded SHA256.
- Preserve the backup off-host or in a separate recovery location.
- Confirm restore procedure is documented and tested in a non-production context if possible.
- Keep the SQLite database file and WAL / SHM files as part of any recovery snapshot.

## Rollback Strategy

If rollout fails before production cutover:

1. Stop the process manager entry.
2. Revert environment selection back to MySQL mode if needed.
3. Restore the previous deployment source from the clean GitHub checkout or known-good release artifact.
4. Restore the saved production backup if database state was changed.
5. Restart only after the source and database state are revalidated.

If SQLite rollout fails after writes:

- Preserve the SQLite database file for forensic review.
- Do not overwrite the backup until recovery is confirmed.
- Roll back to the previous known-good deployment source and restore the backup.

There is no automatic cross-migration between MySQL and SQLite.

## Do-Not-Touch List

- `server/db.ts`
- router logic
- client code
- schema files
- `package.json`
- formal production database
- formal migration execution
- production service startup
- `git add`
- `git commit`
- `git push`
- any changes in the current dirty working tree that are not separately reviewed

## Next Command Plan For Actual Deployment Validation

Planned command sequence on the target host:

1. Fetch or unpack a clean source from GitHub or the release artifact.
2. Verify the commit SHA.
3. Review `.env.production.sqlite.example` and `VPS_DEPLOYMENT_RUNBOOK.md` separately if they have not been committed.
4. Create `.env` from the production SQLite example and set production values.
5. `pnpm install --frozen-lockfile`
6. `pnpm build`
7. `mkdir -p data`
8. Run the SQLite schema push against the intended production path.
9. Start the service with the configured process manager.
10. Validate the health endpoint and basic homepage response.
11. Check logs for MySQL connection errors, module load failures, and SQLite path errors.

## Final Recommendation

This is a validation pass, not a production deployment. The safe next step is to prepare rollout only from a clean GitHub checkout or verified release artifact, then perform a separate deployment validation on the target host.

Do not use the current dirty working tree for formal rollout.

## Final Status

```text
PHASE_2K_DONE                 = YES
REPORT_CREATED                = YES
REMOTE_HEAD                   = 36e02e21cc82661a8ec9ac5635bfd3ec2126ec35
CODE_GATE_COMMIT              = 3927d74b32593968a94aca8b8d668700bcfc49c7
VALIDATION_REPORT_COMMIT      = 36e02e21cc82661a8ec9ac5635bfd3ec2126ec35
RC1_VPS_DEPLOYMENT_VALIDATION = PASS
PRODUCTION_DEPLOYMENT_DONE    = NO
FORMAL_DB_TOUCHED             = NO
SAFE_TO_PLAN_ROLLOUT          = YES
NEXT_RECOMMENDED_PHASE        = Clean checkout deployment execution after separate review of .env.production.sqlite.example and VPS_DEPLOYMENT_RUNBOOK.md
```
