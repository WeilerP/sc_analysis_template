#!/usr/bin/env bash
set -e

create=false
public=false
keep_extra_labels=false
for arg in "$@"; do
  case "$arg" in
    --create) create=true ;;
    --public) public=true ;;
    --keep-extra-labels) keep_extra_labels=true ;;
    *)
      echo "Usage: $0 [--create] [--public] [--keep-extra-labels]" >&2
      exit 1
      ;;
  esac
done

repo_slug="{{ cookiecutter.github_namespace }}/{{ cookiecutter.github_repo_name }}"

# > GitHub provisions a new repo's default labels asynchronously, so `gh repo create` can return
# > before all of them exist. Syncing labels inside that window makes `gh label create` collide
# > with a default that appears mid-run, so wait for the label count to stop changing first.
wait_for_default_labels() {
  local previous_count=-1
  local current_count
  local attempt

  for attempt in $(seq 1 30); do
    sleep 1
    current_count=$(gh label list --repo "$repo_slug" --limit 100 --json name --jq 'length' || echo 0)
    # > A freshly created repo can briefly return nothing here, which would break the comparison.
    current_count=${current_count:-0}
    if [ "$current_count" -gt 0 ] && [ "$current_count" = "$previous_count" ]; then
      return 0
    fi
    previous_count="$current_count"
  done

  # > Timing out on a count of 0 is harmless: with no labels there is nothing to collide with.
  echo "Default labels on $repo_slug did not settle; continuing." >&2
}

source ./.gh_auth.sh

if [ "$create" = true ]; then
  visibility_flag="--private"
  [ "$public" = true ] && visibility_flag="--public"
  gh repo create "$repo_slug" "$visibility_flag"
  wait_for_default_labels
fi

./.set_gh_remote.sh
sync_args=()
[ "$keep_extra_labels" = true ] && sync_args+=(--keep-extra-labels)
./.sync_gh_labels.sh "${sync_args[@]}"
