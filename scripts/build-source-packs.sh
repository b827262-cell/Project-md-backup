#!/usr/bin/env bash
# Deterministic, mechanical SOURCE_PACK builder. NO LLM.
set -euo pipefail
export LC_ALL=C

ROOT="${PROJECT_MD_ROOT:-$HOME/Project-md-backup}"
DOCS="$ROOT/docs/project"
PACKS="$DOCS/SOURCE_PACKS"
RAW="$DOCS/RAW_REPORTS"
MANIFEST="${MANIFEST:-$ROOT/scripts/source-pack-manifest.conf}"
TODAY="$(date +%Y-%m-%d)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

[ -f "$MANIFEST" ] || { echo "FATAL: manifest not found: $MANIFEST" >&2; exit 1; }
mkdir -p "$PACKS" "$RAW"

trim() { local v="$*"; v="${v#"${v%%[![:space:]]*}"}"; v="${v%"${v##*[![:space:]]}"}"; printf '%s' "$v"; }

extract_truth() {
  awk '
    /^##[[:space:]]+(Current Truth|TL;DR)[[:space:]]*$/ { grab=1; next }
    grab && /^##[[:space:]]/ { grab=0 }
    grab { print }
  ' "$1"
}

extract_next_actions() {
  awk '
    /^##[[:space:]]+Next Actions[[:space:]]*$/ { grab=1; next }
    grab && /^##[[:space:]]/ { grab=0 }
    grab { print }
  ' "$1"
}

list_sources() {
  local globs="$1"
  IFS=',' read -ra arr <<< "$globs"
  (
    shopt -s globstar nullglob
    cd "$DOCS" 2>/dev/null || exit 0
    local g m
    for g in "${arr[@]}"; do
      g="$(trim "$g")"
      [ -z "$g" ] && continue
      for m in $g; do [ -f "$m" ] && echo "$m"; done
    done
  ) | sort -u | sort -r
}

build_auto_pack() {
  local file="$1" purpose="$2" readwhen="$3" globs="$4"
  local out="$STAGE/$file"
  local title="${file%.md}"
  {
    echo "# $title"
    echo
    echo "Last Updated: $TODAY"
    echo "Source Pack Version: auto-generated (mechanical, no-LLM)"
    echo "Purpose: $purpose"
    echo "Read This When: $readwhen"
    echo
    echo "> Auto-bundled from RAW_REPORTS. Full detail lives in GitHub; this pack"
    echo "> holds only each report's \`## Current Truth\` section + an index."
    echo
    echo "## Current Truth"
    echo
  } > "$out"

  local files; files="$(list_sources "$globs")"
  if [ -z "$files" ]; then
    echo "_No raw reports matched yet._" >> "$out"
  else
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      local truth; truth="$(extract_truth "$DOCS/$f")"
      if [ -n "$truth" ]; then
        echo "### $(basename "$f")" >> "$out"
        echo >> "$out"
        printf '%s\n\n' "$truth" >> "$out"
      fi
    done <<< "$files"
  fi

  {
    echo "## Related Raw Reports"
    echo
    if [ -z "$files" ]; then
      echo "_None._"
    else
      while IFS= read -r f; do
        [ -z "$f" ] && continue
        echo "- \`docs/project/$f\`"
      done <<< "$files"
    fi
    echo
    echo "## Next Actions"
    echo
    local newest; newest="$(printf '%s\n' "$files" | head -n1)"
    if [ -n "${newest:-}" ] && [ -f "$DOCS/$newest" ]; then
      extract_next_actions "$DOCS/$newest" || true
    fi
  } >> "$out"
}

build_archive_index() {
  local out="$STAGE/14_ARCHIVE_INDEX.md"
  {
    echo "# 14_ARCHIVE_INDEX"
    echo
    echo "Last Updated: $TODAY"
    echo "Purpose: Full index of every raw report (overflow map for the 25-source limit)"
    echo "Read This When: finding archived detail not inlined in any pack"
    echo
    echo "## Current Truth"
    echo
    echo "Total raw reports indexed below. None are uploaded to ChatGPT directly;"
    echo "open them in GitHub when a pack points here."
    echo
    if [ -d "$DOCS/RAW_REPORTS" ]; then
      ( cd "$DOCS" && find RAW_REPORTS -type f -name '*.md' -print 2>/dev/null ) \
        | sort -r | while IFS= read -r f; do echo "- \`docs/project/$f\`"; done
    fi
  } > "$out"
}

while IFS='|' read -r f mode purpose readwhen globs; do
  f="$(trim "$f")"; mode="$(trim "$mode")"
  [ -z "$f" ] && continue
  case "$f" in \#*) continue;; esac
  purpose="$(trim "$purpose")"; readwhen="$(trim "$readwhen")"
  globs="$(trim "${globs:-}")"

  if [ "$f" = "14_ARCHIVE_INDEX.md" ]; then
    build_archive_index
  elif [ "$mode" = "auto" ]; then
    build_auto_pack "$f" "$purpose" "$readwhen" "$globs"
  else
    if [ -f "$PACKS/$f" ]; then
      cp "$PACKS/$f" "$STAGE/$f"
    else
      printf '# %s\n\nLast Updated: %s\nPurpose: %s\n\n_(manual pack — author this by hand)_\n' \
        "${f%.md}" "$TODAY" "$purpose" > "$STAGE/$f"
    fi
  fi
done < "$MANIFEST"

EXPECTED_LIST="$STAGE/.expected-packs"
: > "$EXPECTED_LIST"

for built in "$STAGE"/*.md; do
  [ -e "$built" ] || continue
  base="$(basename "$built")"
  printf '%s\n' "$base" >> "$EXPECTED_LIST"
  if [ ! -f "$PACKS/$base" ] || ! cmp -s "$built" "$PACKS/$base"; then
    mv "$built" "$PACKS/$base"
  fi
done

shopt -s nullglob
for existing in "$PACKS"/*.md; do
  base="$(basename "$existing")"
  [ "$base" = "SOURCE_PACK_HEALTHCHECK_REPORT.md" ] && continue
  grep -Fxq "$base" "$EXPECTED_LIST" || rm -f "$existing"
done

echo "build-source-packs: OK -> $PACKS"
