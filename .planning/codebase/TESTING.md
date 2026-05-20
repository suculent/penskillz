# Testing Patterns

**Analysis Date:** 2026-05-20

## Current State

**There are no automated tests in this repository.** No `tests/` directory, no `pytest`/`unittest` invocation, no CI workflow, no `conftest.py`. The only quality gate today is the manual smoke-test path documented in `docs/CONTRIBUTING.md` ("Testing changes locally", lines 62–70):

```bash
PENSKILLZ_HOME=$PWD bin/penskillz sync
PENSKILLZ_HOME=$PWD bin/penskillz extract
PENSKILLZ_HOME=$PWD PENSKILLZ_PREFIX=$PWD/_test bin/penskillz install
ls _test | head
```

This is the workflow contributors are expected to run before submitting changes that touch extractors or install logic. `_test/` is gitignored and discarded afterwards.

## What Needs Testing (Future Work)

The codebase has several deterministic transformations that would be straightforward to cover with pytest. Listed in rough priority order:

### 1. Extractor Round-Trip

For each of `strix`, `frontmatter-md`, `directory-md`, `yaml-binary`: given a small fixture upstream tree on disk, calling `extract(src=..., dest=tmp_path, log=lambda _: None)` should produce a byte-identical canonical `SKILL.md` tree. This catches accidental changes to the frontmatter shape, footer, slug rules, or description handling — all of which are public contracts because installed agents key off skill names.

Fixture data should live at `tests/fixtures/<extractor>/upstream/` (a minimal real-shaped tree) and the expected output at `tests/fixtures/<extractor>/expected/`. Compare with `pathlib` walks, not snapshot tools, so diffs are readable.

### 2. directory-md Include/Exclude Filter

`lib/extractors/directory-md.py` lines 84–105 contain the most subtle filtering logic in the codebase: `include` matches against `parts[0]` only, `exclude` matches against `any(p in exclude for p in parts)`, top-level nav files (`README`, `SUMMARY`, `index`, `_index`, `changelog`, `contributing`, `disclaimer`, `license`) are dropped at depth 1 but kept as directory indexes at deeper levels, and stubs under 200 chars after frontmatter/include-shortcode stripping are skipped. Each of these branches deserves a unit test — they have all caused real upstream regressions historically (PayloadsAllTheThings, HackTricks, MASTG).

### 3. yaml-binary Flavour Dispatch

`lib/extractors/yaml-binary.py::extract` dispatches on `(src.options or {}).get("flavour") or src.name`, lowercased, with substring matches `"gtfobins" in flavour` / `"lolbas" in flavour`. Tests should cover: explicit `options.flavour: gtfobins`, fallback to `src.name`, unknown flavour raising `SystemExit`, and that the GTFOBins/LOLBAS walkers correctly group by `function` and `Category` respectively (using tiny synthetic YAML inputs, not the real cached submodules).

### 4. YAML Loader Fallback

`bin/penskillz::_yaml_load` (lines 56–136) is a hand-rolled YAML subset used when PyYAML is unavailable. It needs tests for: top-level map of lists of maps (the actual `sources.yaml` shape), inline scalar values, quoted scalars, `true`/`false`/`null`/`~`, comments, mixed dash-prefixed maps with first-key-on-same-line, and parity with PyYAML on the real `sources.yaml`. The easiest formulation: `assert _yaml_load(text) == yaml.safe_load(text)` for a corpus of fixtures, with the `import yaml` line monkeypatched out to force the fallback path.

### 5. Slug Determinism

Each extractor's local `_slug` (and `directory-md.py::_name_from_path`) should be a pure function. Parametrize a table: `("Account Takeover", "account-takeover")`, `("ad/adcs-esc1", "ad-adcs-esc1")`, `("README", "readme")`, etc. Also verify that running the same extractor twice over the same input produces identical output (no nondeterministic dict iteration leaking into output ordering — relevant for the `seen_names` disambiguation branch in `directory-md.py` lines 129–132).

### 6. Install Marker Safety

`bin/penskillz::install_for_agent` (lines 342–365) refuses to overwrite a destination skill directory that exists without the `.penskillz-managed` marker file. This is the only mechanism preventing penskillz from clobbering a user-authored skill. A regression here is silent and destructive. Tests should cover: clean install into empty dir, reinstall over a previous penskillz-managed dir (replaces), refusal when the marker is absent (warns, skips, leaves user dir intact), and `--agent all` fan-out across `AGENT_TARGETS`. Use `tmp_path` as the install target with `PENSKILLZ_PREFIX`.

### 7. Summary Regeneration Determinism

`lib/summary.py::build_summary` reads `dist/skills/index.json` and writes both the meta-skill `SKILL.md` and the pinned `CAPABILITIES.md`. Two consecutive runs against the same `index.json` must produce byte-identical output (`by_src` uses `defaultdict` and sorts in `_render_overview`, so this should hold — but a test pins it). This matters because `CAPABILITIES.md` is checked into git; any nondeterminism produces churn diffs.

## Suggested pytest Layout

```
tests/
├── conftest.py                       # shared fixtures: tmp Source, log capture
├── fixtures/
│   ├── strix/upstream/ + expected/
│   ├── frontmatter-md/...
│   ├── directory-md/...
│   ├── yaml-binary/gtfobins/ + lolbas/
│   └── yaml-loader/                  # sources.yaml-shaped corpora
├── test_extractor_strix.py
├── test_extractor_frontmatter_md.py
├── test_extractor_directory_md.py
├── test_extractor_yaml_binary.py
├── test_yaml_loader.py
├── test_slug.py
├── test_install.py                   # uses PENSKILLZ_PREFIX=tmp_path
└── test_summary.py
```

Run command: `pytest -q` from the repo root, with `bin` and `lib` added to `sys.path` via `conftest.py` (mirroring what `bin/penskillz` does at line 44). No additional runtime deps beyond `pytest` itself — the codebase's no-deps posture should extend to its tests.

## What NOT to Test

- The git operations in `bin/penskillz::git_sync` / `git_rev`. They are thin `subprocess` wrappers around `git clone`/`fetch`/`checkout`/`reset` — mocking them adds no signal and integration coverage is already provided by the manual smoke test.
- The argparse wiring in `build_parser`. Argparse is well-tested upstream; cover the command handlers directly instead.
- Live upstream content. Tests must run offline against fixtures committed under `tests/fixtures/`, not against the real submodules under `sources/`.

## Coverage

No coverage target is enforced today. If tests are introduced, a reasonable initial target is the four extractors and `_yaml_load` at 100% line coverage (they are pure transformations) and `install_for_agent` at branch coverage for the marker-safety paths. The rest of `bin/penskillz` is glue and does not warrant strict coverage.

---

*Testing analysis: 2026-05-20*
