"""Google 2024+ 新规则 detector（spam policy / AI Overviews / HCU 系统级）"""
from __future__ import annotations

import re
from urllib.parse import urlparse


# === 2024 Site Reputation Abuse ===
# Platform 自家已知子路径（first-party content，非寄生）
_PLATFORM_FIRST_PARTY_PATHS = (
    "/cointalk", "/learn", "/blog", "/news", "/support", "/help",
    "/about", "/careers", "/legal", "/terms", "/privacy",
    "/futures", "/spot", "/copy", "/price", "/markets", "/tools",
)


def site_reputation_abuse_check(page_url: str | None = None, visible_text: str | None = None,
                                raw_html: str | None = None, **_) -> dict:
    """寄生 SEO 检测：高权重域名下挂载与主品牌无关的第三方/低质内容
    收敛策略（P1）：
    1. first-party 路径白名单：Platform 自家社区/学院/支持路径不算寄生
    2. 移除 casino/gambling/betting 关键词（加密合规讨论天然重叠 → 大面积误报）
    3. coupon/deal 收紧为完整短语（避免 "best deal" 等中性表述误判）
    4. 阈值改为基于真寄生信号，路径白名单可一票否决
    """
    text = (visible_text or "") + " " + (raw_html or "")
    text_l = text.lower()
    # First-party 路径检测
    is_first_party_known_path = False
    irrelevant_subdir = False
    if page_url:
        path = urlparse(page_url).path.lower()
        is_first_party_known_path = any(path.startswith(p) for p in _PLATFORM_FIRST_PARTY_PATHS)
        irrelevant_subdir = any(k in path for k in ["/coupons/", "/deals/", "/promo/", "/partner/", "/sponsored/", "/affiliates/"])

    # 寄生 SEO 信号（收敛后：仅保留真寄生模式，去除加密天然重叠词）
    signals = {
        # 优惠码/折扣码完整短语（"deal" 单词太泛，已收紧）
        "coupon_or_deals_block": any(k in text_l for k in [
            "coupon code", "promo code", "discount code", "voucher code",
            "优惠码", "折扣码", "优惠券",
        ]),
        # 第三方广告软文（这个准）
        "third_party_offer": any(k in text_l for k in [
            "partner offer", "sponsored content", "advertorial", "广告软文",
            "affiliate disclosure", "this is sponsored",
        ]),
        # 高利贷/快贷（与加密合规借贷区分：保留 payday/quick loan）
        "loan_or_payday": any(k in text_l for k in [
            "payday loan", "quick loan", "cash advance loan",
            "高利贷", "套现贷",
        ]),
        "irrelevant_subdir": irrelevant_subdir,
    }
    risk_score = sum(1 for v in signals.values() if v)

    # First-party 路径一票否决：Platform 自家路径下的内容不视为寄生
    if is_first_party_known_path and not irrelevant_subdir:
        suspect = False
    else:
        suspect = risk_score >= 2

    return {
        "signals": signals,
        "is_first_party_known_path": is_first_party_known_path,
        "parasite_seo_risk_score": risk_score,
        "suspect_parasite_seo": suspect,
    }


# === 2024 Expired Domain Abuse ===
def expired_domain_abuse_check(page_url: str | None = None, domain_whois: dict | None = None,
                              raw_html: str | None = None, **_) -> dict:
    """检测过期域名再利用：内容主题与历史完全不符 / 域名年龄异常"""
    whois = domain_whois or {}
    age_years = whois.get("age_years") or whois.get("domain_age_years")
    creation = whois.get("creation_date")
    expiration = whois.get("expiration_date")
    # 主要靠人工或 WHOIS API；这里给出占位
    return {
        "domain_age_years": age_years,
        "has_whois_data": bool(whois),
        "requires_external_whois_check": not whois,
        "suspect_expired_domain": False,  # 默认 false，需要 WHOIS 数据后判定
    }


