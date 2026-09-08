#!/usr/bin/env bash
set -e

source ./.gh_auth.sh
git remote remove origin 2>/dev/null || true
if [ "$(gh config get git_protocol --host github.com)" = "ssh" ]; then
  git remote add origin "git@github.com:{{ cookiecutter.github_namespace }}/{{ cookiecutter.github_repo_name }}.git"
else
  git remote add origin "https://github.com/{{ cookiecutter.github_namespace }}/{{ cookiecutter.github_repo_name }}.git"
fi
