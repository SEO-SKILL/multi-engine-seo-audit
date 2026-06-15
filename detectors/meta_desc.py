"""Meta description / Featured snippet / Reconsideration detectors"""
from __future__ import annotations

import re


def missing_or_short_check(head_meta: dict | None = None, **_) -> dict:
    """Meta description 缺失或过短"""
    if not head_meta:
        return {"missing": True, "suspect_missing_or_short": True}
    desc = head_meta.get("description") or head_meta.get("og:description") or ""
    length = len(desc.strip()) if desc else 0
    return {
        "description_length": length,
        "missing": length == 0,
        "suspect_missing_or_short": length < 50,
    }


def length_check(head_meta: dict | None = None, **_) -> dict:
    """Meta description 长度合规检查 (120-160 推荐)"""
    if not head_meta:
        return {"checked": False}
    desc = head_meta.get("description") or ""
    length = len(desc.strip())
    if length == 0:
        return {"checked": False, "no_description": True}
    return {
        "description_length": length,
        "too_short": length < 120 and length > 0,
        "too_long": length > 200,
        "suspect_bad_length": length < 120 or length > 200,
    }


def featured_snippet_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    """Featured Snippet readiness — 问句标题 + 直接回答 + 列表"""
    html = (raw_html or "").lower()
    text = visible_text or ""
    # 问句标题
    has_question_heading = bool(re.search(r"<h[2-4][^>]*>\s*(?:what|how|why|when|where|which|is|does|can|should|是什么|如何|为什么|什么时候|哪个)", html, re.IGNORECASE))
    # 50-60 字直接回答（H2/H3 之后第一段）
    direct_answer = False
    for m in re.finditer(r"</h[2-4]>\s*<p[^>]*>([^<]{40,200})</p>", html, re.IGNORECASE):
        if 50 <= len(m.group(1).strip()) <= 200:
            direct_answer = True
            break
    # 列表 / 表格
    has_list_or_table = "<ul" in html or "<ol" in html or "<table" in html
    has_all = sum([has_question_heading, direct_answer, has_list_or_table])
    return {
        "has_question_heading": has_question_heading,
        "has_direct_answer_paragraph": direct_answer,
        "has_list_or_table": has_list_or_table,
        "readiness_score": has_all,
        "suspect_not_snippet_ready": has_all < 2,
    }


def reconsideration_check(raw_html: str | None = None, page_url: str | None = None, **_) -> dict:
    """Manual Action 申诉 readiness — 检查站点是否有 reconsideration request 准备"""
    html = (raw_html or "").lower()
    # 站点是否有 transparency / compliance / 改动记录页面
    has_changelog = any(k in html for k in ["changelog", "what's new", "release-notes", "更新日志"])
    has_compliance_doc = any(k in html for k in ["compliance", "transparency", "trust-center", "合规"])
    has_contact_for_seo = "seo@" in html or "webmaster@" in html
    score = sum([has_changelog, has_compliance_doc, has_contact_for_seo])
    return {
        "has_changelog": has_changelog,
        "has_compliance_doc": has_compliance_doc,
        "has_seo_contact": has_contact_for_seo,
        "reconsideration_readiness_score": score,
        "suspect_appeal_unprepared": score < 1,
    }
