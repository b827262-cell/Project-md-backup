#!/usr/bin/env bash
# Validates SOURCE_PACKS before push. Secret scan covers docs/project, not only packs.
set -uo pipefail
export LC_ALL=C

ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
DOCS="$ROOT/docs/project"
PACKS="$DOCS/SOURCE_PACKS"
REPORT="$PACKS/SOURCE_PACK_HEALTHCHECK_REPORT.md"
LIMIT="${SOURCE_PACK_LIMIT:-25}"
FAIL=0

mkdir -p "$PACKS"
shopt -s nullglob
files=("$PACKS"/*.md)
count=0
for f in "${files[@]}"; do
  [ "$(basename "$f")" = "$(basename "$REPORT")" ] && continue
  count=$((count+1))
done

problems=()
[ "$count" -le "$LIMIT" ] || { problems+=("pack count $count exceeds limit $LIMIT"); FAIL=1; }

for f in "${files[@]}"; do
  [ "$(basename "$f")" = "$(basename "$REPORT")" ] && continue
  [ -s "$f" ] || { problems+=("empty file: $(basename "$f")"); FAIL=1; }
  grep -q "^Last Updated:" "$f" || { problems+=("missing Last Updated: $(basename "$f")"); FAIL=1; }
done

# Strict key-shape scan. Do not grep educational words like token/.env/API key.
SECRET_RE='sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.|xox[baprs]-[A-Za-z0-9-]{10,}'
secret_hits="$(grep -REn "$SECRET_RE" "$DOCS" 2>/dev/null | grep -v "$(basename "$REPORT")" || true)"
[ -z "$secret_hits" ] || { problems+=("possible secret detected"); FAIL=1; }

{
  echo "# SOURCE_PACK_HEALTHCHECK_REPORT"
  echo
  echo "Last Updated: $(date +%Y-%m-%d\ %H:%M:%S)"
  echo
  echo "HEALTHCHECK_PASS = $( [ "$FAIL" -eq 0 ] && echo YES || echo NO )"
  echo "SOURCE_PACK_COUNT = $count"
  echo "UNDER_${LIMIT}_LIMIT = $( [ "$count" -le "$LIMIT" ] && echo YES || echo NO )"
  echo "SECRET_GUARD = $( [ -z "$secret_hits" ] && echo PASS || echo FAIL )"
  echo
  echo "## Problems"
  echo
  if [ "${#problems[@]}" -gt 0 ]; then
    for p in "${problems[@]}"; do echo "- $p"; done
  else
    echo "_None._"
  fi
  if [ -n "$secret_hits" ]; then
    echo
    echo "## Secret hits (filenames only)"
    echo
    echo "$secret_hits" | sed 's/:.*$//' | sort -u | while read -r l; do echo "- $l"; done
  fi
} > "$REPORT"

if [ "$FAIL" -eq 0 ]; then
  echo "healthcheck: PASS ($count packs)"
else
  echo "healthcheck: FAIL" >&2
fi
exit "$FAIL"
