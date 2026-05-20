# Codebase Concerns

**Analysis Date:** 2026-05-20
**Focus:** risks, tech debt, security/operational hazards in the penskillz aggregator.

Scope: `bin/penskillz`, `install.sh`, `sources.yaml`, `.gitmodules`, `lib/extractors/*.py`, `CAPABILITIES.md`. Severity is engagement-impact, not CVSS.

---

## CRITICAL

### Floating refs on every upstream — supply-chain blast radius
- Description: All seven sources track *branches* (`main`/`master`), not commit pins. Any compromise or malicious PR merged upstream lands in agents on the next `penskillz update`.
- Evidence: `sources.yaml:27,40,59,75,98,128,141` all set `ref: main|master`; `.gitmodules` declares `branch = main|master` for every submodule; `bin/penskillz:235` does `git reset --hard origin/{ref}` with no signature/SHA verification.
- Mitigation: pin `ref:` to a commit SHA (or signed tag) per source; gate `penskillz update` on a SHA-allowlist file; verify with `git verify-commit`/`verify-tag` where upstream signs.

### `install.sh` piped from curl executes Python with elevated PATH effects
- Description: One-liner pattern `curl … | bash` clones, inits submodules, runs the extractor, then mutates `~/.zshrc`/`~/.bashrc` to prepend `~/.penskillz/bin` to PATH — all without checksum verification of the script itself or the repo it pulls.
- Evidence: `install.sh:5-7,49,53,67-77`. No `gpg`/`shasum`/`git verify-*` invocation anywhere in the repo (grep confirmed).
- Mitigation: publish a signed release tarball + `shasum -a 256 --check`, or instruct users to `git clone && git verify-tag` before running; stop mutating shell rc files (print the PATH line and let the user paste).

### Extractors silently swallow malformed upstream YAML
- Description: `_safe_load` catches `yaml.YAMLError` and returns `None`, so a maliciously crafted YAML (or a regression) for a GTFOBins/LOLBAS binary just disappears from the catalogue without a non-zero exit. The same skip-on-anomaly philosophy runs through `directory-md.py` (length-200 short-stub skip, frontmatter parse best-effort).
- Evidence: `lib/extractors/yaml-binary.py:49-54`; `lib/extractors/directory-md.py:125` (`len(text.strip()) < 200: continue`); `lib/extractors/strix.py:34-44` (frontmatter parser ignores any line without `:`).
- Mitigation: count and log every skip; fail the run if skip-rate per source exceeds a threshold; emit a per-source `EXTRACT_REPORT.json` and diff it between runs.

---

## HIGH

### No centralized authorization / scope warning in the meta-skill
- Description: `CAPABILITIES.md` is the entry skill an agent loads first, but it contains zero authorization, legal-scope, or rules-of-engagement language. The only such note lives in `README.md:165` which agents do not read at runtime.
- Evidence: `grep -i 'authoriz|consent|legal|warning|disclaimer' CAPABILITIES.md` returns nothing relevant (the one hit is the skill name `strix-broken-function-level-authorization`).
- Mitigation: prepend an `## Authorization` section to `CAPABILITIES.md` (and to every emitted `SKILL.md` footer) stating "only run against systems with written authorization", and have `summary.build_summary` enforce it.

### No aggregated NOTICE / LICENSE manifest
- Description: Sources span FSL-1.1-MIT, CC-BY-NC-4.0, MIT, GPL-3.0, CC-BY-SA-4.0. CC-BY-NC-4.0 (HackTricks, InternalAllTheThings) imposes a non-commercial restriction; GPL-3.0 (GTFOBins) imposes copyleft on derived works; CC-BY-SA-4.0 (MASTG) imposes share-alike. The repo has no `LICENSE`, `NOTICE`, or aggregated attribution file; only a per-skill footer line.
- Evidence: `ls LICENSE* NOTICE*` returns nothing; license surfaced only in `lib/extractors/*.py` footer writers (`directory-md.py:147`, `strix.py:82`, etc.). `sources.yaml` lists conflicting license families with no policy.
- Mitigation: add a top-level `NOTICE.md` enumerating each upstream + license + URL; add a `LICENSE` (or `LICENSE.md`) for penskillz itself; mark the repo (and any redistributed bundle) non-commercial if any CC-BY-NC source is included, or quarantine those sources behind an opt-in flag.

