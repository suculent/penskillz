#!/usr/bin/env python3
"""Validate sources.yaml shape and cross-check with .gitmodules.

Checked invariants:
  1. sources.yaml parses (PyYAML preferred; the CLI's fallback parser is too lenient for CI use).
  2. Every entry has the required keys: name, url, extractor.
  3. Every entry has a unique `name`.
  4. Every entry references an extractor module that exists at lib/extractors/<name>.py.
  5. Every entry has a matching `[submodule "sources/<name>"]` stanza in .gitmodules
     (otherwise `penskillz sync` would clone-and-orphan).
  6. The `url` in .gitmodules matches the `url` in sources.yaml (case-insensitive).
"""

from __future__ import annotations

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.yaml"
GITMODULES = ROOT / ".gitmodules"
EXTRACTORS_DIR = ROOT / "lib" / "extractors"
REQUIRED = {"name", "url", "extractor"}


def fail(msg: str) -> None:
    print(f"check-sources-yaml: FAIL {msg}", file=sys.stderr)
    sys.exit(1)


def load_yaml() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        fail("PyYAML required: pip install pyyaml")
    try:
        return yaml.safe_load(SOURCES.read_text()) or {}
    except Exception as e:  # pragma: no cover
        fail(f"sources.yaml does not parse: {e}")
        return {}


_SUBMODULE = re.compile(r'\[submodule "(?P<name>[^"]+)"\]')
_KV = re.compile(r"^\s*(?P<k>\w+)\s*=\s*(?P<v>.+?)\s*$")


def load_gitmodules() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not GITMODULES.exists():
        return out
    cur: str | None = None
    for line in GITMODULES.read_text().splitlines():
        m = _SUBMODULE.match(line)
        if m:
            cur = m.group("name")
            out[cur] = {}
            continue
        if cur is None:
            continue
        kv = _KV.match(line)
        if kv:
            out[cur][kv.group("k")] = kv.group("v")
    return out


def main() -> int:
    if not SOURCES.exists():
        fail("sources.yaml not found")
    data = load_yaml()
    sources = data.get("sources") or []
    if not isinstance(sources, list):
        fail("sources.yaml: top-level `sources:` must be a list")

    names: set[str] = set()
    gm = load_gitmodules()

    for i, entry in enumerate(sources):
        loc = f"sources[{i}]"
        if not isinstance(entry, dict):
            fail(f"{loc} must be a mapping")
        missing = REQUIRED - set(entry.keys())
        if missing:
            fail(f"{loc} ({entry.get('name', '?')}): missing keys {sorted(missing)}")

        name = entry["name"]
        if name in names:
            fail(f"duplicate source name: {name}")
        names.add(name)

        extractor = entry["extractor"]
        if not (EXTRACTORS_DIR / f"{extractor}.py").exists():
            fail(f"{loc} ({name}): unknown extractor `{extractor}` "
                 f"(no file at lib/extractors/{extractor}.py)")

        submodule_key = f"sources/{name}"
        if submodule_key not in gm:
            fail(f"{loc} ({name}): no `[submodule \"{submodule_key}\"]` stanza in .gitmodules")

        if entry["url"].lower() != gm[submodule_key].get("url", "").lower():
            fail(f"{loc} ({name}): sources.yaml url != .gitmodules url")

    print(f"check-sources-yaml: OK ({len(sources)} sources)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
