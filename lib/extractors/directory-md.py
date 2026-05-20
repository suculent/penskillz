"""Generic extractor for markdown wikis without frontmatter.

Walks `src.path` recursively for `*.md`, emits one Claude-Code skill per file.
The skill name is derived from the file's path (joined with hyphens) and an
optional `src.prefix`. The description is taken from the file's first H1 (with
any blockquote summary that follows) or, if absent, from the directory name.

Path filtering is performed against the relative path's first segment:

- `include`  in `sources.yaml` (list of dir prefixes): only files whose first
              path segment matches one of these are emitted.
- `exclude`  in `sources.yaml`: any file whose first segment matches is dropped.

Filenames like `README.md`, `SUMMARY.md`, `index.md`, `_index.md` at root
level are skipped automatically (they are tables-of-contents, not skills).
Nested READMEs are kept because for many wikis (PayloadsAllTheThings,
InternalAllTheThings) the per-topic README is the whole skill.

Skill name shape: `<prefix><segment1>-<segment2>-...-<stem>`
slugged: lowercase, hyphens, no underscores or whitespace.
"""

from __future__ import annotations

import re
from pathlib import Path


_SLUG_BAD = re.compile(r"[^a-z0-9-]+")
_H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_BLOCKQUOTE = re.compile(r"^>\s*(.+?)(?:\n\n|\Z)", re.DOTALL | re.MULTILINE)
_MULTI_HYPHEN = re.compile(r"-+")
_LEADING_FM = re.compile(r"\A---\s*\n(?P<fm>.*?)\n---\s*\n", re.DOTALL)
_HT_INCLUDE = re.compile(r"\{\{#include[^}]*\}\}\s*\n?")
_MASTG_HIDE = re.compile(r"^---\s*\nhide:\s*toc\s*\n---\s*\n", re.MULTILINE)

# Names that are wiki index files, not standalone content.
_ROOT_NAV_FILES = {"readme", "summary", "index", "_index", "changelog", "contributing", "disclaimer", "license"}


def _slug(s: str) -> str:
    s = s.strip().lower().replace("_", "-").replace(" ", "-")
    s = _SLUG_BAD.sub("-", s)
    return _MULTI_HYPHEN.sub("-", s).strip("-")


def _name_from_path(rel: Path, prefix: str) -> str:
    parts = [_slug(p) for p in rel.with_suffix("").parts]
    parts = [p for p in parts if p]
    # If the file is a directory's index (README/index.md), drop the trailing
    # nav-file stem so e.g. "account-takeover/readme.md" -> "account-takeover".
    if len(parts) > 1 and parts[-1] in _ROOT_NAV_FILES:
        parts = parts[:-1]
    return f"{prefix}{'-'.join(parts)}"


def _description(text: str, fallback: str) -> str:
    h1 = _H1.search(text)
    desc = ""
    if h1:
        desc = h1.group(1).strip()
        # Look for a blockquote summary right after the H1.
        after = text[h1.end():h1.end() + 4000]
        bq = _BLOCKQUOTE.search(after)
        if bq:
            summary = bq.group(1).strip().replace("\n", " ")
            if 20 <= len(summary) <= 280:
                desc = summary
    if not desc:
        desc = fallback
    # Description must be a single line. Trim hard.
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(desc) > 280:
        desc = desc[:277] + "..."
    return desc


def extract(*, src, dest: Path, log) -> int:
    root = Path(src.skills_root())
    if not root.exists():
        log(f"[directory-md] root missing: {root}")
        return 0

    include = set(getattr(src, "include", None) or [])  # extracted from sources.yaml
    # Fall back to a plain dict lookup via to_dict-style attribute if necessary.
    if not include and hasattr(src, "to_dict"):
        include = set((src.to_dict() or {}).get("include") or [])
    exclude = set(src.exclude or [])
    prefix = src.prefix or ""
    written = 0
    seen_names: dict[str, Path] = {}

    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root)
        parts = rel.parts

        if not parts:
            continue
        # Skip top-level nav/meta files.
        if len(parts) == 1 and md.stem.lower() in _ROOT_NAV_FILES:
            continue
        if include and parts[0] not in include:
            continue
        if any(p in exclude for p in parts):
            continue
        raw = md.read_text(encoding="utf-8", errors="replace")

        # Strip upstream YAML frontmatter (MASTG, some HackTricks pages).
        upstream_fm: dict[str, str] = {}
        fm_match = _LEADING_FM.match(raw)
        if fm_match:
            for line in fm_match.group("fm").splitlines():
                if ":" in line and not line.startswith(" "):
                    k, _, v = line.partition(":")
                    upstream_fm[k.strip()] = v.strip().strip('"').strip("'")
            text = raw[fm_match.end():]
        else:
            text = raw

        # HackTricks include shortcodes and MASTG `hide: toc` re-frontmatter -> drop.
        text = _HT_INCLUDE.sub("", text)
        text = _MASTG_HIDE.sub("", text)

        # Skip very short stubs after cleanup.
        if len(text.strip()) < 200:
            continue

        skill_name = _name_from_path(rel, prefix)
        if skill_name in seen_names:
            # Disambiguate by appending the parent directory.
            skill_name = f"{skill_name}-{_slug(rel.parent.name)}"
        seen_names[skill_name] = md

        title = upstream_fm.get("title") or ""
        fallback = title or " ".join(_slug(p).replace("-", " ") for p in rel.with_suffix("").parts).title()
        description = _description(text, fallback)

        skill_dir = dest / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        category = parts[0] if len(parts) > 1 else "root"
        footer = (
            "\n\n---\n\n## Source\n\n"
            f"- Upstream: `{src.url}` (`{src.ref}`)\n"
            f"- Path: `{src.path}/{rel.as_posix()}`\n"
            f"- Category: `{category}`\n"
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
            f"{text.lstrip()}"
            f"{footer}"
        )
        (skill_dir / "SKILL.md").write_text(out, encoding="utf-8")
        written += 1

    return written
