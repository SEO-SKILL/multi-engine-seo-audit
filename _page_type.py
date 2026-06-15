"""
URL → page_type 推断
用于 router/applies_to 过滤 + gatekeeper 守门员判定
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

_LOCALE_PREFIX = re.compile(r"^/(en|ko|ja|ru|zh-cn|zh-hk|vi|tr|pt|es|id|th|ms|fr|de|it)(?:/|$)", re.I)

_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^/?$"), "home"),
    (re.compile(r"^/(learn|academy|guide)(?:/|$)"), "learn"),
    (re.compile(r"^/(blog|news|press)(?:/|$)"), "blog"),
    (re.compile(r"^/(support|help|faq)(?:/|$)"), "support"),
    (re.compile(r"^/(questions?|qa|q&a)(?:/|$)"), "questions"),
    (re.compile(r"^/(review|reviews|crypto-review)(?:/|$)"), "crypto-review"),
    (re.compile(r"^/(price|prices|markets?|quote)(?:/|$)"), "price"),
    (re.compile(r"^/(futures?|spot|options?|copytrading|copy-trading|earn|launchpad|trade)(?:/|$)"), "product"),
    (re.compile(r"^/(tools?|calculator|converter)(?:/|$)"), "tools"),
    (re.compile(r"^/(about|company|team)(?:/|$)"), "about"),
    (re.compile(r"^/(terms|privacy|legal|compliance|risk)(?:/|$)"), "legal"),
    (re.compile(r"^/(login|signup|register|kyc)(?:/|$)"), "account"),
]


def infer_page_type(url: str | None) -> str:
    """从 URL 推断 page_type；未识别返回 'unknown'（router 不会按 page_type 过滤）"""
    if not url:
        return "unknown"
    try:
        path = urlparse(url).path or "/"
    except Exception:
        return "unknown"

    # 剥离 locale 前缀
    path = _LOCALE_PREFIX.sub("/", path)
    if not path.startswith("/"):
        path = "/" + path

    for pat, pt in _PATTERNS:
        if pat.match(path):
            return pt
    return "article"  # 默认有内容的非首页 → article


def is_rule_applicable(rule: dict, page_type: str | None) -> bool:
    """判断规则的 applies_to.page_types 是否覆盖当前 page_type"""
    if not page_type or page_type == "unknown":
        return True  # 未知页类型不过滤（fail-open）
    applies = rule.get("applies_to", {}) or {}
    pts = applies.get("page_types", []) or []
    if not pts or "all" in pts:
        return True
    return page_type in pts
