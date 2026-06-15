"""Spam policy / quality detectors: doorway / UGC spam / lazy loading / soft 404 / pagination / QAPage"""
from __future__ import annotations

import re
from urllib.parse import urlparse


# === Doorway pages ===
def doorway_template_check(raw_html: str | None = None, visible_text: str | None = None,
                          page_corpus: list | None = None, **_) -> dict:
    """单页启发式：模板化 boilerplate 比例 + 极短内容 + 缺原创信号"""
    text = visible_text or ""
    body_len = len(re.sub(r"\s+", " ", text))
    html = raw_html or ""

    # 启发式信号 1：模板 boilerplate 文本占比（typical doorway 用大量框架文案）
    boilerplate_phrases = [
        "best place to buy", "trusted by millions", "secure & reliable",
        "leading exchange", "join now", "start trading today", "world-class",
        "全球领先", "安全可靠", "立即注册", "立即交易", "千万用户信赖",
    ]
    boilerplate_hits = sum(1 for p in boilerplate_phrases if p.lower() in text.lower() or p in text)

    # 启发式信号 2：title/H1 关键词在正文重复率极高
    h1_match = re.search(r"<h1[^>]*>([\s\S]{2,80}?)</h1>", html, re.IGNORECASE)
    h1_text = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip() if h1_match else ""
    h1_repeat_ratio = 0
    if h1_text and len(h1_text) >= 4 and body_len > 0:
        h1_repeat_count = text.lower().count(h1_text.lower())
        h1_repeat_ratio = h1_repeat_count / max(1, body_len / 1000)

    # 启发式信号 3：极短 + 多内链 + 缺独立分析
    internal_link_count = html.lower().count('href="/')

    if not page_corpus:
        # 模板化判定：极短 + 重 boilerplate OR H1 高频重复 + 缺独立分析
        thin = body_len < 600
        templated = boilerplate_hits >= 4 or h1_repeat_ratio >= 5
        return {
            "body_length": body_len,
            "boilerplate_hits": boilerplate_hits,
            "h1_text": h1_text[:80],
            "h1_repeat_ratio_per_kchars": round(h1_repeat_ratio, 2),
            "internal_link_count": internal_link_count,
            "suspect_thin": thin,
            "suspect_templated": templated,
            "suspect_doorway": thin and templated,
            "requires_corpus_for_strict_check": True,
        }
    return {"body_length": body_len, "requires_corpus_compare": True}


def keyword_stuffed_landing_check(visible_text: str | None = None, title: str | None = None, **_) -> dict:
    """关键词堆砌检测：title 关键词在正文出现 ≥ 15 次"""
    text = visible_text or ""
    if not text or not title:
        return {"checked": False}
    # 提取 title 中 2-3 字英文 / 中文关键词
    clean_title = re.sub(r"[\|·\-_,，。、]", " ", title)
    words = [w for w in clean_title.split() if len(w) >= 3]
    overuse = []
    for w in words[:5]:
        count = len(re.findall(re.escape(w), text, re.IGNORECASE))
        if count >= 15:
            overuse.append((w, count))
    return {
        "overused_keywords": overuse,
        "suspect_keyword_stuffing": len(overuse) > 0,
    }


def geo_spam_check(page_url: str | None = None, visible_text: str | None = None, **_) -> dict:
    """检测地理 doorway: /xxx-{city} 路径 + 内容缺城市特异性"""
    if not page_url:
        return {"checked": False}
    path = urlparse(page_url).path
    has_geo_segment = bool(re.search(r"-(in|near|for|at)-[a-z]{4,}/?$", path, re.IGNORECASE))
    return {
        "has_geo_url_pattern": has_geo_segment,
        "requires_corpus_compare": has_geo_segment,
    }


