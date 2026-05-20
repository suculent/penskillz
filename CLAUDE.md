# CLAUDE.md

Guidance for Claude Code (and compatible agents) working in this repo.

## What this repo is

**penskillz** is a pentesting skill registry. It clones upstream pentesting frameworks (Strix, HackTricks, MASTG, PayloadsAllTheThings, InternalAllTheThings, GTFOBins, LOLBAS) as git submodules under `sources/`, runs per-source extractors in `lib/extractors/` to produce canonical `SKILL.md` files under `dist/skills/`, and installs them into agent skill dirs (`~/.claude/skills`, `~/.codex/skills`, `~/.qwen/skills`).

The shipped artefact is ~1,400 drop-in skills plus a `penskillz-capabilities` meta-skill that indexes them.

## Stack

- **Runtime:** Python 3 + bash. The CLI lives at `bin/penskillz`.
- **Node:** only used for `husky`-managed git hooks (`package.json` → `prepare`).
- **No build step** beyond the extract pipeline (`penskillz extract`).
- **Submodules:** `sources/<name>` — never edit upstream content directly; the next `penskillz update` will overwrite.

## Layout

```
bin/penskillz          CLI (sync | extract | install | update | list | status | summarize | add-source | …)
install.sh             one-line bootstrap installer
sources.yaml           registry of upstream sources (slug, url, ref, path, extractor, prefix, exclude, license)
.gitmodules            must round-trip with sources.yaml (enforced by pre-commit)
lib/extractors/        one Python module per extractor type (strix, frontmatter-md, directory-md, yaml-binary)
lib/summary.py         builds penskillz-capabilities meta-skill + CAPABILITIES.md
sources/               git submodules — one per upstream framework
dist/skills/           extracted canonical skills (gitignored; rebuilt by extract)
scripts/               git-hook scripts called from .husky/
docs/                  ARCHITECTURE, CONFIGURATION, CONTRIBUTING, DEVELOPMENT, USAGE
CAPABILITIES.md        pinned snapshot of the meta-skill; auto-refreshed on relevant commits
```

## Working in this repo

- **Adding an upstream source:** prefer `penskillz add-source` — it updates `sources.yaml` *and* `.gitmodules` atomically. Manual edits to either must keep them in sync or pre-commit will block.
- **Adding an extractor:** drop `lib/extractors/<name>.py` exposing `extract(*, src, dest, log) -> int`. See `lib/extractors/strix.py` for the canonical shape. Register it via `--extractor <name>` in `sources.yaml`.
- **Touching extractors, sources.yaml, or lib/summary.py:** the pre-commit hook will rebuild `CAPABILITIES.md` and re-stage it. Don't fight this — let it run.
- **Don't hand-edit `dist/skills/**`** — it's regenerated. Don't hand-edit `~/.claude/skills/strix-*` etc. on a user's machine either; those carry a `.penskillz-managed` marker and get overwritten on `penskillz update`.

## Verification

- `npm install` once after a fresh clone to install husky hooks.
- `npm run verify` runs the same checks the pre-commit hook does (`scripts/verify-staged.sh`): sources.yaml round-trip, staged Python/bash syntax, secret scan.
- `pre-push` runs the full extract pipeline end-to-end. It's skipped on fresh clones where submodules haven't been synced yet.
- `penskillz doctor` diagnoses environment issues.

## Commit conventions

**Conventional Commits, enforced by `.husky/commit-msg`** (`scripts/check-commit-msg.sh`). Examples:

- `feat(extractor): add support for foo upstream`
- `fix(install): handle missing PENSKILLZ_HOME`
- `docs(usage): clarify add-source flow`
- `chore(deps): bump husky`

Allowed types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`, `perf`, `style`, `revert`. Scope is optional but recommended.

## Operational rules

- **Authorized use only.** Skills enable real exploitation paths — treat the repo like any red-team handbook. Don't run extracted skills against systems without written authorization.
- **License footers are load-bearing.** Each `SKILL.md` ends with `## Source` (upstream URL, ref, path, license). Extractors must preserve this — downstream consumers rely on it for compliance.
- **Detection profile:** many extracted skills carry OAST callbacks and noisy fuzzing patterns. Anything that adds new categories of payloads should be noted in PRs.

## Common tasks

| Task | Command |
| --- | --- |
| Pull latest upstream + rebuild + reinstall | `penskillz update` |
| Rebuild only the capabilities summary | `penskillz summarize` |
| List sources and installed counts | `penskillz status` |
| Install to multiple agents | `penskillz install --agent all` |
| Run pre-commit checks manually | `npm run verify` |
