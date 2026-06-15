"""Yandex Search detector functions"""
from __future__ import annotations

import re


def metrica_check(html_scripts: list | str) -> dict:
    text = " ".join(str(s) for s in html_scripts) if isinstance(html_scripts, list) else str(html_scripts)
    has_metrica = "mc.yandex.ru/metrika" in text or "yandex_metrika" in text
    return {"has_yandex_metrica": has_metrica, "passed": has_metrica}


def webmaster_verification_check(domain: str, dns_records: dict | None = None, html_meta: dict | None = None) -> dict:
    return {"requires_external_check": True}


def russian_authenticity(visible_text: str, locale: str | None = None, machine_translation_signals: dict | None = None) -> dict:
    has_cyrillic = bool(re.search(r"[а-яА-Я]", visible_text))
    has_rub = "RUB" in visible_text or "рубл" in visible_text.lower()
    return {"has_cyrillic": has_cyrillic, "has_rub_mention": has_rub, "passed": has_cyrillic}


def serving_region_check(http_headers: dict | None = None, cdn_region: str | None = None, ip_geolocation: str | None = None) -> dict:
    is_russia = "russia" in (cdn_region or "").lower() or "ru" == (ip_geolocation or "").lower()
    return {"served_from_russia": is_russia}


def title_russian_quality(title: str, target_keyword_ru: str | None = None) -> dict:
    cyrillic_count = len(re.findall(r"[а-яА-Я]", title or ""))
    in_first_60 = (target_keyword_ru or "") in (title or "")[:60] if target_keyword_ru else True
    return {"cyrillic_chars": cyrillic_count, "keyword_in_first_60": in_first_60}


def tld_check(domain: str) -> dict:
    return {"tld": domain.split(".")[-1] if domain else "", "is_ru_tld": domain.endswith(".ru") if domain else False}


def russian_contact_check(page_content: str) -> dict:
    has_ru_phone = bool(re.search(r"\+7", page_content or ""))
    return {"has_russian_phone": has_ru_phone}


def geo_meta_check(head_meta: dict | None = None) -> dict:
    meta = head_meta or {}
    has_geo = "geo.region" in str(meta) or "geo.position" in str(meta)
    return {"has_geo_meta": has_geo}


def cdn_check(http_headers: dict | None = None, cdn_region: str | None = None) -> dict:
    return {"cdn_region": cdn_region}


def anchor_overoptimization(internal_links: list) -> dict:
    from collections import Counter
    anchors = [str(l.get("text", "")).strip().lower() for l in (internal_links or []) if isinstance(l, dict)]
    if not anchors:
        return {"over_optimized": False}
    c = Counter(anchors)
    top_ratio = c.most_common(1)[0][1] / len(anchors) if anchors else 0
    return {"top_anchor_ratio": top_ratio, "over_optimized": top_ratio > 0.30}


# === AGS 算法：自动生成 / 采集内容检测 ===
def auto_generated_content_check(visible_text: str | None = None, **_) -> dict:
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True}
    sentences = re.split(r"[.!?\n]", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 5:
        return {"insufficient_content": True, "sentence_count": len(sentences)}
    avg_len = sum(len(s) for s in sentences) / max(1, len(sentences))
    short_ratio = sum(1 for s in sentences if len(s) < 20) / len(sentences)
    return {
        "sentence_count": len(sentences),
        "avg_sentence_length": round(avg_len, 1),
        "short_sentence_ratio": round(short_ratio, 2),
        "suspect_auto_generated": short_ratio > 0.55 and avg_len < 30,
    }


# === Minusinsk 算法：垃圾外链 ===
def spam_backlinks_check(outbound_links: list | None = None, **_) -> dict:
    from collections import Counter
    from urllib.parse import urlparse
    links = outbound_links or []
    if not links:
        return {"link_count": 0, "spam_detected": False}
    domains = [urlparse(l["href"] if isinstance(l, dict) else str(l)).netloc for l in links]
    counts = Counter(domains)
    top_ratio = (counts.most_common(1)[0][1] / max(1, len(domains))) if counts else 0
    spam_anchors = ["казино", "ставки", "купить", "займ", "промокод"]
    spam_hits = sum(1 for l in links if isinstance(l, dict) and any(s in (l.get("text") or "").lower() for s in spam_anchors))
    return {
        "link_count": len(links),
        "top_domain_ratio": round(top_ratio, 2),
        "spam_anchor_hits": spam_hits,
        "spam_detected": top_ratio > 0.4 or spam_hits >= 2,
    }


# === Madrid 算法：商业 trust 信号 ===
def commercial_trust_check(visible_text: str | None = None, raw_html: str | None = None, **_) -> dict:
    text = (visible_text or "") + " " + (raw_html or "")
    text_l = text.lower()
    signals = {
        "has_phone": bool(re.search(r"\+7[\s\(\)\-\d]{10,}", text)),
        "has_email": "@" in text and re.search(r"[\w\.]+@[\w\.]+\.\w+", text) is not None,
        "has_address": any(k in text for k in ["ул.", "пр.", "Москва", "Россия", "Russia", "Moscow"]),
        "has_legal_entity": any(k in text for k in ["ООО", "ОАО", "ЗАО", "ИП ", "LLC", "Ltd"]),
        "has_terms": any(k in text_l for k in ["условия", "terms", "соглашение", "agreement"]),
    }
    score = sum(1 for v in signals.values() if v)
    return {"signals": signals, "trust_score": score, "weak_trust": score < 2}


# === Mobile-Friendly 检测 ===
def mobile_friendly_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_viewport = "<meta" in html and "viewport" in html and "width=device-width" in html
    has_responsive = "@media" in html or "responsive" in html
    return {
        "has_viewport_meta": has_viewport,
        "has_responsive_css": has_responsive,
        "mobile_friendly": has_viewport,
    }


# === HTTPS 检测 ===
def https_check(page_url: str | None = None, **_) -> dict:
    url = page_url or ""
    is_https = url.startswith("https://")
    return {"is_https": is_https, "passed": is_https}
