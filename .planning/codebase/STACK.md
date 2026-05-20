# Technology Stack

**Analysis Date:** 2026-05-20

## Languages

**Primary:**
- Python 3 - Core CLI and extractor modules (`bin/penskillz`, `lib/extractors/*.py`, `lib/summary.py`).
- Bash - Bootstrap installer (`install.sh`).

**Secondary:**
- YAML - Source registry (`sources.yaml`) and submodule config consumed by extractors.
- Markdown - Output format for extracted skills under `dist/skills/` and the canonical `SKILL.md` payload.

## Runtime

**Environment:**
- Python 3 (no minimum version pinned; uses `from __future__ import annotations`, `dataclasses`, `pathlib`, `typing` — works on 3.7+; intended target is system `python3`).
- Bash for the installer; `set -euo pipefail` in `install.sh:19`.

**Package Manager:**
- None for the project itself. `install.sh:36` shells out to `python3 -m pip install --user --quiet pyyaml` only when `import yaml` fails.
- Lockfile: none.

## Frameworks

**Core:**
- None. `bin/penskillz` is a single-file CLI built on `argparse` (stdlib).

**Testing:**
- None detected. No `tests/`, `pytest`, or `unittest` configuration exists.

**Build/Dev:**
- None. The CLI is executed directly; `chmod +x bin/penskillz` in `install.sh:57` is the entire "build" step.

## Key Dependencies

**Critical (runtime, third-party):**
- `PyYAML` - **The only true third-party runtime dependency.** Imported by `lib/extractors/yaml-binary.py:37` and required for the GTFOBins and LOLBAS extractors. Other extractors (`strix`, `frontmatter-md`, `directory-md`) use a tiny built-in YAML subset and have **zero** third-party deps.

**Standard library only (no install needed):**
- `argparse`, `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `dataclasses`, `pathlib`, `typing` (see `bin/penskillz:29-37`).

**Infrastructure tools (must be on `PATH`):**
- `git` - submodule sync, ref pinning (`install.sh:33` `need git`).
- `python3` - CLI interpreter (`install.sh:34` `need python3`).

## Configuration

**Source registry:**
- `sources.yaml` - declarative list of upstream frameworks, extractor module, prefix, include/exclude filters, license SPDX id.
- `.gitmodules` - git-level mirror of the seven sources under `sources/`.

**Environment overrides (read by `bin/penskillz`):**
- `PENSKILLZ_HOME` - project root override (`bin/penskillz:39`).
- `PENSKILLZ_PREFIX` - install prefix override.
- `CLAUDE_SKILLS_DIR`, `CODEX_SKILLS_DIR`, `QWEN_SKILLS_DIR` - per-agent install dir overrides (`bin/penskillz:48-50`).
- `PENSKILLZ_REPO`, `PENSKILLZ_HOME` - installer overrides (`install.sh:21-22`).

**Build / lint config:**
- None. No `pyproject.toml`, `setup.py`, `setup.cfg`, `ruff.toml`, `mypy.ini`, `.flake8`, or `.editorconfig` at the repo root.

## Platform Requirements

**Development:**
- POSIX shell (macOS, Linux). Installer rewrites `~/.zshrc` / `~/.bashrc` (`install.sh:73-83`).
- `git` 2.x with submodule support; `--depth 1` shallow fetch is used.
- `python3` on `PATH`; pip available for the lazy PyYAML install.

**Production / install target:**
- Same as development. `install.sh` clones the repo to `$PENSKILLZ_HOME` (default `~/.penskillz`) and copies skills into `~/.claude/skills/`, `~/.codex/skills/`, or `~/.qwen/skills/` depending on `--agent`.

## Why No Requirements File

The project intentionally avoids a `requirements.txt` / `pyproject.toml`:

1. The core CLI and three of four extractors are **stdlib-only**, so `pip install` would be pure ceremony for most users.
2. The single optional dep (`PyYAML`) is installed lazily by `install.sh:36-40` only when `import yaml` fails, with a graceful degradation message: extraction continues, GTFOBins/LOLBAS are skipped.
3. The installer is the one-line entry point; a separate dependency file would duplicate state and risk drift with `install.sh`.
4. The project is distributed as a flat script, not as a Python package — there is nothing for `pip` to consume.

If PyYAML is ever joined by a second real dependency, a `requirements.txt` should be introduced and `install.sh:36` updated accordingly.

---

*Stack analysis: 2026-05-20*
