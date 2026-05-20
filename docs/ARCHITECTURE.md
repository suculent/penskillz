# Architecture

User-facing overview of how penskillz works end-to-end. For the deeper engineering map (file:line citations, internal data model), see [.planning/codebase/ARCHITECTURE.md](../.planning/codebase/ARCHITECTURE.md).

## Pipeline

```
sources.yaml ──┐
               ▼
        ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
        │   sync      │    │   extract    │    │   install   │
        │ (submodule  │ -> │ (per-source  │ -> │ (copy into  │
        │  update)    │    │  extractor)  │    │ agent dirs) │
        └─────────────┘    └──────┬───────┘    └─────────────┘
                                  │
                                  ▼
                          ┌──────────────────┐
                          │ summarize        │
                          │ (meta-skill +    │
                          │  CAPABILITIES.md)│
                          └──────────────────┘

penskillz update = sync + extract + install + summarize (one shot)
```

## Components

### 1. Source registry — `sources.yaml`

One YAML stanza per upstream framework. Each entry declares:

| Field | Purpose |
| --- | --- |
| `name` | Slug used for submodule path, install marker, and skill prefix base. |
| `url` / `ref` | Where to pull from and which branch / tag / commit to track. |
| `path` | Sub-path inside the cloned repo where source skills live. |
| `extractor` | Which `lib/extractors/<name>.py` module to apply. |
| `prefix` | Prefix prepended to every extracted skill name (collision avoidance). |
| `include` / `exclude` | First-segment directory filters for huge wikis. |
| `options` | Extractor-specific knobs (e.g. `flavour: gtfobins`). |
| `license` | SPDX id; surfaced in each emitted `SKILL.md` footer. |

### 2. Source clones — `sources/<name>/`

Real git submodules. Pinned via `.gitmodules`. `penskillz sync` does a shallow fetch and hard-resets to the configured `ref`. The working tree is read-only from penskillz's perspective.

### 3. Extractors — `lib/extractors/<name>.py`

Each extractor is a Python module exposing one function:

```python
def extract(*, src, dest: pathlib.Path, log) -> int:
    """Walk src.skills_root(), emit <skill_name>/SKILL.md per skill into dest, return count."""
```

Built-in extractors:

- **`strix`** — Strix's own frontmatter format, one skill per `.md`.
- **`frontmatter-md`** — generic wrapper for any source already using YAML frontmatter.
- **`directory-md`** — markdown wikis *without* frontmatter; one skill per `.md`, name derived from the file path, supports `include` / `exclude` first-segment filters. Strips upstream frontmatter, HackTricks include shortcodes, and MkDocs-style `hide: toc` snippets.
- **`yaml-binary`** — per-binary YAML catalogues (GTFOBins, LOLBAS). Set `options.flavour` to `gtfobins` or `lolbas`. Regroups by *technique* (e.g. `shell-escape`, `Execute`) rather than producing one-skill-per-binary.

The CLI looks up the extractor by `src.extractor` and calls it with a `Source` dataclass and an output directory it owns.

### 4. Canonical output — `dist/skills/<source>/<skill>/SKILL.md`

Every extracted skill is a directory with one `SKILL.md` file. The file format is the Anthropic skill convention:

```markdown
---
name: <prefix>-<slug>
description: <one-line>
metadata:
  source: <upstream-name>
  category: <upstream-category>
---

<verbatim upstream body, cleaned of upstream-specific noise>

---

## Source

- Upstream: `<git-url>` (`<ref>`)
- Path: `<path-within-upstream>`
- License: <SPDX>
```

`dist/skills/` is gitignored — it is build output, always reproducible from `sources/` + `lib/extractors/`.

### 5. Index + summary

After every extract, two artifacts are rebuilt automatically:

- **`dist/skills/index.json`** — flat list of every emitted skill (`name`, `description`, `source`, `path`). The summary builder reads this.
- **`dist/skills/_meta/penskillz-capabilities/SKILL.md`** — an installable meta-skill (~18 KB) that lets an agent learn what 1,400+ skills exist without paying for every individual frontmatter. Hierarchical source → category breakdown plus a curated intent → skill lookup table.
- **`CAPABILITIES.md`** — pinned snapshot at the repo root, committed to git so the latest overview is always visible without a rebuild.

### 6. Installer

`penskillz install --agent <name>` copies every directory under `dist/skills/<source>/` and `dist/skills/_meta/` into the agent's skill directory:

| Agent       | Default                      | Env override            |
| ----------- | ---------------------------- | ----------------------- |
| Claude Code | `~/.claude/skills/`          | `CLAUDE_SKILLS_DIR`     |
| Codex       | `~/.codex/skills/`           | `CODEX_SKILLS_DIR`      |
| Qwen Code   | `~/.qwen/skills/`            | `QWEN_SKILLS_DIR`       |

Or pass `--agent all` to install everywhere.

Each installed skill directory is tagged with a `.penskillz-managed` marker file. `penskillz update` will overwrite a managed skill but **never** an unmanaged one — so any skill you hand-authored under the same name survives.

## Why this shape

1. **Upstream is authoritative.** We don't fork content; we extract and footer-link. Refreshing is `git submodule update` + re-extract.
2. **Extractors are small.** A new upstream needs ~30 lines of Python (or zero, if the existing `directory-md` / `frontmatter-md` fit).
3. **The build is reproducible.** `dist/skills/` is derived state. The pinned `CAPABILITIES.md` is the only build output tracked in git.
4. **Agents stay light.** Meta-skill loads once for ~18 KB instead of every full skill description for ~200 KB.
