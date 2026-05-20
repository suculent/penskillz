"""Generic extractor for sources that already author skills as frontmatter+markdown.

Walks `src.path` recursively, picks up every `*.md` that has a YAML frontmatter
block with at least `name:` (description optional), and emits one Claude Code
skill per file. Use this for any upstream that organises content the same way
Strix does. For more bespoke layouts, write a dedicated extractor next to this.
"""

from __future__ import annotations

import re
from pathlib import Path


_FM = re.compile(r"^---\s*\n(?P<fm>.*?)\n---\s*\n", re.DOTALL)
_SLUG_BAD = re.compile(r"[^a-z0-9-]+")


def _slug(s: str) -> str:
    return _SLUG_BAD.sub("-", s.strip().lower().replace("_", "-")).strip("-")


def _parse(text: str) -> tuple[dict, str]:
    m = _FM.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group("fm").splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def extract(*, src, dest: Path, log) -> int:
    root = Path(src.skills_root())
    if not root.exists():
        log(f"[frontmatter-md] root missing: {root}")
        return 0
    excluded = set(src.exclude or [])
    prefix = src.prefix or ""
    written = 0
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        if any(part in excluded for part in rel.parts):
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        fm, body = _parse(text)
        if not fm.get("name"):
            continue
        category = rel.parts[0] if len(rel.parts) > 1 else "general"
        skill_name = f"{prefix}{_slug(fm['name'])}"
        skill_dir = dest / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        description = fm.get("description") or f"{src.name} skill: {md.stem}"
        footer = (
            f"\n\n---\n\n## Source\n\n"
            f"- Upstream: `{src.url}` (`{src.ref}`)\n"
            f"- Path: `{src.path}/{rel.as_posix()}`\n"
            + (f"- License: {src.license}\n" if src.license else "")
        )
        out = (
            "---\n"
            f"name: {skill_name}\n"
            f"description: {description}\n"
            "metadata:\n"
            f"  source: {src.name}\n"
            f"  category: {category}\n"
            "---\n\n"
            f"{body.lstrip()}"
            f"{footer}"
        )
        (skill_dir / "SKILL.md").write_text(out, encoding="utf-8")
        written += 1
    return written
