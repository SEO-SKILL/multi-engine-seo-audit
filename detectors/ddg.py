"""DuckDuckGo detector functions"""
from __future__ import annotations


def tracker_count(resources: list | None = None) -> dict:
    tracker_domains = ["google-analytics", "googletagmanager", "facebook.net/tr", "doubleclick", "amazon-adsystem"]
    trackers = [r for r in (resources or []) if any(t in str(r).lower() for t in tracker_domains)]
    return {"tracker_count": len(trackers), "tracker_heavy": len(trackers) > 5}


def cookie_banner_check(first_screen: str | None = None) -> dict:
    text = (first_screen or "").lower()
    has_banner = any(k in text for k in ["cookie", "accept all", "gdpr", "consent"])
    return {"has_cookie_banner": has_banner}
