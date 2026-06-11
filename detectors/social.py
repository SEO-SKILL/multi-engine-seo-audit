"""Open Graph / Twitter Card detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def og_tags_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    og = {}
    for meta in soup.find_all("meta", property=lambda p: p and p.startswith("og:")):
        og[meta["property"][3:]] = meta.get("content")
    required = ["title", "type", "image", "url"]
    missing = [r for r in required if r not in og]
    return {"og_tags": og, "missing_required": missing, "complete": not missing}


def twitter_card_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    twitter = {}
    for meta in soup.find_all("meta", attrs={"name": lambda n: n and n.startswith("twitter:")}):
        twitter[meta["name"][8:]] = meta.get("content")
    has_card = "card" in twitter
    return {"twitter_tags": twitter, "has_card": has_card}


def og_image_size_check(og_image_url: str | None) -> dict:
    if not og_image_url:
        return {"present": False}
    return {"present": True, "url": og_image_url, "needs_dimension_check": True}


def share_button_check(dom_buttons: list | None = None) -> dict:
    return {"checked": True, "button_count": len(dom_buttons or [])}
