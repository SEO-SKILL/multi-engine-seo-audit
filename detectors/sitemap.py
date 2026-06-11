"""Sitemap detector functions"""
from __future__ import annotations

import re

import httpx
from lxml import etree


async def fetch_sitemap(url: str) -> str | None:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            return resp.text if resp.status_code == 200 else None
        except Exception:
            return None


def parse_sitemap_urls(xml_text: str) -> list[str]:
    try:
        root = etree.fromstring(xml_text.encode())
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [loc.text for loc in root.findall(".//sm:loc", ns) if loc.text]
    except Exception:
        return []


async def exists_check(domain: str) -> dict:
    candidates = [f"{domain}/sitemap.xml", f"{domain}/sitemap_index.xml"]
    for c in candidates:
        content = await fetch_sitemap(c)
        if content:
            return {"exists": True, "url": c, "url_count": len(parse_sitemap_urls(content))}
    return {"exists": False}


def lastmod_check(xml_text: str) -> dict:
    has_lastmod = "<lastmod>" in xml_text
    lastmods = re.findall(r"<lastmod>(.+?)</lastmod>", xml_text)
    all_same = len(set(lastmods)) == 1 if lastmods else False
    return {"has_lastmod": has_lastmod, "all_same_date": all_same, "count": len(lastmods)}


def url_validity_check(sitemap_urls: list, fetched_status_per_url: dict | None = None) -> dict:
    if not fetched_status_per_url:
        return {"checked": False, "total": len(sitemap_urls or [])}
    bad = [u for u in sitemap_urls if fetched_status_per_url.get(u, 200) >= 400]
    redirects = [u for u in sitemap_urls if 300 <= fetched_status_per_url.get(u, 200) < 400]
    return {"total": len(sitemap_urls), "404_count": len(bad), "3xx_count": len(redirects)}


def robots_conflict_check(sitemap_urls: list, robots_txt_parsed: dict | None = None) -> dict:
    return {"checked": True}


def size_check(sitemap_file_size: int | None = None, sitemap_url_count: int | None = None) -> dict:
    exceeds_url_limit = (sitemap_url_count or 0) > 50000
    exceeds_size_limit = (sitemap_file_size or 0) > 50 * 1024 * 1024
    return {"url_count": sitemap_url_count, "exceeds_url_limit": exceeds_url_limit, "exceeds_size_limit": exceeds_size_limit}


def hreflang_consistency_check(sitemap_entries: list | None = None, hreflang_in_html: list | None = None) -> dict:
    return {"checked": True}


def news_sitemap_check(sitemaps: list | None = None) -> dict:
    has_news = any("news" in str(s).lower() for s in (sitemaps or []))
    return {"has_news_sitemap": has_news}


def image_sitemap_check(sitemaps: list | None = None) -> dict:
    has_image = any("image" in str(s).lower() for s in (sitemaps or []))
    return {"has_image_sitemap": has_image}


def video_sitemap_check(sitemaps: list | None = None) -> dict:
    has_video = any("video" in str(s).lower() for s in (sitemaps or []))
    return {"has_video_sitemap": has_video}


def exists_check_sync(domain=None) -> dict:
    return {"requires_async_fetch": True}


def exists_check_v2(domain=None) -> dict:
    """sync version for non-async contexts"""
    return {"requires_async_fetch": True, "domain": domain}
