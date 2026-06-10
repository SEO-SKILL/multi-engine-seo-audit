"""Canonical 相关 detector functions"""
from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup


def find_canonical_in_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    link = soup.find("link", rel="canonical")
    if link and link.get("href"):
        return link["href"]
    return None


def find_canonical_in_headers(headers: dict[str, str]) -> str | None:
    link_header = headers.get("link") or headers.get("Link")
    if not link_header:
        return None
    for part in link_header.split(","):
        if 'rel="canonical"' in part or "rel=canonical" in part:
            url_part = part.split(";")[0].strip()
            return url_part.strip("<>")
    return None


def exists_and_valid(raw_html: str, rendered_html: str | None = None, http_headers: dict | None = None) -> dict:
    """检测 canonical 是否存在 + SSR 输出"""
    raw_canonical = find_canonical_in_html(raw_html)
    rendered_canonical = find_canonical_in_html(rendered_html) if rendered_html else None
    header_canonical = find_canonical_in_headers(http_headers or {})

    result = {
        "passed": True,
        "raw_canonical": raw_canonical,
        "rendered_canonical": rendered_canonical,
        "header_canonical": header_canonical,
        "issues": [],
    }

    if not raw_canonical and not header_canonical:
        if rendered_canonical:
            result["passed"] = False
            result["issues"].append("canonical 仅 CSR 渲染后存在，raw HTML 缺失")
        else:
            result["passed"] = False
            result["issues"].append("canonical 完全缺失")
        return result

    canonical = raw_canonical or header_canonical
    if canonical and not canonical.startswith("http"):
        result["passed"] = False
        result["issues"].append("canonical 不是绝对 URL")

    return result


def is_self_canonical(canonical_url: str, page_url: str) -> bool:
    if not canonical_url or not page_url:
        return False
    return _normalize(canonical_url) == _normalize(page_url)


def _normalize(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"
