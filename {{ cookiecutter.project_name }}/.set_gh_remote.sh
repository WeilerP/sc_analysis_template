#!/bin/bash
set -e
if [ -z "$1" ]; then
  echo "Usage: $0 <github_pat>"
  exit 1
fi
git remote remove origin 2>/dev/null || true
git remote add origin "https://{{ cookiecutter.github_username }}:$1@github.com/{{ cookiecutter.github_namespace }}/{{ cookiecutter.github_repo_name }}.git"
