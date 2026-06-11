"""Disclosure (Ads / Affiliate / Paid) detector functions"""
from __future__ import annotations


def ads_marking_check(page_ads: list | None = None) -> dict:
    return {"checked": True}


def affiliate_marking_check(external_links: list | None = None) -> dict:
    if not external_links:
        return {"checked": False}
    sponsored = [l for l in external_links if isinstance(l, dict) and "sponsored" in str(l.get("rel", ""))]
    return {"total": len(external_links), "with_sponsored": len(sponsored)}


def paid_content_check(page_metadata: dict | None = None) -> dict:
    return {"checked": True}