# === UGC Spam ===
def ugc_spam_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    """评论区 spam 启发式：未审核评论 + spam 关键词"""
    html = (raw_html or "").lower()
    text = (visible_text or "").lower()
    spam_keywords = ["casino", "gambling", "viagra", "loan", "porn", "色情", "赌博", "贷款", "代孕"]
    spam_hits = sum(1 for k in spam_keywords if k in text)
    has_comment_section = any(k in html for k in ["disqus", "<form", "comment-form", "评论", "comments"])
    has_rel_ugc = "rel=\"ugc\"" in html or "rel='ugc'" in html or 'rel="nofollow' in html
    return {
        "has_comment_section": has_comment_section,
        "spam_keyword_hits": spam_hits,
        "has_rel_ugc_or_nofollow": has_rel_ugc,
        "suspect_ugc_spam": has_comment_section and spam_hits >= 1 and not has_rel_ugc,
    }


# === Lazy Loading 验证 ===
def lazy_loading_check(raw_html: str | None = None, **_) -> dict:
    """检测：首屏图片不该 lazy（影响 LCP）；首屏外图片应该 lazy"""
    html = raw_html or ""
    all_imgs = re.findall(r"<img[^>]+>", html, re.IGNORECASE)
    if not all_imgs:
        return {"image_count": 0}
    first_5 = all_imgs[:5]
    later = all_imgs[5:]
    first_5_lazy = sum(1 for i in first_5 if re.search(r'loading\s*=\s*["\']?lazy', i, re.IGNORECASE))
    later_lazy = sum(1 for i in later if re.search(r'loading\s*=\s*["\']?lazy', i, re.IGNORECASE))
    later_total = len(later)
    return {
        "first_5_lazy_count": first_5_lazy,
        "later_lazy_ratio": round(later_lazy / max(1, later_total), 2),
        "first_5_misuse_lazy": first_5_lazy >= 1,
        "later_missing_lazy": later_total >= 5 and (later_lazy / max(1, later_total)) < 0.5,
    }


# === Soft 404 ===
SOFT_404_PHRASES = [
    "page not found", "页面未找到", "暂无数据", "no results found",
    "コミングスーン", "coming soon", "即将上线", "页面正在维护",
    "404 error", "404 not found", "该页面不存在",
]


def soft_404_check(raw_html: str | None = None, visible_text: str | None = None,
                   status_code: int | None = None, **_) -> dict:
    """Soft 404 = 200 状态码但内容是 not found / 暂无数据"""
    text_l = (visible_text or "").lower()
    html_l = (raw_html or "").lower()
    matched = [p for p in SOFT_404_PHRASES if p in text_l or p in html_l]
    is_200 = status_code == 200 if status_code else None
    return {
        "status_code": status_code,
        "matched_phrases": matched[:3],
        "suspect_soft_404": is_200 and len(matched) >= 1,
    }


# === Pagination ===
def pagination_check(raw_html: str | None = None, page_url: str | None = None, **_) -> dict:
    """检测 rel=next/prev 或分页页面 canonical 处理"""
    html = (raw_html or "").lower()
    has_rel_next = 'rel="next"' in html or "rel='next'" in html
    has_rel_prev = 'rel="prev"' in html or "rel='prev'" in html
    path = urlparse(page_url or "").path
    is_paginated = bool(re.search(r"/page/\d+|[?&]page=\d+|/p\d+", path, re.IGNORECASE)) if page_url else False
    return {
        "is_paginated_url": is_paginated,
        "has_rel_next": has_rel_next,
        "has_rel_prev": has_rel_prev,
        "needs_pagination_handling": is_paginated and not (has_rel_next or has_rel_prev),
    }


# === QAPage Schema ===
def qapage_schema_check(raw_html: str | None = None, **_) -> dict:
    """检测 schema.org QAPage（与 FAQPage 不同）"""
    html = (raw_html or "").lower().replace(" ", "")
    has_qapage = '"@type":"qapage"' in html or '"qapage"' in html
    return {"has_qapage_schema": has_qapage, "passed": has_qapage}
