#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"

bash "$ROOT/scripts/sync-smartbook-md-to-raw.sh"
bash "$ROOT/scripts/md-autopush-hook.sh"

if [ -x "$ROOT/scripts/sync-source-packs-to-gdrive.sh" ]; then
  bash "$ROOT/scripts/sync-source-packs-to-gdrive.sh" || {
    echo "[autopush] warning: Google Drive sync failed; GitHub/local backup may still be OK." >&2
  }
else
  echo "[autopush] Google Drive sync script not found or not executable; skipped." >&2
fi
