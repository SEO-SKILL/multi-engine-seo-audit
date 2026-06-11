"""Naver Search detector functions"""
from __future__ import annotations


def korean_authenticity(visible_text: str, locale: str | None = None, machine_translation_signals: dict | None = None) -> dict:
    import re
    has_korean = bool(re.search(r"[\uac00-\ud7af]", visible_text))
    has_krw = "KRW" in visible_text or "원" in visible_text
    return {"has_korean_chars": has_korean, "has_krw_mention": has_krw, "passed": has_korean}


def creator_authority_check(author_metadata: dict | None = None, author_history_data: dict | None = None, naver_blog_signals: dict | None = None) -> dict:
    return {"checked": True}


def topic_focus_check(site_recent_content_topics: list | None = None) -> dict:
    return {"checked": True}


def engagement_signals_check(naver_webmaster_data: dict | None = None, ga_data: dict | None = None) -> dict:
    return {"requires_external_data": True}


def ecosystem_links_check(outbound_links: list | None = None) -> dict:
    has_naver = any("naver.com" in str(l) for l in (outbound_links or []))
    return {"has_naver_ecosystem_link": has_naver}


def serving_region_check(http_headers: dict | None = None, cdn_region: str | None = None) -> dict:
    server = (http_headers or {}).get("server", "").lower()
    is_korea = "korea" in (cdn_region or "").lower() or "kr" in (cdn_region or "").lower()
    return {"served_from_korea": is_korea}


def brand_presence_check(brand_name: str | None = None) -> dict:
    return {"requires_external_api": True}


def korean_payment_check(html: str) -> dict:
    text = html.lower() if html else ""
    methods = [m for m in ["kakaopay", "tosspay", "naverpay", "samsungpay", "카카오페이", "토스"] if m in text]
    return {"korean_payment_methods": methods, "passed": len(methods) >= 1}


def korean_ecosystem_links(outbound_links: list | None = None, content_references: list | None = None) -> dict:
    refs = [r for r in (content_references or []) if any(k in str(r).lower() for k in ["upbit", "bithumb", "kakao"])]
    return {"korean_ecosystem_refs": refs}


def character_consistency(visible_text: str) -> dict:
    import re
    korean_chars = len(re.findall(r"[\uac00-\ud7af]", visible_text))
    cjk_other = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", visible_text))
    total = max(1, korean_chars + cjk_other)
    mixed = cjk_other / total > 0.10 if korean_chars > 100 else False
    return {"korean_chars": korean_chars, "cjk_other": cjk_other, "mixed_script_suspect": mixed}
