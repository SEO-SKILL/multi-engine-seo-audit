"""Japan-specific (Yahoo Japan / JFSA) detector functions"""
from __future__ import annotations

import re


def jfsa_disclosure_check(page_content: str) -> dict:
    text = (page_content or "").lower()
    has_jfsa = "金融庁" in (page_content or "") or "jfsa" in text or "japan financial services agency" in text
    return {"has_jfsa_mention": has_jfsa}


def payment_method_check(page_content: str) -> dict:
    text = (page_content or "").lower()
    methods = [m for m in ["paypay", "linepay", "bank transfer", "銀行振込"] if m in text]
    return {"japanese_payment_methods": methods}
