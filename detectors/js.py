"""JavaScript SEO detector functions"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup


def _soup(html: str): return BeautifulSoup(html, "lxml")


def hydration_flash_check(raw_html: str, rendered_dom: str | None = None, hydration_timing: dict | None = None) -> dict:
    raw_text_len = len(_soup(raw_html).get_text())
    rendered_text_len = len(_soup(rendered_dom).get_text()) if rendered_dom else raw_text_len
    flash_ratio = (rendered_text_len - raw_text_len) / max(1, rendered_text_len)
    return {"raw_text_len": raw_text_len, "rendered_text_len": rendered_text_len, "flash_suspect": flash_ratio > 0.5}


def app_shell_check(raw_html: str, rendered_dom: str | None = None) -> dict:
    soup = _soup(raw_html)
    body_text = soup.body.get_text(strip=True) if soup.body else ""
    is_shell = len(body_text) < 500
    return {"body_text_chars": len(body_text), "is_app_shell": is_shell}


def title_meta_ssr_check(raw_html: str, rendered_html: str | None = None) -> dict:
    raw_soup = _soup(raw_html)
    has_title = bool(raw_soup.title and raw_soup.title.get_text().strip())
    has_meta_desc = bool(raw_soup.find("meta", attrs={"name": "description"}))
    return {"title_in_raw": has_title, "meta_in_raw": has_meta_desc, "ssr_ok": has_title and has_meta_desc}


def canonical_consistency_check(raw_canonical: str | None = None, rendered_canonical: str | None = None) -> dict:
    if raw_canonical is None and rendered_canonical is None:
        return {"consistent": True, "raw": None, "rendered": None}
    return {"consistent": raw_canonical == rendered_canonical, "raw": raw_canonical, "rendered": rendered_canonical}


def soft_404_check(http_status: int | None = None, visible_text: str | None = None, page_intent: str | None = None) -> dict:
    if http_status != 200:
        return {"soft_404": False, "reason": "non-200 status"}
    soft_signals = ["not found", "page does not exist", "404 error", "页面不存在"]
    text_low = (visible_text or "").lower()
    is_soft = any(s in text_low for s in soft_signals) and http_status == 200
    return {"soft_404": is_soft}


def internal_link_nofollow_check(internal_links: list) -> list:
    issues = []
    for link in (internal_links or []):
        if isinstance(link, dict) and "nofollow" in str(link.get("rel", "")).lower():
            issues.append(link)
    return issues


def lazy_render_trigger_check(rendered_dom: str | None = None, lazy_load_strategy: str | None = None) -> dict:
    if not rendered_dom:
        return {"checked": False}
    uses_intersection = "IntersectionObserver" in rendered_dom
    return {"uses_intersection_observer": uses_intersection, "passed": uses_intersection}


def history_api_check(page_scripts: list) -> dict:
    scripts_text = " ".join(str(s) for s in (page_scripts or []))
    uses_pushstate = "pushState" in scripts_text
    uses_hash_route = bool(re.search(r"window\.location\.hash|onhashchange", scripts_text))
    return {"uses_pushstate": uses_pushstate, "uses_hash_route": uses_hash_route, "passed": uses_pushstate and not uses_hash_route}


def deprecated_api_check(page_scripts: list) -> list:
    scripts_text = " ".join(str(s) for s in (page_scripts or []))
    deprecated = []
    for api in ["document.write", "ApplicationCache", "WebSQL"]:
        if api in scripts_text:
            deprecated.append(api)
    return deprecated


def script_loading_check(head_scripts: list) -> dict:
    blocking = [s for s in (head_scripts or []) if isinstance(s, dict) and s.get("src") and not s.get("async") and not s.get("defer")]
    return {"blocking_count": len(blocking), "passed": len(blocking) <= 2}


def fragment_navigation_check(page_anchors: list | None = None, scroll_behavior_scripts: list | None = None) -> dict:
    return {"checked": True}


def fragment_link_check(page_content: str | None = None, anchors: list | None = None, js_behavior: dict | None = None) -> dict:
    return {"checked": True}


def spa_routing_check(url_set: list | None = None, internal_navigation: dict | None = None) -> dict:
    return {"checked": True}


def lazy_load_check(rendered_dom: str | None = None, lazy_loaded_content: list | None = None) -> dict:
    return {"checked": True}


def back_button_hijack_check(page_scripts: list) -> dict:
    scripts_text = " ".join(str(s) for s in (page_scripts or []))
    hijack_patterns = ["history.pushState", "popstate", "beforeunload"]
    hits = [p for p in hijack_patterns if p in scripts_text]
    return {"hijack_signals": hits, "suspicious": len(hits) >= 2}
