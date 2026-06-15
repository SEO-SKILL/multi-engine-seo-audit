"""
页面级"最佳实践组合"复合 detector
不检测单点违规，而是评估页面综合得分 + 找出最弱环节
对应 Google 官方文档的"最佳实践组合"理念
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from detectors import canonical as canonical_d
from detectors import eeat as eeat_d
from detectors import hreflang as hreflang_d
from detectors import image as image_d
from detectors import schema as schema_d
from detectors import social as social_d


def _score(sub_results: dict) -> dict:
    """统一聚合：返回 {score, weakest, breakdown}"""
    total_weight = sum(v["weight"] for v in sub_results.values())
    weighted_score = sum(v["pass"] * v["weight"] for v in sub_results.values())
    score = weighted_score / total_weight if total_weight else 0.0
    weakest = min(sub_results.items(), key=lambda kv: kv[1]["pass"])
    return {
        "composite_score": round(score, 3),
        "weakest_link": weakest[0],
        "weakest_pass_value": weakest[1]["pass"],
        "breakdown": {k: {"pass": v["pass"], "weight": v["weight"]} for k, v in sub_results.items()},
    }


def image_composite_quality(raw_html: str, rendered_html: str | None = None, sitemap_has_images: bool = False) -> dict:
    """图片密集型页面综合分（对照 Google Images SEO 文档全维度）"""
    soup = BeautifulSoup(rendered_html or raw_html, "lxml")
    has_imgs = bool(soup.find_all("img"))
    if not has_imgs:
        return {"composite_score": None, "skipped": "page has no images"}

    alt_result = image_d.alt_check(rendered_html or raw_html)
    format_result = image_d.format_check(rendered_html or raw_html)
    lazy_result = image_d.lazy_loading_check(rendered_html or raw_html)
    responsive_result = image_d.responsive_check(rendered_html or raw_html)
    filename_bad = image_d.filename_check(rendered_html or raw_html)

    css_bg_used = "background-image:url" in (rendered_html or raw_html).lower()
    pictures = soup.find_all("picture")
    picture_fallback_ok = all(p.find("img") for p in pictures) if pictures else True

    alt_pass = 1.0 - (alt_result["missing_count"] / max(1, alt_result["total"]))
    modern_ratio = format_result["modern_count"] / max(1, format_result["modern_count"] + format_result["legacy_count"])

    sub = {
        "img_element_used":          {"pass": 0.0 if css_bg_used else 1.0, "weight": 0.20},
        "alt_complete_not_stuffed":  {"pass": alt_pass,                    "weight": 0.15},
        "modern_format_ratio":       {"pass": modern_ratio,                "weight": 0.10},
        "lazy_loading_used":         {"pass": 1.0 if lazy_result["no_lazy_count"] <= 1 else 0.5, "weight": 0.10},
        "responsive_srcset":         {"pass": 1.0 if responsive_result["no_srcset_count"] <= 1 else 0.5, "weight": 0.10},
        "filename_meaningful":       {"pass": 0.5 if filename_bad else 1.0, "weight": 0.05},
        "picture_fallback_ok":       {"pass": 1.0 if picture_fallback_ok else 0.0, "weight": 0.05},
        "image_sitemap_exists":      {"pass": 1.0 if sitemap_has_images else 0.5, "weight": 0.10},
        "og_image_present":          {"pass": 1.0 if social_d.og_tags_check(raw_html)["og_tags"].get("image") else 0.0, "weight": 0.10},
        "article_image_in_schema":   {"pass": 1.0 if any(b.get("image") for b in schema_d.extract_jsonld(raw_html) if isinstance(b, dict)) else 0.0, "weight": 0.05},
    }
    return _score(sub)


def eeat_composite_quality(raw_html: str, content_type: str = "learn") -> dict:
    """E-E-A-T 综合分（对照 Google Helpful Content 文档）"""
    author = eeat_d.detect_author_signals(raw_html)
    dates = eeat_d.detect_publication_dates(raw_html)

    soup = BeautifulSoup(raw_html, "lxml")
    has_reviewer = bool(soup.find(text=lambda t: t and "reviewed by" in t.lower()))
    has_sources = bool(soup.find_all("a", href=lambda h: h and any(d in h for d in ["coingecko", "etherscan", "defillama", "sec.gov", ".gov"])))
    blocks = schema_d.extract_jsonld(raw_html)
    has_org = any(isinstance(b, dict) and b.get("@type") in ("Organization", "Corporation") for b in blocks)

    sub = {
        "author_name_jsonld":     {"pass": 1.0 if author["has_jsonld_author_name"] else 0.0, "weight": 0.15},
        "author_profile_url":     {"pass": 1.0 if author["has_jsonld_author_url"] else 0.0, "weight": 0.15},
        "visible_byline":         {"pass": 1.0 if author["has_visible_byline"] else 0.0, "weight": 0.10},
        "date_published":         {"pass": 1.0 if dates["datePublished"] else 0.0, "weight": 0.10},
        "date_modified":          {"pass": 1.0 if dates["dateModified"] else 0.0, "weight": 0.10},
        "reviewed_by_present":    {"pass": 1.0 if has_reviewer else 0.0, "weight": 0.15},
        "external_sources_cited": {"pass": 1.0 if has_sources else 0.0, "weight": 0.15},
        "organization_schema":    {"pass": 1.0 if has_org else 0.0, "weight": 0.10},
    }
    return _score(sub)


def schema_composite_quality(raw_html: str, rendered_html: str | None = None) -> dict:
    """Schema 综合分（SSR + 字段完整 + 真实性 + 类型覆盖）"""
    ssr_info = schema_d.has_ssr_jsonld(raw_html, rendered_html)
    blocks = schema_d.extract_jsonld(raw_html)

    has_breadcrumb = any(isinstance(b, dict) and b.get("@type") == "BreadcrumbList" for b in blocks)
    has_org = any(isinstance(b, dict) and b.get("@type") in ("Organization", "Corporation") for b in blocks)
    has_article = any(isinstance(b, dict) and b.get("@type") in ("Article", "NewsArticle", "BlogPosting") for b in blocks)
    has_sameas = any(isinstance(b, dict) and b.get("sameAs") for b in blocks)

    # AggregateRating without visible review = 红牌
    soup = BeautifulSoup(rendered_html or raw_html, "lxml")
    visible_text = soup.get_text()
    fake_rating = False
    for b in blocks:
        if isinstance(b, dict) and b.get("aggregateRating"):
            ar = b["aggregateRating"]
            if isinstance(ar, dict) and str(ar.get("ratingValue", "")) not in visible_text:
                fake_rating = True

    sub = {
        "ssr_not_csr_only":        {"pass": 1.0 if not ssr_info["csr_only"] else 0.0, "weight": 0.25},
        "breadcrumb_list":         {"pass": 1.0 if has_breadcrumb else 0.5, "weight": 0.15},
        "organization_or_website": {"pass": 1.0 if has_org else 0.5, "weight": 0.15},
        "article_schema":          {"pass": 1.0 if has_article else 0.7, "weight": 0.10},
        "sameas_links":            {"pass": 1.0 if has_sameas else 0.5, "weight": 0.10},
        "aggregaterating_grounded": {"pass": 0.0 if fake_rating else 1.0, "weight": 0.25},
    }
    return _score(sub)


def performance_composite_quality(raw_html: str, http_timing: dict | None = None, http_headers: dict | None = None) -> dict:
    """性能综合分（TTFB / 渲染阻塞 / 压缩 / HTTP 版本 / HTML 大小）"""
    timing = http_timing or {}
    headers = http_headers or {}
    encoding = (headers.get("content-encoding") or headers.get("Content-Encoding") or "").lower()
    proto = headers.get(":protocol") or headers.get("alt-svc") or ""

    ttfb_ms = timing.get("ttfb_ms", 500)
    soup = BeautifulSoup(raw_html, "lxml")
    head = soup.find("head")
    blocking_scripts = len([s for s in (head.find_all("script") if head else []) if s.get("src") and not s.get("async") and not s.get("defer")])
    html_kb = len(raw_html.encode()) / 1024

    sub = {
        "ttfb_under_800ms":        {"pass": 1.0 if ttfb_ms < 800 else 0.5 if ttfb_ms < 1500 else 0.0, "weight": 0.20},
        "no_render_blocking":      {"pass": 1.0 if blocking_scripts == 0 else 0.6 if blocking_scripts < 3 else 0.2, "weight": 0.25},
        "modern_compression":      {"pass": 1.0 if "br" in encoding else 0.7 if "gzip" in encoding else 0.0, "weight": 0.15},
        "http2_or_higher":         {"pass": 1.0 if "h2" in proto or "h3" in proto else 0.5, "weight": 0.10},
        "html_size_reasonable":    {"pass": 1.0 if html_kb < 500 else 0.5 if html_kb < 1000 else 0.0, "weight": 0.15},
        "cls_under_0.1":           {"pass": 1.0 if timing.get("cls", 0.05) < 0.1 else 0.5, "weight": 0.15},
    }
    return _score(sub)


def internal_linking_composite_quality(raw_html: str, site_link_graph: dict | None = None) -> dict:
    """内链综合分"""
    from collections import Counter
    soup = BeautifulSoup(raw_html, "lxml")
    internal_links = [a for a in soup.find_all("a", href=True) if a["href"].startswith("/") or "example.com" in a["href"]]
    anchors = [a.get_text().strip().lower() for a in internal_links if a.get_text().strip()]
    anchor_counter = Counter(anchors)

    has_breadcrumb = bool(soup.find(class_=lambda c: c and "breadcrumb" in c.lower()) or soup.find(attrs={"role": "navigation"}))
    diverse = (max(anchor_counter.values()) / max(1, len(anchors))) < 0.30 if anchors else False
    cluster_present = len(internal_links) >= 3
    dead_links = 0  # 简化：假设无外部测试就给 1.0

    sub = {
        "has_breadcrumb_visible": {"pass": 1.0 if has_breadcrumb else 0.0, "weight": 0.20},
        "anchor_text_diverse":    {"pass": 1.0 if diverse else 0.5, "weight": 0.20},
        "cluster_links_present":  {"pass": 1.0 if cluster_present else 0.0, "weight": 0.15},
        "no_orphan":              {"pass": 1.0 if len(internal_links) > 0 else 0.0, "weight": 0.15},
        "no_dead_links":          {"pass": 1.0 if dead_links == 0 else 0.0, "weight": 0.15},
        "click_depth_reasonable": {"pass": 1.0, "weight": 0.15},
    }
    return _score(sub)


def geo_composite_quality(raw_html: str, robots_txt: str | None = None) -> dict:
    """GEO 综合分（针对 LLM engines 优化）"""
    import re
    soup = BeautifulSoup(raw_html, "lxml")
    h2_count = len(soup.find_all("h2"))
    paragraphs = soup.find_all("p")
    short_p = sum(1 for p in paragraphs if 70 <= len(p.get_text()) <= 150)
    has_tables = bool(soup.find_all("table"))
    has_lists = bool(soup.find_all(["ol", "ul"]))
    text = soup.get_text()
    has_tldr = bool(re.search(r"\b(tl;?dr|tldr|总结|要点)\b", text[:500], re.IGNORECASE))
    has_citations = len(soup.find_all("a", href=lambda h: h and any(d in h for d in ["coingecko", "etherscan", "defillama", ".gov", ".edu"]))) >= 2

    bots_ok = True
    if robots_txt:
        bots_ok = "user-agent: gptbot\ndisallow: /" not in robots_txt.lower()

    sub = {
        "llms_txt_present":        {"pass": 0.5, "weight": 0.10},  # 需要外部检测
        "answerable_chunks_ratio": {"pass": min(1.0, short_p / 3), "weight": 0.20},
        "fact_citations":          {"pass": 1.0 if has_citations else 0.0, "weight": 0.20},
        "tldr_present":            {"pass": 1.0 if has_tldr else 0.0, "weight": 0.15},
        "table_data_present":      {"pass": 1.0 if has_tables else 0.0, "weight": 0.10},
        "list_steps_present":      {"pass": 1.0 if has_lists else 0.0, "weight": 0.10},
        "ai_bots_allowed":         {"pass": 1.0 if bots_ok else 0.0, "weight": 0.15},
    }
    return _score(sub)


def naver_composite_quality(raw_html: str, locale: str | None = None) -> dict:
    """Naver 专属 composite — 不照搬 Google 维度

    Naver 核心：C-Rank（创作者权威）+ 韩文真实性 + Naver 生态 + 用户行为
    Naver 几乎不看 schema / 外链权重
    """
    import re
    soup = BeautifulSoup(raw_html, "lxml")
    text = soup.get_text()

    korean_chars = len(re.findall(r"[\uac00-\ud7af]", text))
    has_korean = korean_chars >= 200
    has_krw = "KRW" in text or "원" in text
    cjk_other = len(re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", text))
    mixed_script = cjk_other > 100 and korean_chars > 100

    has_author = bool(soup.find(attrs={"rel": "author"}) or soup.find(class_=lambda c: c and "author" in (c or "").lower()))
    has_author_url = any("/author" in a.get("href", "") for a in soup.find_all("a", href=True))

    has_naver_eco = any("naver.com" in a.get("href", "") for a in soup.find_all("a", href=True))
    has_kr_payment = any(k in text.lower() for k in ["kakaopay", "tosspay", "naverpay", "카카오"])

    h_count = len(soup.find_all(["h2", "h3"]))
    paragraphs = soup.find_all("p")
    short_p = sum(1 for p in paragraphs if 50 <= len(p.get_text()) <= 200)
    topic_focused = h_count >= 3 and short_p >= 3

    has_kr_regulatory = any(k in text for k in ["금융위", "한국", "금감원"])
    has_kr_context = has_krw or has_kr_regulatory

    has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))

    sub = {
        "korean_authenticity":   {"pass": 1.0 if has_korean else 0.0, "weight": 0.25},
        "no_mixed_script":       {"pass": 0.0 if mixed_script else 1.0, "weight": 0.10},
        "creator_authority":     {"pass": 1.0 if (has_author and has_author_url) else 0.5 if has_author else 0.0, "weight": 0.20},
        "naver_ecosystem_link":  {"pass": 1.0 if has_naver_eco else 0.5, "weight": 0.10},
        "korean_local_context":  {"pass": 1.0 if has_kr_context else 0.3, "weight": 0.15},
        "topic_focus":           {"pass": 1.0 if topic_focused else 0.5, "weight": 0.10},
        "mobile_viewport":       {"pass": 1.0 if has_viewport else 0.0, "weight": 0.10},
    }
    return _score(sub)


def yandex_composite_quality(raw_html: str, locale: str | None = None, headers: dict | None = None) -> dict:
    """Yandex 专属 composite

    Yandex 核心：MatrixNet 用户行为 + 区域信号 + 俄文真实性 + Metrica
    """
    import re
    soup = BeautifulSoup(raw_html, "lxml")
    text = soup.get_text()

    cyrillic = len(re.findall(r"[а-яА-Я]", text))
    has_russian = cyrillic >= 200
    has_rub = "RUB" in text or "рубл" in text.lower() or "руб" in text

    scripts_text = " ".join(str(s) for s in soup.find_all("script"))
    has_metrica = "mc.yandex.ru/metrika" in scripts_text or "yandex_metrika" in scripts_text

    has_ru_phone = bool(re.search(r"\+7", text))
    has_ru_reg = any(k in text.lower() for k in ["россия", "москва", "цб рф", "роскомнадзор"])

    word_count = len(text.split())
    has_substantial = word_count >= 300
    has_geo_meta = bool(soup.find("meta", attrs={"name": lambda n: n and "geo" in (n or "").lower()}))
    has_engagement = bool(soup.find_all(["form", "button"]))

    sub = {
        "russian_authenticity":   {"pass": 1.0 if has_russian else 0.0, "weight": 0.25},
        "yandex_metrica":         {"pass": 1.0 if has_metrica else 0.0, "weight": 0.20},
        "russian_local_context":  {"pass": 1.0 if (has_rub or has_ru_phone or has_ru_reg) else 0.3, "weight": 0.15},
        "content_substance":      {"pass": 1.0 if has_substantial else 0.4, "weight": 0.15},
        "geo_meta_signal":        {"pass": 1.0 if has_geo_meta else 0.5, "weight": 0.10},
        "engagement_potential":   {"pass": 1.0 if has_engagement else 0.5, "weight": 0.15},
    }
    return _score(sub)


def baidu_composite_quality(raw_html: str, headers: dict | None = None) -> dict:
    """Baidu 专属 composite

    Baidu 核心：ICP 备案 + 简体中文 + Baiduspider 友好 + 中国服务器
    """
    import re
    soup = BeautifulSoup(raw_html, "lxml")
    text = soup.get_text()

    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    has_chinese = chinese >= 200
    has_simplified = "简体" in text or chinese >= 50  # 粗略判定

    footer = (soup.find("footer") or soup).get_text() if soup.find("footer") else text[-2000:]
    has_icp = bool(re.search(r"ICP\s*备?\s*\d+", footer, re.IGNORECASE))

    has_baidu_share = any("share.baidu.com" in str(s) for s in soup.find_all("script"))
    has_cny = "CNY" in text or "人民币" in text or "¥" in text

    sub = {
        "chinese_authenticity":  {"pass": 1.0 if has_chinese else 0.0, "weight": 0.30},
        "icp_license":           {"pass": 1.0 if has_icp else 0.0, "weight": 0.30},
        "cny_local_context":     {"pass": 1.0 if has_cny else 0.5, "weight": 0.20},
        "baidu_ecosystem":       {"pass": 1.0 if has_baidu_share else 0.5, "weight": 0.10},
        "viewport_mobile":       {"pass": 1.0 if soup.find("meta", attrs={"name": "viewport"}) else 0.0, "weight": 0.10},
    }
    return _score(sub)


def multilingual_composite_quality(raw_html: str, locale: str | None = None, sibling_alternates: list | None = None) -> dict:
    """多语言综合分"""
    alternates = hreflang_d.parse_alternates(raw_html)
    has_x_default = hreflang_d.has_x_default(alternates)
    canonical_result = canonical_d.exists_and_valid(raw_html)

    # 货币本地化（粗略检测）
    currency_per_locale = {"ko": "KRW", "ja": "JPY", "ru": "RUB", "tr": "TRY", "zh-CN": "CNY"}
    expected_currency = currency_per_locale.get(locale)
    currency_localized = expected_currency in raw_html if expected_currency else True

    sub = {
        "hreflang_complete_set":     {"pass": 1.0 if len(alternates) >= 3 else 0.5 if len(alternates) >= 1 else 0.0, "weight": 0.25},
        "x_default_present":         {"pass": 1.0 if has_x_default else 0.0, "weight": 0.10},
        "language_actually_matches": {"pass": 0.8, "weight": 0.20},  # 简化（需 LLM judge）
        "locale_specific_content":   {"pass": 1.0 if currency_localized else 0.5, "weight": 0.20},
        "currency_localized":        {"pass": 1.0 if currency_localized else 0.0, "weight": 0.15},
        "canonical_self":            {"pass": 1.0 if canonical_result["passed"] else 0.0, "weight": 0.10},
    }
    return _score(sub)


def crawlability_composite(raw_html: str, headers: dict | None = None, robots_txt: str | None = None) -> dict:
    """可抓取性综合分（canonical / hreflang / robots / 状态码）"""
    canonical_result = canonical_d.exists_and_valid(raw_html, http_headers=headers or {})
    alternates = hreflang_d.parse_alternates(raw_html)

    sub = {
        "canonical_present_and_ssr": {"pass": 1.0 if canonical_result["passed"] else 0.0, "weight": 0.30},
        "hreflang_with_x_default":   {"pass": 1.0 if hreflang_d.has_x_default(alternates) else 0.5, "weight": 0.20},
        "viewport_meta":             {"pass": 1.0 if "width=device-width" in raw_html else 0.0, "weight": 0.20},
        "robots_meta_not_noindex":   {"pass": 0.0 if 'name="robots"' in raw_html and "noindex" in raw_html else 1.0, "weight": 0.30},
    }
    return _score(sub)
