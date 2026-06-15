"""
规则作用域推断
区分"单 URL 能跑"vs"必须 batch / 跨页 / 外部抓取"
"""
from __future__ import annotations

# 检测器输入中出现以下字段 = 需跨页/多 locale 抓取
CROSS_PAGE_INPUTS = {
    "page_corpus",
    "sibling_urls",
    "fetched_status_per_alternate",
    "fetched_alternate_hreflang",
    "fetched_alternate_content",
    "canonical_per_alternate",
    "competitor_pages",
    "date_modified_history",
    "content_hash_history",
}

# 必须外部 SaaS / GSC / Lighthouse 实测
EXTERNAL_INPUTS = {
    "lighthouse_report",
    "crux_data",
    "search_console_data",
    "ga_data",
    "log_files",
}


def scope_requirement(rule: dict) -> str | None:
    """返回 'cross_page' | 'external' | None"""
    det = rule.get("detector", {}) or {}
    inputs = set(det.get("inputs", []) or [])
    if inputs & CROSS_PAGE_INPUTS:
        return "cross_page"
    if inputs & EXTERNAL_INPUTS:
        return "external"
    return None


SCOPE_LABELS = {
    "cross_page": "需 batch / 全站抓取才能验证（单页 audit 跳过）",
    "external": "需外部数据源（GSC / Lighthouse / CrUX），单页 audit 跳过",
}


def collect_skipped_rules(rules_map: dict, page_type: str | None = None,
                         platforms: set[str] | None = None,
                         min_severity: set[str] | None = None) -> list[dict]:
    """收集本次 audit 因 scope 无法验证、但若 batch 模式下会触发的规则。

    只列「与本页类型相关 + 严重度 ≥ medium」的，避免淹没。
    """
    from _page_type import is_rule_applicable
    min_severity = min_severity or {"blocker", "high", "medium"}

    out = []
    for rid, rule in rules_map.items():
        scope = scope_requirement(rule)
        if not scope:
            continue
        if rule.get("severity") not in min_severity:
            continue
        if page_type and not is_rule_applicable(rule, page_type):
            continue
        if platforms:
            rp = (rule.get("applies_to", {}) or {}).get("platforms", []) or []
            if rp and not (set(rp) & platforms):
                continue
        out.append({
            "id": rid,
            "severity": rule.get("severity"),
            "scope": scope,
            "scope_label": SCOPE_LABELS[scope],
            "source_url": rule.get("source_url") or rule.get("source"),
            "bydfi_impact": (rule.get("bydfi_business_impact") or "").strip()[:200],
        })
    out.sort(key=lambda r: ({"blocker":0,"high":1,"medium":2}.get(r["severity"],3),))
    return out
