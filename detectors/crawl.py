"""Crawl & indexing detector functions"""
from __future__ import annotations


def soft_404_check(page_response: dict | None = None, content: str | None = None) -> dict:
    status = (page_response or {}).get("status_code", 200)
    text = (content or "").lower()
    soft_signals = ["not found", "page does not exist", "404"]
    return {"is_soft_404": status == 200 and any(s in text for s in soft_signals)}
