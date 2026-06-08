#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
SRC="$ROOT/docs/project/SOURCE_PACKS"
REMOTE="${GDRIVE_REMOTE:-rclone:}"
DRIVE_FOLDER_ID="${GDRIVE_FOLDER_ID:-1mnPM3QkUBUQuy0T14kgqYqqEp8BUdsBn}"

echo "[gdrive-sync] source: $SRC"
echo "[gdrive-sync] remote: $REMOTE"
echo "[gdrive-sync] folder id: $DRIVE_FOLDER_ID"

test -d "$SRC"

if ! command -v rclone >/dev/null 2>&1; then
  echo "[gdrive-sync] rclone not installed. Please install rclone first." >&2
  exit 2
fi

if ! rclone listremotes | grep -qx "${REMOTE}"; then
  echo "[gdrive-sync] rclone remote not found: $REMOTE" >&2
  echo "[gdrive-sync] Run: rclone config" >&2
  exit 2
fi

rclone sync "$SRC" "$REMOTE" \
  --drive-root-folder-id "$DRIVE_FOLDER_ID" \
  --include "*.md" \
  --exclude "*" \
  --checksum \
  --progress

echo "[gdrive-sync] SOURCE_PACKS synced to Google Drive folder id: $DRIVE_FOLDER_ID"
