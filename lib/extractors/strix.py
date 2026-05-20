"""Extractor for Strix (github.com/usestrix/strix).

Strix already authors its skills as markdown files with YAML frontmatter
(`name:` + `description:` + body) under `strix/skills/<category>/<name>.md`.
Each file maps cleanly to one Claude Code skill: we copy the body, normalize
the slug (apply optional prefix, namespace category), and emit `SKILL.md`
inside its own directory under `dest/`.

Source-of-truth fields the extractor expects from `Source`:
  path        e.g. "strix/skills"
  prefix      e.g. "strix-"   (prepended to skill names so they don't clash)
  exclude     category dirs to skip entirely
  license     SPDX id to surface in a `# Source` footer

Returns the number of skills written.
"""

from __future__ import annotations

import re
from pathlib import Path


_FM = re.compile(r"^---\s*\n(?P<fm>.*?)\n---\s*\n", re.DOTALL)
_SLUG_BAD = re.compile(r"[^a-z0-9-]+")


def _slug(s: str) -> str:
    s = s.strip().lower().replace("_", "-")
    s = _SLUG_BAD.sub("-", s)
    return s.strip("-")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FM.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group("fm").splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def extract(*, src, dest: Path, log) -> int:
    skills_root = Path(src.skills_root())
    if not skills_root.exists():
        log(f"[strix] skills root missing: {skills_root}")
        return 0

    excluded = set(src.exclude or [])
    prefix = src.prefix or ""
    written = 0

    for category_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        if category_dir.name.startswith("_") or category_dir.name in excluded:
            continue
        category = category_dir.name
        for md_file in sorted(category_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8", errors="replace")
            fm, body = _parse_frontmatter(text)

            base_name = fm.get("name") or md_file.stem
            description = fm.get("description") or f"Strix {category} skill: {md_file.stem}"

            skill_name = f"{prefix}{_slug(base_name)}"
            skill_dir = dest / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)

            footer_lines = [
                "",
                "---",
                "",
                "## Source",
                "",
                f"- Upstream: `{src.url}` (`{src.ref}`)",
                f"- Path: `{src.path}/{category}/{md_file.name}`",
                f"- Category: `{category}`",
            ]
            if src.license:
                footer_lines.append(f"- License: {src.license}")
            footer = "\n".join(footer_lines) + "\n"

            out = (
                "---\n"
                f"name: {skill_name}\n"
                f"description: {description}\n"
                f"metadata:\n"
                f"  source: {src.name}\n"
                f"  category: {category}\n"
                "---\n\n"
                f"{body.lstrip()}"
                f"{footer}"
            )
            (skill_dir / "SKILL.md").write_text(out, encoding="utf-8")
            written += 1

    return written
