<!-- refreshed: 2026-05-20 -->
# Architecture

**Analysis Date:** 2026-05-20

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                  Declarative Registry                        │
│   `sources.yaml` (list[Source])  +  `.gitmodules`            │
└──────────────────────────┬──────────────────────────────────┘
                           │  load_sources()  bin/penskillz:203
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLI Orchestrator                          │
│                    `bin/penskillz`                           │
│   sync → extract → install → summarize   (update = all 3)    │
└────┬─────────────┬─────────────────┬──────────────┬─────────┘
     │             │                 │              │
     ▼             ▼                 ▼              ▼
┌─────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│ git_sync│  │ _load_      │  │ install_for_│  │ build_       │
│ shallow │  │ extractor() │  │ agent()     │  │ summary()    │
│ clone   │  │ dynamic     │  │ copytree +  │  │ lib/         │
│ (250)   │  │ import      │  │ marker file │  │ summary.py   │
└────┬────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
     │              │                 │                │
     ▼              ▼                 ▼                ▼
┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ sources/ │  │ dist/skills/ │  │ ~/.claude/   │  │ CAPABILITIES │
│ <name>/  │  │ <src>/<skill>│  │ skills/...   │  │ .md  + meta- │
│ (clones) │  │ /SKILL.md    │  │ + .penskillz │  │ skill in     │
│          │  │ + index.json │  │ -managed     │  │ dist/_meta/  │
└──────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Source dataclass | Per-upstream config (name, url, ref, path, extractor, prefix, include, exclude, options, license) | `bin/penskillz:151-200` |
| `load_sources()` / `save_sources()` | Parse / serialize `sources.yaml` via PyYAML or a built-in fallback parser | `bin/penskillz:203-211` |
| `git_sync()` | Shallow clone or `fetch + reset --hard origin/<ref>` per source | `bin/penskillz:220-235` |
| `_load_extractor()` | Per-source dispatch — `importlib.util.spec_from_file_location` on `lib/extractors/<name>.py` and call its `extract(src, dest, log)` | `bin/penskillz:248-259` |
| `extract_sources()` | Wipe `dist/skills/<src>/`, invoke extractor, then `write_index()` + `build_capabilities_summary()` | `bin/penskillz:262-280` |
| `write_index()` | Build `dist/skills/index.json` by reading frontmatter from every emitted `SKILL.md` (skips `_meta/`) | `bin/penskillz:295-312` |
| `install_for_agent()` | Copy each skill dir under `dist/skills/<src>/<skill>/` to the agent skills dir, drop a `.penskillz-managed` marker file, refuse to overwrite un-marked existing skills | `bin/penskillz:342-365` |
| `build_summary()` | Read `index.json`, group by source/category, emit `dist/skills/_meta/penskillz-capabilities/SKILL.md` and pinned `CAPABILITIES.md` | `lib/summary.py:161-189` |

## Pattern Overview

**Overall:** Pipeline orchestrator with pluggable per-source extractors.

**Key Characteristics:**
- Single-file Python 3.9+ CLI (`bin/penskillz`, ~518 LOC), zero non-stdlib hard deps (PyYAML optional; falls back to a built-in YAML subset parser at `bin/penskillz:56-136`).
- Extractors are dynamically loaded modules, not registered classes — drop a `lib/extractors/<name>.py` exporting `extract(*, src, dest, log) -> int` and reference it from `sources.yaml` under `extractor:` (`bin/penskillz:248-259`).
- Pure functional pipeline: each stage reads from a directory and writes to the next directory. No databases, no servers.
- Idempotent at every layer (sync resets to origin, extract wipes `dist/skills/<src>/`, install rewrites managed targets, install.sh re-runs the whole thing).

## Layers

**Registry (declarative):** `sources.yaml` + `.gitmodules`. Source-of-truth for what to pull and how to extract it. `.gitmodules` is the install-time bootstrap (so `install.sh` can `submodule update --init`); `sources.yaml` is authoritative for the CLI.

**Orchestration:** `bin/penskillz`. Parses CLI args, loads sources, drives sync/extract/install/summarize.

**Extraction:** `lib/extractors/*.py`. Four built-ins:
- `strix.py` — frontmatter+markdown under `strix/skills/<category>/<file>.md`, one skill per file.
- `frontmatter-md.py` — generic frontmatter-md walker (any upstream that authors `name:`/`description:` frontmatter).
- `directory-md.py` — generic markdown wiki walker; derives slug from path, description from first H1/blockquote, applies `include`/`exclude` against first path segment (`lib/extractors/directory-md.py:102-104`).
- `yaml-binary.py` — per-binary YAML catalogues (GTFOBins, LOLBAS) regrouped by *technique category* (one skill per technique, not per binary); flavour selected via `options.flavour` (`lib/extractors/yaml-binary.py:251-260`).

**Summary:** `lib/summary.py`. Pure function over `index.json` — categories pulled from each `SKILL.md`'s `category:` frontmatter line (`lib/summary.py:86-100`).

**Install:** copy `dist/skills/<src>/<skill>/` → `<agent skills dir>/<skill>/`, write a `.penskillz-managed` marker so subsequent runs know which dirs they own (`bin/penskillz:348-362`).

## Data Flow

### Primary Pipeline (`penskillz update`)

