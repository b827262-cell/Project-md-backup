#!/usr/bin/env bash
set +e

ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
LOG_DIR="$ROOT/logs"
SYNC_SCRIPT="$ROOT/scripts/sync-smartbook-md-and-autopush.sh"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/codex-stop-sync-$TIMESTAMP.log"
LOG_TARGET="/dev/null"

if [ -d "$LOG_DIR" ] || mkdir -p "$LOG_DIR" >/dev/null 2>&1; then
  LOG_TARGET="$LOG_FILE"
fi

exec 3>>"$LOG_TARGET" || exit 0

{
  echo "[codex-stop-wrapper] started: $(date -Iseconds)"
  echo "[codex-stop-wrapper] root: $ROOT"

  if [ -x "$SYNC_SCRIPT" ]; then
    bash "$SYNC_SCRIPT"
    STATUS=$?
  else
    echo "[codex-stop-wrapper] missing sync script: $SYNC_SCRIPT"
    STATUS=127
  fi

  echo "[codex-stop-wrapper] status: $STATUS"
  echo "[codex-stop-wrapper] finished: $(date -Iseconds)"
} >&3 2>&1

exec 3>&-
exit 0
