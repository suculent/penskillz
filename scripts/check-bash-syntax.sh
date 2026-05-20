#!/usr/bin/env bash
# bash -n every staged shell script under project source (not submodules).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

FILES=()
while IFS= read -r line; do
  [[ -n "$line" ]] && FILES+=("$line")
done < <(git diff --cached --name-only --diff-filter=ACM \
  | grep -E '^(install\.sh$|scripts/.*\.sh$|\.husky/[a-z-]+$)' \
  | grep -Ev '^sources/' || true)

[[ ${#FILES[@]} -eq 0 ]] && { echo "check-bash-syntax: OK (no staged shell files)"; exit 0; }

failed=0
for f in "${FILES[@]}"; do
  if ! bash -n "$f" 2>/tmp/penskillz-bashn.err; then
    echo "check-bash-syntax: FAIL $f"
    cat /tmp/penskillz-bashn.err
    failed=$((failed + 1))
  fi
done

if [[ $failed -gt 0 ]]; then
  echo "check-bash-syntax: $failed file(s) failed"
  exit 1
fi
echo "check-bash-syntax: OK (${#FILES[@]} file(s))"
