"""Site Migration detector functions"""
from __future__ import annotations

import re


def staging_indexability_check(domain: str, raw_html: str, meta_robots: dict | None = None) -> dict:
    is_staging = bool(re.match(r"(beta|staging|preview|test|dev)\.", domain or "", re.IGNORECASE))
    has_noindex = "noindex" in (raw_html or "").lower()
    return {"is_staging": is_staging, "has_noindex": has_noindex, "passed": not is_staging or has_noindex}


def staging_robots_leftover_check(robots_txt: str | None = None, deployment_metadata: dict | None = None) -> dict:
    text = (robots_txt or "").lower()
    is_blocking_all = "user-agent: *" in text and "disallow: /" in text
    return {"production_blocked_by_robots": is_blocking_all}


def gsc_verification_check(domain: str, verification_meta: str | None = None, dns_txt: list | None = None) -> dict:
    return {"requires_external_api": True}


def dual_serving_check(old_server_logs: dict | None = None, new_server_logs: dict | None = None) -> dict:
    return {"requires_log_data": True}
