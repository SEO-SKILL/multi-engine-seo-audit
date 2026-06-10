"""Schema.org JSON-LD 相关 detector functions"""
from __future__ import annotations

import json

from bs4 import BeautifulSoup


def extract_jsonld(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    blocks = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            blocks.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return blocks


def has_ssr_jsonld(raw_html: str, rendered_html: str | None) -> dict:
    raw_blocks = extract_jsonld(raw_html)
    rendered_blocks = extract_jsonld(rendered_html) if rendered_html else []
    return {
        "raw_count": len(raw_blocks),
        "rendered_count": len(rendered_blocks),
        "csr_only": len(raw_blocks) == 0 and len(rendered_blocks) > 0,
        "raw_types": [b.get("@type") for b in raw_blocks if isinstance(b, dict)],
        "rendered_types": [b.get("@type") for b in rendered_blocks if isinstance(b, dict)],
    }


def check_aggregaterating_grounded(jsonld_blocks: list[dict], visible_text: str) -> list[dict]:
    """检测 AggregateRating 是否对应页面可见评分"""
    issues = []
    for block in jsonld_blocks:
        if not isinstance(block, dict):
            continue
        ar = block.get("aggregateRating")
        if not ar:
            continue
        rating_value = str(ar.get("ratingValue", ""))
        review_count = str(ar.get("reviewCount", ""))
        # 检查可见文本是否出现这些值
        if rating_value and rating_value not in visible_text:
            issues.append({
                "field": "aggregateRating.ratingValue",
                "value": rating_value,
                "reason": "页面可见内容找不到该评分值",
            })
        if review_count and review_count not in visible_text:
            issues.append({
                "field": "aggregateRating.reviewCount",
                "value": review_count,
                "reason": "页面可见内容找不到该评论数",
            })
    return issues


def get_jsonld_field(blocks: list[dict], path: str) -> str | None:
    """提取 JSON-LD 字段，如 'author.name' / 'copyrightNotice.email'"""
    parts = path.split(".")
    for block in blocks:
        if not isinstance(block, dict):
            continue
        cur = block
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if cur is not None:
            return str(cur)
    return None
