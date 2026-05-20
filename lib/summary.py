"""Generate a single 'capabilities overview' skill and a top-level CAPABILITIES.md.

Reads `dist/skills/index.json` (built by extract) and produces:

  dist/skills/_meta/penskillz-capabilities/SKILL.md
      Installable skill the agent loads once to learn what's in the library
      without paying for every individual skill's description.

  CAPABILITIES.md   (at repo root)
      Human-readable snapshot, checked into git so the latest summary is
      always pinned. Regenerated whenever extract / update runs.

Strategy:
  * group by source -> category
  * for each (source, category), list up to MAX_PER_CATEGORY skill names
  * append a curated lookup table so common pentesting intents route
    directly to the right skill name(s)
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict


MAX_PER_CATEGORY = 5

# One-line "what this source is good for". Keep concise — this lands in the
# agent's context every time the meta-skill is loaded.
SOURCE_BLURBS = {
    "strix":
        "Authoritative web/API methodology. Frontmatter-authored playbooks for SQLi, XSS, SSRF, SSTI, IDOR, RCE, GraphQL, "
        "mass-assignment, business logic, race conditions, plus tooling syntax (nmap, sqlmap, ffuf, nuclei, httpx, ...).",
    "internal-all-the-things":
        "Active Directory and internal-network attack catalogue: Kerberos (asreproast, kerberoasting, S4U, RBCD, "
        "delegation), ADCS ESC1-ESC15, lateral movement, post-ex, cloud, container, DB-pivot techniques.",
    "payloads-all-the-things":
        "Payload library complementing Strix. Use when you need raw payload variants / WAF bypass strings for a "
        "vulnerability class — XSS, SSRF, SSTI, NoSQLi, LFI, command injection, CSV/CRLF/header injection, etc.",
    "mastg":
        "OWASP Mobile Application Security Testing Guide — per-test playbooks across Android and iOS, organised "
        "by MASVS category (STORAGE, AUTH, CRYPTO, CODE, NETWORK, PLATFORM, RESILIENCE).",
    "hacktricks":
        "Broad offsec wiki. Strongest for per-port network-services pentesting, Linux/Windows/macOS hardening, "
        "mobile reversing, binary exploitation, forensics. Use when you need depth Strix and IATT don't cover.",
    "gtfobins":
        "Linux/Unix legit-binary abuse, grouped by technique (shell, file-read, file-write, suid, sudo, "
        "capabilities, library-load). Use when you have local code-exec on a Linux host and need to escalate.",
    "lolbas":
        "Windows signed-binary abuse, grouped by MITRE-aligned category (Execute, Download, Upload, ADS, AWL Bypass, "
        "UAC Bypass, Compile, Credentials, Reconnaissance). Use when operating in a constrained Windows host.",
}

# Curated lookup table — concise enough to keep verbatim in the meta-skill.
# Format: (intent description, comma-separated skill-name hints).
INTENT_LOOKUP = [
    ("Web vuln testing (SQLi/XSS/SSRF/SSTI/IDOR/RCE/...)",        "strix-<class>, patat-<class>"),
    ("GraphQL or REST API hardening",                              "strix-graphql, strix-mass-assignment, strix-broken-function-level-authorization"),
    ("JWT / OIDC token attacks",                                   "strix-authentication-jwt"),
    ("Kubernetes / container security",                            "strix-kubernetes, ht-linux-hardening-*"),
    ("Active Directory + Kerberos",                                "iatt-active-directory-*, ht-windows-hardening-*"),
    ("ADCS certificate-services abuse (ESC1..ESC15)",              "iatt-active-directory-ad-adcs-esc*"),
    ("Per-port network-services pentest",                          "ht-network-services-pentesting-pentesting-<service>"),
    ("Linux privilege escalation via legit binaries",              "gtfobins-suid, gtfobins-sudo, gtfobins-capabilities, gtfobins-shell"),
    ("Linux post-ex shell / file IO",                              "gtfobins-shell, gtfobins-file-read, gtfobins-file-write"),
    ("Windows execution / persistence via signed binaries",        "lolbas-execute, lolbas-awl-bypass, lolbas-uac-bypass, lolbas-ads"),
    ("Windows download / exfil via LOLBAS",                        "lolbas-download, lolbas-upload"),
    ("Android app testing (storage/crypto/auth/network)",          "mastg-tests-android-masvs-<category>-*"),
    ("iOS app testing",                                            "mastg-tests-ios-masvs-<category>-*"),
    ("Subdomain / asset recon",                                    "strix-subfinder, strix-httpx, strix-katana, strix-naabu"),
    ("Nmap / port scanning",                                       "strix-nmap, strix-naabu"),
    ("Source-aware SAST",                                          "strix-source-aware-sast, strix-semgrep"),
    ("File upload + path traversal exploitation",                  "strix-insecure-file-uploads, strix-path-traversal-lfi-rfi, patat-file-inclusion"),
    ("Subdomain takeover",                                         "strix-subdomain-takeover"),
    ("Open redirect / CSRF / header injection",                    "strix-open-redirect, strix-csrf, strix-header-injection"),
]


def _entries_by_source(index_path: Path) -> dict[str, dict[str, list[dict]]]:
    if not index_path.exists():
        return {}
    by_src: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for entry in json.loads(index_path.read_text()):
        src = entry.get("source", "?")
        # Pull category from per-skill metadata if it was emitted by the extractor.
        cat = "general"
        skill_md = Path(entry.get("path", ""))
        # Cheap parse: extractors emit `  category: <cat>` in frontmatter metadata.
        try:
            text = skill_md.read_text()
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("category:"):
                    cat = line.split(":", 1)[1].strip()
                    break
                if line == "---" and cat != "general":
                    break
        except OSError:
            pass
        by_src[src][cat].append(entry)
    return by_src


def _render_overview(by_src: dict[str, dict[str, list[dict]]]) -> str:
    lines: list[str] = []
    lines.append("# penskillz — capabilities overview")
    lines.append("")
    total = sum(len(es) for cats in by_src.values() for es in cats.values())
    lines.append(
        f"Pentesting skill library aggregated from upstream frameworks. "
        f"**{total} skills** across **{len(by_src)} sources**. Load this skill once to learn "
        f"what's available, then load specific skills by name as the engagement demands."
    )
    lines.append("")
    lines.append("## How to use this index")
    lines.append("")
    lines.append(
        "Each skill below is loadable directly by its `name`. Skill names follow the pattern "
        "`<source-prefix>-<topic>` (e.g. `strix-sql-injection`, `ht-network-services-pentesting-pentesting-rdp`, "
        "`gtfobins-suid`). When the task matches a row in the **Intent → skill lookup** at the bottom, prefer "
        "the named skill over re-deriving the approach."
    )
    lines.append("")

    for src in sorted(by_src):
        blurb = SOURCE_BLURBS.get(src, "")
        src_total = sum(len(es) for es in by_src[src].values())
        lines.append(f"## {src} — {src_total} skills")
        lines.append("")
        if blurb:
            lines.append(blurb)
            lines.append("")
        lines.append("| category | count | example skill names |")
        lines.append("| --- | ---: | --- |")
        for cat in sorted(by_src[src]):
            entries = by_src[src][cat]
            sample = sorted(entries, key=lambda e: e["name"])[:MAX_PER_CATEGORY]
            names = ", ".join(f"`{e['name']}`" for e in sample)
            if len(entries) > MAX_PER_CATEGORY:
                names += f", _+{len(entries) - MAX_PER_CATEGORY} more_"
            lines.append(f"| {cat} | {len(entries)} | {names} |")
        lines.append("")

    lines.append("## Intent → skill lookup")
    lines.append("")
    lines.append("| Want to do... | Load |")
    lines.append("| --- | --- |")
    for intent, names in INTENT_LOOKUP:
        lines.append(f"| {intent} | `{names}` |")
    lines.append("")
    lines.append(
        "Patterns with `<class>`, `<category>`, `<service>` are placeholders — substitute the relevant "
        "term and try the matching skill name (e.g. `strix-sql-injection`, "
        "`ht-network-services-pentesting-pentesting-smb`, `mastg-tests-android-masvs-storage-mastg-test-0001`)."
    )
    lines.append("")
    return "\n".join(lines)


def build_summary(root: Path) -> tuple[Path, Path]:
    """Build the meta-skill and the pinned CAPABILITIES.md. Returns their paths."""
    dist = root / "dist" / "skills"
    index_path = dist / "index.json"
    by_src = _entries_by_source(index_path)
    overview = _render_overview(by_src)

    # Installable meta-skill — lives next to the other extracted skills so
    # `penskillz install` picks it up automatically.
    meta_dir = dist / "_meta" / "penskillz-capabilities"
    meta_dir.mkdir(parents=True, exist_ok=True)
    skill_md = (
        "---\n"
        "name: penskillz-capabilities\n"
        "description: Capabilities overview of the penskillz library — load first to discover which specific pentest skill to load next without paying for every skill's description.\n"
        "metadata:\n"
        "  source: penskillz\n"
        "  category: meta\n"
        "---\n\n"
        + overview
    )
    meta_path = meta_dir / "SKILL.md"
    meta_path.write_text(skill_md, encoding="utf-8")

    # Pinned snapshot at repo root, committed into git.
    pinned = root / "CAPABILITIES.md"
    pinned.write_text(overview, encoding="utf-8")

    return meta_path, pinned
