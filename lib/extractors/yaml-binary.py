"""Extractor for per-binary YAML catalogues (GTFOBins + LOLBAS).

Both projects ship one YAML file per "living off the land" binary. Producing one
skill per binary would explode the catalogue and dilute signal. Instead, this
extractor regroups every binary's entries by **technique category** and emits
one consolidated skill per category. Pick `options.flavour:` in `sources.yaml`:

  gtfobins   GTFOBins shape — _gtfobins/<bin> files. Each file has:
                functions:
                  <function>:
                    - code: |- ...
                      contexts: { sudo:, suid:, unprivileged: }
             Skills emitted: one per `<function>` key (shell, file-read,
             file-write, sudo, suid, capabilities, library-load, command, ...).

  lolbas     LOLBAS shape — yml/<group>/<Binary>.yml files. Each file has:
                Name, Description
                Commands:
                  - Command, Description, Usecase, Category, MitreID,
                    OperatingSystem, Privileges
             Skills emitted: one per `Category` value (ADS, AWL Bypass,
             Compile, Copy, Credentials, Download, Execute, Reconnaissance,
             UAC Bypass, Upload, ...).

Each emitted skill is a Markdown table of entries with the binary, command,
MITRE ID / context, and any provided notes. Source URL preserved.

Requires PyYAML. If not installed: `python3 -m pip install pyyaml`.
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError as e:
    raise SystemExit("yaml-binary extractor requires PyYAML: pip install pyyaml") from e


_SLUG_BAD = re.compile(r"[^a-z0-9-]+")


def _slug(s: str) -> str:
    return _SLUG_BAD.sub("-", s.strip().lower().replace("_", "-").replace(" ", "-")).strip("-")


def _safe_load(p: Path) -> dict | None:
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace"))
    except yaml.YAMLError:
        return None


# --- GTFOBins -----------------------------------------------------------------

def _walk_gtfobins(root: Path):
    """Yield (binary_name, function_name, entry_dict) for every GTFOBins entry."""
    for fp in sorted(root.iterdir()):
        if not fp.is_file():
            continue
        data = _safe_load(fp)
        if not isinstance(data, dict):
            continue
        binary = fp.name
        functions = data.get("functions") or {}
        if not isinstance(functions, dict):
            continue
        for func_name, entries in functions.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                yield binary, func_name, entry


def _emit_gtfobins(src, dest: Path, log) -> int:
    root = Path(src.skills_root())
    grouped: dict[str, list[tuple]] = {}
    for binary, func, entry in _walk_gtfobins(root):
        grouped.setdefault(func, []).append((binary, entry))

    if not grouped:
        log("[yaml-binary] gtfobins: nothing parsed")
        return 0

    descriptions = {
        "shell":                       "GTFOBins binaries that spawn an interactive shell — for jail breakout and post-exploitation",
        "command":                     "GTFOBins binaries that execute arbitrary single commands",
        "non-interactive-bind-shell":  "GTFOBins binaries that bind a non-interactive shell to a port",
        "non-interactive-reverse-shell":"GTFOBins binaries that fire a non-interactive reverse shell",
        "bind-shell":                  "GTFOBins binaries that bind an interactive shell to a port",
        "reverse-shell":               "GTFOBins binaries that establish an interactive reverse shell",
        "file-upload":                 "GTFOBins binaries that exfiltrate / upload files",
        "file-download":               "GTFOBins binaries that download files to disk",
        "file-write":                  "GTFOBins binaries that write attacker-controlled content to files",
        "file-read":                   "GTFOBins binaries that read arbitrary files (privilege-bounded)",
        "library-load":                "GTFOBins binaries that load attacker-controlled libraries",
        "suid":                        "GTFOBins SUID escalation primitives — abuse the suid bit to escalate to root",
        "sudo":                        "GTFOBins sudo escalation primitives — abuse a sudo allowance to escalate",
        "capabilities":                "GTFOBins binaries that abuse Linux capabilities (cap_setuid, cap_dac_read_search, etc.)",
        "limited-suid":                "GTFOBins SUID binaries with limited (non-root) escalation paths",
    }

    written = 0
    for func, entries in sorted(grouped.items()):
        skill_name = f"{src.prefix}{_slug(func)}"
        skill_dir = dest / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        description = descriptions.get(func, f"GTFOBins entries for the `{func}` technique across Linux/Unix binaries")
        lines = [
            f"# GTFOBins — {func} ({len(entries)} binaries)",
            "",
            f"Linux/Unix binaries that can be abused for `{func}` per GTFOBins. Each entry shows the binary, exploit code, and applicable contexts (`sudo`, `suid`, `unprivileged`).",
            "",
            "Use this as a lookup when you have local code execution on a Linux/Unix host: enumerate which of the listed binaries are present (SUID, NOPASSWD sudo entries, capabilities), then apply the matching technique.",
            "",
        ]
        for binary, entry in sorted(entries, key=lambda x: x[0]):
            code = (entry.get("code") or "").strip()
            comment = (entry.get("comment") or "").strip()
            contexts = entry.get("contexts") or {}
            ctx_keys = [k for k, _ in (contexts.items() if isinstance(contexts, dict) else [])]
            ctx_str = ", ".join(ctx_keys) if ctx_keys else "?"
            lines.append(f"## `{binary}`")
            lines.append("")
            lines.append(f"*Contexts:* {ctx_str}")
            if comment:
                lines.append("")
                lines.append(f"> {comment}")
            lines.append("")
            lines.append("```sh")
            lines.append(code)
            lines.append("```")
            lines.append("")
            lines.append(f"<https://gtfobins.github.io/gtfobins/{binary}/>")
            lines.append("")

        body = "\n".join(lines)
        out = (
            "---\n"
            f"name: {skill_name}\n"
            f"description: {description}\n"
            "metadata:\n"
            f"  source: {src.name}\n"
            f"  category: {func}\n"
            "---\n\n"
            f"{body}\n\n---\n\n## Source\n\n"
            f"- Upstream: `{src.url}` (`{src.ref}`)\n"
            + (f"- License: {src.license}\n" if src.license else "")
        )
        (skill_dir / "SKILL.md").write_text(out, encoding="utf-8")
        written += 1
    return written


# --- LOLBAS -------------------------------------------------------------------

def _walk_lolbas(root: Path):
    """Yield (binary_name, group, command_dict, top_dict) for every LOLBAS entry."""
    for group_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for fp in sorted(group_dir.glob("*.yml")):
            data = _safe_load(fp)
            if not isinstance(data, dict):
                continue
            binary = data.get("Name") or fp.stem
            for cmd in (data.get("Commands") or []):
                if isinstance(cmd, dict):
                    yield binary, group_dir.name, cmd, data


def _emit_lolbas(src, dest: Path, log) -> int:
    root = Path(src.skills_root())
    grouped: dict[str, list[tuple]] = {}
    for binary, group, cmd, top in _walk_lolbas(root):
        category = cmd.get("Category") or "Uncategorised"
        grouped.setdefault(category, []).append((binary, group, cmd, top))

    if not grouped:
        log("[yaml-binary] lolbas: nothing parsed")
        return 0

    written = 0
    for category, entries in sorted(grouped.items()):
        skill_name = f"{src.prefix}{_slug(category)}"
        skill_dir = dest / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        description = f"LOLBAS Windows binaries cataloged under the `{category}` technique ({len(entries)} commands across native and other Microsoft binaries)"
        lines = [
            f"# LOLBAS — {category} ({len(entries)} commands)",
            "",
            f"Signed Windows binaries and scripts abusable for `{category}` per the LOLBAS project. Use this when operating on a Windows host with constrained tooling — these binaries are present by default and frequently trusted by EDR/AV signature lists.",
            "",
        ]
        for binary, group, cmd, top in sorted(entries, key=lambda x: x[0]):
            command = (cmd.get("Command") or "").strip()
            cdesc = (cmd.get("Description") or "").strip()
            usecase = (cmd.get("Usecase") or "").strip()
            mitre = cmd.get("MitreID") or ""
            os_list = cmd.get("OperatingSystem") or ""
            privs = cmd.get("Privileges") or ""
            lines.append(f"## `{binary}` — {group}")
            lines.append("")
            if cdesc:
                lines.append(f"**What:** {cdesc}")
                lines.append("")
            if usecase:
                lines.append(f"**Use case:** {usecase}")
                lines.append("")
            meta_bits = []
            if mitre:
                meta_bits.append(f"MITRE: `{mitre}`")
            if privs:
                meta_bits.append(f"Privs: `{privs}`")
            if os_list:
                meta_bits.append(f"OS: {os_list}")
            if meta_bits:
                lines.append(" · ".join(meta_bits))
                lines.append("")
            lines.append("```cmd")
            lines.append(command)
            lines.append("```")
            lines.append("")
            lines.append(f"<https://lolbas-project.github.io/lolbas/{group}/{binary.split('.')[0]}/>")
            lines.append("")

        body = "\n".join(lines)
        out = (
            "---\n"
            f"name: {skill_name}\n"
            f"description: {description}\n"
            "metadata:\n"
            f"  source: {src.name}\n"
            f"  category: {_slug(category)}\n"
            "---\n\n"
            f"{body}\n\n---\n\n## Source\n\n"
            f"- Upstream: `{src.url}` (`{src.ref}`)\n"
            + (f"- License: {src.license}\n" if src.license else "")
        )
        (skill_dir / "SKILL.md").write_text(out, encoding="utf-8")
        written += 1
    return written


# --- entry point --------------------------------------------------------------

def extract(*, src, dest: Path, log) -> int:
    flavour = (src.options or {}).get("flavour") or src.name
    flavour = flavour.lower()
    if "gtfobins" in flavour:
        return _emit_gtfobins(src, dest, log)
    if "lolbas" in flavour:
        return _emit_lolbas(src, dest, log)
    raise SystemExit(
        f"yaml-binary extractor: unknown flavour '{flavour}' (set options.flavour to gtfobins or lolbas)"
    )
