"""Baidu Search detector functions"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup


def icp_check(page_footer: str | None = None) -> dict:
    has_icp = bool(re.search(r"ICP\s*备?\s*\d+", page_footer or "", re.IGNORECASE))
    return {"has_icp_license": has_icp}


def robots_baiduspider_check(robots_txt: str | None = None) -> dict:
    text = (robots_txt or "").lower()
    has_ua = "user-agent: baiduspider" in text
    blocked = has_ua and "disallow: /" in text.split("user-agent: baiduspider")[-1][:200]
    return {"has_baiduspider_section": has_ua, "blocked": blocked}


def simplified_chinese_check(visible_text: str) -> dict:
    # 简单检测：包含简体中文且不包含大量繁体
    has_simplified = bool(re.search(r"[\u4e00-\u9fff]", visible_text or ""))
    return {"has_chinese": has_simplified}
