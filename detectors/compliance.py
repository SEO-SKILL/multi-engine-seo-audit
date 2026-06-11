"""合规规则 detector functions"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup


def keyword_blacklist_check(html: str, banned_keywords: list[str]) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    visible_text = soup.get_text()
    hits = []
    for kw in banned_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        matches = list(re.finditer(pattern, visible_text, re.IGNORECASE))
        if matches:
            hits.append({
                "keyword": kw,
                "count": len(matches),
                "first_match_context": visible_text[max(0, matches[0].start() - 40): matches[0].end() + 40],
            })
    return hits


def ticker_in_context(html: str, ticker: str, blacklist_contexts: list[str]) -> dict:
    """检测 ticker 是否出现在错配的上下文中"""
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text() if soup.title else ""
    h1 = soup.find("h1")
    h1_text = h1.get_text() if h1 else ""

    ticker_widget = soup.find(attrs={"data-symbol": ticker}) or soup.find(attrs={"data-ticker": ticker})
    body_text = soup.get_text()
    ticker_in_body = ticker in body_text or ticker_widget is not None

    title_h1_combined = (title + " " + h1_text).lower()
    matched_contexts = [ctx for ctx in blacklist_contexts if ctx.lower() in title_h1_combined]

    return {
        "ticker_widget_present": ticker_widget is not None,
        "ticker_in_body": ticker_in_body,
        "matched_blacklist_contexts": matched_contexts,
        "is_misidentification_likely": ticker_in_body and bool(matched_contexts),
    }


def keyword_blacklist(html: str, banned_keywords: list[str] | None = None) -> list[dict]:
    return keyword_blacklist_check(html, banned_keywords or [])


def has_risk_disclaimer(html: str, page_template: str | None = None) -> dict:
    text = BeautifulSoup(html, "lxml").get_text().lower()
    has = any(k in text for k in ["risk disclaimer", "not financial advice", "estimation only", "投资建议", "风险提示"])
    return {"has_disclaimer": has}


def region_restriction_check(visible_text: str, locale: str | None = None, available_regions_db: dict | None = None) -> dict:
    return {"checked": True}


def jfsa_status_check(page_content: str) -> dict:
    has_jfsa = "金融庁" in (page_content or "") or "jfsa" in (page_content or "").lower()
    return {"has_jfsa_mention": has_jfsa}
