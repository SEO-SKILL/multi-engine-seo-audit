"""Bing Search detector functions"""
from __future__ import annotations


def webmaster_verification_check(domain: str, dns_records: dict | None = None, html_meta: dict | None = None) -> dict:
    meta = html_meta or {}
    has_msvalidate = "msvalidate.01" in str(meta)
    return {"has_bing_verification": has_msvalidate}


def indexnow_setup_check(domain: str, indexnow_key_file: str | None = None) -> dict:
    return {"checked": True, "key_file_present": bool(indexnow_key_file)}


def title_quality(title: str, target_keyword: str | None = None) -> dict:
    if not title:
        return {"passed": False, "reason": "no title"}
    length = len(title)
    too_long = length > 65
    too_short = length < 30
    return {"length": length, "too_long": too_long, "too_short": too_short, "passed": not too_long and not too_short}


def media_richness(images: list | None = None, videos: list | None = None, infographics: list | None = None) -> dict:
    img_count = len(images or [])
    vid_count = len(videos or [])
    return {"image_count": img_count, "video_count": vid_count, "media_rich": img_count + vid_count >= 2}


def url_keyword_match(url: str, primary_keyword: str | None = None) -> dict:
    if not primary_keyword:
        return {"checked": False}
    kw_in_url = primary_keyword.lower().replace(" ", "-") in (url or "").lower()
    return {"keyword_in_url": kw_in_url, "passed": kw_in_url}


# === Bing Image Pack ===
def image_pack_check(raw_html: str | None = None, **_) -> dict:
    import re
    html = raw_html or ""
    img_tags = re.findall(r"<img[^>]+>", html, re.IGNORECASE)
    if not img_tags:
        return {"image_count": 0, "alt_coverage": 0, "passed": True}
    with_alt = sum(1 for t in img_tags if re.search(r'\balt\s*=\s*["\'][^"\']+["\']', t, re.IGNORECASE))
    bad_filenames = sum(1 for t in img_tags
                       if re.search(r'src=["\'][^"\']*(?:img_\d|image\d|dsc_\d|p\d{3,}|untitled)', t, re.IGNORECASE))
    return {
        "image_count": len(img_tags),
        "alt_coverage": round(with_alt / max(1, len(img_tags)), 2),
        "bad_filename_count": bad_filenames,
        "passed": with_alt / max(1, len(img_tags)) >= 0.8 and bad_filenames < 3,
    }


# === Bing News Publisher ===
def news_publisher_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_newsarticle = '"newsarticle"' in html or '"@type":"newsarticle"' in html.replace(" ", "")
    has_article = '"article"' in html or '"@type":"article"' in html.replace(" ", "")
    has_publisher = '"publisher"' in html
    has_dateline = bool(visible_text and any(k in (visible_text or "") for k in ["发布于", "Published", "更新时间", "Last updated"]))
    return {
        "has_newsarticle_schema": has_newsarticle,
        "has_article_schema": has_article,
        "has_publisher": has_publisher,
        "has_dateline": has_dateline,
        "passed": (has_newsarticle or has_article) and has_publisher,
    }


# === Bing Trust Signals ===
def trust_signals_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    text = (visible_text or "") + " " + (raw_html or "")
    text_l = text.lower()
    signals = {
        "has_contact": any(k in text_l for k in ["contact us", "联系我们", "kontakt", "связаться"]),
        "has_about": any(k in text_l for k in ["about us", "about-us", "关于我们", "о компании"]),
        "has_legal": any(k in text_l for k in ["terms", "privacy", "/legal", "条款", "隐私"]),
        "has_address": bool(any(k in text_l for k in ["address:", "office:", "headquartered", "总部", "地址"])),
        "has_phone_or_email": bool("@" in text and "." in text),
    }
    score = sum(1 for v in signals.values() if v)
    return {"signals": signals, "trust_score": score, "weak_trust": score < 3}


# === Bing Mobile-Friendly ===
def mobile_friendly_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_viewport = "<meta" in html and "viewport" in html and "width=device-width" in html
    return {"has_viewport_meta": has_viewport, "passed": has_viewport}


# === Bing HTTPS ===
def https_check(page_url: str | None = None, **_) -> dict:
    return {"is_https": (page_url or "").startswith("https://"), "passed": (page_url or "").startswith("https://")}
