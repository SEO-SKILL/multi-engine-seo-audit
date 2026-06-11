"""Keyword strategy detector functions"""
from __future__ import annotations

import re
from collections import Counter


def density_check(visible_text: str, target_keyword: str | None = None) -> dict:
    if not target_keyword or not visible_text:
        return {"checked": False}
    words = visible_text.lower().split()
    total = len(words)
    kw_count = visible_text.lower().count(target_keyword.lower())
    density = kw_count / max(1, total)
    return {"density": density, "too_low": density < 0.005, "too_high": density > 0.025}


def title_position_check(title: str, target_keyword: str | None = None) -> dict:
    if not target_keyword or not title:
        return {"checked": False}
    position = title.lower().find(target_keyword.lower())
    in_first_60 = 0 <= position < 60
    return {"position": position, "in_first_60_chars": in_first_60}


def cannibalization_check(page_inventory: list | None = None, target_keyword: str | None = None) -> dict:
    return {"checked": True, "requires_site_corpus": True}