### Hand-rolled YAML fallback parser doesn't handle the schema it now sees
- Description: `_yaml_load` in `bin/penskillz:56-136` is a tiny recursive parser used when PyYAML is absent. It mis-handles two patterns currently present in `sources.yaml`: (1) `options:` blocks (nested map under a list item) and (2) `include:` / `exclude:` block sequences mixed with inline scalars on the same dash. The block(indent, i) state machine assumes `indent + 2` for children and uses a single global `parse_scalar` that won't preserve quoted strings with embedded `:`.
- Evidence: `bin/penskillz:107-118` only merges the per-item map when `sub` is a `dict`; nested `options.flavour:` (`sources.yaml:131-133,143-145`) works only because PyYAML is present. `install.sh:38-42` makes PyYAML best-effort, so a `pip install` failure silently degrades into the broken fallback path.
- Mitigation: hard-fail if PyYAML import fails *and* any source uses `options:`/`include:`/`exclude:`; add a self-test that round-trips `sources.yaml` through the fallback and compares to PyYAML output.

### `shallow=true` clone + `--depth 1` defeats forensic auditability
- Description: Every clone is depth-1 (`install.sh:53`, `bin/penskillz:225,233`). When a compromise is detected upstream, you cannot diff against the previous synced HEAD locally, and `git_rev` only ever reports a single SHA with no parent chain.
- Evidence: `install.sh:53` `--depth 1`; `bin/penskillz:225,233`; `.gitmodules:5` `shallow = true`.
- Mitigation: keep a `sources.lock` (name → SHA) and append-only history of synced SHAs; or run full-depth on a security-audit cadence.

### HackTricks accounts for ~47% of the catalogue and auto-grows
- Description: 670 of 1430 skills come from HackTricks, included by *directory whitelist* (`include:` covers 13 broad folders). Any new file the upstream adds under those folders is automatically extracted on the next branch sync. There is no upper bound or per-source cap.
- Evidence: `sources.yaml:102-122`; `CAPABILITIES.md:3,27`.
- Mitigation: pin HackTricks to a tag; track a per-source `expected_skill_count`/tolerance in `sources.yaml` and warn on drift; add a `--max-new-skills-per-source` guard.

---

## MEDIUM

### `penskillz update` re-extracts every source unconditionally
- Description: `cmd_update` syncs all, then runs `extract_sources` over the full list and rebuilds `dist/skills/<src>` from scratch (`out_dir.rmtree() + mkdir`). Wasteful on multi-GB clones and makes diffs noisy; also means an unrelated extractor crash can wipe a previously valid catalogue.
- Evidence: `bin/penskillz:400-405,270-274`.
- Mitigation: compare `git rev-parse HEAD` per source against a `sources.lock` SHA; only re-extract changed sources; extract to a temp dir and rename atomically.

### No tests, no CI
- Description: No `tests/` directory, no `.github/` workflows, no linter config beyond stdlib. A schema change in `sources.yaml` or a regex tweak in `directory-md.py` ships untested.
- Evidence: `ls tests .github` both fail; no `pyproject.toml`/`pytest.ini` at root.
- Mitigation: add golden-fixture tests for each extractor (small synthetic upstream tree → expected `SKILL.md` set); add a GitHub Action that runs `penskillz sync && extract` on a pinned fixture monthly.

### Skill-name collisions handled only within a single source
- Description: `directory-md.py:129-132` disambiguates duplicates *within* one source by appending the parent dir, but collisions *across* sources rely solely on the `prefix` convention. There is no check that two prefixes don't share a suffix or that two sources don't both set the same prefix.
- Evidence: `bin/penskillz:342-364` will refuse to overwrite an unmanaged skill but happily overwrites a penskillz-managed skill from a different source if names collide.
- Mitigation: enforce prefix-uniqueness in `add_source`; assert global skill-name uniqueness in `write_index`; fail extract if a name appears twice across sources.

