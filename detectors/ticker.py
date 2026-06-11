"""Ticker handling detector functions (Web3 specific)"""
from __future__ import annotations

from detectors.compliance import ticker_in_context


def context_match(visible_text: str, title: str | None = None, h1: str | None = None,
                  ticker_candidates: list | None = None, page_topic_classification: str | None = None) -> dict:
    return {"ticker_candidate_count": len(ticker_candidates or [])}


def is_linked(visible_text: str | None = None, dom_links: list | None = None) -> dict:
    return {"checked": True}
