"""Japan-specific (Yahoo Japan / JFSA) detector functions"""
from __future__ import annotations

import re

JFSA_KEYWORDS = [
    "金融庁", "JFSA", "Financial Services Agency",
    "暗号資産交換業", "暗号資産交換業者",
    "関東財務局長", "fsa.go.jp",
]

NON_JFSA_DISCLOSURE = [
    "未登録", "登録していません", "未登録業者", "海外取引所",
    "not registered", "not licensed in japan",
]

JP_PAYMENT_METHODS = [
    "paypay", "ペイペイ", "linepay", "ラインペイ", "merpay", "メルペイ",
    "bankjp", "銀行振込", "コンビニ", "セブン銀行", "三井住友",
    "三菱ufj", "みずほ", "ゆうちょ", "auじぶん銀行",
]


def japanese_authenticity(visible_text: str) -> dict:
    text = visible_text or ""
    hiragana = len(re.findall(r"[\u3040-\u309f]", text))
    katakana = len(re.findall(r"[\u30a0-\u30ff]", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    has_jpy = "JPY" in text or "円" in text or "¥" in text
    total_jp = hiragana + katakana
    return {
        "hiragana_chars": hiragana,
        "katakana_chars": katakana,
        "cjk_chars": cjk,
        "has_jpy_mention": has_jpy,
        "passed": total_jp >= 20,
    }


def jfsa_disclosure_check(page_content: str | None = None) -> dict:
    text = (page_content or "")
    text_l = text.lower()
    has_jfsa = any(k.lower() in text_l for k in JFSA_KEYWORDS) or "金融庁" in text
    has_disclosure = any(k.lower() in text_l for k in NON_JFSA_DISCLOSURE) or "未登録" in text
    return {
        "has_jfsa_mention": has_jfsa,
        "discloses_non_registration": has_disclosure,
        "passed": has_jfsa or has_disclosure,
    }


def payment_method_check(page_content: str | None = None) -> dict:
    text = (page_content or "").lower()
    methods = [m for m in JP_PAYMENT_METHODS if m.lower() in text]
    return {
        "japanese_payment_methods": methods,
        "passed": len(methods) >= 1,
    }


def tax_disclosure_check(page_content: str | None = None) -> dict:
    text = page_content or ""
    has_tax_rate = "20.315" in text
    has_tax_term = "総合課税" in text or "確定申告" in text
    return {
        "mentions_jp_tax_rate": has_tax_rate,
        "mentions_jp_tax_filing": has_tax_term,
        "passed": has_tax_rate or has_tax_term,
    }


JP_AUTHORITY_SOURCES = [
    "ロイター", "Reuters", "日経", "Nikkei", "Bloomberg", "ブルームバーグ",
    "朝日新聞", "毎日新聞", "読売新聞", "産経新聞", "NHK", "TBS",
    "金融庁", "日本銀行", "Bank of Japan", "JFSA",
]


def news_source_citation_check(visible_text: str | None = None, raw_html: str | None = None, **_) -> dict:
    text = (visible_text or "") + " " + (raw_html or "")
    hits = [s for s in JP_AUTHORITY_SOURCES if s in text]
    return {
        "authority_sources_cited": hits[:5],
        "citation_count": len(hits),
        "passed": len(hits) >= 1,
    }


def jp_tld_or_cdn_check(page_url: str | None = None, http_headers: dict | None = None, **_) -> dict:
    url = page_url or ""
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc if url else ""
    is_jp_tld = netloc.endswith(".jp") or netloc.endswith(".co.jp")
    headers = http_headers or {}
    cf_country = (headers.get("cf-ipcountry") or "").upper()
    has_jp_cdn = cf_country == "JP"
    return {
        "is_jp_tld": is_jp_tld,
        "has_jp_cdn": has_jp_cdn,
        "passed": is_jp_tld or has_jp_cdn,
    }


def qa_schema_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_qapage = '"qapage"' in html or '"@type":"qapage"' in html.replace(" ", "")
    has_faqpage = '"faqpage"' in html or '"@type":"faqpage"' in html.replace(" ", "")
    return {
        "has_qapage_schema": has_qapage,
        "has_faqpage_schema": has_faqpage,
        "passed": has_qapage or has_faqpage,
    }


def mobile_responsive_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_viewport = "<meta" in html and "viewport" in html and "width=device-width" in html
    has_responsive = "@media" in html or "responsive" in html
    return {
        "has_viewport_meta": has_viewport,
        "has_responsive_css": has_responsive,
        "passed": has_viewport,
    }


def honorific_consistency_check(visible_text: str | None = None, **_) -> dict:
    """日文敬语等级一致性检测（です・ます调 vs だ・である调）"""
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True}
    desumasu = len(re.findall(r"です[。、 \n]|ます[。、 \n]|ました[。、 \n]|でしょう", text))
    dakana = len(re.findall(r"だ[。、 \n]|である[。、 \n]|だろう|であろう", text))
    total = desumasu + dakana
    if total < 10:
        return {"insufficient_signals": True, "desumasu": desumasu, "dakana": dakana}
    mix_ratio = min(desumasu, dakana) / total
    return {
        "desumasu_count": desumasu,
        "dakana_count": dakana,
        "mix_ratio": round(mix_ratio, 2),
        "mixed_honorific_suspect": mix_ratio > 0.20,
    }
