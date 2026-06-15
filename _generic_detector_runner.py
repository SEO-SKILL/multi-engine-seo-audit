"""
万能 detector runner — 按 yaml `detector.fn` 动态调用，按 trigger condition 生成 Finding。

设计：约定每个 detector 输出 dict 含某个 'suspect_*' / 'passed' / 'has_*' 字段，
runner 通过预定义 trigger map 判定是否触发。
"""
from __future__ import annotations

import importlib
import re
from typing import Any
from urllib.parse import urlparse

from agents._schema import Evidence, Finding, FindingSource, Platform, Severity

# 字段名 → 触发判定（True 表示触发）
# 多数 detector 返回 {"suspicious": True/False} / {"suspect_*": True} / {"passed": False}
# 简化：默认遍历常见 trigger 字段
TRIGGER_FIELDS_POSITIVE = [  # field=True 触发
    "suspect_thin", "suspect_doorway", "suspect_templated", "suspect_hidden_text",
    "suspect_same_color", "suspect_off_screen", "suspect_zero_font", "suspect_hidden_links",
    "suspect_keyword_stuffing", "suspect_ugc_spam", "first_5_misuse_lazy", "later_missing_lazy",
    "suspect_soft_404", "needs_pagination_handling", "suspicious", "spam_suspect", "spam_detected",
    "suspect_paid", "suspect_ai_generated", "suspect_auto_generated", "suspect_low_value",
    "suspect_thin_promo", "suspect_code_spam", "missing_value_prop", "suspect_plagiarism_no_value_add",
    "weak_trust", "weak_citation", "shallow_review", "topic_mismatch", "mixed_honorific_suspect",
    "mixed_script_suspect", "over_optimized", "discloses_non_registration",
    # Will 9 兜底
    "suspect_no_analysis_signal", "suspect_weak_ymyl_signal", "deprecation_notice_required",
    "suspect_snippet_strategy_missing", "monitoring_setup_pending",
    # Manual action / 标题
    "suspect_appeal_unprepared", "suspect_weak_org_signal",
    # Meta description
    "suspect_missing_or_short", "suspect_bad_length",
    # 新 featured snippet
    "suspect_not_snippet_ready",
    # Deprecated schema
    "suspect_deprecated_faqpage", "suspect_deprecated_howto",
]
TRIGGER_FIELDS_NEGATIVE = [  # field=False 触发（即"未通过"）
    "passed", "is_https", "has_korean_chars", "has_yandex_metrica", "served_from_russia",
    "served_from_korea", "is_ru_tld", "has_russian_phone", "has_jpy_mention",
    "has_naver_verification", "mobile_friendly", "has_viewport_meta",
    "has_publication_date", "has_jsonld_datepublished",
    "has_authority_sources", "has_jp_cdn",
    "has_canonical", "has_x_default", "answerable_passed",
]


def _trigger(result: dict) -> bool:
    if not isinstance(result, dict):
        return False
    if result.get("checked") is False:
        return False
    if result.get("requires_external_data") or result.get("requires_corpus"):
        return False
    if result.get("requires_llm_check") and not any(k in result for k in TRIGGER_FIELDS_POSITIVE):
        return False
    for f in TRIGGER_FIELDS_POSITIVE:
        if result.get(f):
            return True
    for f in TRIGGER_FIELDS_NEGATIVE:
        if f in result and not result[f]:
            return True
    return False


def _platform_from_rid(rid: str) -> Platform:
    p = rid.split(".")[0]
    return {
        "google": Platform.GOOGLE, "bing": Platform.BING, "naver": Platform.NAVER,
        "yandex": Platform.YANDEX, "yahoo-jp": Platform.YAHOO_JAPAN,
    }.get(p, Platform.GOOGLE)


def _severity(sev_str: str) -> Severity:
    return {"blocker": Severity.BLOCKER, "high": Severity.HIGH, "medium": Severity.MEDIUM,
            "low": Severity.LOW, "info": Severity.INFO}.get((sev_str or "low").lower(), Severity.LOW)


def _build_kwargs(inputs: list[str], ctx: dict) -> dict:
    """根据 detector 声明的 inputs 名字从 ctx 取值"""
    kwargs = {}
    for k in inputs:
        if k in ctx:
            kwargs[k] = ctx[k]
    return kwargs


# 平台白名单：不区分 locale，所有审计都应跑
_PLATFORM_AGNOSTIC = {"shared", "platform", "all", ""}

# locale → 主平台 + Google 兜底
_LOCALE_PLATFORMS = {
    "en": {"google"}, "en-US": {"google"}, "en-GB": {"google"},
    "zh-CN": {"google"}, "zh-TW": {"google"},
    "ko": {"naver", "google"}, "ko-KR": {"naver", "google"},
    "ja": {"yahoo-jp", "google"}, "ja-JP": {"yahoo-jp", "google"},
    "ru": {"yandex", "google"}, "ru-RU": {"yandex", "google"},
    "vi": {"google"}, "tr": {"google"}, "pt": {"google"},
    "es": {"google"}, "es-ES": {"google"}, "pt-BR": {"google"},
}


