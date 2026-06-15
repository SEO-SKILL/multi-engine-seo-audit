"""
technical-agent — 技术 SEO 硬规则
对应能力 #13 URL/Sitemap + 部分 #1 Schema
"""
from __future__ import annotations

import time

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Evidence,
    Finding,
    FindingSource,
    Metrics,
    PatchHint,
    Platform,
    Severity,
)
from detectors import canonical as canonical_detect
from detectors import eeat as eeat_detect
from detectors import hreflang as hreflang_detect
from detectors import schema as schema_detect


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    findings: list[Finding] = []

    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")
    rendered_html = crawler_artifacts.get("rendered_html")
    headers = crawler_artifacts.get("headers", {})
    page_url = input_.target.url or ""

    if not raw_html:
        return AgentOutput(
            trace_id=input_.trace_id,
            agent="technical",
            status=AgentStatus.SKIPPED,
            errors=[],
            next_actions=["crawler-agent 未提供 raw_html"],
        )

    findings += _check_canonical(raw_html, rendered_html, headers, page_url, input_.trace_id)
    findings += _check_hreflang(raw_html, input_.trace_id)
    findings += _check_jsonld_ssr(raw_html, rendered_html, input_.trace_id)
    findings += _check_eeat_basic(raw_html, input_.trace_id)
    findings += _check_google_2024_signals(raw_html, page_url, input_.trace_id)
    findings += _check_hidden_content(raw_html, input_.trace_id)
    findings += _check_quality_signals(raw_html, page_url, input_.trace_id, headers=headers)
    findings += _check_web_vitals(raw_html, headers, input_.trace_id)
    findings += _check_thin_content_platform_incident(raw_html, page_url, input_.trace_id)
    findings += _check_platform_promo_page(raw_html, page_url, input_.trace_id)
    findings += _check_manual_action_signals(raw_html, page_url, crawler_artifacts, input_.trace_id)
    findings += _check_generic_unhooked(raw_html, rendered_html, headers, page_url, input_.trace_id, [f.id for f in findings], locale=(input_.target.locale or ""))

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = None
    for sev in severity_order:
        if any(f.severity == sev for f in findings):
            severity_max = sev
            break

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="technical",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _check_canonical(raw_html: str, rendered_html: str | None, headers: dict, page_url: str, trace_id: str) -> list[Finding]:
    result = canonical_detect.exists_and_valid(raw_html, rendered_html, headers)
    findings: list[Finding] = []
    if not result["passed"]:
        for issue in result["issues"]:
            findings.append(Finding(
                id="google.canonical.missing" if "缺失" in issue else "google.canonical.chain-too-long",
                source=FindingSource.HARD_RULE,
                platform=Platform.GOOGLE,
                severity=Severity.HIGH,
                confidence=0.95,
                evidence=Evidence(url=page_url, text_snippet=issue),
                recommendation="添加 canonical 标签到 <head> 且必须 SSR 输出",
                patch_hint=PatchHint(template="patches/add_canonical.diff.j2", priority="P0"),
            ))
    return findings


def _check_hreflang(raw_html: str, trace_id: str) -> list[Finding]:
    alternates = hreflang_detect.parse_alternates(raw_html)
    findings: list[Finding] = []
    if alternates and not hreflang_detect.has_x_default(alternates):
        findings.append(Finding(
            id="google.hreflang.x-default-handling",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.LOW,
            confidence=0.88,
            evidence=Evidence(text_snippet=f"hreflang 数量: {len(alternates)}，缺 x-default"),
            recommendation="添加 hreflang='x-default' 兜底",
        ))
    return findings


def _check_jsonld_ssr(raw_html: str, rendered_html: str | None, trace_id: str) -> list[Finding]:
    findings: list[Finding] = []
    ssr_info = schema_detect.has_ssr_jsonld(raw_html, rendered_html)
    if ssr_info["csr_only"]:
        findings.append(Finding(
            id="google.schema.jsonld-csr-only",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.HIGH,
            confidence=0.95,
            evidence=Evidence(text_snippet=f"raw_count=0, rendered_count={ssr_info['rendered_count']}, rendered_types={ssr_info['rendered_types']}"),
            recommendation="JSON-LD 必须 SSR 输出，不能仅 CSR 后注入",
            patch_hint=PatchHint(template="patches/move_jsonld_to_ssr.diff.j2", priority="P0"),
        ))
    return findings


