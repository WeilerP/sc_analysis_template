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

source ./.gh_auth.sh

if [ "$create" = true ]; then
  visibility_flag="--private"
  [ "$public" = true ] && visibility_flag="--public"
  gh repo create "{{ cookiecutter.github_namespace }}/{{ cookiecutter.github_repo_name }}" "$visibility_flag"
fi

./.set_gh_remote.sh
sync_args=()
[ "$keep_extra_labels" = true ] && sync_args+=(--keep-extra-labels)
./.sync_gh_labels.sh "${sync_args[@]}"
