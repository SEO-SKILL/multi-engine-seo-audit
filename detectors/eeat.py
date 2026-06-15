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


def author_signal(jsonld=None, visible_text=None, dom_metadata=None) -> dict:
    return detect_author_signals(visible_text or "")


def publication_dates(jsonld=None, visible_text=None, headers=None) -> dict:
    return detect_publication_dates(visible_text or "")


def author_profile_page_exists(author_name=None, author_url=None, fetched_author_page=None) -> dict:
    return {"requires_fetch": True, "url_given": bool(author_url)}


def author_bio_page_check(author_url=None, fetched_author_page=None) -> dict:
    return {"requires_fetch": True}


def author_social_check(author_metadata=None) -> dict:
    meta = author_metadata or {}
    has_social = any(k in str(meta).lower() for k in ["twitter", "linkedin", "github"])
    return {"has_social_link": has_social}


def reviewer_check(page_content=None, jsonld=None) -> dict:
    text = (page_content or "").lower()
    has_reviewed = "reviewed by" in text or "审核" in (page_content or "")
    has_schema = any(isinstance(b, dict) and b.get("reviewedBy") for b in (jsonld or []))
    return {"has_reviewer": has_reviewed or has_schema}


def ymyl_signal_check(visible_text=None, jsonld=None, author_metadata=None) -> dict:
    author = detect_author_signals(visible_text or "") if visible_text else {"ymyl_strong_signal": False}
    return {"author_score": author.get("author_signals_score", 0)}


def org_credentials_check(page_content=None, jsonld_organization=None, footer=None) -> dict:
    text = (page_content or "") + " " + (footer or "")
    has = any(k in text.lower() for k in ["address", "phone", "registered", "license"])
    return {"has_credentials": has}


def organization_signal_check(raw_html=None, jsonld_parsed=None, **_) -> dict:
    """首页/落地页 Organization 信号（about/contact + JSON-LD Organization）"""
    html = (raw_html or "").lower()
    has_about = "/about" in html or "关于我们" in (raw_html or "")
    has_contact = "/contact" in html or "/help" in html or "联系我们" in (raw_html or "")
    has_org_jsonld = False
    for item in (jsonld_parsed or []):
        if isinstance(item, dict):
            t = str(item.get("@type", ""))
            if "Organization" in t or "Corporation" in t:
                has_org_jsonld = True
                break
    score = sum([has_about, has_contact, has_org_jsonld])
    return {
        "has_about_link": has_about,
        "has_contact_link": has_contact,
        "has_organization_jsonld": has_org_jsonld,
        "org_signal_score": score,
        "suspect_weak_org_signal": score < 2,
    }
