"""Platform 推广中心专属 detector — referral / partnership / invite 业务规则"""
from __future__ import annotations

import re
from urllib.parse import urlparse


PROMO_URL_PATTERNS = [
    r"/partnership", r"/invite", r"/referral", r"/affiliate", r"/promo",
    r"/bonus", r"/airdrop", r"/campaign", r"/event",
]

PLATFORM_REFERRAL_LINK_PATTERNS = [
    r"[?&](?:invite|invitecode|invite_code|inviteCode|code|referrer|invitation|ref)=",
    r"/register\?[^\s\"']*(?:code|invite|ref)",
    r"/sign-?up\?[^\s\"']*(?:code|invite|ref)",
    r"[?&]utm_source=referral",
    r"[?&]utm_medium=affiliate",
    r"/r/\w{4,}",
    r"/i/\w{4,}",
]

PLATFORM_VALUE_PROPS = [
    # 中文
    "手续费", "0.026", "0.06", "储备金", "100%储备", "流动性", "深度",
    "kyc", "实名", "24/7", "客服", "杠杆", "100x", "200x",
    # 英文
    "lowest fee", "0.026%", "0.06%", "proof of reserves", "1:1 backing",
    "liquidity", "depth", "kyc", "24/7 support", "leverage",
    "regulated", "licensed",
]


def _is_promo_page(page_url: str) -> bool:
    if not page_url:
        return False
    path = urlparse(page_url).path.lower()
    return any(re.search(p, path) for p in PROMO_URL_PATTERNS)


def thin_promo_check(page_url: str | None = None, raw_html: str | None = None,
                    visible_text: str | None = None, **_) -> dict:
    """推广中心页内容贫乏检测：只触发推广类 URL，避免误报普通页"""
    if not _is_promo_page(page_url):
        return {"is_promo_page": False, "checked": False}
    html = raw_html or ""
    text = visible_text or ""
    # 推广特征：referral 链接 + CTA 按钮多
    referral_count = 0
    for p in PLATFORM_REFERRAL_LINK_PATTERNS:
        referral_count += len(re.findall(p, html, re.IGNORECASE))
    cta_count = html.lower().count("<button") + html.count('class="btn') + html.count("class='btn")
    # 内容信号：教程 / 收益示例 / 数据
    has_tutorial = any(k in text.lower() or k in text for k in
                      ["how to", "step 1", "tutorial", "guide", "教程", "步骤", "第一步", "如何"])
    has_earnings_example = any(k in text for k in ["示例", "例如", "假设", "example",
                                                     "case study", "calculation"]) and \
                          bool(re.search(r"\d+\s*(?:%|USDT|USD|元|％)", text))
    has_faq = "faq" in text.lower() or "常见问题" in text or "よくある質問" in text
    body_chars = len(re.sub(r"\s+", "", text))
    # 推广页 thin 判定（多条独立触发）：
    # ① 体积 < 1500 字符（活动页字数过少，典型 SPA 缺 SSR 或真的内容贫乏）
    # ② referral 链接 ≥ 2 + 无教程 / 收益示例
    # ③ 推广 URL pattern + 缺核心内容元素（tutorial + earnings + faq 都缺）
    thin_by_size = body_chars < 1500
    thin_by_referral = (referral_count >= 2 or cta_count >= 4) and not (has_tutorial and (has_earnings_example or has_faq)) and body_chars < 3000
    thin_by_missing_content = not has_tutorial and not has_earnings_example and not has_faq and body_chars < 2000
    thin = thin_by_size or thin_by_referral or thin_by_missing_content
    return {
        "is_promo_page": True,
        "referral_link_count": referral_count,
        "cta_count": cta_count,
        "has_tutorial": has_tutorial,
        "has_earnings_example": has_earnings_example,
        "has_faq": has_faq,
        "body_char_count": body_chars,
        "suspect_thin_promo": thin,
    }


def code_density_check(raw_html: str | None = None, **_) -> dict:
    """单页 referral code / invite link 密度检测"""
    html = raw_html or ""
    total = 0
    for p in PLATFORM_REFERRAL_LINK_PATTERNS:
        total += len(re.findall(p, html, re.IGNORECASE))
    # 独立 code 数（不重复）
    codes = set(re.findall(r"[?&](?:code|invite|ref)=([\w-]{3,20})", html, re.IGNORECASE))
    return {
        "referral_link_count": total,
        "unique_code_count": len(codes),
        "suspect_code_spam": total >= 8 or len(codes) >= 5,
    }


def value_prop_check(visible_text: str | None = None, raw_html: str | None = None, **_) -> dict:
    """推广页是否阐述 Platform 产品价值（手续费 / 安全 / 流动性等）"""
    text = (visible_text or "") + " " + (raw_html or "")
    text_l = text.lower()
    hits = [v for v in PLATFORM_VALUE_PROPS if v in text or v.lower() in text_l]
    return {
        "value_prop_hits": hits[:8],
        "value_prop_count": len(hits),
        "missing_value_prop": len(hits) < 2,
    }


def promo_template_check(page_url: str | None = None, visible_text: str | None = None,
                        page_corpus: list | None = None, **_) -> dict:
    """多个推广页内容雷同（doorway 信号 — 需要 corpus 比对）"""
    if not _is_promo_page(page_url):
        return {"is_promo_page": False, "checked": False}
    if not page_corpus:
        return {"is_promo_page": True, "requires_corpus_for_template_compare": True}
    # 简化：用本页 H1 + 第一段哈希；corpus 中比对
    return {"is_promo_page": True, "requires_corpus_compare": True}
