"""Site search detector functions"""
from __future__ import annotations


def indexability_check(url_pattern: str, meta_robots: dict | None = None) -> dict:
    is_search = "/search" in (url_pattern or "") or "?q=" in (url_pattern or "")
    is_noindex = (meta_robots or {}).get("noindex", False)
    return {"is_search_url": is_search, "noindex": is_noindex, "passed": not is_search or is_noindex}


def faceted_navigation_check(url_inventory: list | None = None) -> dict:
    return {"requires_full_site_corpus": True}
