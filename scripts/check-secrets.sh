#!/usr/bin/env bash
# Scan staged content for high-confidence secret patterns.
#
# Only scans staged blobs of the current commit, not the working tree, so the
# check is fast and accurate on what is about to be persisted.
#
# Restricted to top-level project files — we don't lint upstream submodules.
# If you intentionally want to commit something matching a pattern, prefix
# the value with `EXAMPLE_` or rename the variable to include the substring
# `EXAMPLE` or `PLACEHOLDER`.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Files staged in this commit, excluding paths under sources/ (submodules).
FILES=()
while IFS= read -r line; do
  [[ -n "$line" ]] && FILES+=("$line")
done < <(git diff --cached --name-only --diff-filter=ACM | grep -Ev '^sources/' || true)
[[ ${#FILES[@]} -eq 0 ]] && { echo "check-secrets: OK (no staged top-level files)"; exit 0; }

PATTERNS=(
  # AWS access key id
  'AKIA[0-9A-Z]{16}'
  # AWS secret key (40-char base64)
  'aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}'
  # GitHub PAT (classic + fine-grained)
  'ghp_[A-Za-z0-9]{36,}'
  'github_pat_[A-Za-z0-9_]{82}'
  # Google API key
  'AIza[0-9A-Za-z\-_]{35}'
  # Slack token
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  # Private keys (BEGIN block) — leading dashes stripped so grep doesn't treat the pattern as a flag
  'BEGIN (RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY'
  # JWT (header.payload.signature) — three base64 segments separated by dots
  'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'
)

# Capture the diff once so we can scan it many times cheaply. -U0 keeps only
# the changed lines; we then look at added lines (starting with `+`) and skip
# diff headers and known-benign tokens.
DIFF=$(git diff --cached --diff-filter=ACM -U0 -- "${FILES[@]}" \
       | grep -E '^\+' \
       | grep -Ev '^\+\+\+' \
       | grep -Ev '(EXAMPLE|PLACEHOLDER|FAKE_)' || true)

hits=0
for pat in "${PATTERNS[@]}"; do
  matches=$(printf '%s\n' "$DIFF" | grep -E -- "$pat" || true)
  if [[ -n "$matches" ]]; then
    echo "check-secrets: FAIL pattern matched: $pat"
    printf '%s\n' "$matches" | head -3
    hits=$((hits + 1))
  fi
done

if [[ $hits -gt 0 ]]; then
  echo
  echo "If a match is a false positive, rename the symbol to include EXAMPLE/PLACEHOLDER/FAKE_,"
  echo "or move the file out of the top-level scope."
  exit 1
fi

echo "check-secrets: OK"
