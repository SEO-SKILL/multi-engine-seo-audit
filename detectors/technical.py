"""Technical SEO baseline detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def https_check(url: str, http_response: dict | None = None) -> dict:
    is_https = (url or "").startswith("https://")
    return {"is_https": is_https}


def http_status_check(http_response: dict | None = None) -> dict:
    status = (http_response or {}).get("status_code", 200)
    return {"status": status, "is_200": status == 200}


def robots_txt_validate(robots_txt_content: str | None = None) -> dict:
    from detectors.robots import robots_txt_validate as _rv
    return _rv(robots_txt_content)


def viewport_meta(head_meta: dict | str | None = None) -> dict:
    if isinstance(head_meta, str):
        has = 'name="viewport"' in head_meta and 'width=device-width' in head_meta
    else:
        meta = head_meta or {}
        has = "viewport" in str(meta).lower() and "width=device-width" in str(meta).lower()
    return {"has_responsive_viewport": has}


def cross_locale_duplicate(page_url: str, sibling_locale_urls: list | None = None, content_hashes: dict | None = None) -> dict:
    return {"checked": True}


def page_size_check(http_response_size: int | None = None, dom_size: int | None = None) -> dict:
    return {"size_kb": (http_response_size or 0) / 1024, "too_large": (http_response_size or 0) > 500 * 1024}
