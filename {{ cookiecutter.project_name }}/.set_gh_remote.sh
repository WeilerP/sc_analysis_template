#!/usr/bin/env bash
set -e

source ./.gh_auth.sh
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/{{ cookiecutter.github_namespace }}/{{ cookiecutter.github_repo_name }}.git"
