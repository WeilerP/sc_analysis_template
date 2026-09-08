#!/usr/bin/env bash
set -e

keep_extra_labels=false
for arg in "$@"; do
  case "$arg" in
    --keep-extra-labels) keep_extra_labels=true ;;
    *)
      echo "Usage: $0 [--keep-extra-labels]" >&2
      exit 1
      ;;
  esac
done

source ./.gh_auth.sh

repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)

if [ "$(gh api "repos/$repo" --jq .permissions.push)" != "true" ]; then
  echo "The used token does not include push access to $repo." >&2
  exit 1
fi

labels=(
  "bug|d73a4a|Something is not working"
  "feature|0e8a16|New functionality that does not yet exist"
  "enhancement|a2eeef|Improvement to existing functionality"
  "refactor|008672|Refactor without any behavioral changes."
  "chore|7057ff|Generic maintenance"
  "performance|ae9969|Speed/memory/scalability"
  "debugging|d93f0b|Something is not behaving as expected; root cause not yet known"
  "research|5319e7|Open design/methodology question, no observed anomaly"
  "documentation|0075ca|Improvements or additions to documentation"
  "duplicate|cfd3d7|This issue or pull request already exists"
  "invalid|e4e669|This does not seem right"
  "wontfix|ffffff|This will not be worked on"
)

label_query='.[] | .name + "|" + .color + "|" + (.description // "")'
before=$(gh label list --repo "$repo" --limit 100 --json name,color,description --jq "$label_query")

for entry in "${labels[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  current=$(grep "^${name}|" <<< "$before" || true)
  if [ -z "$current" ]; then
    gh label create "$name" --repo "$repo" --color "$color" --description "$description"
  else
    IFS='|' read -r _ current_color current_description <<< "$current"
    if [ "$current_color" != "$color" ] || [ "$current_description" != "$description" ]; then
      gh label edit "$name" --repo "$repo" --color "$color" --description "$description"
    fi
  fi
done

if [ "$keep_extra_labels" != true ]; then
  known_names=$(printf '%s\n' "${labels[@]}" | cut -d'|' -f1)
  while IFS='|' read -r existing_name _ _; do
    [ -z "$existing_name" ] && continue
    if ! grep -qx "$existing_name" <<< "$known_names"; then
      gh label delete "$existing_name" --repo "$repo" --yes
    fi
  done <<< "$before"
fi

after=$(gh label list --repo "$repo" --limit 100 --json name,color,description --jq "$label_query")

if diff_output=$(diff <(sort <<< "$before") <(sort <<< "$after")); then
  echo "No label changes needed for $repo."
else
  echo "Label changes applied to $repo:"
  echo "$diff_output"
fi