def _applies_to_passes(rule: dict, active_platforms: set[str], locale: str) -> bool:
    """检查规则的 applies_to 是否匹配当前 (platforms, locale)。
    无 applies_to 字段 = 默认通用，放行。
    """
    at = rule.get("applies_to") or {}
    if not isinstance(at, dict):
        return True
    # platforms 过滤
    plats = at.get("platforms") or []
    if isinstance(plats, str):
        plats = [plats]
    if plats:
        plat_set = {str(p).lower().strip() for p in plats}
        # 含 agnostic 关键字 → 总是放行
        if plat_set & _PLATFORM_AGNOSTIC:
            pass
        elif not (plat_set & active_platforms):
            return False
    # locales 过滤
    locs = at.get("locales") or []
    if isinstance(locs, str):
        locs = [locs]
    if locs:
        loc_set = {str(l).lower().strip() for l in locs}
        if "all" in loc_set or "" in loc_set:
            return True
        # locale 前缀匹配：rule[ko] 匹配 ko / ko-KR；rule[ko-KR] 严格
        cur = (locale or "").lower().strip()
        cur_prefix = cur.split("-")[0]
        if cur not in loc_set and cur_prefix not in loc_set:
            return False
    return True


def _build_recommendation(rule: dict, result: dict) -> str:
    """生成精确 recommendation：优先用规则定义的 patch_hint / 显式 recommendation，再 fallback platform_impact"""
    # 1. 显式 recommendation 字段
    if rule.get("recommendation"):
        return str(rule["recommendation"])[:300]
    # 2. patch_hint 提示
    ph = rule.get("patch_hint", {}) or {}
    if isinstance(ph, dict) and ph.get("template"):
        return f"应用补丁模板: {ph['template']}（优先级 {ph.get('priority','P2')}）"
    # 3. tags 反推一句话提示
    tags = rule.get("tags", []) or []
    if "manual-action-risk" in tags or "manual-action" in tags:
        return f"⚠️ Manual Action 风险 — 立即修复（参考 source_doc）"
    if "spam-policy" in tags:
        return f"⚠️ Spam policy 违反 — 整改后申请复审"
    if "ymyl" in tags or "compliance" in tags:
        return f"⚠️ YMYL/合规底线 — 必须修复"
    # 4. platform_impact 首段
    bi = (rule.get("business_impact") or "").strip()
    if bi:
        first_line = bi.split("\n")[0].strip()
        return first_line[:300] if first_line else f"修复 {rule.get('id','规则')}"
    return f"修复 {rule.get('id','此规则')}（详见规则定义）"


def run_generic_detectors(rules: list[dict], ctx: dict, hooked_rule_ids: set[str],
                          locale: str = "", active_platforms: set[str] | None = None) -> list[Finding]:
    """
    遍历 rules，对每条规则：
    1. 跳过已被 hook 的（避免重复）
    2. 跳过同 rule_id 重复（按 rule_id 去重，保留 confidence 最高）
    3. **新增**：applies_to (platforms / locales) 不匹配则跳过 — 收敛广播触发
    4. 跳过需要 corpus / external 的
    5. 动态 import detector fn，按 inputs 解包 ctx 调用
    6. 用 _trigger 判定，触发就生成 Finding
    """
    # 确定当前活跃平台
    if active_platforms is None:
        active_platforms = _LOCALE_PLATFORMS.get(locale, {"google"})
    findings: list[Finding] = []
    seen_rids: set[str] = set()
    for r in rules:
        rid = r.get("id", "")
        if not rid or rid in hooked_rule_ids or rid in seen_rids:
            continue
        seen_rids.add(rid)
        # applies_to 平台 / locale 闭环过滤
        if not _applies_to_passes(r, active_platforms, locale):
            continue
        det = r.get("detector", {}) or {}
        fn_path = det.get("fn", "")
        if not fn_path or not fn_path.startswith("detectors."):
            continue
        inputs = det.get("inputs", []) or []
        # 跳过需要外部数据 / corpus
        if any(k in str(inputs).lower() for k in [
            "page_corpus", "sibling_urls", "gsc", "metrica", "webmaster",
            "fetched_status_per_alternate", "fetched_alternate", "canonical_per_alternate",
            "log_files", "ga_data", "crux", "page_inventory", "site_inventory",
            "content_similarity_matrix", "url_set", "site_graph", "internal_link_graph",
            "topic_clusters", "computed_styles", "fetch_results_per_region",
            "fetch_results_per_ua", "googlebot_render_comparison", "hydration_timing",
            "ssl_cert", "fetched_canonical_target",
        ]):
            continue
        # 动态 import
        try:
            parts = fn_path.split(".")  # ["detectors", "module", "func"]
            if len(parts) < 3:
                continue
            mod_name = "detectors." + parts[1]
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, parts[-1], None)
            if not callable(fn):
                continue
            # 调用 detector
            kwargs = _build_kwargs(inputs, ctx)
            result = fn(**kwargs) if kwargs else fn()
        except Exception:
            continue
        if not _trigger(result):
            continue
        findings.append(Finding(
            id=rid,
            source=FindingSource.HARD_RULE,
            platform=_platform_from_rid(rid),
            severity=_severity(r.get("severity")),
            confidence=float(r.get("confidence_default", 0.65)),
            evidence=Evidence(text_snippet=str(result)[:200]),
            recommendation=_build_recommendation(r, result),
        ))
    return findings


