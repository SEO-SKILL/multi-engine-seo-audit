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
