"""Redirect handling detector functions"""
from __future__ import annotations

import re


def status_check(redirect_history: list | None = None) -> dict:
    if not redirect_history:
        return {"has_redirects": False}
    return {"has_redirects": True, "chain_length": len(redirect_history)}


def meta_refresh_check(head_meta: dict | str | None = None) -> dict:
    text = str(head_meta or "")
    has_refresh = bool(re.search(r'http-equiv="refresh"', text, re.IGNORECASE))
    return {"has_meta_refresh": has_refresh, "passed": not has_refresh}


def js_redirect_check(raw_html: str) -> dict:
    patterns = [
        r"window\.location\s*=",
        r"window\.location\.href\s*=",
        r"window\.location\.replace\s*\(",
        r"location\.assign\s*\(",
    ]
    matches = [p for p in patterns if re.search(p, raw_html)]
    return {"js_redirect_patterns": matches, "has_js_redirect": len(matches) > 0}


def normalize_check(url_variants: list | None = None) -> dict:
    return {"checked": True}
