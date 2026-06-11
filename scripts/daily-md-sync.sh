#!/usr/bin/env bash
# daily-md-sync.sh
# First-run-of-day guard: copy project MD reports to Project-md-backup RAW_REPORTS.
# Then always calls md-autopush-hook.sh to rebuild packs + push.
set -uo pipefail
export LC_ALL=C

PROJECT="${PROJECT_DIR:-$HOME/project/smartbook-lite-rc1}"
ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
STATE="$ROOT/.daily-md-sync-date"
TODAY="$(date +%Y-%m-%d)"

SQLITE_RC1="$ROOT/docs/project/RAW_REPORTS/SQLITE_RC1"
VPS_LITE="$ROOT/docs/project/RAW_REPORTS/VPS_LITE"
HANDOFF="$ROOT/docs/project/RAW_REPORTS/HANDOFF"

if [ ! -f "$STATE" ] || [ "$(cat "$STATE" 2>/dev/null)" != "$TODAY" ]; then
  mkdir -p "$SQLITE_RC1" "$VPS_LITE" "$HANDOFF"
  cd "$PROJECT"

  # --- SQLITE_RC1 ---
  for f in \
    BETTER_SQLITE3_INSTALL_PROBE.md \
    DB_RUNTIME_AUDIT.md \
    DUAL_MODE_PILOT_REPORT.md \
    DUAL_MODE_RUNTIME_PILOT_REPORT.md \
    LESSON_POINTS_SQLITE_AUDIT.md \
    LESSON_POINTS_SQLITE_PILOT_REPORT.md \
    LOCAL_AUTH_SQLITE_PATCH_REPORT.md \
    LOCAL_AUTH_SQLITE_RUNTIME_AUDIT.md \
    MYSQL_TO_SQLITE_LITE_SCOPE_AUDIT.md \
    MYSQL_TO_SQLITE_SCHEMA_AUDIT.md \
    NODE22_SQLITE_VALIDATION_REPORT.md \
    PHASE_3_PROTECTION_FINAL_REPORT.md \
    RC1_FINAL_VALIDATION_REPORT.md \
    RC1_READINESS_REVIEW_FINAL.md \
    RC1_READINESS_REVIEW.md \
    SMARTBOOK_LEARNING_SQLITE_AUDIT.md \
    SMARTBOOK_LEARNING_SQLITE_PILOT_REPORT.md \
    SMARTBOOK_ROUTER_RC1_FIX_A_REPORT.md \
    SMARTBOOK_ROUTER_SQLITE_AUDIT.md \
    SMARTBOOKROUTER_PATCH_1C_REPORT.md \
    TUTOR_ROUTER_SQLITE_AUDIT.md \
    TUTOR_ROUTER_STRUCTURAL_REVIEW.md; do
    [ -f "$f" ] && cp -u "$f" "$SQLITE_RC1/"
  done
  for pat in \
    "DB_RUNTIME_PATCH_*.md" \
    "SMARTBOOK_ROUTER_PATCH_*.md" \
    "SQLITE_*.md" \
    "TUTOR_ROUTER_PATCH_*.md" \
    "docs/project/sqlite/PHASE_2*.md"; do
    # shellcheck disable=SC2086
    for f in $pat; do [ -f "$f" ] && cp -u "$f" "$SQLITE_RC1/"; done
  done

  # --- VPS_LITE ---
  for f in \
    DEPLOYMENT_BLOCKER_REMEDIATION_REPORT.md \
    POST_REMEDIATION_DEPLOYMENT_REVIEW.md \
    RC1_DEPLOYMENT_BLOCKER_ARBITRATION.md \
    SQLITE_VPS_ENVIRONMENT_VERIFICATION.md \
    VPS_BETTER_SQLITE3_PROBE.md \
    VPS_DEPLOYMENT_RUNBOOK.md \
    VPS_LITE_DEPLOYMENT_HANDOFF.md \
    VPS_LITE_DEPLOYMENT_VALIDATION.md; do
    [ -f "$f" ] && cp -u "$f" "$VPS_LITE/"
  done

  # --- HANDOFF ---
  for f in \
    DEPLOYMENT_MANIFEST.md \
    RC1_DEPLOYMENT_CHECKLIST.md \
    RC1_RELEASE_ARTIFACT_INVENTORY.md \
    RC1_RELEASE_BUNDLE_REPORT.md \
    RC1_RELEASE_BUNDLE_REVIEW.md \
    RC1_RELEASE_CHECKLIST.md \
    RC1_RELEASE_READINESS.md; do
    [ -f "$f" ] && cp -u "$f" "$HANDOFF/"
  done

  # Remove SQLITE_VPS from SQLITE_RC1 if accidentally copied by SQLITE_* glob
  rm -f "$SQLITE_RC1/SQLITE_VPS_ENVIRONMENT_VERIFICATION.md"

  printf '%s\n' "$TODAY" > "$STATE"
  echo "daily-md-sync: [$TODAY] copied smartbook-lite-rc1 MD reports -> $ROOT"
else
  echo "daily-md-sync: already ran today ($TODAY), skipping cp."
fi

# Always rebuild packs + push
bash "$ROOT/scripts/md-autopush-hook.sh"
