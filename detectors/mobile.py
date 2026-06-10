"""Mobile-first SEO detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def viewport_responsive_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        return {"present": False}
    content = viewport.get("content", "")
    return {
        "present": True,
        "responsive": "width=device-width" in content,
        "content": content,
    }
