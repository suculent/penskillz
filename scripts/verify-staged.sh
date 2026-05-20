#!/usr/bin/env bash
# Aggregator. Runs every pre-commit check in sequence; first failure aborts.
# Exposed as `npm run verify` so you can invoke the same checks ad hoc.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

echo "==> check-sources-yaml"
python3 scripts/check-sources-yaml.py

echo "==> check-python-syntax"
bash scripts/check-python-syntax.sh

echo "==> check-bash-syntax"
bash scripts/check-bash-syntax.sh

echo "==> check-secrets"
bash scripts/check-secrets.sh

echo "==> refresh-capabilities"
bash scripts/refresh-capabilities.sh

echo "all checks passed"
