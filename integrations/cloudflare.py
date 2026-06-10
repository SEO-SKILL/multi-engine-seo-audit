"""Cloudflare API + log 拉取（占位）"""
from __future__ import annotations

import os


def is_configured() -> bool:
    return bool(os.environ.get("CLOUDFLARE_API_TOKEN"))


async def get_zone_log_sample(zone: str, hours: int = 24) -> dict:
    if not is_configured():
        return {"skipped": True, "reason": "cloudflare_not_configured"}
    return {"stub": True}
