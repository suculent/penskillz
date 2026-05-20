#!/usr/bin/env bash
# If extractors / summary code / sources.yaml are staged, rebuild CAPABILITIES.md
# and re-stage it. Keeps the pinned snapshot in lock-step with the code that
# generates it. No-op when these files are not in the changeset.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Did anything that affects the summary change?
if ! git diff --cached --name-only --diff-filter=ACMR \
   | grep -Eq '^(lib/extractors/.*\.py$|lib/summary\.py$|sources\.yaml$|bin/penskillz$)'; then
  echo "refresh-capabilities: SKIP (no extractor/summary/source-config changes staged)"
  exit 0
fi

# Refuse to run if dist/skills/index.json is missing — we can't summarise from
# nothing. The developer must run `penskillz extract` first.
if [[ ! -f dist/skills/index.json ]]; then
  echo "refresh-capabilities: FAIL dist/skills/index.json missing"
  echo "  Run: PENSKILLZ_HOME=\$PWD bin/penskillz extract"
  exit 1
fi

PENSKILLZ_HOME="$PWD" bin/penskillz summarize >/dev/null 2>&1 || {
  echo "refresh-capabilities: FAIL penskillz summarize errored"
  exit 1
}

# Stage the regenerated snapshot so the commit picks it up.
if ! git diff --quiet -- CAPABILITIES.md; then
  git add CAPABILITIES.md
  echo "refresh-capabilities: OK CAPABILITIES.md regenerated and re-staged"
else
  echo "refresh-capabilities: OK (already in sync)"
fi
