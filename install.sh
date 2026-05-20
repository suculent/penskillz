#!/usr/bin/env bash
# penskillz one-line installer.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/<owner>/penskillz/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/<owner>/penskillz/main/install.sh | bash -s -- --agent codex
#   PENSKILLZ_REPO=git@github.com:<owner>/penskillz.git ... | bash
#
# What it does:
#   1. Clones (or updates) the penskillz repo to $PENSKILLZ_HOME (default ~/.penskillz).
#   2. Initializes git submodules (Strix and any other registered sources).
#   3. Runs `penskillz sync && penskillz extract && penskillz install --agent <agent>`.
#   4. Adds $PENSKILLZ_HOME/bin to your PATH via shell rc (idempotent).
#
# Re-running is safe and idempotent: pulls latest, re-extracts, re-installs.

set -euo pipefail

REPO_URL="${PENSKILLZ_REPO:-https://github.com/suculent/penskillz.git}"
HOME_DIR="${PENSKILLZ_HOME:-$HOME/.penskillz}"
AGENT="claude-code"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --home)  HOME_DIR="$2"; shift 2 ;;
    --repo)  REPO_URL="$2"; shift 2 ;;
    *)       echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1" >&2; exit 1; }; }
need git
need python3

if [[ -d "$HOME_DIR/.git" ]]; then
  echo ">> updating $HOME_DIR"
  git -C "$HOME_DIR" pull --ff-only
else
  echo ">> cloning $REPO_URL -> $HOME_DIR"
  git clone "$REPO_URL" "$HOME_DIR"
fi

echo ">> initializing submodules"
git -C "$HOME_DIR" submodule update --init --recursive --depth 1 || true

export PENSKILLZ_HOME="$HOME_DIR"
PENSKILLZ="$HOME_DIR/bin/penskillz"
chmod +x "$PENSKILLZ"

echo ">> sync"
"$PENSKILLZ" sync
echo ">> extract"
"$PENSKILLZ" extract
echo ">> install --agent $AGENT"
"$PENSKILLZ" install --agent "$AGENT"

# PATH hint (only append if not already present in common rc files).
LINE="export PATH=\"\$HOME/.penskillz/bin:\$PATH\""
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
  [[ -f "$rc" ]] || continue
  if ! grep -qsF '/.penskillz/bin' "$rc"; then
    {
      echo ""
      echo "# penskillz"
      echo "$LINE"
    } >> "$rc"
    echo ">> appended PATH entry to $rc"
  fi
done

cat <<EOF

penskillz installed. Two one-liners:

  # Install / refresh (this command):
  curl -fsSL ${REPO_URL%.git}/raw/main/install.sh | bash

  # Update later (assuming PATH is set):
  penskillz update --agent ${AGENT}

Status: \$($PENSKILLZ status | head -1)
EOF
