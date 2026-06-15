"""Thin content detection — 对齐 BYDFi 2026-05 Google 人工处置事故"""
from __future__ import annotations

import re


# === ① 联属网站低附加价值 ===
AFFILIATE_LINK_PATTERNS = [
    # 第三方联盟营销平台
    r"[?&](?:ref|aff|affiliate|partner|via|utm_source=affiliate)=",
    r"/aff/[\w-]+",
    r"/ref/[\w-]+",
    r"/r/[\w-]+\?",
    r"go\.[\w.]+\?",
    r"shrsl\.|ck\.com/|click\.linksynergy",
    # BYDFi / 交易所自家 referral 系统（精准对齐业务）
    r"[?&](?:invite|invite_code|invitecode|code|inviteCode|referrer|invitation)=",
    r"/register\?[^\s\"']*(?:code|invite)",
    r"/sign-?up\?[^\s\"']*(?:code|invite|ref)",
    r"[?&]utm_source=referral",
    r"[?&]utm_medium=affiliate",
    r"/r/\w{4,}",  # /r/{code}
    r"/i/\w{4,}",  # /i/{invite_code}
]


def affiliate_low_value_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    """检测联属链接堆砌 + 内容字数过少 = 内容贫乏的联属页"""
    html = raw_html or ""
    text = visible_text or ""
    # 1. 联属链接数量
    affiliate_link_count = 0
    for p in AFFILIATE_LINK_PATTERNS:
        affiliate_link_count += len(re.findall(p, html, re.IGNORECASE))
    # 2. 推荐/促销关键词
    promo_keywords = ["sign up", "register", "claim bonus", "get reward", "limited time",
                      "立即注册", "立即领取", "新人福利", "推荐返佣", "邀请码", "邀请奖励"]
    promo_hits = sum(1 for k in promo_keywords if k.lower() in text.lower() or k in text)
    # 3. 内容字数（剔除空白）
    body_chars = len(re.sub(r"\s+", "", text))
    # 4. CTA 按钮数（boilerplate 信号）
    cta_count = html.lower().count("<button") + html.count('class="btn') + html.count("class='btn")
    return {
        "affiliate_link_count": affiliate_link_count,
        "promo_keyword_hits": promo_hits,
        "body_char_count": body_chars,
        "cta_count": cta_count,
        "affiliate_to_content_ratio": round(affiliate_link_count / max(1, body_chars / 100), 2),
        "suspect_thin_affiliate": (
            (affiliate_link_count >= 3 and body_chars < 1500) or
            (promo_hits >= 5 and body_chars < 2000)
        ),
    }


# === ② 复制 / 抄袭 / 低质转载（启发式 + LLM judge）===
def plagiarism_check(visible_text: str | None = None, title: str | None = None,
                     page_url: str | None = None, **_) -> dict:
    """启发式：检测转载/抄袭信号 + 缺乏原创分析（适配 BYDFi 列表页 / 聚合页 / 子页面）"""
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True}
    text_l = text.lower()
    body_chars = len(re.sub(r"\s+", "", text))

    # 转载信号（拓展）
    republish_signals = {
        "has_source_citation": any(k in text_l for k in ["source:", "来源：", "来源:", "转自", "via:", "原文：", "原文链接",
                                                            "reposted from", "reproduced from"]),
        "has_news_agency": any(k in text_l for k in ["reuters", "bloomberg", "coindesk", "cointelegraph", "the block",
                                                       "decrypt", "forbes crypto", "wsj", "ft.com",
                                                       "路透社", "彭博社", "新浪财经", "凤凰财经"]),
        "blockquote_density": text.count("\u201c") + text.count("\u201d") + text.count("「") + text.count("」"),
        "has_repost_url": "reposted" in text_l or "republished" in text_l,
        # 聚合页特征：大量短卡片 + 重复结构
        "aggregator_signal": (text.count("Read more") + text.count("更多") + text.count("阅读更多")) >= 5,
        # H3/H4 标题数 / 字数比 → 短卡片密度高
        "card_density_per_kchars": 0,  # 在外层填入
    }
    # 缺原创信号（拓展）
    no_original_signals = {
        "no_first_person": not any(k in text for k in ["我们认为", "我们分析", "我们测试", "我们的观点",
                                                         "we analyzed", "we tested", "in our view",
                                                         "BYDFi believes", "we believe", "our take",
                                                         "经我们", "据我们"]),
        "no_data_charts": not any(k in text_l for k in ["chart", "图表", "数据显示", "分析数据",
                                                          "according to our data", "our data shows"]),
    }
    # 触发条件（任一）：转载信号 + 缺乏第一人称分析
    # 修：no_original 从 AND 改 OR — 列表/聚合页缺第一人称就够
    no_original = no_original_signals["no_first_person"]  # 主信号
    suspect = no_original and (
        republish_signals["has_source_citation"] or
        republish_signals["has_news_agency"] or
        republish_signals["has_repost_url"] or
        republish_signals["aggregator_signal"] or
        republish_signals["blockquote_density"] >= 10
    )
    return {
        "body_chars": body_chars,
        "republish_signals": republish_signals,
        "no_original_signals": no_original_signals,
        "suspect_plagiarism_no_value_add": suspect,
        "requires_llm_check": True,
    }


# === ⑤ 单页附加价值低 ===
def low_value_page_check(raw_html: str | None = None, visible_text: str | None = None, **_) -> dict:
    """单页 thin content 检测：字数 + 信息密度 + 独立观点"""
    text = visible_text or ""
    if not text:
        return {"insufficient_content": True, "suspect_low_value": True}
    body_chars = len(re.sub(r"\s+", "", text))
    # 句子数
    sentences = re.split(r"[.!?。！？\n]", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    # 独立观点信号（剔除品牌自引用，只算真分析动词 + 第一人称表达）
    # Bug 修：之前把 "BYDFi" 文本计入 original_signals，导致自家页面永远不算 thin
    analysis_verbs = [
        # 中文真分析
        "我们认为", "我们分析", "我们发现", "我们测试", "我们的观点", "我们的看法",
        "经分析", "经测算", "实际测试", "在我们看来", "据我们", "我们建议",
        # 英文真分析（不含 BYDFi/we 单独词）
        "we believe", "we analyzed", "we tested", "we found", "we measured",
        "our analysis shows", "our research", "our take is", "in our view",
        "based on our", "after testing", "we recommend", "we observed",
    ]
    original_signals = sum(1 for k in analysis_verbs if k in text or k.lower() in text.lower())
    # 章节数（h2/h3）
    html = raw_html or ""
    heading_count = html.lower().count("<h2") + html.lower().count("<h3")
    # 信息密度评分
    score = 0
    if body_chars >= 1500: score += 2
    elif body_chars >= 800: score += 1
    if len(sentences) >= 15: score += 1
    if original_signals >= 1: score += 2
    if heading_count >= 3: score += 1
    # Google "附加价值低" 核心 = 信息密度低（原创信号/千字 < 0.3 = 无真分析的营销/堆量页）
    kchars = max(1, body_chars / 1000)
    original_density = original_signals / kchars  # 每千字真分析动词数
    sparse_original = original_density < 0.3 and body_chars >= 600  # 有内容但缺真分析
    return {
        "body_char_count": body_chars,
        "sentence_count": len(sentences),
        "original_signal_count": original_signals,
        "heading_count": heading_count,
        "original_density_per_kchar": round(original_density, 2),
        "value_score": score,
        "sparse_original_analysis": sparse_original,
        "suspect_low_value": score < 3 or sparse_original,
    }
