#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="/home/b827262/project/AI-SmartBook-R1"
DEST_REPO="/home/b827262/Project-md-backup"
DEST_MD_DIR="${DEST_REPO}/md/AI-SmartBook-R1"
LOG_FILE="${DEST_REPO}/logs/ai-smartbook-r1-docs-sync.log"

mkdir -p "${DEST_REPO}/logs"
exec >> "$LOG_FILE" 2>&1

echo "=== Sync Started at $(date) ==="

if [ ! -d "$SRC_DIR/docs" ]; then
    echo "Source docs directory does not exist: $SRC_DIR/docs"
    exit 1
fi

if [ ! -d "$DEST_REPO/.git" ]; then
    echo "Destination is not a git repo: $DEST_REPO"
    exit 1
fi

mkdir -p "$DEST_MD_DIR"

# Rsync docs
rsync -av --delete \
  --include='*/' \
  --include='*.md' \
  --exclude='*' \
  "$SRC_DIR/docs/" \
  "$DEST_MD_DIR/"

# Get source git info
cd "$SRC_DIR"
SRC_BRANCH=$(git branch --show-current)
SRC_COMMIT=$(git rev-parse --short HEAD)
cd "$DEST_REPO"

# Update index
cat > "$DEST_MD_DIR/README_INDEX.md" <<EOF
# AI-SmartBook-R1 Docs Index

Docs-only handoff snapshot for ChatGPT / Claude.

Current phase:

AI-SmartBook-R1 Phase 0.5

Recommended reading order:

1. PHASE_0_5_HANDOFF.md
2. PHASE_0_5_PLAN.md
3. ARCHITECTURE.md
4. MODULE_DESIGN.md
5. ADMIN_AI_MODULES.md
6. STUDENT_1GB_SYSTEMD_DEPLOYMENT.md
7. SMOKE_TEST.md
8. OPUS_ARCHITECTURE_REVIEW_PHASE_0_5.md

---
Sync Information:
- Date: $(date -Iseconds)
- Source Branch: $SRC_BRANCH
- Source Commit: $SRC_COMMIT
EOF

# Git status and commit
git add "md/AI-SmartBook-R1"

if git status --porcelain | grep -q "md/AI-SmartBook-R1"; then
    echo "Changes detected, committing..."
    git commit -m "docs: daily sync AI-SmartBook-R1 docs $(date +%Y-%m-%d)"
    git push origin main
    echo "Push successful. Latest commit: $(git rev-parse HEAD)"
else
    echo "No MD changes detected. Skipping commit."
fi

echo "=== Sync Finished at $(date) ==="
