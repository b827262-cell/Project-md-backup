#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${SMARTBOOK_PROJECT_ROOT:-$HOME/project/smartbook-lite-rc1}"
BACKUP_ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
DEST="$BACKUP_ROOT/docs/project/RAW_REPORTS/SQLITE_RC1"

mkdir -p "$DEST"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "[sync-smartbook-md] project root not found: $PROJECT_ROOT" >&2
  exit 0
fi

echo "[sync-smartbook-md] source: $PROJECT_ROOT"
echo "[sync-smartbook-md] dest:   $DEST"

find "$PROJECT_ROOT" -maxdepth 1 -type f -name "*.md" \
  ! -name "README.md" \
  ! -name "LICENSE.md" \
  -print0 |
while IFS= read -r -d '' f; do
  base="$(basename "$f")"
  cp -p "$f" "$DEST/$base"
  echo "[sync-smartbook-md] copied: $base"
done

echo "[sync-smartbook-md] done"