1. `load_sources()` parses `sources.yaml` into `Source` objects (`bin/penskillz:203`).
2. For each source, `git_sync()` clones into `sources/<name>/` or hard-resets to `origin/<ref>` (`bin/penskillz:220`).
3. `extract_sources()` wipes `dist/skills/<name>/`, dynamically loads `lib/extractors/<src.extractor>.py`, and invokes its `extract()` (`bin/penskillz:262-275`).
4. Each extractor emits `dist/skills/<src>/<skill>/SKILL.md` with normalized frontmatter (`name`, `description`, `metadata.source`, `metadata.category`).
5. `write_index()` rebuilds `dist/skills/index.json` from every emitted `SKILL.md` (`bin/penskillz:295`).
6. `build_capabilities_summary()` reads `index.json`, writes `dist/skills/_meta/penskillz-capabilities/SKILL.md` and pinned `CAPABILITIES.md` (`bin/penskillz:283-292`).
7. `install_for_agent()` recursively copies every `dist/skills/<src>/<skill>/` (including `_meta/`) into `~/.claude/skills/`, `~/.codex/skills/`, or `~/.qwen/skills/`, dropping a `.penskillz-managed` marker (`bin/penskillz:342`).

### Standalone `summarize`

If `dist/skills/index.json` is missing, `cmd_summarize` rebuilds it cheaply from disk before invoking `build_summary()` (`bin/penskillz:462-467`).

**State Management:** filesystem only. No in-memory cross-command state; each invocation reloads `sources.yaml` and walks directories from scratch.

## Key Abstractions

**`Source` dataclass:**
- Purpose: declarative description of one upstream + how to extract it.
- Defined: `bin/penskillz:151-200`.
- Fields drive everything downstream: `path` → `skills_root()` for the extractor, `prefix` → name namespacing, `include`/`exclude` → directory-md path filter, `options` → extractor knobs (`flavour` for yaml-binary).

**Extractor contract:**
- `extract(*, src: Source, dest: Path, log) -> int` — returns count of skills written.
- Loaded by name via `_load_extractor()` (`bin/penskillz:248`). No registration, no base class.

## Entry Points

**`bin/penskillz`** (CLI) — all subcommands routed via argparse `set_defaults(func=cmd_*)` (`bin/penskillz:486-507`).

**`install.sh`** — bootstrap script: clones the repo to `~/.penskillz`, runs `submodule update --init --depth 1`, then `sync && extract && install --agent <agent>`, then appends `PATH` line to `~/.zshrc` / `~/.bashrc` (`install.sh:44-78`).

## Architectural Constraints

- **Threading:** single-threaded; subprocesses (`git`) run sequentially per source.
- **Global state:** module-level `ROOT`, `SOURCES_DIR`, `DIST_DIR`, `LIB_DIR`, `SOURCES_YAML` constants in `bin/penskillz:38-42`; `sys.path` is mutated to import extractors (`bin/penskillz:44`).
- **Submodules vs. live clones:** `.gitmodules` lists 7 upstreams for bootstrap, but `sources.yaml` (8 entries — same 7 plus driven config) is authoritative for the CLI. Adding via `add-source` writes only `sources.yaml`, not `.gitmodules` (`bin/penskillz:439-450`).
- **PyYAML optional:** stdlib-only YAML fallback at `bin/penskillz:56-136`; the `yaml-binary` extractor hard-requires PyYAML and exits on import failure (`lib/extractors/yaml-binary.py:36-39`).

## Anti-Patterns

### Reading from `sources/<name>/` after a failed sync

**What happens:** `extract_sources` skips a source whose `skills_root()` doesn't exist with a log line; partial syncs (e.g. a missing submodule) silently emit fewer skills (`bin/penskillz:266-268`).
**Why it's wrong:** the user may not notice missing categories until `CAPABILITIES.md` regenerates.
**Do this instead:** run `penskillz status` to confirm every source shows `synced=yes` before extracting (`bin/penskillz:422-436`).

### Hand-editing files under `~/.claude/skills/`

**What happens:** on the next `install`, any directory carrying the `.penskillz-managed` marker is `rmtree`'d and re-copied; edits are lost (`bin/penskillz:359-362`).
**Do this instead:** edit the upstream source or write a new extractor and re-run `penskillz extract && penskillz install`. Non-managed skills are protected — install refuses to overwrite them (`bin/penskillz:356-358`).

## Error Handling

**Strategy:** fail-fast `SystemExit` for unrecoverable misconfiguration (unknown extractor at `bin/penskillz:251`, unknown agent at `bin/penskillz:374`, missing PyYAML at `lib/extractors/yaml-binary.py:39`); `check=False` `git` invocations for resilient sync paths (`bin/penskillz:225,233-235`).

**Patterns:**
- Per-source isolation in extract: only the current source's `dist/skills/<src>/` is wiped, so a broken extractor never deletes peers (`bin/penskillz:270-272`).
- Lazy import of `summary.build_summary` so an extractor crash still allows `penskillz summarize` to run standalone (`bin/penskillz:288-292`).

## Cross-Cutting Concerns

**Logging:** every command receives a `log` callable that writes to stderr (`bin/penskillz:512`). No logging framework.
**Validation:** schema validation is implicit — `Source.from_dict()` `.get()`s with defaults (`bin/penskillz:164-177`).
**Authentication:** none; all upstreams are public git.

---

*Architecture analysis: 2026-05-20*