def _check_google_2024_signals(raw_html: str, page_url: str, trace_id: str) -> list[Finding]:
    """Google 2024 新规则：site reputation / scaled AI / AI Overviews"""
    from detectors import google_2024 as g24
    from bs4 import BeautifulSoup
    findings: list[Finding] = []
    soup = BeautifulSoup(raw_html or "", "lxml")
    visible_text = soup.get_text(" ", strip=True)[:50000]

    # Site Reputation Abuse
    r = g24.site_reputation_abuse_check(page_url, visible_text, raw_html)
    if r.get("suspect_parasite_seo"):
        findings.append(Finding(
            id="google.spam-2024.site-reputation-abuse",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.BLOCKER,
            confidence=0.78,
            evidence=Evidence(text_snippet=f"parasite risk score={r.get('parasite_seo_risk_score')} signals={r.get('signals')}"),
            recommendation="检查是否在主域名下挂载第三方 / 联盟营销 / 优惠码 / 寄生内容 — 2024 Google 已开始 manual action",
        ))

    # Scaled AI Content
    r = g24.scaled_ai_content_check(visible_text)
    if r.get("suspect_ai_generated"):
        findings.append(Finding(
            id="google.spam-2024.scaled-ai-content",
            source=FindingSource.LLM_JUDGE,
            platform=Platform.GOOGLE,
            severity=Severity.HIGH,
            confidence=0.70,
            evidence=Evidence(text_snippet=f"ai_phrase_hits={r.get('ai_phrase_hits')} sentences={r.get('sentence_count')}"),
            recommendation="内容疑似 LLM 量产，应加入编辑加工 + 第一手经验 + 数据 — 2024 spam policy 目标",
        ))

    # AI Overviews 可问答块
    r = g24.answerable_block_check(raw_html, visible_text)
    if not r.get("passed"):
        findings.append(Finding(
            id="google.ai-overviews.answerable-block-missing",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.MEDIUM,
            confidence=0.70,
            evidence=Evidence(text_snippet=f"answerable_score={r.get('answerable_score')}/4"),
            recommendation="加 FAQPage / HowTo schema + 问句标题 + 列表，提升 AI Overviews 引用概率",
        ))

    # AI Overviews citation signals
    r = g24.ai_citation_signals_check(raw_html, visible_text)
    if r.get("weak_citation"):
        findings.append(Finding(
            id="google.ai-overviews.author-and-citation-signals",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.MEDIUM,
            confidence=0.72,
            evidence=Evidence(text_snippet=f"citation_score={r.get('citation_score')}/4 signals={r.get('signals')}"),
            recommendation="补 JSON-LD Article + 作者 + datePublished + 引用源链接，提升 AI Overviews 引用概率",
        ))

    # Reviews System：in-depth
    r = g24.in_depth_review_check(visible_text)
    if r.get("shallow_review"):
        findings.append(Finding(
            id="google.reviews-system.in-depth-evaluation-missing",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.MEDIUM,
            confidence=0.65,
            evidence=Evidence(text_snippet=f"depth_score={r.get('depth_score')}/5"),
            recommendation="评测内容应包含：优缺点对比 + 定量数据 + 第一人称体验 + 截图 — Google Reviews System Update 要求",
        ))

    return findings


def _check_generic_unhooked(raw_html: str, rendered_html: str | None, headers: dict, page_url: str,
                            trace_id: str, already_hit_ids: list[str], locale: str = "") -> list[Finding]:
    """万能 runner：遍历所有 home/all 适用规则，按 detector.fn 动态调用，trigger 就出 Finding"""
    import yaml
    from pathlib import Path
    from bs4 import BeautifulSoup
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _generic_detector_runner import run_generic_detectors, build_ctx
    from detectors.schema import extract_jsonld

    SKILL_ROOT = Path(__file__).parent.parent
    rules: list[dict] = []
    for f in (SKILL_ROOT / "rules" / "platforms").rglob("*.yaml"):
        try:
            d = yaml.safe_load(f.read_text())
            if isinstance(d, dict):
                rules.extend(d.get("rules", []))
        except Exception:
            continue

    soup = BeautifulSoup(raw_html or "", "lxml")
    visible_text = soup.get_text(" ", strip=True)[:50000]
    try:
        jsonld_parsed = extract_jsonld(raw_html or "")
    except Exception:
        jsonld_parsed = []

    ctx = build_ctx(raw_html or "", rendered_html or raw_html or "", headers or {},
                   page_url or "", soup, jsonld_parsed, visible_text)
    return run_generic_detectors(rules, ctx, set(already_hit_ids), locale=locale)


