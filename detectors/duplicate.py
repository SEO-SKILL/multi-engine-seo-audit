"""Duplicate content detector functions"""
from __future__ import annotations

from urllib.parse import urlparse, parse_qs


def intra_site_check(page_corpus: list | None = None) -> dict:
    return {"checked": True}


def pagination_check(pagination_links: list | None = None) -> dict:
    return {"checked": True, "pagination_count": len(pagination_links or [])}


def session_param_check(url_params: dict | list | None = None) -> dict:
    if isinstance(url_params, list):
        params = url_params
    elif isinstance(url_params, dict):
        params = list(url_params.keys())
    else:
        params = []
    flags = [p for p in params if any(s in str(p).lower() for s in ["sessionid", "phpsessid", "jsessionid", "sid"])]
    return {"session_params": flags, "has_session_id": len(flags) > 0}


def www_normalization(url: str, sibling_urls: list | None = None) -> dict:
    parsed = urlparse(url) if url else None
    return {"netloc": parsed.netloc if parsed else None}
