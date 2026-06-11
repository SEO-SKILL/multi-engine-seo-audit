"""Content freshness detector functions"""
from __future__ import annotations

from datetime import datetime, timedelta


def staleness_check(date_modified: str | None, max_age_days: int = 180) -> dict:
    if not date_modified:
        return {"has_date": False, "stale": True}
    try:
        # 简化：只支持 YYYY-MM-DD 格式
        dt = datetime.strptime(date_modified[:10], "%Y-%m-%d")
        age = (datetime.utcnow() - dt).days
        return {"has_date": True, "age_days": age, "stale": age > max_age_days}
    except Exception:
        return {"has_date": False, "parse_error": True}


def last_reviewed_format_check(text: str) -> dict:
    import re
    iso_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    has_iso = bool(iso_pattern.search(text))
    return {"has_iso_date": has_iso}


def update_history_check(page_content: str | None = None) -> dict:
    text = (page_content or "").lower()
    has = any(k in text for k in ["update history", "changelog", "revision history", "更新历史"])
    return {"has_update_history": has}
