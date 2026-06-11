"""Tagging / taxonomy detector functions"""
from __future__ import annotations


def topic_match_check(visible_text: str, tags_assigned: list | None = None, page_topic_classification: str | None = None, source_article_tags: list | None = None) -> dict:
    return {"checked": True, "requires_llm_classification": True}


def tag_page_quality_check(tag_page_url: str, indexed_articles: list | None = None, content_consistency: float | None = None) -> dict:
    article_count = len(indexed_articles or [])
    return {"article_count": article_count, "indexable": article_count >= 5}
