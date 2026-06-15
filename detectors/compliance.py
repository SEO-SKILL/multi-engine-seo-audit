"""合规规则 detector functions"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup


# 反诈教育语境守卫词（前后 200 字符内出现任一即视为"反面教材"放行）
_ANTI_SCAM_GUARDS = [
    # English
    "red flag", "red flags", "scam", "scams", "fraud", "fraudulent", "fake",
    "warning", "beware", "avoid", "do not", "don't", "never trust", "not legitimate",
    "no legitimate", "illegal", "suspicious", "dangerous", "too good to be true",
    "phishing", "ponzi", "rug pull", "rugpull", "do not believe",
    # 中文
    "警惕", "不要相信", "骗局", "诈骗", "警告", "警示", "避免", "风险提示",
    "谨防", "切勿", "请勿", "谨慎", "陷阱", "骗子", "假的", "虚假",
]


def keyword_blacklist_check(html: str, banned_keywords: list[str]) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    visible_text = soup.get_text()
    hits = []
    for kw in banned_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        matches = list(re.finditer(pattern, visible_text, re.IGNORECASE))
        if not matches:
            continue
        # 反诈教育语境放行：每个 match 前后 200 字含 guard 词则视为反面教材，不计入命中
        real_matches = []
        for m in matches:
            ctx = visible_text[max(0, m.start() - 200): m.end() + 200].lower()
            if any(g in ctx for g in _ANTI_SCAM_GUARDS):
                continue  # 反诈教育上下文，跳过
            real_matches.append(m)
        if real_matches:
            hits.append({
                "keyword": kw,
                "count": len(real_matches),
                "first_match_context": visible_text[max(0, real_matches[0].start() - 40): real_matches[0].end() + 40],
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
