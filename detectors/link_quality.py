"""Link quality / backlink analysis detector functions (V2)"""
from __future__ import annotations

from collections import Counter


def anchor_text_distribution(internal_anchors: list[str]) -> dict:
    if not internal_anchors:
        return {"total": 0, "distribution": {}}
    counter = Counter(internal_anchors)
    total = len(internal_anchors)
    return {
        "total": total,
        "distribution": {a: c / total for a, c in counter.most_common(20)},
        "exact_match_ratio": max((c for _, c in counter.most_common(1)), default=0) / total,
    }


def link_velocity_check(backlink_history: list[dict]) -> dict:
    """检测外链增长速度突变"""
    if len(backlink_history) < 2:
        return {"sufficient_data": False}
    sorted_history = sorted(backlink_history, key=lambda x: x.get("date", ""))
    recent = sorted_history[-1]
    previous = sorted_history[-2]
    growth_rate = (recent.get("count", 0) - previous.get("count", 0)) / max(1, previous.get("count", 1))
    return {
        "growth_rate": growth_rate,
        "spike_suspicious": growth_rate > 0.5,
    }


def disavow_candidates(backlinks: list[dict]) -> list[dict]:
    """识别应该 disavow 的低质外链"""
    candidates = []
    red_flags = {
        "spam_score_above": 80,
        "domain_authority_below": 10,
        "language_mismatch": True,
        "irrelevant_topic": True,
    }
    for link in backlinks:
        flags = []
        if link.get("spam_score", 0) > red_flags["spam_score_above"]:
            flags.append("high_spam_score")
        if link.get("domain_authority", 100) < red_flags["domain_authority_below"]:
            flags.append("low_da")
        if flags:
            candidates.append({"url": link.get("url"), "reasons": flags})
    return candidates
