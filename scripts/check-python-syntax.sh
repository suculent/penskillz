#!/usr/bin/env bash
# Syntax-check every staged Python file under project source (not submodules).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

FILES=()
while IFS= read -r line; do
  [[ -n "$line" ]] && FILES+=("$line")
done < <(git diff --cached --name-only --diff-filter=ACM \
  | grep -E '^(bin/penskillz$|lib/.*\.py$|scripts/.*\.py$)' \
  | grep -Ev '^sources/' || true)

[[ ${#FILES[@]} -eq 0 ]] && { echo "check-python-syntax: OK (no staged Python files)"; exit 0; }

failed=0
for f in "${FILES[@]}"; do
  if ! python3 -m py_compile "$f" 2>/tmp/penskillz-pycompile.err; then
    echo "check-python-syntax: FAIL $f"
    cat /tmp/penskillz-pycompile.err
    failed=$((failed + 1))
  fi
done

if [[ $failed -gt 0 ]]; then
  echo "check-python-syntax: $failed file(s) failed"
  exit 1
fi
echo "check-python-syntax: OK (${#FILES[@]} file(s))"
