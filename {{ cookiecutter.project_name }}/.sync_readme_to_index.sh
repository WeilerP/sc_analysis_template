#!/bin/bash
set -euo pipefail
README="README.md"
INDEX="notebooks/index.md"
BASE="$(mktemp)"
trap 'rm -f "$BASE"' EXIT
if git show HEAD:"$README" > "$BASE" 2>/dev/null; then
  git merge-file --diff3 "$INDEX" "$BASE" "$README"
else
  cp "$README" "$INDEX"
fi
