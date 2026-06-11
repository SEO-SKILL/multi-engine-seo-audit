"""Multilingual SEO detector functions"""
from __future__ import annotations


def currency_check(visible_text: str, locale: str | None = None) -> dict:
    text = visible_text or ""
    expected = {"ko": "KRW", "ja": "JPY", "ru": "RUB", "tr": "TRY", "zh-CN": "CNY"}
    target = expected.get(locale)
    if not target:
        return {"checked": False}
    return {"locale_currency_present": target in text}
