"""Content quality detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def has_data_tables(dom_tables: list | None = None) -> dict:
    if isinstance(dom_tables, list):
        return {"table_count": len(dom_tables), "has_table": len(dom_tables) > 0}
    return {"checked": False}


def republished_originality_check(visible_text: str, canonical_url: str | None = None, external_source_url: str | None = None, source_article_text: str | None = None) -> dict:
    if not external_source_url or not source_article_text:
        return {"is_republished": False}
    if not visible_text:
        return {"checked": False}
    common = sum(1 for w in source_article_text.split() if w in visible_text)
    similarity = common / max(1, len(source_article_text.split()))
    return {"is_republished": True, "similarity": similarity, "low_increment": similarity > 0.7}
