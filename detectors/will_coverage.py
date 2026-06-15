"""Will 知识库 9 问题兜底信息级 detector"""
from __future__ import annotations

import re


def scaled_content_awareness_check(visible_text: str | None = None, **_) -> dict:
    """① AI 规模化低价值——任何页面都给出 awareness 提示（除非已包含 Platform 真分析信号）"""
    text = visible_text or ""
    has_byline = any(k in text for k in ["analyzed by", "by Platform", "我们分析", "we tested", "we measured"])
    return {"has_first_party_analysis": has_byline, "suspect_no_analysis_signal": not has_byline}


def ymyl_awareness_check(visible_text: str | None = None, raw_html: str | None = None, **_) -> dict:
    """② YMYL/EEAT——金融页应有风险披露 + Organization JSON-LD + about/contact 链接"""
    text = (visible_text or "")
    html = (raw_html or "").lower()
    has_risk_disclaimer = any(k in text for k in ["risk disclosure", "投资有风险", "Past performance", "Investment risk"])
    has_organization = '"organization"' in html or '"@type":"organization"' in html.replace(" ", "")
    has_about = "/about" in html
    score = sum([has_risk_disclaimer, has_organization, has_about])
    return {"ymyl_signal_score": score, "suspect_weak_ymyl_signal": score < 2}


def faq_deprecation_notice_check(raw_html: str | None = None, **_) -> dict:
    """⑤ FAQ 富结果 2026-05 弃用——所有页面给出提示让用户知道这个 V2 风险"""
    html = (raw_html or "").lower()
    has_faqpage = '"faqpage"' in html.replace(" ", "")
    # 弃用提示规则总是触发（让用户看到 V2 风险），但有 faqpage 时 confidence 更高
    return {"has_faqpage_schema": has_faqpage, "deprecation_notice_required": True}


def snippet_strategy_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    """⑥ Featured Snippet 策略 — 检查页面 snippet 优化质量，给 Platform 持续 awareness 提示"""
    html = (raw_html or "").lower()
    has_question_heading = bool(re.search(r"<h[2-4][^>]*>\s*(?:what|how|why|when|where|是什么|如何|为什么)", html, re.IGNORECASE))
    has_list = "<ul" in html or "<ol" in html
    has_table = "<table" in html
    has_direct_answer = bool(re.search(r"</h[2-4]>\s*<p[^>]*>([^<]{40,200})</p>", html, re.IGNORECASE))
    # 全部 3 条满足才 snippet-optimal；否则建议优化
    snippet_score = sum([has_question_heading, has_list or has_table, has_direct_answer])
    return {
        "snippet_optimization_score": snippet_score,
        "has_question_heading": has_question_heading,
        "has_list_or_table": has_list or has_table,
        "has_direct_answer": has_direct_answer,
        "suspect_snippet_strategy_missing": snippet_score < 3,
    }


def core_update_monitoring_check(page_url: str | None = None, **_) -> dict:
    """⑧ 核心更新时机——所有页面提示需要 GSC 监控（信息级）"""
    return {"requires_gsc_monitoring": True, "monitoring_setup_pending": True}


def featured_snippet_strategy_awareness_check(raw_html: str | None = None, **_) -> dict:
    """⑥ Featured Snippet 策略提示——总是触发 awareness，让 Platform 关注 0 位流量"""
    return {"featured_snippet_strategy_required": True, "suspect_snippet_strategy_missing": True}
