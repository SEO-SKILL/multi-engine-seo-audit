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


# === AiRSearch 内容连贯性 ===
def content_coherence_check(visible_text: str | None = None, **_) -> dict:
    import re
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True}
    # 韩文句子（。 / 다. / 요.）
    sentences = re.split(r"[.!?\n。]|다\.|요\.", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    korean_sentences = [s for s in sentences if re.search(r"[\uac00-\ud7af]", s)]
    if len(korean_sentences) < 5:
        return {"insufficient_korean_content": True, "korean_sentence_count": len(korean_sentences)}
    avg_len = sum(len(s) for s in korean_sentences) / max(1, len(korean_sentences))
    very_short = sum(1 for s in korean_sentences if len(s) < 8) / len(korean_sentences)
    return {
        "korean_sentence_count": len(korean_sentences),
        "avg_sentence_length": round(avg_len, 1),
        "very_short_ratio": round(very_short, 2),
        "low_coherence_suspect": very_short > 0.4 or avg_len < 15,
    }


# === Smart Block（FAQPage / HowTo schema）===
def smart_block_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower().replace(" ", "")
    has_faqpage = '"@type":"faqpage"' in html or '"faqpage"' in html
    has_howto = '"@type":"howto"' in html or '"howto"' in html
    has_breadcrumb = '"@type":"breadcrumblist"' in html
    return {
        "has_faqpage_schema": has_faqpage,
        "has_howto_schema": has_howto,
        "has_breadcrumb_schema": has_breadcrumb,
        "passed": has_faqpage or has_howto or has_breadcrumb,
    }


# === Knowledge iN (지식인) 引用 ===
def knowledge_in_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    text = (visible_text or "") + " " + (raw_html or "")
    text_l = text.lower()
    has_kin_link = "kin.naver.com" in text_l
    has_kin_mention = "지식인" in text or "kin.naver" in text_l
    return {
        "has_kin_link": has_kin_link,
        "has_kin_mention": has_kin_mention,
        "passed": has_kin_link or has_kin_mention,
    }


# === Mobile-Friendly ===
def mobile_friendly_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_viewport = "<meta" in html and "viewport" in html and "width=device-width" in html
    return {"has_viewport_meta": has_viewport, "passed": has_viewport}


# === HTTPS ===
def https_check(page_url: str | None = None, **_) -> dict:
    return {"is_https": (page_url or "").startswith("https://"), "passed": (page_url or "").startswith("https://")}


# === Webmaster Tools 验证 ===
def webmaster_verification_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_naver_verify = "naver-site-verification" in html
    return {"has_naver_verification": has_naver_verify, "passed": has_naver_verify}
