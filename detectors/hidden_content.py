"""Hidden text / hidden links detection (Google manual action 高发区)"""
from __future__ import annotations

import re


def display_none_text_check(raw_html: str | None = None, **_) -> dict:
    """检测 display:none / visibility:hidden 隐藏的文字块（>50 字符）"""
    html = raw_html or ""
    # 匹配 inline style 隐藏
    hidden_blocks = re.findall(
        r'<(\w+)[^>]*style=["\'][^"\']*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^"\']*["\'][^>]*>([\s\S]{50,1000}?)</\1>',
        html, re.IGNORECASE)
    suspect_blocks = []
    for tag, content in hidden_blocks:
        # 文字大于 30 字符且不含 script/style 标签内容才算可疑
        text = re.sub(r"<[^>]+>", "", content).strip()
        if len(text) > 30 and tag.lower() not in ("script", "style", "noscript"):
            suspect_blocks.append(text[:80])
    return {
        "hidden_block_count": len(suspect_blocks),
        "samples": suspect_blocks[:3],
        "suspect_hidden_text": len(suspect_blocks) > 0,
    }


def same_color_check(raw_html: str | None = None, **_) -> dict:
    """检测同色文本（白底白字 / 黑底黑字）— 启发式扫 inline style"""
    html = raw_html or ""
    same_color_matches = re.findall(
        r'style=["\'][^"\']*color\s*:\s*(white|#fff|#ffffff)[^"\']*;[^"\']*background[^:]*:\s*\1',
        html, re.IGNORECASE)
    same_color_matches += re.findall(
        r'style=["\'][^"\']*color\s*:\s*(black|#000|#000000)[^"\']*;[^"\']*background[^:]*:\s*\1',
        html, re.IGNORECASE)
    return {
        "same_color_match_count": len(same_color_matches),
        "suspect_same_color": len(same_color_matches) > 0,
    }


def off_screen_check(raw_html: str | None = None, **_) -> dict:
    """检测屏外定位隐藏（left:-9999px / top:-9999px / text-indent:-9999px）"""
    html = raw_html or ""
    patterns = [
        r"left\s*:\s*-?\d{4,}px",
        r"top\s*:\s*-?\d{4,}px",
        r"text-indent\s*:\s*-?\d{4,}px",
        r"position\s*:\s*absolute[^;]*;\s*left\s*:\s*-9999",
    ]
    hits = sum(1 for p in patterns if re.search(p, html, re.IGNORECASE))
    return {"off_screen_hit_count": hits, "suspect_off_screen": hits >= 1}


def zero_font_check(raw_html: str | None = None, **_) -> dict:
    """检测 font-size:0 / 1px 隐藏文字"""
    html = raw_html or ""
    matches = re.findall(r"font-size\s*:\s*(0|1)px?\s*[;\"']", html, re.IGNORECASE)
    return {"zero_font_count": len(matches), "suspect_zero_font": len(matches) > 0}


def hidden_links_check(raw_html: str | None = None, **_) -> dict:
    """检测疑似隐藏链接：单字符 anchor / 标点 anchor / 空 anchor"""
    html = raw_html or ""
    # 提取所有 <a> 文本
    anchors = re.findall(r"<a[^>]+>([\s\S]{0,200}?)</a>", html, re.IGNORECASE)
    suspect_count = 0
    for a in anchors:
        text = re.sub(r"<[^>]+>", "", a).strip()
        if len(text) == 0:
            suspect_count += 1
        elif len(text) == 1 and not text.isalnum() and ord(text) < 128:
            suspect_count += 1  # 单标点 anchor
    return {
        "anchor_count": len(anchors),
        "suspect_anchor_count": suspect_count,
        "suspect_hidden_links": suspect_count >= 3,
    }
