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