def _check_manual_action_signals(raw_html: str, page_url: str, crawler_artifacts: dict, trace_id: str) -> list[Finding]:
    """Manual Action 防复发 — 接入 6 个核心 detector"""
    from detectors import cloaking, security, ugc, linking
    findings: list[Finding] = []
    per_ua = crawler_artifacts.get("per_ua", {}) or {}
    rendered_dom = crawler_artifacts.get("rendered_html") or raw_html

    # 1. UA Cloaking
    try:
        r = cloaking.ua_content_diff(per_ua)
        if isinstance(r, dict) and (r.get("topic_mismatch") or (r.get("text_similarity") is not None and r.get("text_similarity") < 0.7)):
            findings.append(Finding(
                id="google.manual-action.cloaking-content-mismatch",
                source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.BLOCKER,
                confidence=0.78,
                evidence=Evidence(text_snippet=str(r)[:200]),
                recommendation="多 UA 抓取内容不一致 = Cloaking",
            ))
    except Exception:
        pass

    # 2. Hidden text via cloaking module（用真返回字段 `suspicious`）
    try:
        r = cloaking.hidden_text_check(rendered_dom)
        if isinstance(r, dict) and r.get("suspicious"):
            findings.append(Finding(
                id="google.manual-action.hidden-text",
                source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
                confidence=0.72,
                evidence=Evidence(text_snippet=str(r)[:200]),
                recommendation="检测到隐藏文本（Manual Action 高发）",
            ))
    except Exception:
        pass

    # 3. Hacked content（`suspicious` 字段）
    try:
        r = security.hacked_content_check(raw_html)
        if isinstance(r, dict) and r.get("suspicious"):
            findings.append(Finding(
                id="google.manual-action.hacked-content",
                source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.BLOCKER,
                confidence=0.80,
                evidence=Evidence(text_snippet=str(r)[:200]),
                recommendation="疑似被黑内容（注入垃圾关键词/恶意脚本）",
            ))
    except Exception:
        pass

    # 4. UGC spam（`spam_suspect` 字段）
    try:
        r = ugc.spam_pattern_check(raw_html)
        if isinstance(r, dict) and r.get("spam_suspect"):
            findings.append(Finding(
                id="google.manual-action.user-generated-spam",
                source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.MEDIUM,
                confidence=0.65,
                evidence=Evidence(text_snippet=str(r)[:200]),
                recommendation="UGC 区疑似 spam",
            ))
    except Exception:
        pass

    # 5. 付费外链（detector 返回 total / paid_signal_count）
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw_html or "", "lxml")
        out_links = [{"href": a.get("href", ""), "text": a.get_text(strip=True), "rel": a.get("rel", [])}
                     for a in soup.find_all("a", href=True) if a.get("href", "").startswith("http")]
        r = linking.paid_outbound_check(out_links)
        if isinstance(r, dict) and (r.get("paid_signal_count", 0) >= 2 or r.get("suspect_paid")):
            findings.append(Finding(
                id="google.manual-action.unnatural-outbound-links",
                source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
                confidence=0.65,
                evidence=Evidence(text_snippet=str(r)[:200]),
                recommendation="可疑付费外链 / 不自然出链",
            ))
    except Exception:
        pass

    return findings


