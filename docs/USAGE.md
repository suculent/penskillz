# penskillz — Usage

Detailed walkthroughs. For the 30-second overview, see the top-level [README](../README.md).

## 1. First-time install

```bash
curl -fsSL https://raw.githubusercontent.com/suculent/penskillz/main/install.sh | bash
```

What that does, step by step:

1. Clones the penskillz repo to `~/.penskillz` (or `$PENSKILLZ_HOME`).
2. `git submodule update --init --recursive --depth 1` — pulls Strix and any other registered upstream into `sources/<name>/`.
3. `penskillz sync` — fetches latest commits on the pinned ref of each source.
4. `penskillz extract` — runs the configured extractor for each source, writing canonical Claude-Code skills into `dist/skills/<source>/<skill>/SKILL.md`. Also builds `dist/skills/index.json`.
5. `penskillz install --agent claude-code` — copies each `dist/skills/<source>/<skill>/` into `~/.claude/skills/<skill>/`, tagging it with `.penskillz-managed`.
6. Appends `export PATH="$HOME/.penskillz/bin:$PATH"` to `~/.zshrc` and `~/.bashrc` if not present.

Pick a different agent (or all of them) at install:

```bash
curl -fsSL .../install.sh | bash -s -- --agent all
curl -fsSL .../install.sh | bash -s -- --agent codex
```

## 2. Keep up with upstream

```bash
penskillz update            # claude-code by default
penskillz update --agent all
```

This is the second one-liner. Re-running is always safe — the `.penskillz-managed` marker scopes overwrites to skills penskillz placed.

## 3. Inspect

```bash
penskillz list              # sources + flat list of every extracted skill
penskillz status            # source revs, install dirs, install counts per agent
penskillz doctor            # environment sanity check
```

The flat index is also written as JSON:

```bash
jq '.[] | select(.source=="strix") | .name' ~/.penskillz/dist/skills/index.json
```

## 4. Pick which skills to install

The default installer copies *every* extracted skill. If you want a narrower set (e.g. only web-app skills for a specific engagement):

- Edit `sources.yaml` and use `exclude:` to drop entire categories (`scan_modes`, `coordination` are excluded for Strix by default).
- Or, after `penskillz extract`, manually `rm -rf dist/skills/strix/strix-firebase-*` before `penskillz install`. The marker system means a later `penskillz update` will re-add them unless you keep the exclusion in `sources.yaml`.

For category-level pinning add a new source entry pointed at a subpath:

```yaml
- name: strix-web
  url: https://github.com/usestrix/strix.git
  ref: main
  path: strix/skills/vulnerabilities
  extractor: frontmatter-md
  prefix: "strix-web-"
```

## 5. Add a new upstream source

### 5a. The source already uses YAML frontmatter + markdown body

This is the common case (matches Strix, matches many community playbook repos).

```bash
penskillz add-source nuclei-playbooks https://github.com/projectdiscovery/nuclei-templates.git \
  --path docs/playbooks \
  --extractor frontmatter-md \
  --prefix nuclei-
git -C ~/.penskillz submodule add --depth 1 \
  https://github.com/projectdiscovery/nuclei-templates.git sources/nuclei-playbooks
penskillz update
```

### 5b. The source needs a custom extractor

Write `lib/extractors/<name>.py`:

```python
from pathlib import Path

def extract(*, src, dest: Path, log) -> int:
    root = Path(src.skills_root())
    count = 0
    for upstream_file in root.rglob("*.yaml"):
        # ... parse upstream layout, derive skill_name, body, description ...
        skill_dir = dest / f"{src.prefix}{skill_name}"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {src.prefix}{skill_name}\ndescription: {desc}\n---\n\n{body}"
        )
        count += 1
    return count
```

The contract: emit one directory per skill under `dest`, each containing a `SKILL.md` with Anthropic-style frontmatter (`name:` and `description:` at minimum). penskillz handles the rest (index, install, update).

Then register it:

```bash
penskillz add-source <name> <url> --path <subpath> --extractor <name> --prefix <name>-
```

## 6. Per-agent install paths

| Agent         | Default                      | Override env var       |
| ------------- | ---------------------------- | ---------------------- |
| Claude Code   | `~/.claude/skills/`          | `CLAUDE_SKILLS_DIR`    |
| Codex         | `~/.codex/skills/`           | `CODEX_SKILLS_DIR`     |
| Qwen Code     | `~/.qwen/skills/`            | `QWEN_SKILLS_DIR`      |

A one-off install to an arbitrary directory:

```bash
PENSKILLZ_PREFIX=/path/to/somewhere penskillz install
```

If an agent reads skills from a project-local `.claude/skills/` directory instead of the user-global one, point the env var at it before running `penskillz install`.

## 7. Removing penskillz

```bash
# Drop installed skills (one per agent dir)
for d in ~/.claude/skills ~/.codex/skills ~/.qwen/skills; do
  [ -d "$d" ] && find "$d" -maxdepth 2 -name .penskillz-managed -execdir sh -c 'cd .. && rm -rf "$PWD"' \;
done

# Remove the project itself
rm -rf ~/.penskillz
```

The `.penskillz-managed` marker is what makes uninstall safe even if you sprinkled your own skills into the same directories.

## 8. Authorization & safe operation

These skills enable real exploitation: SQLi, RCE, SSRF, deserialization, JWT forgery, etc. Treat them like any other offensive content.

- Only run against systems you have written authorization to test.
- Honour engagement scope, time windows, rate limits, and OAST/callback policies.
- Don't ship penskillz-managed skills as part of a customer deliverable — link to the source instead.
