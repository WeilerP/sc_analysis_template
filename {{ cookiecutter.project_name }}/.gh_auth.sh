if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  read -r -s -p "GitHub PAT: " PAT
  echo
  gh auth login --with-token <<< "$PAT"
  unset PAT
fi
gh auth setup-git --hostname github.com