def _check_platform_promo_page(raw_html: str, page_url: str, trace_id: str) -> list[Finding]:
    """Platform 推广中心专属检测（/partnership /invite-friends /referral-program）"""
    from detectors import platform_promo as bp
    from bs4 import BeautifulSoup
    findings: list[Finding] = []
    soup = BeautifulSoup(raw_html or "", "lxml")
    visible_text = soup.get_text(" ", strip=True)[:50000]

    # 1. thin promo page
    r = bp.thin_promo_check(page_url, raw_html, visible_text)
    if r.get("suspect_thin_promo"):
        findings.append(Finding(
            id="platform.referral.promo-page-thin-content",
            source=FindingSource.HARD_RULE, platform=Platform.PLATFORM, severity=Severity.HIGH,
            confidence=0.78,
            evidence=Evidence(text_snippet=f"referral_links={r.get('referral_link_count')} cta={r.get('cta_count')} tutorial={r.get('has_tutorial')} earnings={r.get('has_earnings_example')} chars={r.get('body_char_count')}"),
            recommendation="推广页只有 CTA + referral 链接，缺独立教程 / 收益示例 / FAQ — 对应 Google 事故原因 ①",
        ))

    # 2. code density spam
    r = bp.code_density_check(raw_html)
    if r.get("suspect_code_spam"):
        findings.append(Finding(
            id="platform.referral.code-density-spam",
            source=FindingSource.HARD_RULE, platform=Platform.PLATFORM, severity=Severity.MEDIUM,
            confidence=0.85,
            evidence=Evidence(text_snippet=f"referral_links={r.get('referral_link_count')} unique_codes={r.get('unique_code_count')}"),
            recommendation="单页 referral code 数量异常高 — Google 视为 link manipulation",
        ))

    # 3. value prop missing（仅推广页适用）
    if bp._is_promo_page(page_url):
        r = bp.value_prop_check(visible_text, raw_html)
        if r.get("missing_value_prop"):
            findings.append(Finding(
                id="platform.referral.value-proposition-missing",
                source=FindingSource.HARD_RULE, platform=Platform.PLATFORM, severity=Severity.MEDIUM,
                confidence=0.70,
                evidence=Evidence(text_snippet=f"value_prop_hits={r.get('value_prop_hits')} count={r.get('value_prop_count')}/2"),
                recommendation="推广页应明示 Platform 产品价值（手续费 0.026% / 储备金 / 流动性 / KYC 速度）",
            ))

    return findings


def _check_thin_content_platform_incident(raw_html: str, page_url: str, trace_id: str) -> list[Finding]:
    """对齐 Platform 2026-05 Google 人工处置事故 5 大原因"""
    from detectors import thin_content as tc
    from bs4 import BeautifulSoup
    findings: list[Finding] = []
    soup = BeautifulSoup(raw_html or "", "lxml")
    visible_text = soup.get_text(" ", strip=True)[:50000]
    title = soup.title.get_text() if soup.title else ""

    # ① 联属网站低附加价值
    r = tc.affiliate_low_value_check(raw_html, visible_text)
    if r.get("suspect_thin_affiliate"):
        findings.append(Finding(
            id="google.thin-content.affiliate-low-value",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.BLOCKER,
            confidence=0.78,
            evidence=Evidence(text_snippet=f"affiliate_links={r.get('affiliate_link_count')} promo_hits={r.get('promo_keyword_hits')} chars={r.get('body_char_count')}"),
            recommendation="联属链接 / 推荐链接堆砌但内容字数过少 — 加独立分析 / 评测 / 数据。Platform 2026-05 事故同款。",
        ))

    # ② 抄袭转载（启发式）— 降为 high，启发式信号易在论坛聚合页误触发，保留预警但不阻塞
    r = tc.plagiarism_check(visible_text, title, page_url)
    if r.get("suspect_plagiarism_no_value_add"):
        findings.append(Finding(
            id="google.duplicate-content.plagiarism-no-value-add",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.68,
            evidence=Evidence(text_snippet=f"republish={r.get('republish_signals')} no_original={r.get('no_original_signals')}"),
            recommendation="疑似低价值转载（有引用源但无第一手分析）— 加入独立观点 + Platform 数据。Platform 2026-05 事故同款。",
        ))

    # ⑤ 单页附加价值低
    r = tc.low_value_page_check(raw_html, visible_text)
    if r.get("suspect_low_value"):
        findings.append(Finding(
            id="google.thin-content.low-value-single-page",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.72,
            evidence=Evidence(text_snippet=f"chars={r.get('body_char_count')} sentences={r.get('sentence_count')} original_signals={r.get('original_signal_count')} value_score={r.get('value_score')}/6"),
            recommendation="单页字数少 + 无独立观点 + 章节少 = 附加价值低。补 Platform 第一人称分析 / 数据 / 章节。",
        ))

    return findings


