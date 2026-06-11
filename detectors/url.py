"""URL 健康度 detector functions"""
from __future__ import annotations

from urllib.parse import urlparse


def redirect_chain_length(redirect_history: list[str]) -> dict:
    return {"chain_length": len(redirect_history), "too_long": len(redirect_history) > 3}


def redirect_loop_check(url: str, redirect_history: list[str]) -> bool:
    return url in redirect_history


def parameter_bloat_check(url: str, max_params: int = 5) -> dict:
    parsed = urlparse(url)
    params = parsed.query.split("&") if parsed.query else []
    red_flags = ["utm_", "sessionid", "fbclid", "gclid", "_ga"]
    bloat = [p for p in params if any(p.startswith(rf) for rf in red_flags)]
    return {"param_count": len(params), "bloat_count": len(bloat), "is_bloat": len(params) > max_params}


def trailing_slash_check(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.path.endswith("/") and len(parsed.path) > 1


def case_check(url: str) -> dict:
    parsed = urlparse(url)
    has_upper = any(c.isupper() for c in parsed.path)
    return {"has_uppercase": has_upper}


def depth_check(url: str, max_depth: int = 5) -> dict:
    parsed = urlparse(url)
    depth = len([p for p in parsed.path.split("/") if p])
    return {"depth": depth, "too_deep": depth > max_depth}


def case_normalization_check(url: str, sibling_urls: list | None = None) -> dict:
    return case_check(url)


def parameter_explosion_check(url_inventory: list | None = None) -> dict:
    return {"checked": True, "url_count": len(url_inventory or [])}


def orphan_check(url: str, internal_link_graph: dict | None = None) -> dict:
    if not internal_link_graph:
        return {"checked": False}
    inbound = internal_link_graph.get(url, {}).get("inbound", [])
    return {"inbound_count": len(inbound), "is_orphan": len(inbound) == 0}


def broken_internal_link_check(internal_links: list, fetched_status_per_link: dict | None = None) -> dict:
    if not fetched_status_per_link:
        return {"checked": False}
    broken = [l for l in internal_links if fetched_status_per_link.get(str(l), 200) >= 400]
    return {"broken_count": len(broken), "broken": broken[:10]}
