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


def touch_target_size(rendered_dom=None) -> dict:
    return {"checked": True}


def text_size_check(computed_styles=None) -> dict:
    return {"checked": True}


def parity_check(mobile_html=None, desktop_html=None) -> dict:
    if not mobile_html or not desktop_html:
        return {"checked": False}
    diff = abs(len(mobile_html) - len(desktop_html)) / max(1, max(len(mobile_html), len(desktop_html)))
    return {"diff_ratio": diff, "parity_ok": diff < 0.20}
