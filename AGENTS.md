# AGENTS.md

Guidance for coding agents (Codex, Qwen Code, Cursor, Aider, etc.) working in this repo. Claude Code reads `CLAUDE.md` — the content is equivalent.

## TL;DR

`penskillz` extracts pentesting playbooks from upstream frameworks into a canonical `SKILL.md` format and installs them into agent skill directories. It is Python 3 + bash; Node is only used to manage git hooks via `husky`.

## Repo map

```
bin/penskillz          CLI entrypoint (sync | extract | install | update | list | status | summarize | add-source | doctor)
install.sh             one-line bootstrap installer
sources.yaml           registry of upstream sources — must round-trip with .gitmodules
.gitmodules            git submodule definitions for sources/<name>
lib/extractors/        per-extractor Python modules (strix, frontmatter-md, directory-md, yaml-binary)
lib/summary.py         builds the penskillz-capabilities meta-skill + CAPABILITIES.md
sources/               git submodules; do not hand-edit upstream content
dist/skills/           extracted canonical skills (gitignored, rebuilt by `penskillz extract`)
scripts/               check scripts invoked by husky hooks in .husky/
docs/                  ARCHITECTURE, CONFIGURATION, CONTRIBUTING, DEVELOPMENT, USAGE
CAPABILITIES.md        pinned summary of all extracted skills; refreshed automatically
```

## Conventions

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, etc.) — enforced by `.husky/commit-msg`.
- **Don't bypass hooks** (`--no-verify`, `--no-gpg-sign`) unless the user explicitly asks.
- **`sources.yaml` ↔ `.gitmodules`** must agree. Prefer `penskillz add-source` / `penskillz remove-source` over hand-editing.
- **Don't edit `dist/skills/**`** — it's regenerated.
- **Don't edit upstream content under `sources/<name>/`** — they're submodules; changes belong upstream.
- **License footers** (`## Source` at the bottom of every extracted `SKILL.md`) are required. Any new extractor must emit one.

## Extending the registry

**New upstream source** with `name:` / `description:` frontmatter:
```bash
penskillz add-source <slug> <url> --path <subpath> --extractor frontmatter-md --prefix <slug>-
penskillz update
```

**New extractor:** create `lib/extractors/<name>.py` with:
```python
def extract(*, src, dest, log) -> int:
    # walk src.skills_root(), emit one <skill>/SKILL.md per skill under dest
    # return count of skills emitted
```
`src` exposes `name`, `url`, `ref`, `path`, `prefix`, `exclude`, `license`, `skills_root()`. See `lib/extractors/strix.py` as a worked example.

## Verification before commit

- `npm install` once after clone (installs husky hooks via `prepare`).
- `npm run verify` runs `scripts/verify-staged.sh` — same checks as pre-commit: sources.yaml round-trip, Python/bash syntax on staged files, secret scan.
- Pre-push runs the full extract pipeline end-to-end (skipped on fresh clones with unsynced submodules).
- `penskillz doctor` reports environment problems.

If a hook fails, fix the underlying issue and create a new commit. Don't `--amend` — the failed commit didn't happen.

## Skill output contract

Every emitted `dist/skills/<source>/<skill>/SKILL.md` must:

1. Start with YAML frontmatter containing at least `name` and `description`.
2. Preserve upstream content verbatim in the body.
3. End with a `## Source` footer carrying upstream URL, ref, path, and license.
4. Be accompanied by a `.penskillz-managed` marker file in the same directory (added at install time, not extract time).

## Operational caveats

- **Authorized targets only.** These skills enable real exploitation chains. Treat changes the same as you would changes to any offensive-security handbook.
- **OAST / noisy payloads:** if you add an extractor or source whose skills emit out-of-band callbacks or high-rate fuzzing, call it out in the PR.
- **No secrets in commits.** `scripts/check-secrets.sh` greps for AWS keys, GitHub PATs, private-key headers, etc. on every commit.

## Common commands

| Goal | Command |
| --- | --- |
| Sync submodules + extract + install | `penskillz update` |
| Rebuild meta-skill + CAPABILITIES.md | `penskillz summarize` |
| Inspect state | `penskillz status` / `penskillz list` |
| Install to all supported agents | `penskillz install --agent all` |
| Run pre-commit checks ad hoc | `npm run verify` |
