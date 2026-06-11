"""Content Pruning detector functions"""
from __future__ import annotations


def merge_candidate_check(page_inventory: list | None = None) -> dict:
    return {"requires_full_site_corpus": True}
