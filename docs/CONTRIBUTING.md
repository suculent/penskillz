# Contributing

penskillz is intentionally small. Most contributions land in one of three places:

1. **Add an upstream source** — register a framework's playbooks. See [USAGE §5](USAGE.md#5-add-a-new-upstream-source).
2. **Write an extractor** — handle a source whose layout doesn't match `frontmatter-md`.
3. **Add an agent target** — wire up a new agent's skill directory.

## Adding an extractor

An extractor is a Python module under `lib/extractors/`. It must expose:

```python
def extract(*, src, dest: pathlib.Path, log) -> int:
    """
    src:  Source dataclass — fields name, url, ref, path, prefix, exclude,
          license, plus checkout_dir() and skills_root().
    dest: a fresh, empty directory the extractor owns. Write one
          subdirectory per skill, each containing SKILL.md.
    log:  callable(str) — write progress/warnings here.

    Return the number of skills written.
    """
```

`SKILL.md` requirements:

- Starts with a YAML frontmatter block: at minimum `name:` and `description:`.
- Body is plain Markdown; treat upstream content as authoritative and don't rewrite it semantically.
- End with a `## Source` section linking upstream URL, ref, path, and license. The Strix extractor in `lib/extractors/strix.py` shows the canonical layout.

Skill name discipline:

- Always apply `src.prefix`. Without it, two upstreams with the same skill name collide on install.
- Slugify: lowercase, hyphens only, no whitespace, no underscores.

When you're done, register the extractor in `sources.yaml` (`extractor: <name>`) and run `penskillz extract <source>` to verify output. Then `penskillz install --agent claude-code`.

## Adding an agent target

Edit `AGENT_TARGETS` in `bin/penskillz`:

```python
AGENT_TARGETS = {
    "claude-code": ("CLAUDE_SKILLS_DIR", Path.home() / ".claude" / "skills"),
    "codex":       ("CODEX_SKILLS_DIR",  Path.home() / ".codex"  / "skills"),
    "qwen":        ("QWEN_SKILLS_DIR",   Path.home() / ".qwen"   / "skills"),
    # add yours here
}
```

If the agent expects a different on-disk format (not `<dir>/<skill>/SKILL.md`), wrap the install copy in a small adapter function instead of hard-coding the path.

## Source-of-truth conventions

- `sources.yaml` is the only registry. Don't add hidden defaults in code.
- `dist/skills/` is build output and is gitignored. Never commit it.
- Submodules are pinned to a branch (`ref:`) and refreshed by `penskillz sync`. Don't pin to floating refs you don't trust.
- License of extracted content is the upstream's, surfaced in the `## Source` footer of every `SKILL.md`. Don't strip it.

## Testing changes locally

```bash
PENSKILLZ_HOME=$PWD bin/penskillz sync
PENSKILLZ_HOME=$PWD bin/penskillz extract
PENSKILLZ_HOME=$PWD PENSKILLZ_PREFIX=$PWD/_test bin/penskillz install
ls _test | head
```

Drop `_test/` when done. It's gitignored.
