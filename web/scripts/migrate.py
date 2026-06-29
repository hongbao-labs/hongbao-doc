#!/usr/bin/env python3
"""Migrate CN/ and EN/ markdown into Starlight content collections."""

from __future__ import annotations

import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
OUT = WEB / "src" / "content" / "docs"

LOCALES = {
    "en": ROOT / "EN",
    "zh": ROOT / "CN",
}

DESCRIPTIONS: dict[str, dict[str, str]] = {
    "index": {
        "en": "Hongbao on-chain asset distribution protocol overview",
        "zh": "Hongbao 链上资产分发协议总览",
    },
    "contact": {
        "en": "Contact channels for partnerships, support, and security disclosure",
        "zh": "商务合作、技术支持与安全披露联系方式",
    },
    "receiver/overview": {
        "en": "Introduction for cardholders — what a Hongbao card is and why it is safe",
        "zh": "持卡人入门 — 红包卡是什么、为什么安全",
    },
    "receiver/claim": {
        "en": "Step-by-step claim guide for Hongbao cardholders",
        "zh": "红包卡领取分步指南",
    },
    "receiver/faq": {
        "en": "Frequently asked questions for Hongbao cardholders",
        "zh": "持卡人常见问题",
    },
    "issuer/overview": {
        "en": "Issuer overview — offline growth campaigns with physical task cards",
        "zh": "发卡方总览 — 用实体任务卡做线下增长",
    },
    "issuer/flow": {
        "en": "End-to-end issuer flow from order to reclaim",
        "zh": "发卡方端到端流程：下单到赎回",
    },
    "issuer/customization": {
        "en": "Co-branded card face customization specification",
        "zh": "卡面联名定制规格",
    },
    "issuer/faq": {
        "en": "Frequently asked questions for Hongbao issuers",
        "zh": "发卡方常见问题",
    },
    "security": {
        "en": "Security overview — contract, hardware, and liveness guarantees",
        "zh": "安全总览 — 合约、硬件与可用性保障",
    },
    "glossary": {
        "en": "Glossary of Hongbao terms",
        "zh": "Hongbao 术语表",
    },
}

CONTACT_EN = """# Contact

| Channel | For |
|---|---|
| **Partnerships / bulk orders** | partnerships@hongbao.digital — Enterprises and projects: bulk card issuance, co-branded customization, new-chain expansion |
| **Retail purchase** | shop@hongbao.digital — Individuals buying a small number as gifts *(waitlist only — retail not yet open)* |
| **Ecosystem partnerships** | bd@hongbao.digital — Wallet / exchange / dapp integration & referral partnerships |
| **Open-source code & issues** | dev@hongbao.digital — GitHub repo, bug reports, PRs |
| **Security disclosure** | security@hongbao.digital — Vulnerabilities, cryptography questions, contract risks |
| **General inquiries** | hello@hongbao.digital — Anything else |
"""


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Directory-style links to a section's landing page, e.g. [receiver/](receiver/).
SECTION_LANDING = {"receiver/": "receiver/overview", "issuer/": "issuer/overview"}


def transform_links(body: str, slug: str) -> str:
    """Rewrite GitHub-relative .md links for the rendered URL layout.

    Every page renders at /<locale>/<slug>/ (the index at /<locale>/), so a
    browser-relative link must climb `depth` levels back to the locale root
    before descending into the target slug. Source links are relative to the
    source file's own directory; we resolve them to a target slug and re-root.
    """
    depth = 0 if slug == "index" else slug.count("/") + 1
    up = "../" * depth
    cur_dir = posixpath.dirname(slug)

    def repl(m: "re.Match[str]") -> str:
        text, target = m.group(1), m.group(2)
        if target in SECTION_LANDING:
            dest = SECTION_LANDING[target]
            return f"[{dest.split('/')[0].capitalize()}]({up}{dest})"
        path, sep, anchor = target.partition("#")
        if not path.endswith(".md"):
            return m.group(0)  # external / asset / anchor-only — leave as-is
        resolved = posixpath.normpath(posixpath.join(cur_dir, path[:-3]))
        if posixpath.basename(resolved).lower() == "readme":
            new_target = up or "./"  # the locale-root overview page
        else:
            new_target = f"{up}{resolved}"
        return f"[{text}]({new_target}{sep}{anchor})"

    return LINK_RE.sub(repl, body)


def parse_markdown(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("Expected markdown file to start with # title")
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:]).lstrip("\n")
    return title, body


def write_doc(locale: str, slug: str, title: str, body: str) -> None:
    description = DESCRIPTIONS[slug][locale]
    ext = "mdx" if slug == "index" else "md"
    out_path = OUT / locale / f"{slug}.{ext}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = f"""---
title: {json_escape(title)}
description: {json_escape(description)}
draft: false
---

"""
    out_path.write_text(frontmatter + body, encoding="utf-8")


def json_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def migrate_locale(locale: str, source_dir: Path) -> None:
    mappings = [
        ("README.md", "index"),
        ("contact.md", "contact"),
        ("receiver/overview.md", "receiver/overview"),
        ("receiver/claim.md", "receiver/claim"),
        ("receiver/faq.md", "receiver/faq"),
        ("issuer/overview.md", "issuer/overview"),
        ("issuer/flow.md", "issuer/flow"),
        ("issuer/customization.md", "issuer/customization"),
        ("issuer/faq.md", "issuer/faq"),
        ("security.md", "security"),
        ("glossary.md", "glossary"),
    ]

    for source_rel, slug in mappings:
        if slug == "contact" and locale == "en":
            title, body = parse_markdown(CONTACT_EN)
        else:
            raw = (source_dir / source_rel).read_text(encoding="utf-8")
            title, body = parse_markdown(raw)
        body = transform_links(body, slug)
        write_doc(locale, slug, title, body)


def main() -> None:
    for locale, source_dir in LOCALES.items():
        migrate_locale(locale, source_dir)
    print(f"Migrated docs into {OUT}")


if __name__ == "__main__":
    main()