def _check_hidden_content(raw_html: str, trace_id: str) -> list[Finding]:
    from detectors import hidden_content as hc
    findings: list[Finding] = []
    r = hc.display_none_text_check(raw_html)
    if r.get("suspect_hidden_text"):
        findings.append(Finding(
            id="google.hidden-text.css-display-none",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.BLOCKER,
            confidence=0.80, evidence=Evidence(text_snippet=f"hidden_blocks={r.get('hidden_block_count')} samples={r.get('samples')}"),
            recommendation="移除 display:none / visibility:hidden 中含关键词的文本块（manual action 高发）",
        ))
    r = hc.same_color_check(raw_html)
    if r.get("suspect_same_color"):
        findings.append(Finding(
            id="google.hidden-text.same-color-background",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.BLOCKER,
            confidence=0.78, evidence=Evidence(text_snippet=f"match_count={r.get('same_color_match_count')}"),
            recommendation="同色文本（白底白字 / 黑底黑字）必须改色或移除",
        ))
    r = hc.off_screen_check(raw_html)
    if r.get("suspect_off_screen"):
        findings.append(Finding(
            id="google.hidden-text.off-screen-positioning",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.72, evidence=Evidence(text_snippet=f"hits={r.get('off_screen_hit_count')}"),
            recommendation="移除 left:-9999px / text-indent:-9999px 等屏外隐藏",
        ))
    r = hc.zero_font_check(raw_html)
    if r.get("suspect_zero_font"):
        findings.append(Finding(
            id="google.hidden-text.zero-font-size",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.85, evidence=Evidence(text_snippet=f"count={r.get('zero_font_count')}"),
            recommendation="font-size:0 / 1px 文字视为隐藏，必须移除",
        ))
    r = hc.hidden_links_check(raw_html)
    if r.get("suspect_hidden_links"):
        findings.append(Finding(
            id="google.hidden-links.anchor-text-spam",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.70, evidence=Evidence(text_snippet=f"suspect_count={r.get('suspect_anchor_count')}/{r.get('anchor_count')}"),
            recommendation="检查空 anchor / 单标点 anchor — Manual Action 风险",
        ))
    return findings


def _check_quality_signals(raw_html: str, page_url: str, trace_id: str, headers: dict | None = None) -> list[Finding]:
    from detectors import spam_quality as sq
    from bs4 import BeautifulSoup
    findings: list[Finding] = []
    soup = BeautifulSoup(raw_html or "", "lxml")
    visible_text = soup.get_text(" ", strip=True)[:50000]
    title = (soup.title.get_text() if soup.title else "")
    # Doorway template (单页启发式)
    r = sq.doorway_template_check(raw_html, visible_text)
    if r.get("suspect_doorway"):
        findings.append(Finding(
            id="google.doorway.thin-template-pages",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.65,
            evidence=Evidence(text_snippet=f"chars={r.get('body_length')} boilerplate={r.get('boilerplate_hits')} h1_repeat={r.get('h1_repeat_ratio_per_kchars')}"),
            recommendation="模板化短内容 + boilerplate 文案多 = 疑似 doorway。补独立内容 + 减模板话术",
        ))
    # Keyword stuffing
    r = sq.keyword_stuffed_landing_check(visible_text, title)
    if r.get("suspect_keyword_stuffing"):
        findings.append(Finding(
            id="google.doorway.keyword-stuffed-landing",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.78, evidence=Evidence(text_snippet=f"overused={r.get('overused_keywords')}"),
            recommendation="关键词出现频率异常高（≥15 次）— 视为 doorway / 关键词堆砌",
        ))
    # UGC spam
    r = sq.ugc_spam_check(raw_html, visible_text)
    if r.get("suspect_ugc_spam"):
        findings.append(Finding(
            id="google.ugc-spam.unmoderated-comments",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.MEDIUM,
            confidence=0.62, evidence=Evidence(text_snippet=f"spam_keyword_hits={r.get('spam_keyword_hits')}"),
            recommendation="评论区疑似 spam，必须加 rel=ugc 或 nofollow + 审核",
        ))
    # Lazy loading
    r = sq.lazy_loading_check(raw_html)
    if r.get("first_5_misuse_lazy"):
        findings.append(Finding(
            id="google.lazy-loading.misused-or-missing",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.LOW,
            confidence=0.78, evidence=Evidence(text_snippet=f"first_5_lazy={r.get('first_5_lazy_count')}"),
            recommendation="首屏图片不应用 loading='lazy'（影响 LCP），首屏外图片应用",
        ))
    elif r.get("later_missing_lazy"):
        findings.append(Finding(
            id="google.lazy-loading.misused-or-missing",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.LOW,
            confidence=0.70, evidence=Evidence(text_snippet=f"later_lazy_ratio={r.get('later_lazy_ratio')}"),
            recommendation="首屏外图片应加 loading='lazy'，节省带宽",
        ))
    # Soft 404
    status = (headers or {}).get("__status_code")  # 占位
    r = sq.soft_404_check(raw_html, visible_text, status)
    if r.get("suspect_soft_404"):
        findings.append(Finding(
            id="google.soft-404.empty-or-not-found",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.MEDIUM,
            confidence=0.72, evidence=Evidence(text_snippet=f"phrases={r.get('matched_phrases')}"),
            recommendation="返回 200 但内容是 not found / 暂无数据 — 应返回真 404",
        ))
    # Pagination
    r = sq.pagination_check(raw_html, page_url)
    if r.get("needs_pagination_handling"):
        findings.append(Finding(
            id="google.pagination.next-prev-or-canonical",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.LOW,
            confidence=0.68,
            evidence=Evidence(text_snippet=f"paginated_url={r.get('is_paginated_url')} next/prev=miss"),
            recommendation="分页页面应有 canonical 指向自身或 view-all 页面",
        ))
    return findings


