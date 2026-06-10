"""robots.txt / meta robots / X-Robots-Tag detector functions"""
from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup


async def fetch_robots_txt(domain: str) -> str | None:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"{domain}/robots.txt")
            return resp.text if resp.status_code == 200 else None
        except Exception:
            return None


def parse_disallow_patterns(robots_txt: str, user_agent: str = "*") -> list[str]:
    disallows = []
    current_ua = None
    for line in robots_txt.splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            current_ua = line.split(":", 1)[1].strip()
        elif line.lower().startswith("disallow:") and current_ua in (user_agent, "*"):
            disallows.append(line.split(":", 1)[1].strip())
    return disallows


def meta_robots_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    meta = soup.find("meta", attrs={"name": "robots"})
    if not meta:
        return {"present": False, "directives": []}
    content = meta.get("content", "").lower()
    return {
        "present": True,
        "directives": [d.strip() for d in content.split(",")],
        "noindex": "noindex" in content,
        "nofollow": "nofollow" in content,
        "nosnippet": "nosnippet" in content,
    }


def x_robots_tag_check(headers: dict) -> dict:
    tag = headers.get("x-robots-tag") or headers.get("X-Robots-Tag")
    if not tag:
        return {"present": False}
    return {
        "present": True,
        "value": tag,
        "noindex": "noindex" in tag.lower(),
        "nofollow": "nofollow" in tag.lower(),
    }


def conflict_check(robots_txt: str | None, meta_robots: dict, x_robots: dict) -> list[str]:
    conflicts = []
    if meta_robots.get("noindex") and x_robots.get("present") and not x_robots.get("noindex"):
        conflicts.append("meta noindex but X-Robots-Tag allows")
    return conflicts
