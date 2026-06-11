"""
F11 Plugin Example: BYDFi 内部自定义规则
展示 plugin 如何扩展 skill
"""
from __future__ import annotations


def custom_check(html: str) -> dict:
    """示例：检查页面是否提及 BYDFi 客服联系方式"""
    text = (html or "").lower()
    has = any(k in text for k in ["support@bydfi.com", "@bydfi_support", "bydfi support"])
    return {"has_support_contact": has}


def register(registry) -> None:
    """Plugin 入口"""
    registry.custom_detectors["bydfi.internal.support_contact_check"] = custom_check
    print(f"[Plugin] example_bydfi_internal registered 1 detector")