def _check_web_vitals(raw_html: str, headers: dict, trace_id: str) -> list[Finding]:
    from detectors import web_vitals as wv
    findings: list[Finding] = []
    r = wv.lcp_estimate(raw_html, headers)
    if r.get("suspect_slow_lcp"):
        findings.append(Finding(
            id="google.web-vitals.lcp-too-slow",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.HIGH,
            confidence=0.72, evidence=Evidence(text_snippet=f"blocking_css={r.get('blocking_css_count')} blocking_js={r.get('blocking_js_count')} score={r.get('estimated_lcp_score')}"),
            recommendation="减少 render-blocking CSS/JS + hero 图片加 fetchpriority=high",
        ))
    r = wv.cls_check(raw_html)
    if r.get("suspect_layout_shift"):
        findings.append(Finding(
            id="google.web-vitals.cls-layout-shift",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.MEDIUM,
            confidence=0.70, evidence=Evidence(text_snippet=f"dim_ratio={r.get('dim_ratio')} ({r.get('dimensioned_count')}/{r.get('media_count')})"),
            recommendation="所有 img/iframe 必须声明 width/height 防 CLS",
        ))
    r = wv.inp_estimate(raw_html)
    if r.get("suspect_slow_inp"):
        findings.append(Finding(
            id="google.web-vitals.inp-interactivity",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.MEDIUM,
            confidence=0.65, evidence=Evidence(text_snippet=f"3rd_party_js={r.get('third_party_script_count')} large_inline={r.get('large_inline_script_count')}"),
            recommendation="减少第三方 JS / 拆分大 inline JS 防 INP > 200ms",
        ))
    r = wv.ttfb_check(headers)
    if r.get("suspect_slow_ttfb"):
        findings.append(Finding(
            id="google.web-vitals.ttfb-server-slow",
            source=FindingSource.HARD_RULE, platform=Platform.GOOGLE, severity=Severity.MEDIUM,
            confidence=0.75, evidence=Evidence(text_snippet=f"cf_cache={r.get('cf_cache_status')} dur_ms={r.get('server_timing_dur_ms')}"),
            recommendation="启用 CDN edge cache（cf-cache-status=HIT）让 TTFB < 800ms",
        ))
    return findings


def _check_eeat_basic(raw_html: str, trace_id: str) -> list[Finding]:
    findings: list[Finding] = []
    author_signals = eeat_detect.detect_author_signals(raw_html)
    if author_signals["author_signals_score"] < 0.25:
        findings.append(Finding(
            id="google.eeat.author-attribution-missing",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.HIGH,
            confidence=0.92,
            evidence=Evidence(text_snippet=f"作者信号得分: {author_signals['author_signals_score']:.2f}"),
            recommendation="添加作者元数据（meta[name=author] / JSON-LD author / 可见 byline）",
            patch_hint=PatchHint(template="patches/add_author_metadata.diff.j2", priority="P1"),
        ))
    dates = eeat_detect.detect_publication_dates(raw_html)
    if not dates["datePublished"]:
        findings.append(Finding(
            id="google.eeat.publication-date-missing-or-stale",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.MEDIUM,
            confidence=0.93,
            evidence=Evidence(text_snippet="JSON-LD 缺 datePublished"),
            recommendation="添加 datePublished + dateModified",
        ))
    return findings
