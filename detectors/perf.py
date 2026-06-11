"""Performance detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def render_blocking_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    head = soup.find("head")
    if not head:
        return {"head_scripts": 0, "head_styles": 0}
    blocking_scripts = [s for s in head.find_all("script") if not s.get("async") and not s.get("defer") and s.get("src")]
    blocking_styles = [s for s in head.find_all("link", rel="stylesheet")]
    return {"head_scripts": len(blocking_scripts), "head_styles": len(blocking_styles)}


def compression_check(headers: dict) -> dict:
    encoding = headers.get("content-encoding", "") or headers.get("Content-Encoding", "")
    return {
        "encoding": encoding,
        "using_brotli": "br" in encoding.lower(),
        "using_gzip": "gzip" in encoding.lower(),
    }


def http_version_check(http_protocol: str | None) -> dict:
    return {"http_version": http_protocol, "is_http2_plus": http_protocol in ("HTTP/2", "HTTP/3", "h2", "h3")}


def page_size_check(html: str) -> dict:
    return {"html_size_kb": len(html.encode()) / 1024}


def ttfb_check(http_timing=None) -> dict:
    ttfb = (http_timing or {}).get("ttfb_ms", 0)
    return {"ttfb_ms": ttfb, "too_slow": ttfb > 800}


def minification_check(resources=None) -> dict:
    return {"checked": True}
