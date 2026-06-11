"""GEO detector functions"""
from __future__ import annotations


def llms_txt_exists(domain=None) -> dict:
    return {"requires_external_fetch": True}


def content_freshness(date_modified=None, content_topic_volatility=None) -> dict:
    return {"date_modified": date_modified, "checked": True}


def citation_friendliness(visible_text=None, jsonld=None, structured_elements=None) -> dict:
    return {"checked": True, "text_len": len(visible_text or "")}


def brand_mention_count(visible_text=None) -> dict:
    count = (visible_text or "").lower().count("bydfi")
    return {"count": count}
