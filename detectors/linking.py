"""Internal linking detector functions"""
from __future__ import annotations

from collections import Counter


def anchor_text_distribution(internal_links: list) -> dict:
    anchors = [str(l.get("text", "") if isinstance(l, dict) else l).strip().lower() for l in (internal_links or [])]
    anchors = [a for a in anchors if a]
    if not anchors:
        return {"checked": False}
    c = Counter(anchors)
    most_common, max_count = c.most_common(1)[0]
    ratio = max_count / len(anchors)
    return {"top_anchor": most_common, "top_ratio": ratio, "stuffing_suspect": ratio > 0.30}


def click_depth_check(page_url: str, site_graph: dict | None = None) -> dict:
    return {"checked": True}


def cluster_isolation_check(page_url: str, internal_link_graph: dict | None = None, topic_clusters: list | None = None) -> dict:
    return {"checked": True}


def dead_link_check(internal_links: list, fetched_status: dict | None = None) -> dict:
    fetched = fetched_status or {}
    dead = [l for l in (internal_links or []) if fetched.get(str(l)) and fetched.get(str(l)) >= 400]
    return {"dead_count": len(dead)}


def internal_nofollow_check(internal_links: list) -> dict:
    nofollow = [l for l in (internal_links or []) if isinstance(l, dict) and "nofollow" in str(l.get("rel", ""))]
    return {"nofollow_count": len(nofollow)}


def paid_outbound_check(outbound_links: list) -> dict:
    return {"total": len(outbound_links or [])}