def build_ctx(raw_html: str, rendered_dom: str, headers: dict, page_url: str,
              soup, jsonld_parsed: list, visible_text: str) -> dict:
    """构造 detector 通用 ctx — 覆盖大部分 inputs 名字"""
    import re as _re
    # 提取常见 input
    images = []
    for img in soup.find_all("img"):
        images.append({"src": img.get("src", ""), "alt": img.get("alt"), "title": img.get("title"),
                      "width": img.get("width"), "height": img.get("height")})
    image_urls = [i["src"] for i in images if i.get("src")]
    head_meta = {}
    if soup.head:
        for m in soup.head.find_all("meta"):
            n = m.get("name") or m.get("property") or m.get("http-equiv")
            if n:
                head_meta[n.lower()] = m.get("content", "")
    head_scripts = [{"src": s.get("src"), "async": s.has_attr("async"), "defer": s.has_attr("defer")}
                   for s in (soup.head.find_all("script") if soup.head else [])]
    page_scripts = [str(s) for s in soup.find_all("script") if s.string]
    internal_links = [{"href": a.get("href", ""), "text": a.get_text(strip=True), "rel": a.get("rel", [])}
                     for a in soup.find_all("a", href=True) if a.get("href", "").startswith("/")]
    outbound_links = [{"href": a.get("href", ""), "text": a.get_text(strip=True), "rel": a.get("rel", [])}
                     for a in soup.find_all("a", href=True) if a.get("href", "").startswith("http")]
    canonical_tag = soup.find("link", rel="canonical")
    canonical_url = canonical_tag.get("href") if canonical_tag else None
    title = soup.title.get_text() if soup.title else ""
    h1_list = [h.get_text(strip=True) for h in soup.find_all("h1")]
    headings = [h.get_text(strip=True) for h in soup.find_all(re.compile("^h[1-6]$"))]
    picture_elements = [str(p) for p in soup.find_all("picture")]
    svg_elements = [str(s) for s in soup.find_all("svg")]
    videos = []
    for v in soup.find_all("video"):
        videos.append({"src": v.get("src"), "poster": v.get("poster")})
    # robots meta
    robots_meta_tag = soup.find("meta", attrs={"name": "robots"})
    meta_robots = robots_meta_tag.get("content", "") if robots_meta_tag else ""
    # URL params
    parsed = urlparse(page_url or "")
    url_params = parsed.query
    domain = parsed.netloc
    # JSONLD raw - 用 jsonld_parsed
    return {
        "raw_html": raw_html,
        "rendered_dom": rendered_dom,
        "rendered_html": rendered_dom,
        "visible_text": visible_text,
        "headers": headers,
        "http_headers": headers,
        "page_url": page_url,
        "url": page_url,
        "domain": domain,
        "url_params": url_params,
        "title": title,
        "h1": h1_list[0] if h1_list else "",
        "h1_list": h1_list,
        "headings": headings,
        "images": images,
        "image_urls": image_urls,
        "head_meta": head_meta,
        "head_scripts": head_scripts,
        "page_scripts": page_scripts,
        "internal_links": internal_links,
        "outbound_links": outbound_links,
        "canonical_url": canonical_url,
        "raw_canonical": canonical_url,
        "rendered_canonical": canonical_url,
        "picture_elements": picture_elements,
        "svg_elements": svg_elements,
        "videos": videos,
        "meta_robots": meta_robots,
        "x_robots_tag_header": headers.get("x-robots-tag", "") if isinstance(headers, dict) else "",
        "robots_txt": "",  # 单页 audit 通常没抓 robots.txt
        "jsonld": jsonld_parsed,
        "jsonld_parsed": jsonld_parsed,
        "page_content": visible_text,
        "head": str(soup.head) if soup.head else "",
        "dom_metadata": head_meta,
        "dom_components": {},
        "page_metadata": head_meta,
        "redirect_history": [],  # 需 follow_redirects 数据
        "lazy_load_strategy": None,
        "primary_keyword": None,
    }
