"""User-Generated Content detector functions"""
from __future__ import annotations


def spam_pattern_check(user_content: str | None = None, user_links: list | None = None) -> dict:
    text = (user_content or "").lower()
    red_flags = ["viagra", "casino", "free movie", "watch online", "buy now cheap"]
    hits = [f for f in red_flags if f in text]
    return {"spam_hits": hits, "spam_suspect": len(hits) > 0}


def rel_ugc_check(user_links: list | None = None) -> dict:
    if not user_links:
        return {"checked": False, "no_ugc_links": True}
    with_rel = [l for l in user_links if isinstance(l, dict) and ("ugc" in str(l.get("rel", "")) or "nofollow" in str(l.get("rel", "")))]
    return {"total": len(user_links), "with_rel_ugc": len(with_rel), "passed": len(with_rel) == len(user_links)}


def moderation_signal_check(page_content: str | None = None) -> dict:
    text = (page_content or "").lower()
    has_signal = any(k in text for k in ["verified", "moderated", "已审核", "verified user"])
    return {"has_moderation_signal": has_signal}


def author_auth_check(user_metadata: dict | None = None) -> dict:
    return {"checked": True}
