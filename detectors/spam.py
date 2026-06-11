"""Spam pattern detector functions"""
from __future__ import annotations


def scaled_content_signals(page_inventory: list | None = None, content_similarity_matrix: dict | None = None, template_detection: dict | None = None) -> dict:
    return {"requires_full_site_corpus": True}
