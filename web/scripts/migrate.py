#!/usr/bin/env python3
"""Migrate CN/ and EN/ markdown into Starlight content collections."""

from __future__ import annotations

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
    "receiver/guide": {
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
    "issuer/guide": {
        "en": "End-to-end issuer workflow from order to reclaim",
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


def transform_links(body: str) -> str:
    body = re.sub(r"\[issuer/\]\(issuer/\)", "[Issuer](issuer/overview)", body)
    body = re.sub(r"\[receiver/\]\(receiver/\)", "[Receiver](receiver/overview)", body)
    body = re.sub(
        r"\[README\]\(\.\./README\.md\)",
        "[Overview](../)",
        body,
    )
    body = re.sub(
        r"\[contact\.md\]\(\.\./contact\.md\)",
        "[Contact](../contact)",
        body,
    )
    body = re.sub(r"\[contact\.md\]\(contact\.md\)", "[Contact](contact)", body)
    body = re.sub(r"\[guide\.md\]\(guide\.md\)", "[Claim Guide](guide)", body)
    body = re.sub(r"\[faq\.md\]\(faq\.md\)", "[FAQ](faq)", body)
    body = re.sub(
        r"\[customization\.md\]\(customization\.md\)",
        "[Customization](customization)",
        body,
    )
    body = re.sub(
        r"\[Cardholder Claim Guide\]\(\.\./receiver/guide\.md\)",
        "[Cardholder Claim Guide](../receiver/guide)",
        body,
    )
    body = re.sub(
        r"\[持卡人领取指南\]\(\.\./receiver/guide\.md\)",
        "[持卡人领取指南](../receiver/guide)",
        body,
    )
    body = re.sub(
        r"\[Claim Guide\]\(guide\.md\)",
        "[Claim Guide](guide)",
        body,
    )
    body = re.sub(
        r"\[领取指南\]\(guide\.md\)",
        "[领取指南](guide)",
        body,
    )
    body = re.sub(
        r"\[常见问题\]\(faq\.md\)",
        "[常见问题](faq)",
        body,
    )
    body = re.sub(
        r"\[端到端指南\]\(guide\.md\)",
        "[端到端指南](guide)",
        body,
    )
    body = re.sub(
        r"\[端到端流程\]\(guide\.md\)",
        "[端到端流程](guide)",
        body,
    )
    body = re.sub(
        r"\[卡面联名定制\]\(customization\.md\)",
        "[卡面联名定制](customization)",
        body,
    )
    body = re.sub(
        r"\[Co-branded customization\]\(customization\.md\)",
        "[Co-branded customization](customization)",
        body,
    )
    body = re.sub(
        r"\[End-to-end flow\]\(guide\.md\)",
        "[End-to-end flow](guide)",
        body,
    )
    return body


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
        ("receiver/guide.md", "receiver/guide"),
        ("receiver/faq.md", "receiver/faq"),
        ("issuer/overview.md", "issuer/overview"),
        ("issuer/guide.md", "issuer/guide"),
        ("issuer/customization.md", "issuer/customization"),
        ("issuer/faq.md", "issuer/faq"),
    ]

    for source_rel, slug in mappings:
        if slug == "contact" and locale == "en":
            title, body = parse_markdown(CONTACT_EN)
        else:
            raw = (source_dir / source_rel).read_text(encoding="utf-8")
            title, body = parse_markdown(raw)
        body = transform_links(body)
        write_doc(locale, slug, title, body)


def main() -> None:
    for locale, source_dir in LOCALES.items():
        migrate_locale(locale, source_dir)
    print(f"Migrated docs into {OUT}")


if __name__ == "__main__":
    main()
