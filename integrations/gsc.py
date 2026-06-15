"""
Google Search Console API 集成（占位）
认证优先级：service-account JSON > OAuth token > ADC (gcloud auth application-default login)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

_ADC_PATH = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"


def is_configured() -> bool:
    return bool(
        os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
        or os.environ.get("GSC_OAUTH_TOKEN")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or _ADC_PATH.exists()
    )


async def url_inspection(url: str) -> dict[str, Any]:
    if not is_configured():
        return {"skipped": True, "reason": "gsc_not_configured"}
    # TODO: 实际 GSC API 调用
    return {"stub": True}


async def search_analytics(property_url: str, *, dimensions: list[str], days: int = 28) -> dict:
    if not is_configured():
        return {"skipped": True, "reason": "gsc_not_configured"}
    return {"stub": True}
