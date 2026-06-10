"""E-E-A-T 相关 detector functions"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from detectors.schema import extract_jsonld, get_jsonld_field


def detect_author_signals(html: str) -> dict:
    """检测页面是否有作者信号"""
    soup = BeautifulSoup(html, "lxml")
    blocks = extract_jsonld(html)

    author_jsonld_name = get_jsonld_field(blocks, "author.name")
    author_jsonld_url = get_jsonld_field(blocks, "author.url")
    meta_author = soup.find("meta", attrs={"name": "author"})
    byline = soup.select_one(".byline, .author-name, [rel='author']")

    return {
        "has_jsonld_author_name": bool(author_jsonld_name),
        "has_jsonld_author_url": bool(author_jsonld_url),
        "has_meta_author": meta_author is not None,
        "has_visible_byline": byline is not None,
        "author_signals_score": sum([
            bool(author_jsonld_name),
            bool(author_jsonld_url),
            meta_author is not None,
            byline is not None,
        ]) / 4.0,
    }


def detect_publication_dates(html: str) -> dict:
    blocks = extract_jsonld(html)
    return {
        "datePublished": get_jsonld_field(blocks, "datePublished"),
        "dateModified": get_jsonld_field(blocks, "dateModified"),
        "has_visible_date": bool(re.search(r"\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}", BeautifulSoup(html, "lxml").get_text())),
    }


def detect_risk_disclaimer(html: str, templates: list[str]) -> dict:
    soup = BeautifulSoup(html, "lxml")
    visible_text = soup.get_text().lower()
    matches = []
    for template in templates:
        # 简化匹配：检查 5+ 关键词重叠
        keywords = [w.lower() for w in template.split() if len(w) > 3]
        overlap = sum(1 for kw in keywords if kw in visible_text)
        if overlap >= 5:
            matches.append({"template_preview": template[:100], "overlap_keywords": overlap})
    return {
        "has_disclaimer": len(matches) > 0,
        "matches": matches,
    }
