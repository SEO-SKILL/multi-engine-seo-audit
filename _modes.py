"""
守门员 vs 优化 模式分类
基于 Google 官方文档的严格度区分
"""
from __future__ import annotations

# 守门员规则前缀（违反 = Google manual action 风险）
GATEKEEPER_RULE_PREFIXES = {
    # 某加密交易所行业案例 7 类（防复发）
    "platform.l01", "platform.l02", "platform.l05",
    # Platform 合规硬要求
    "example.compliance.banned-keywords",
    "example.compliance.risk-disclaimer-required",
    "example.compliance.region-restricted-content",
    "example.compliance.us-sec",
    "example.compliance.eu-mica",
    "example.compliance.jp-jfsa",
    "example.compliance.sg-mas",
    "example.compliance.hk-sfc",
    # Google 官方 manual action 同类
    "google.manual-action",
    "google.cloaking",
    "google.schema.field-not-grounded",
    "google.schema.jsonld-csr-only",
    "google.schema.aggregaterating-without",
    "google.schema.relatedlink-topic-mismatch",
    "google.canonical.self-canonical-on-republished",
    "google.canonical.missing",
    "google.canonical.points-to-noindex",
    "google.hreflang.alternate-blocked-by-robots",
    "google.hreflang.alternate-returns-404",
    "google.robots.noindex-on-critical",
    "google.robots.conflicting-directives",
    # Security
    "shared.security.hacked-content",
    "shared.security.mixed-content",
    "shared.security.ssl-expiry",
    # Spam policy
    "google.eeat.fake-freshness-pattern",
    "google.spam-update",
    # 隐藏文字 / 关键词堆砌
    "google.manual-action.hidden-text",
    "google.manual-action.keyword-stuffing",
}


def classify_rule(rule_id: str, severity: str = "low", tags: list[str] | None = None,
                  page_type: str | None = None, rule_applies_to: dict | None = None) -> str:
    """根据 rule_id + severity + tags + page_type 判定模式

    Returns: 'gatekeeper' | 'optimizer'

    page_type 二元守门：即使 rule_id 在 GATEKEEPER 前缀里，若 applies_to.page_types
    不覆盖当前 page_type，则降级为 optimizer（避免首页被误判 EEAT 必修）。
    """
    tags = tags or []

    def _page_type_blocks_gatekeeper() -> bool:
        if not page_type or page_type == "unknown" or not rule_applies_to:
            return False
        pts = (rule_applies_to.get("page_types") or [])
        if not pts or "all" in pts:
            return False
        return page_type not in pts

    # 任何 blocker 都是守门员（compliance/security 兜底，page_type 不放过）
    if severity == "blocker":
        return "gatekeeper"

    # rule_id 前缀匹配 — 但 page_type 不覆盖时降级
    for prefix in GATEKEEPER_RULE_PREFIXES:
        if rule_id.startswith(prefix):
            if _page_type_blocks_gatekeeper():
                return "optimizer"
            return "gatekeeper"

    # 含 case-exchange/blocker/manual-action 标签
    keeper_tags = {"case-exchange-critical", "case-exchange-incident", "case-exchange-related", "manual-action-risk",
                   "platform-critical", "blocker", "regulatory", "manual-action"}
    if any(t in keeper_tags for t in tags):
        if _page_type_blocks_gatekeeper():
            return "optimizer"
        return "gatekeeper"

    # 含 high 严重度 + 合规/安全 标签
    if severity == "high":
        if any(t in {"security", "compliance", "ymyl"} for t in tags):
            if _page_type_blocks_gatekeeper():
                return "optimizer"
            return "gatekeeper"

    return "optimizer"


def mode_summary(findings: list[dict]) -> dict:
    """统计 finding 按模式分组"""
    gatekeeper = [f for f in findings if f.get("mode") == "gatekeeper"]
    optimizer = [f for f in findings if f.get("mode") == "optimizer"]
    return {
        "gatekeeper": {
            "count": len(gatekeeper),
            "blocker": sum(1 for f in gatekeeper if f.get("severity") == "blocker"),
            "high": sum(1 for f in gatekeeper if f.get("severity") == "high"),
            "passed": len(gatekeeper) == 0,
        },
        "optimizer": {
            "count": len(optimizer),
            "high": sum(1 for f in optimizer if f.get("severity") == "high"),
            "medium": sum(1 for f in optimizer if f.get("severity") == "medium"),
            "low": sum(1 for f in optimizer if f.get("severity") == "low"),
        },
    }
