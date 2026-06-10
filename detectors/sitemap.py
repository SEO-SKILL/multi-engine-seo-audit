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
    # 检测是否全部相同（假新鲜信号）
    lastmods = re.findall(r"<lastmod>(.+?)</lastmod>", xml_text)
    all_same = len(set(lastmods)) == 1 if lastmods else False
    return {"has_lastmod": has_lastmod, "all_same_date": all_same, "count": len(lastmods)}
