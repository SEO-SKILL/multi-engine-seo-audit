"""Video SEO detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def schema_check(videos: list | None = None, jsonld: list | None = None) -> dict:
    has_video_schema = any(isinstance(b, dict) and b.get("@type") in ("VideoObject", "LiveBroadcastEvent") for b in (jsonld or []))
    return {"has_video_schema": has_video_schema, "passed": has_video_schema or not videos}


def thumbnail_check(videos: list | None = None, jsonld: list | None = None) -> dict:
    has_thumbnail = any(isinstance(b, dict) and b.get("thumbnailUrl") for b in (jsonld or []))
    return {"has_thumbnail": has_thumbnail}


def transcript_check(page_content: str | None = None) -> dict:
    text = (page_content or "").lower()
    return {"has_transcript": "transcript" in text or "字幕" in (page_content or "")}


def duration_check(jsonld: list | None = None) -> dict:
    has_duration = any(isinstance(b, dict) and b.get("duration") for b in (jsonld or []))
    return {"has_duration": has_duration}


def live_check(jsonld: list | None = None) -> dict:
    is_live = any(isinstance(b, dict) and b.get("@type") == "LiveBroadcastEvent" for b in (jsonld or []))
    return {"is_live_broadcast": is_live}
