"""Google Discover detector functions"""
from __future__ import annotations


def eligibility_check(page_url: str | None = None, jsonld: list | None = None, content_quality: dict | None = None, image_quality: dict | None = None) -> dict:
    has_article = any(isinstance(b, dict) and b.get("@type") in ("Article", "NewsArticle") for b in (jsonld or []))
    return {"has_article_schema": has_article}


def image_size_check(page_images: list | None = None) -> dict:
    return {"checked": True, "requires_image_dimensions": True}