# === 2024 Scaled AI Content ===
def scaled_ai_content_check(visible_text: str | None = None, page_purpose: str | None = None, **_) -> dict:
    """AI 量产内容启发式检测（多维信号 + LLM judge 兜底）"""
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True}
    sentences = re.split(r"[.!?。！？\n]", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    body_chars = len(re.sub(r"\s+", "", text))

    # 信号 1：常见 AI typical phrases
    common_ai_phrases = [
        "in this article", "in this guide", "in this comprehensive",
        "let's explore", "let's dive", "let's take a look",
        "it's important to note", "it's worth noting", "it is essential",
        "in conclusion", "to summarize", "in summary",
        "本文将", "接下来我们", "需要注意的是", "总而言之", "综上所述",
        "首先", "其次", "再次", "最后",
    ]
    ai_phrase_hits = sum(1 for p in common_ai_phrases if p in text.lower() or p in text)

    # 信号 2：句长均匀度（AI 量产句长趋同）
    if len(sentences) >= 10:
        lens = [len(s) for s in sentences if 10 < len(s) < 200]
        if lens:
            avg_len = sum(lens) / len(lens)
            variance = sum((l - avg_len) ** 2 for l in lens) / len(lens)
            std_dev = variance ** 0.5
            uniformity_ratio = std_dev / max(1, avg_len)
        else:
            uniformity_ratio = 0
    else:
        uniformity_ratio = 0

    # 信号 3：标题对称结构（AI 倾向规整 H2/H3）
    # 这里 raw_html 未传，跳过
    # 信号 4：缺独立分析动词
    analysis_verbs_count = sum(1 for k in ["we tested", "we analyzed", "我们测试", "我们分析", "实测", "实际试用"]
                              if k in text or k.lower() in text.lower())

    suspect = (
        ai_phrase_hits >= 4
        or (ai_phrase_hits >= 2 and analysis_verbs_count == 0 and body_chars >= 1500)
        or (len(sentences) >= 30 and uniformity_ratio < 0.35 and analysis_verbs_count == 0)
    )
    return {
        "sentence_count": len(sentences),
        "ai_phrase_hits": ai_phrase_hits,
        "uniformity_ratio": round(uniformity_ratio, 2),
        "analysis_verbs_count": analysis_verbs_count,
        "suspect_ai_generated": suspect,
        "requires_llm_check": True,
    }


# === Reviews System：in-depth 评测 ===
def in_depth_review_check(visible_text: str | None = None, **_) -> dict:
    """评测内容深度检测：定量数据 / 优缺点平衡 / 第一手经验"""
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True}
    text_l = text.lower()
    signals = {
        "has_pros_cons": ("pros" in text_l and "cons" in text_l) or ("优点" in text and "缺点" in text),
        "has_quantitative": bool(re.search(r"\d+\.?\d*\s*(%|fee|手续费|秒|hours|days)", text, re.IGNORECASE)),
        "has_comparison": any(k in text_l for k in [" vs ", " versus ", "compared to", "对比", "相比"]),
        "has_first_person": any(k in text for k in ["I tested", "we tested", "I tried", "我测试", "我们试用", "实际使用"]),
        "has_screenshots": "screenshot" in text_l or "截图" in text,
    }
    score = sum(1 for v in signals.values() if v)
    return {"signals": signals, "depth_score": score, "shallow_review": score < 2}


# === HCU 站点级（需要 corpus）===
def site_level_hcu_check(page_corpus: list | None = None, visible_text: str | None = None, **_) -> dict:
    """站点级 HCU 评估（需要 corpus，单页 audit 跳过）"""
    if not page_corpus:
        return {"requires_corpus": True, "checked": False}
    # 评估 corpus 中 thin pages / 重复落地页比例
    return {"requires_external_audit": True}


# === AI Overviews：可问答块 ===
def answerable_block_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_faq = '"faqpage"' in html.replace(" ", "") or '<dt' in html and '<dd' in html
    has_howto = '"howto"' in html.replace(" ", "") or any(k in (visible_text or "").lower() for k in ["step 1", "步骤 1", "第一步"])
    has_questions = bool(re.search(r"<h[2-4][^>]*>\s*(?:what|how|why|when|where|是什么|如何|为什么)", html, re.IGNORECASE))
    has_lists = html.count("<ul") + html.count("<ol") >= 2
    return {
        "has_faq_schema_or_dl": has_faq,
        "has_howto": has_howto,
        "has_question_headings": has_questions,
        "has_lists": has_lists,
        "answerable_score": sum([has_faq, has_howto, has_questions, has_lists]),
        "passed": (has_faq + has_howto + has_questions + has_lists) >= 2,
    }


# === AI Overviews：引用源 trust signal ===
def ai_citation_signals_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    text = visible_text or ""
    signals = {
        "has_jsonld_article": '"article"' in html or '"newsarticle"' in html,
        "has_author": '"author"' in html or "by " in text.lower()[:1000] or "作者" in text[:1000],
        "has_date": '"datepublished"' in html or bool(re.search(r"\d{4}-\d{2}-\d{2}", text)),
        "has_citations": text.count('"http') >= 2 or text.count("source:") + text.count("来源：") >= 2,
    }
    score = sum(1 for v in signals.values() if v)
    return {"signals": signals, "citation_score": score, "weak_citation": score < 2}


# === AI Overviews：移动可读性 ===
def mobile_readability_check(raw_html: str | None = None, **_) -> dict:
    html = (raw_html or "").lower()
    has_viewport = "<meta" in html and "viewport" in html and "width=device-width" in html
    h_count = html.count("<h2") + html.count("<h3")
    list_count = html.count("<ul") + html.count("<ol")
    # 文字密度 - 简化：检查段落数
    p_count = html.count("<p")
    return {
        "has_viewport_meta": has_viewport,
        "heading_count": h_count,
        "list_count": list_count,
        "paragraph_count": p_count,
        "mobile_readable": has_viewport and h_count >= 2 and (list_count + p_count) >= 3,
    }