### `install_for_agent` blindly removes managed skill dirs
- Description: For each extracted skill it does `shutil.rmtree(dest_dir)` then `copytree`. A user who manually edits a managed skill (e.g. to add an op-specific note) loses it on every `update`. The marker `.penskillz-managed` is not a content hash, so there's no way to detect drift.
- Evidence: `bin/penskillz:359-362`.
- Mitigation: store a SHA256 of the original install in `.penskillz-managed`; warn on drift instead of clobbering; expose `--force` to opt into the clobber.

### Frontmatter parsers are not real YAML
- Description: `strix.py:_parse_frontmatter`, `directory-md.py` upstream-fm extraction, and `frontmatter-md.py:_parse` all split on the *first* `:` and strip exactly one layer of quotes. Multi-line strings, block scalars (`|`, `>`), and lists in frontmatter are silently dropped or mis-interpreted.
- Evidence: `lib/extractors/strix.py:34-44`; `lib/extractors/directory-md.py:111-115`; `lib/extractors/frontmatter-md.py:23-32`.
- Mitigation: use `yaml.safe_load` for the frontmatter block (PyYAML is already a dependency for the yaml-binary extractor); fall back to the regex parser only when PyYAML is missing.

### HackTricks `{{#include …}}` shortcodes are removed but referenced content is not inlined
- Description: `_HT_INCLUDE` regex strips `{{#include path}}` directives outright (`directory-md.py:34,121`). Pages that rely on includes to carry actual content become hollow shells; the 200-char minimum filter catches the worst but not all.
- Evidence: `lib/extractors/directory-md.py:34,121,125`.
- Mitigation: resolve the include path against `src.skills_root()` and inline the referenced markdown; or log every stripped include so missing content is visible.

---

## LOW

### Description placeholder for the prompt mentioning GPG signing
- Description: The orchestrator prompt mentions "GPG signing required but breaks in non-TTY environments" — but `grep -n gpg` against the entire repo (`bin/penskillz`, `install.sh`, `lib/extractors/*.py`, root configs) returns nothing. Either the requirement is enforced elsewhere (commit hooks not in tree) or the claim is stale. Either way, behaviour is undocumented.
- Evidence: no `gpg` or `commit.gpgsign` reference anywhere in the read files.
- Mitigation: if commits/tags must be signed, document it in `README.md` and add a `pre-commit`/CI check that fails non-signed commits.

### `install.sh` uses `pull --ff-only` and a broad `submodule update`
- Description: A diverged `~/.penskillz` (e.g. local fork) breaks update silently because `pull --ff-only` will error mid-script and `set -e` aborts — but only *after* PyYAML install and before extract; user is left in a half-state.
- Evidence: `install.sh:17,46`.
- Mitigation: detect divergence first and ask, or stash; or refuse to operate on a non-clean working tree.

### `cmd_remove_source` leaves the clone behind
- Description: Removing a source from `sources.yaml` keeps the `sources/<name>` clone and any extracted output under `dist/skills/<name>`. On next `install`, the orphan skills are still copied into agents.
- Evidence: `bin/penskillz:453-459`; `install_for_agent` iterates `DIST_DIR.iterdir()` (`bin/penskillz:349`).
- Mitigation: in `cmd_remove_source`, also remove `dist/skills/<name>` and prompt about `sources/<name>`; in `install_for_agent`, skip directories whose source no longer exists in `sources.yaml`.

### `dest_dir.exists() and not (dest_dir / marker).exists()` check is racy and ext-sensitive
- Description: The "is this skill penskillz-managed?" check looks for a hidden file by name. A user copying a skill with `cp -R` would carry the marker over; a hostile skill author could ship a marker to make their content overwritable by us (low value) or unowned to block us.
- Evidence: `bin/penskillz:348,356-362`.
- Mitigation: track managed skills in a central manifest under `~/.claude/skills/.penskillz-manifest.json` keyed by name+source+SHA.

### Length-200 stub filter is locale/whitespace-sensitive
- Description: `len(text.strip()) < 200` after stripping frontmatter and includes — a page that's mostly whitespace + a long code block (e.g. CTF payload) could fall under or over 200 unpredictably, depending on upstream formatting.
- Evidence: `lib/extractors/directory-md.py:125`.
- Mitigation: count non-code, non-link characters or word count; or make the threshold per-source-configurable.

---

*Concerns audit: 2026-05-20*
