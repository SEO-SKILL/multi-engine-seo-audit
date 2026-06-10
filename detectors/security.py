"""Security headers + mixed content detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def mixed_content_check(html: str, page_url: str) -> dict:
    if not page_url.startswith("https://"):
        return {"page_https": False, "mixed_resources": []}
    soup = BeautifulSoup(html, "lxml")
    mixed = []
    for tag, attr in [("img", "src"), ("script", "src"), ("link", "href"), ("iframe", "src")]:
        for el in soup.find_all(tag):
            url = el.get(attr, "")
            if url.startswith("http://"):
                mixed.append({"tag": tag, "url": url})
    return {"page_https": True, "mixed_resources": mixed, "has_mixed": len(mixed) > 0}


def hsts_header_check(headers: dict) -> dict:
    hsts = headers.get("strict-transport-security") or headers.get("Strict-Transport-Security")
    if not hsts:
        return {"present": False}
    return {"present": True, "value": hsts, "has_preload": "preload" in hsts.lower()}


def csp_check(headers: dict) -> dict:
    csp = headers.get("content-security-policy") or headers.get("Content-Security-Policy")
    return {"present": bool(csp), "value": csp}
