"""Google News detector functions"""
from __future__ import annotations


def byline_clickable(dom_links: list | None = None) -> dict:
    return {"checked": True}


def review_freshness_check(jsonld: list | None = None) -> dict:
    has_date_modified = any(isinstance(b, dict) and b.get("dateModified") for b in (jsonld or []))
    return {"has_date_modified": has_date_modified}
