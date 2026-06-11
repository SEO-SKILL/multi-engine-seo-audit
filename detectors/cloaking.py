"""Cloaking detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def ua_content_diff(fetch_results_per_ua: dict | None = None) -> dict:
    if not fetch_results_per_ua:
        return {"checked": False}
    bodies = {ua: (data.get("body") or "") for ua, data in fetch_results_per_ua.items()}
    if len(bodies) < 2:
        return {"checked": False}
    lens = [len(b) for b in bodies.values()]
    diff_ratio = (max(lens) - min(lens)) / max(1, max(lens))
    return {"length_diff_ratio": diff_ratio, "suspicious": diff_ratio > 0.30}


def geoip_content_diff(fetch_results_per_region: dict | None = None) -> dict:
    if not fetch_results_per_region:
        return {"checked": False}
    return ua_content_diff(fetch_results_per_region)


def csr_post_render_diff(raw_html: str, rendered_dom: str | None = None, googlebot_render_comparison: dict | None = None) -> dict:
    if not rendered_dom:
        return {"checked": False}
    raw_text = BeautifulSoup(raw_html, "lxml").get_text(strip=True)
    rendered_text = BeautifulSoup(rendered_dom, "lxml").get_text(strip=True)
    diff_chars = abs(len(rendered_text) - len(raw_text))
    return {"diff_chars": diff_chars, "suspicious": diff_chars > 5000}


def hidden_text_check(rendered_dom: str | None = None, computed_styles: list | None = None) -> dict:
    if not rendered_dom:
        return {"checked": False}
    dom = rendered_dom.lower()
    flags = []
    if "left: -9999px" in dom or "left:-9999px" in dom:
        flags.append("offscreen_positioning")
    if "font-size: 1px" in dom or "font-size:1px" in dom:
        flags.append("tiny_font")
    if "color: white" in dom and "background: white" in dom:
        flags.append("white_on_white")
    return {"hidden_text_flags": flags, "suspicious": len(flags) > 0}
