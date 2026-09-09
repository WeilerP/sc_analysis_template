#!/usr/bin/env bash
set -e

git init

existing_name="$(git config user.name 2>/dev/null || true)"
existing_email="$(git config user.email 2>/dev/null || true)"

if [ -n "$existing_name" ] && [ -n "$existing_email" ]; then
  echo "Git identity already configured: $existing_name <$existing_email>. Leaving as is."
else
  read -r -p "Configure git identity locally (this repo only) or globally (~/.gitconfig)? [L/g] " scope
  case "$scope" in
    [Gg]*) scope_flag="--global" ;;
    *) scope_flag="--local" ;;
  esac

  default_name="${existing_name:-{{ cookiecutter.author_name }}}"
  default_email="${existing_email:-{{ cookiecutter.author_email }}}"

  read -r -p "git user.name ($default_name): " name
  name="${name:-$default_name}"

  read -r -p "git user.email ($default_email): " email
  email="${email:-$default_email}"

  git config $scope_flag user.name "$name"
  git config $scope_flag user.email "$email"
  echo "Configured $scope_flag git user.name/user.email."
fi

if git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "Repository already has commits. Skipping initial commit."
else
  git add -A
  if git diff --cached --quiet; then
    echo "Nothing to commit."
  else
    if git commit -m "chore: initial commit"; then
      echo "Created initial commit."
    else
      echo "Initial commit failed (e.g., pre-commit hooks modified files)." >&2
      echo "Resolve, then commit manually: git add -A && git commit -m 'chore: initial commit'" >&2
      exit 1
    fi
  fi
fi
