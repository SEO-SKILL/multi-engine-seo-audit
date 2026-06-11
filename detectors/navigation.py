"""Navigation / Breadcrumb detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def _soup(html: str): return BeautifulSoup(html, "lxml")


def breadcrumb_depth_check(breadcrumbs: list | None = None) -> dict:
    depth = len(breadcrumbs or [])
    return {"depth": depth, "too_deep": depth > 5}


def breadcrumb_visible_check(rendered_dom: str | None = None, jsonld_parsed: list | None = None) -> dict:
    if not rendered_dom:
        return {"checked": False}
    soup = _soup(rendered_dom)
    has_visible = bool(soup.find(class_=lambda c: c and "breadcrumb" in (c or "").lower()))
    has_schema = any(isinstance(b, dict) and b.get("@type") == "BreadcrumbList" for b in (jsonld_parsed or []))
    return {"visible": has_visible, "in_schema": has_schema, "consistent": has_visible == has_schema}


def breadcrumb_last_clickable(breadcrumbs: list | None = None) -> dict:
    if not breadcrumbs:
        return {"checked": False}
    last = breadcrumbs[-1] if isinstance(breadcrumbs, list) else None
    last_clickable = isinstance(last, dict) and bool(last.get("href"))
    return {"last_clickable": last_clickable, "should_not_be": True}


def breadcrumb_first_check(breadcrumbs: list | None = None) -> dict:
    if not breadcrumbs:
        return {"checked": False}
    first = breadcrumbs[0] if isinstance(breadcrumbs, list) else None
    is_home = isinstance(first, dict) and (first.get("name", "").lower() in ("home", "首页"))
    return {"first_is_home": is_home}
