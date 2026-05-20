# penskillz

**Agent skills for penetration testing.** Web apps, APIs, networks, mobile apps, Windows and Linux hosts — extracted from upstream pentesting frameworks and packaged as drop-in skills for Claude Code, Codex, and Qwen Code.

Today the registry ships [Strix](https://github.com/usestrix/strix) (37 skills covering web vulnerabilities, recon, protocols, frameworks, technologies, and tooling). Adding a new upstream is one YAML stanza.

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/suculent/penskillz/main/install.sh | bash
```

That clones the repo to `~/.penskillz`, pulls all source submodules (Strix, etc.), extracts skills, and installs them into `~/.claude/skills/`. Flags:

```bash
curl -fsSL .../install.sh | bash -s -- --agent codex     # or qwen | all
curl -fsSL .../install.sh | bash -s -- --home /opt/penskillz
```

## Update

```bash
penskillz update
```

Pulls the latest upstream commits for every source, re-extracts, and re-installs. Safe to run repeatedly — managed skills are tagged with a `.penskillz-managed` marker so non-managed skills of the same name are never overwritten.

---

## How it works

```
sources.yaml          ──┐
sources/<name>/       ──┤  (git submodules; one per upstream framework)
lib/extractors/<x>.py ──┘  (read upstream layout, emit canonical SKILL.md)
                  │
                  ▼
dist/skills/<source>/<skill>/SKILL.md   (canonical extracted form, checked-in or rebuilt)
                  │
                  ▼  (install)
~/.claude/skills/<skill>/                  Claude Code
~/.codex/skills/<skill>/                   Codex (override path with CODEX_SKILLS_DIR)
~/.qwen/skills/<skill>/                    Qwen Code (override with QWEN_SKILLS_DIR)
```

Each extracted skill is a Claude-Code-compatible directory:

```
strix-sql-injection/
├── SKILL.md                # frontmatter (name, description, metadata) + body
└── .penskillz-managed      # marker so `penskillz update` can safely refresh it
```

The skill body keeps the upstream content verbatim and appends a `## Source` footer with upstream URL, ref, path, and license. The skill is loadable by any agent that consumes the Anthropic skill convention (frontmatter + markdown body).

---

## CLI

```text
penskillz sync                       Clone/update all source submodules.
penskillz extract [SOURCE...]        Run extractors -> dist/skills/.
penskillz install [--agent NAME]     Copy to agent skill dir. NAME = claude-code|codex|qwen|all
penskillz update [--agent NAME]      sync + extract + install in one shot.
penskillz list                       Sources + extracted skill index.
penskillz status                     Source revs and per-agent install counts.
penskillz add-source NAME URL [opts] Register new upstream in sources.yaml.
penskillz remove-source NAME         Drop a source from sources.yaml.
penskillz doctor                     Diagnose environment.
```

Environment overrides:

| Variable               | Meaning                                                 |
| ---------------------- | ------------------------------------------------------- |
| `PENSKILLZ_HOME`       | Repo root (default `~/.penskillz` after install)        |
| `PENSKILLZ_PREFIX`     | Override install target for the next `install` call    |
| `CLAUDE_SKILLS_DIR`    | Override Claude Code install dir                        |
| `CODEX_SKILLS_DIR`     | Override Codex install dir                              |
| `QWEN_SKILLS_DIR`      | Override Qwen Code install dir                          |

---

## Add a new upstream source

Most pentesting frameworks publish their playbooks as `name: ...` / `description: ...` markdown files. If yours does (Strix does), one command is enough:

```bash
penskillz add-source nuclei-playbooks https://github.com/projectdiscovery/nuclei-templates.git \
  --path docs/playbooks \
  --extractor frontmatter-md \
  --prefix nuclei-
penskillz update
```

If the upstream uses a custom layout, drop a Python module at `lib/extractors/<name>.py` exposing one function:

```python
def extract(*, src, dest, log) -> int:
    """Walk src.skills_root(), emit one <skill_name>/SKILL.md per skill under dest, return count."""
```

`src` exposes `name`, `url`, `ref`, `path`, `prefix`, `exclude`, `license`, plus `skills_root()`. See `lib/extractors/strix.py` for a worked example. Register it with `--extractor <name>` and re-run `penskillz update`.

`sources.yaml` schema (annotated in-file):

```yaml
sources:
  - name: strix                                 # slug — used as submodule dirname + skill prefix base
    url: https://github.com/usestrix/strix.git
    ref: main                                   # branch | tag | commit
    path: strix/skills                          # subpath inside the cloned repo
    extractor: strix                            # module under lib/extractors/
    prefix: "strix-"                            # avoid name collisions across sources
    exclude: [scan_modes, coordination]         # categories/dirs to drop
    license: FSL-1.1-MIT                        # surfaced in extracted SKILL.md footer
```

---

## Two one-liners (the whole point)

| Goal              | Command                                                                              |
| ----------------- | ------------------------------------------------------------------------------------ |
| **Install**       | `curl -fsSL https://raw.githubusercontent.com/suculent/penskillz/main/install.sh \| bash` |
| **Update latest** | `penskillz update`                                                                   |

---

## Usage guidelines

- **Targets**: only run against systems you have written authorization to test. These skills enable real exploitation paths; treat them like the same content in any other red-team handbook.
- **Skill scope**: pick the smallest set you need. Agents perform better when their skill load is focused on the engagement (e.g. web app + the relevant frameworks/protocols) than when given every skill at once. Use `penskillz list` to pick categories.
- **Provenance**: each `SKILL.md` carries a `## Source` footer with upstream URL, ref, path, and license. Keep it intact — downstream consumers rely on it for compliance.
- **Local edits**: don't hand-edit skills in `~/.claude/skills/strix-*`; the next `penskillz update` will overwrite them. If you need a tweaked variant, copy it to a new name without the `.penskillz-managed` marker — the installer will leave it alone.
- **Detection profile**: many skills include OAST callbacks, blind/time-based payloads, and high-noise fuzzing patterns. Honour customer rules of engagement (rate limits, allowed scan windows, OAST domain allowlists).
- **Multi-agent**: install to `--agent all` if you bounce between Claude Code, Codex, and Qwen Code; the layout is identical so the same SKILL.md works in all three.

---

## Status

```
$ penskillz status
Project root : ~/.penskillz
Sources dir  : ~/.penskillz/sources
Dist dir     : ~/.penskillz/dist/skills

  strix          synced=yes ref=main rev=<sha>

  claude-code  dir=~/.claude/skills        installed=37
  codex        dir=~/.codex/skills         installed=0
  qwen         dir=~/.qwen/skills          installed=0
```

---

## Layout

```
penskillz/
├── bin/penskillz           # the CLI
├── install.sh              # one-line installer
├── sources.yaml            # registry of upstream sources
├── lib/extractors/         # per-source extractors (strix.py, frontmatter-md.py, ...)
├── sources/                # git submodules — one per upstream
│   └── strix/              # github.com/usestrix/strix
├── dist/skills/            # extracted canonical skills (built; gitignored)
└── docs/
    ├── USAGE.md            # detailed walkthroughs
    └── CONTRIBUTING.md     # how to add a new upstream + extractor
```

## License

penskillz itself: MIT. Extracted content carries its upstream license — surfaced in each `SKILL.md` footer. Strix content is FSL-1.1-MIT per upstream.
