"""
Google Search Console API 集成（占位）
等 Kelly 配置 OAuth 凭证后启用
"""
from __future__ import annotations

import os
from typing import Any


def is_configured() -> bool:
    return bool(os.environ.get("GSC_SERVICE_ACCOUNT_JSON") or os.environ.get("GSC_OAUTH_TOKEN"))


async def url_inspection(url: str) -> dict[str, Any]:
    if not is_configured():
        return {"skipped": True, "reason": "gsc_not_configured"}
    # TODO: 实际 GSC API 调用
    return {"stub": True}


async def search_analytics(property_url: str, *, dimensions: list[str], days: int = 28) -> dict:
    if not is_configured():
        return {"skipped": True, "reason": "gsc_not_configured"}
    return {"stub": True}
