"""hreflang 相关 detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def parse_alternates(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    alternates = []
    for link in soup.find_all("link", rel="alternate"):
        hreflang = link.get("hreflang")
        href = link.get("href")
        if hreflang and href:
            alternates.append({"hreflang": hreflang, "href": href})
    return alternates


def has_x_default(alternates: list[dict[str, str]]) -> bool:
    return any(a["hreflang"] == "x-default" for a in alternates)


def check_robots_conflict(alternates: list[dict[str, str]], robots_disallow_patterns: list[str]) -> list[dict]:
    """检测 alternate 是否被 robots.txt Disallow"""
    conflicts = []
    for alt in alternates:
        for pattern in robots_disallow_patterns:
            if pattern in alt["href"]:
                conflicts.append({
                    "alternate": alt,
                    "blocked_by_pattern": pattern,
                })
    return conflicts


def check_alternate_status(alternates: list[dict[str, str]], status_map: dict[str, int]) -> list[dict]:
    """检测 alternate 是否返回 404 / 5xx"""
    invalid = []
    for alt in alternates:
        status = status_map.get(alt["href"])
        if status is None:
            continue
        if status >= 400:
            invalid.append({"alternate": alt, "status": status})
    return invalid


def detect_language_mismatch(alternate: dict[str, str], detected_language: str) -> bool:
    """alternate 声明的 hreflang 与实际页面语言是否匹配"""
    declared_lang = alternate["hreflang"].split("-")[0]
    return declared_lang != detected_language
