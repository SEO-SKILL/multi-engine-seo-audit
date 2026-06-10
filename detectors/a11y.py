"""Accessibility SEO detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def html_lang_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    html_tag = soup.find("html")
    if not html_tag:
        return {"present": False}
    lang = html_tag.get("lang")
    return {"present": bool(lang), "lang": lang}


def h1_count_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    h1s = soup.find_all("h1")
    return {"count": len(h1s), "texts": [h.get_text().strip() for h in h1s]}


def heading_hierarchy_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    headings = [(int(h.name[1]), h.get_text().strip()) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    broken = []
    for i in range(1, len(headings)):
        prev_level, _ = headings[i - 1]
        cur_level, _ = headings[i]
        if cur_level > prev_level + 1:
            broken.append(f"H{prev_level} → H{cur_level} skipping levels")
    return {"total": len(headings), "broken_jumps": broken}


def link_text_check(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    vague = []
    for a in soup.find_all("a", href=True):
        text = a.get_text().strip().lower()
        if text in {"click here", "read more", "more", "here", "了解更多", "点击"}:
            vague.append({"href": a["href"], "text": text})
    return vague
