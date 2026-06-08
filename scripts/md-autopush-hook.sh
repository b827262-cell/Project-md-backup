#!/usr/bin/env bash
# Idempotent: rebuilds + pushes only when inputs changed.
# Inputs include RAW_REPORTS + manual SOURCE_PACKS.
set -uo pipefail
export LC_ALL=C

ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
DOCS="$ROOT/docs/project"
SCRIPTS="$ROOT/scripts"
STATE="$ROOT/.source-pack-state"

cd "$ROOT" || { echo "FATAL: cannot cd $ROOT" >&2; exit 1; }

LOCK="$ROOT/.source-pack.lock"
exec 9>"$LOCK"
if command -v flock >/dev/null 2>&1; then
  if ! flock -w 60 9; then
    echo "autopush: another run holds the lock, skipping."
    exit 0
  fi
fi

new_hash="$(
  {
    {
      cd "$DOCS" || exit 0
      find RAW_REPORTS HANDOFF AI_COLLAB_CONFIG -type f -name '*.md' -print 2>/dev/null || true
      awk -F'|' '
        /^[[:space:]]*#/ { next }
        NF >= 2 {
          f=$1; mode=$2
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", f)
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", mode)
          if (mode == "manual" && f != "") print "SOURCE_PACKS/" f
        }
      ' "$ROOT/scripts/source-pack-manifest.conf" 2>/dev/null || true
    } | sort -u | while IFS= read -r rel; do
      [ -f "$DOCS/$rel" ] && sha256sum "$DOCS/$rel"
    done

    for path in \
      "$ROOT/scripts/source-pack-manifest.conf" \
      "$ROOT/scripts/build-source-packs.sh" \
      "$ROOT/scripts/source-pack-healthcheck.sh" \
      "$ROOT/scripts/md-autopush-hook.sh"; do
      [ -f "$path" ] && sha256sum "$path"
    done
  } | sha256sum | cut -d' ' -f1
)"

old_hash="$(cat "$STATE" 2>/dev/null || echo none)"
if [ "$new_hash" = "$old_hash" ]; then
  echo "autopush: no input changes, skipping."
  exit 0
fi

bash "$SCRIPTS/build-source-packs.sh"

if ! bash "$SCRIPTS/source-pack-healthcheck.sh"; then
  echo "autopush: healthcheck FAILED — not pushing. See SOURCE_PACK_HEALTHCHECK_REPORT.md" >&2
  exit 1
fi

git add docs/project >/dev/null 2>&1 || true
if git diff --cached --quiet; then
  echo "autopush: nothing to commit."
  echo "$new_hash" > "$STATE"
  exit 0
fi

git commit -m "docs: auto compact and backup project source packs" >/dev/null
if [ "${NO_PUSH:-0}" = "1" ]; then
  echo "$new_hash" > "$STATE"
  echo "autopush: committed; push skipped by NO_PUSH=1."
  exit 0
fi

git push --no-force 2>/dev/null || git push
echo "$new_hash" > "$STATE"
echo "autopush: committed + pushed."
