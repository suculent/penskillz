# Coding Conventions

**Analysis Date:** 2026-05-20

These conventions are extracted from `bin/penskillz`, `lib/summary.py`, and the four extractors under `lib/extractors/`. They are descriptive of what the code actually does — match the existing style when contributing.

## Language Baseline

- Python 3.9+ (`bin/penskillz` `cmd_doctor` enforces this); `from __future__ import annotations` is used at the top of every project module so PEP 604 union syntax (`list[Source]`, `dict | None`, `Path | None`) parses on 3.9 even though it is a 3.10 feature at runtime.
- Type hints are present on every public function signature (`extract(*, src, dest: Path, log) -> int`, `load_sources() -> list[Source]`, `_run(cmd: list[str], cwd: Path | None = None, ...)`). Internal `dict` / `list` annotations for locals are also common (`grouped: dict[str, list[tuple]] = {}` in `lib/extractors/yaml-binary.py`).
- Standard library only, with PyYAML as the **only** third-party dependency. PyYAML is imported lazily/optionally everywhere except `lib/extractors/yaml-binary.py`, which `raise SystemExit` if PyYAML is missing. New code should keep the no-deps posture.

## Dataclasses for Config

The `Source` config object in `bin/penskillz` is a `@dataclass` with `field(default_factory=list)` / `field(default_factory=dict)` for collections, paired with explicit `from_dict` / `to_dict` classmethods that normalize `None` to empty collections and drop empty fields from the YAML round-trip. New config objects should follow this pattern (dataclass + explicit dict round-trip), not bare dicts.

## Docstring Style

- Every module begins with a multi-line `"""..."""` describing purpose, inputs, and output shape. See `lib/extractors/yaml-binary.py` lines 1–29 for the most complete example (per-flavour input shape + skills emitted).
- Function docstrings are reserved for non-obvious behavior (`_yaml_load`, `build_summary`, `build_capabilities_summary`). Trivial helpers stay undocumented; the surrounding section comment (`# ---- extraction ----`) carries the context.
- `bin/penskillz`'s module docstring doubles as the `argparse` description (`description=__doc__`, `formatter_class=argparse.RawDescriptionHelpFormatter`). Keep the `Usage:` block synchronized with `build_parser`.

## Section Comments

Files are organized with `# ---- <section> ----------------------` banner comments (see `bin/penskillz`: `minimal YAML loader`, `data model`, `git operations`, `extraction`, `agent install`, `command handlers`, `argparse`). Use the same banner style when adding a new logical section.

## Slug & Regex Helpers

Every extractor declares its regex constants as module-level `_PRIVATE` `re.compile` objects (`_SLUG_BAD`, `_FM`, `_H1`, `_BLOCKQUOTE`, `_MULTI_HYPHEN`, `_LEADING_FM`, `_HT_INCLUDE`, `_MASTG_HIDE`) and re-implements `_slug(s: str) -> str` locally. The canonical slug rule (used in `strix.py`, `frontmatter-md.py`, `directory-md.py`, `yaml-binary.py`) is: `.strip().lower()`, underscores → hyphens, spaces → hyphens, anything outside `[a-z0-9-]+` collapses to `-`, then `.strip("-")`. `directory-md.py` also collapses `-+` via `_MULTI_HYPHEN`. New extractors should copy this helper verbatim rather than depend on a shared utility — the codebase deliberately keeps extractors self-contained.

## Frontmatter Handling

The YAML frontmatter parser is duplicated (intentionally) across `strix.py`, `frontmatter-md.py`, `directory-md.py`, and `bin/penskillz::_read_frontmatter`. All four use the same `_FM = re.compile(r"^---\s*\n(?P<fm>.*?)\n---\s*\n", re.DOTALL)` and a line-by-line `partition(":")` parse that strips surrounding `"` and `'`. This is not full YAML — it handles only flat scalar maps, which is all SKILL.md frontmatter ever contains. Do not switch to PyYAML here; the parser must work without the optional dep.

## Extractor Contract

Documented in `docs/CONTRIBUTING.md` lines 13–24 and enforced by `bin/penskillz::_load_extractor` (checks `hasattr(mod, "extract")`):

```python
def extract(*, src, dest: pathlib.Path, log) -> int
```

- Keyword-only arguments (`*,`) — positional calls are not supported.
- `src` is a `Source` dataclass; rely on `src.skills_root()`, `src.prefix`, `src.exclude`, `src.include`, `src.license`, `src.options`, `src.url`, `src.ref`, `src.path`, `src.name`.
- `dest` is a fresh empty directory the extractor owns; `extract_sources` `rmtree`s it before calling.
- `log` is a `callable(str)` (it's `print(..., file=sys.stderr)` in practice). Use `log(f"[<extractor-name>] ...")` for warnings.
- Return the integer count of skills written.

## SKILL.md Output Format

Every extractor emits identically shaped files at `dest/<skill-name>/SKILL.md`:

```
---
name: <prefix><slug>
description: <single-line, ≤280 chars>
metadata:
  source: <src.name>
  category: <category>
---

<body>

---

## Source

- Upstream: `<src.url>` (`<src.ref>`)
- Path: `<src.path>/<rel>`
- Category: `<category>`
- License: <src.license>     # only when set
```

Rules observed across all four extractors:
- `description` must be a single line. `directory-md.py::_description` collapses whitespace and hard-truncates to 280 chars with `...`.
- `metadata.source` is always `src.name`; `metadata.category` is the first path segment (`directory-md`, `frontmatter-md`) or the technique/category key (`strix`, `yaml-binary`).
- The trailing `## Source` footer is mandatory — `docs/CONTRIBUTING.md` explicitly calls this out and `strix.py` is the canonical layout.
- License lines are omitted (not blank) when `src.license` is empty.

## Naming

- Files: lowercase with hyphens for extractors (`directory-md.py`, `frontmatter-md.py`, `yaml-binary.py`), lowercase no hyphens for libs (`summary.py`).
- Functions: `snake_case`; private helpers prefixed `_` (`_slug`, `_yaml_load`, `_emit_gtfobins`, `_walk_lolbas`, `_read_frontmatter`).
- Regex constants: `_UPPER_SNAKE` (`_FM`, `_SLUG_BAD`, `_H1`).
- Skill names (output slugs): `<source-prefix>-<topic>`, lowercase, hyphens only.

## Error Handling

- User-facing failures raise `SystemExit("...")` with a one-line message — never `sys.exit(code)` and never tracebacks for expected conditions. Examples: unknown extractor (`bin/penskillz` line 251), missing PyYAML (`yaml-binary.py` line 39), unknown flavour (`yaml-binary.py` line 258), unknown agent (`bin/penskillz` line 375).
- Subprocess invocations go through `_run` which wraps `subprocess.run(..., check=True, text=True, capture_output=True)`. Pass `check=False` explicitly for best-effort steps (the second-attempt `git checkout` in `git_sync`).
- File reads always pass `encoding="utf-8", errors="replace"` (every extractor does this). Match that — upstream content is sometimes mojibake.

## Logging

There is no logging framework. `log` is `print(msg, file=sys.stderr)` defined in `main()`. Messages are prefixed with the subsystem in brackets: `[sync]`, `[extract]`, `[install]`, `[summary]`, `[<extractor-name>]`. New code should match this prefix convention.

## Imports

Order observed in every file: future imports → stdlib → optional third-party (guarded `try: import yaml`). No internal cross-imports between extractors. `bin/penskillz` injects `LIB_DIR` onto `sys.path` so `from summary import build_summary` works without packaging.

---

*Convention analysis: 2026-05-20*
