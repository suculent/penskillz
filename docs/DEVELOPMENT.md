# Development

How to work on penskillz itself — local loop, adding upstreams, writing extractors, commit conventions.

## Local loop

```bash
PENSKILLZ_HOME=$PWD bin/penskillz sync                          # refresh all submodules
PENSKILLZ_HOME=$PWD bin/penskillz extract                       # re-run extractors → dist/skills/
PENSKILLZ_HOME=$PWD bin/penskillz extract <source>              # one source only
PENSKILLZ_HOME=$PWD PENSKILLZ_PREFIX=$PWD/_test bin/penskillz install   # dry-run install
PENSKILLZ_HOME=$PWD bin/penskillz summarize                     # rebuild CAPABILITIES + meta-skill
```

`bin/penskillz status` shows source revisions and per-agent install counts. `bin/penskillz doctor` runs an environment sanity check.

`PENSKILLZ_HOME=$PWD` is only needed when running an in-place dev copy. After `install.sh` puts the CLI on PATH at `~/.penskillz/bin/penskillz`, that env var is no longer required.

## Adding an upstream source

For sources already authored as YAML-frontmatter + markdown (the common case):

```bash
penskillz add-source nuclei-playbooks https://github.com/projectdiscovery/nuclei-templates.git \
  --path docs/playbooks \
  --extractor frontmatter-md \
  --prefix nuclei-
git submodule add --depth 1 https://github.com/projectdiscovery/nuclei-templates.git sources/nuclei-playbooks
penskillz update
```

For markdown wikis without frontmatter, use `--extractor directory-md` and add `include:` / `exclude:` lines in `sources.yaml` to narrow the surface.

For per-binary YAML catalogues, use `--extractor yaml-binary` and set `options.flavour` (see [CONFIGURATION.md](CONFIGURATION.md#extractor-knobs)).

## Writing a custom extractor

Drop a Python module at `lib/extractors/<name>.py` exposing one function:

```python
from pathlib import Path

def extract(*, src, dest: Path, log) -> int:
    """
    src   — Source dataclass: name, url, ref, path, prefix, exclude, include,
            options, license, plus checkout_dir() and skills_root().
    dest  — empty directory the extractor owns. Write one subdirectory per skill,
            each containing SKILL.md.
    log   — callable(str). Write progress/warnings here.
    Return the number of skills written.
    """
```

The contract: emit one directory per skill under `dest`, each containing a `SKILL.md` with Anthropic-style frontmatter (`name:` and `description:` at minimum). The orchestrator handles indexing, summary, and install. See `lib/extractors/strix.py` for the cleanest reference.

Skill name discipline:

- Always apply `src.prefix`.
- Slugify: lowercase, hyphens only, no whitespace, no underscores.
- Don't collide across sources — `prefix:` exists exactly for this.

`SKILL.md` body shape:

```markdown
---
name: <slug>
description: <one-line, ≤280 chars>
metadata:
  source: <upstream>
  category: <upstream-category>
---

<upstream body>

---

## Source

- Upstream: `<url>` (`<ref>`)
- Path: `<path>`
- License: <SPDX>
```

Always emit the `## Source` footer — downstream consumers and compliance reviews depend on it.

## Coding conventions

Observed across `bin/penskillz` and `lib/extractors/*.py` — match these in new code:

- `from __future__ import annotations` + modern union syntax (`str | None`).
- Module-level docstring on every file.
- `@dataclass` for config-shaped types; private regex constants at module top.
- Stdlib only, with PyYAML the single accepted soft-runtime dep (only for `yaml-binary`).
- Log via the `log` callable passed in by the orchestrator — don't `print` from extractors.
- Short, lookup-style functions; no class hierarchies.
- No comments restating the code. Only call out the non-obvious *why*.

## Tests

There are no tests yet. See [TESTING.md](TESTING.md) for what would belong if you add them — extractor round-trip, slug determinism, install-marker safety, YAML loader fallback, summary regeneration.

The pragmatic smoke test is the local loop above plus a diff of `dist/skills/` between runs.

## Commit methodology

Pre-commit hooks (husky-managed) enforce the following on every commit:

- `sources.yaml` parses cleanly and every `name` matches a submodule entry in `.gitmodules`.
- `bin/penskillz` and `lib/**/*.py` pass syntax check (`python3 -m py_compile`).
- Shell scripts pass `bash -n` syntax check.
- A staged grep for known secret patterns (AWS keys, GitHub tokens, private keys).
- If `lib/extractors/`, `lib/summary.py`, or `sources.yaml` changed: `CAPABILITIES.md` is regenerated and re-staged so the pinned snapshot never drifts.

Commit messages follow conventional-commit style — `<type>(<scope>): <subject>` — checked by the `commit-msg` hook. Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`. Scopes: `cli`, `extract`, `summary`, `docs`, `infra`.

See [`.husky/`](../.husky/) for the actual hook scripts.

## Pushing

`origin` is dual-push (corpus + GitHub). `git push origin main` updates both. The GitHub mirror exists so off-corpus hosts can install without VPN.

If you only want to push to one:

```bash
git push github main                                      # GitHub mirror only
git push ssh://git@git.corpus.intra:7999/cs-offensivesecurity/penskillz.git main  # corpus only
```

## Updating the codebase map

The `.planning/codebase/` documents are produced by `gsd-map-codebase`. Re-run that command after significant structural changes (new extractor module, new source category, new pipeline stage). The map is *snapshot* documentation — keep it accurate but don't expect every PR to refresh it.
