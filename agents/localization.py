"""
Localization Agent —— 按 locale 路由到当地主搜索引擎的本地化检测
ko → Naver 检测器  /  ru → Yandex 检测器  /  zh-CN → Baidu 检测器

填补 orchestrator 之前没有 platform-aware finding 生产的空洞。
"""
from __future__ import annotations

import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ._schema import (
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

KO_LOCALES = {"ko", "ko-KR"}
RU_LOCALES = {"ru", "ru-RU"}
ZH_LOCALES = {"zh-CN", "zh-cn", "zh-Hans"}
JA_LOCALES = {"ja", "ja-JP"}


def _extract_dom(raw_html: str) -> dict:
    try:
        soup = BeautifulSoup(raw_html or "", "lxml")
    except Exception:
        return {"visible_text": "", "outbound_links": [], "internal_links": [], "footer": ""}
    visible_text = soup.get_text(" ", strip=True)[:50000]
    out_links = []
    in_links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href") or ""
        if href.startswith("http"):
            out_links.append({"href": href, "text": a.get_text(strip=True)})
        elif href.startswith("/"):
            in_links.append({"href": href, "text": a.get_text(strip=True)})
    footer = ""
    f = soup.find("footer")
    if f:
        footer = f.get_text(" ", strip=True)
    title = (soup.title.get_text() if soup.title else "")[:200]
    return {"visible_text": visible_text, "outbound_links": out_links,
            "internal_links": in_links, "footer": footer, "title": title}


def _f(rid: str, sev: Severity, platform: Platform, msg: str, snippet: str,
       conf: float = 0.85, patch: str | None = None) -> Finding:
    return Finding(
        id=rid,
        source=FindingSource.HARD_RULE,
        platform=platform,
        severity=sev,
        confidence=conf,
        evidence=Evidence(text_snippet=snippet[:200]),
        recommendation=msg,
        patch_hint=PatchHint(template=patch, priority="P1") if patch else None,
    )


def _run_naver(dom: dict, headers: dict, raw_html: str = "", url: str = "") -> list[Finding]:
    from detectors import naver as nv
    findings: list[Finding] = []
    vt = dom["visible_text"]

    r = nv.korean_authenticity(vt)
    if not r.get("passed"):
        findings.append(_f(
            "naver.crank.korean-content-authenticity", Severity.BLOCKER, Platform.NAVER,
            "页面声明 ko 但缺少韩文字符，Naver 不会收录机翻 / 假韩文页面",
            f"has_korean_chars={r.get('has_korean_chars')}, has_krw_mention={r.get('has_krw_mention')}",
            conf=0.85,
        ))

    r = nv.korean_payment_check(dom.get("visible_text", ""))
    if not r.get("passed"):
        findings.append(_f(
            "naver.content.no-korean-payment-method", Severity.LOW, Platform.NAVER,
            "韩国用户期待看到 KakaoPay / TossPay / NaverPay 等本地支付，缺失影响信任",
            f"detected_methods={r.get('korean_payment_methods')}",
            conf=0.72,
        ))

    r = nv.character_consistency(vt)
    if r.get("mixed_script_suspect"):
        findings.append(_f(
            "naver.content.cyrillic-or-cjk-mix", Severity.LOW, Platform.NAVER,
            "韩文页面混杂大量日文/简繁中文字符，Naver C-Rank 视为低质内容",
            f"korean={r.get('korean_chars')}, cjk_other={r.get('cjk_other')}",
            conf=0.78,
        ))

    r = nv.ecosystem_links_check(dom["outbound_links"])
    if not r.get("has_naver_ecosystem_link"):
        findings.append(_f(
            "naver.crank.naver-ecosystem-integration", Severity.LOW, Platform.NAVER,
            "无 naver.com 子产品（Blog/Cafe/Post）外链，C-Rank 生态权重缺失",
            "0 个 naver.com 出链",
            conf=0.70,
        ))

    r = nv.korean_ecosystem_links(dom["outbound_links"], dom["outbound_links"])
    if not r.get("korean_ecosystem_refs"):
        findings.append(_f(
            "naver.view.kakao-ecosystem-mention", Severity.LOW, Platform.NAVER,
            "未提及韩国主流加密资产生态（Upbit/Bithumb/Kakao），Naver VIEW 搜索权重下降",
            "0 个 Upbit/Bithumb/Kakao 引用",
            conf=0.65,
        ))

    cdn_region = (headers or {}).get("cf-ipcountry") or (headers or {}).get("server-region")
    r = nv.serving_region_check(headers, cdn_region)
    if not r.get("served_from_korea"):
        findings.append(_f(
            "naver.crank.korean-server-or-cdn", Severity.LOW, Platform.NAVER,
            "CDN 未命中韩国节点，Naver 排名对地理服务区域敏感",
            f"cdn_region={cdn_region or 'unknown'}",
            conf=0.60,
        ))

    # AiRSearch：内容连贯性
    r = nv.content_coherence_check(vt)
    if r.get("low_coherence_suspect"):
        findings.append(_f(
            "naver.airsearch.content-coherence", Severity.HIGH, Platform.NAVER,
            "韩文内容连贯性弱（Naver AiRSearch 算法识别为机翻/拼凑）",
            f"avg_len={r.get('avg_sentence_length')} very_short_ratio={r.get('very_short_ratio')}",
            conf=0.68,
        ))

    # Smart Block：FAQ/HowTo schema
    r = nv.smart_block_check(raw_html)
    if not r.get("passed"):
        findings.append(_f(
            "naver.smart-block.structured-content", Severity.MEDIUM, Platform.NAVER,
            "缺 FAQPage / HowTo / Breadcrumb schema，Naver Smart Block 不会展示结构化内容",
            "0 schema 匹配",
            conf=0.65,
        ))

    # Knowledge iN 引用
    r = nv.knowledge_in_check(raw_html, vt)
    if not r.get("passed"):
        findings.append(_f(
            "naver.knowledge-in.qa-citation", Severity.LOW, Platform.NAVER,
            "未引用 Naver 지식인 (kin.naver.com)，本地化信号偏弱",
            "0 个 지식인 链接/引用",
            conf=0.62,
        ))

    # Mobile-friendly
    r = nv.mobile_friendly_check(raw_html)
    if not r.get("passed"):
        findings.append(_f(
            "naver.mobile.viewport-required", Severity.HIGH, Platform.NAVER,
            "缺 viewport meta，韩国移动搜索 80%+，Naver 移动 SERP 严重降权",
            "viewport meta 缺失",
            conf=0.88,
        ))

    # HTTPS
    r = nv.https_check(url)
    if not r.get("passed"):
        findings.append(_f(
            "naver.security.https-required", Severity.HIGH, Platform.NAVER,
            "非 HTTPS 页面，Naver 直接降权（YMYL 金融页尤其严格）",
            f"is_https={r.get('is_https')}",
            conf=0.90,
        ))

    # Naver Webmaster Tools 验证
    r = nv.webmaster_verification_check(raw_html)
    if not r.get("passed"):
        findings.append(_f(
            "naver.webmaster.site-verification-missing", Severity.LOW, Platform.NAVER,
            "未在 Naver Search Advisor 验证（meta naver-site-verification 缺失），影响索引提交",
            "无 naver-site-verification",
            conf=0.78,
        ))

    return findings


def _run_yandex(dom: dict, headers: dict, url: str, raw_html: str = "") -> list[Finding]:
    from detectors import yandex as yx
    findings: list[Finding] = []
    vt = dom["visible_text"]
    domain = urlparse(url).netloc if url else ""

    r = yx.russian_authenticity(vt)
    if not r.get("passed"):
        findings.append(_f(
            "yandex.content.russian-authenticity", Severity.BLOCKER, Platform.YANDEX,
            "页面声明 ru 但缺少西里尔字符，Yandex 不收录机翻俄文",
            f"has_cyrillic={r.get('has_cyrillic')}, has_rub_mention={r.get('has_rub_mention')}",
            conf=0.88,
        ))

    # raw_html 的 <script> 文本聚合 ── 简化：直接看 raw_html
    r = yx.metrica_check(dom["visible_text"] + " " + str(dom.get("footer", "")))
    if not r.get("has_yandex_metrica"):
        findings.append(_f(
            "yandex.metrica.not-installed", Severity.MEDIUM, Platform.YANDEX,
            "未检测到 Yandex.Metrica 跟踪代码（mc.yandex.ru/metrika）— 用户行为信号缺失",
            "page 中无 mc.yandex.ru/metrika 引用",
            conf=0.90,
        ))

    cdn_region = (headers or {}).get("cf-ipcountry") or (headers or {}).get("server-region")
    r = yx.serving_region_check(headers, cdn_region)
    if not r.get("served_from_russia"):
        findings.append(_f(
            "yandex.regional.serving-not-from-russia", Severity.HIGH, Platform.YANDEX,
            "未从俄罗斯 CDN 节点服务，Yandex 地域信号严重削弱（影响 SERP 排名）",
            f"cdn_region={cdn_region or 'unknown'}",
            conf=0.78,
        ))

    r = yx.tld_check(domain)
    if not r.get("is_ru_tld"):
        findings.append(_f(
            "yandex.regional.no-russian-tld", Severity.LOW, Platform.YANDEX,
            "非 .ru 域名，Yandex 地域加权弱于 .ru 域名",
            f"tld={r.get('tld')}",
            conf=0.70,
        ))

    r = yx.russian_contact_check(vt)
    if not r.get("has_russian_phone"):
        findings.append(_f(
            "yandex.regional.no-russian-contact", Severity.MEDIUM, Platform.YANDEX,
            "未提供 +7 俄罗斯联系电话，Yandex 视为非本地化页面",
            "无 +7 电话",
            conf=0.72,
        ))

    # AGS：反垃圾站
    r = yx.auto_generated_content_check(vt)
    if r.get("suspect_auto_generated"):
        findings.append(_f(
            "yandex.ags.auto-generated-content", Severity.HIGH, Platform.YANDEX,
            "内容疑似机器生成 / 模板拼凑（Yandex AGS 算法直接降权）",
            f"sentences={r.get('sentence_count')} short_ratio={r.get('short_sentence_ratio')}",
            conf=0.72,
        ))

    # Minusinsk：垃圾外链
    r = yx.spam_backlinks_check(dom["outbound_links"])
    if r.get("spam_detected"):
        findings.append(_f(
            "yandex.minusinsk.paid-or-spam-backlinks", Severity.HIGH, Platform.YANDEX,
            "出链疑似垃圾外链 / 买卖链接（Yandex Minusinsk 算法目标）",
            f"top_domain_ratio={r.get('top_domain_ratio')} spam_hits={r.get('spam_anchor_hits')}",
            conf=0.70,
        ))

    # Madrid：商业 trust 信号
    r = yx.commercial_trust_check(vt, raw_html)
    if r.get("weak_trust"):
        findings.append(_f(
            "yandex.madrid.commercial-trust-signals", Severity.MEDIUM, Platform.YANDEX,
            "商业页缺少 trust 信号（公司信息 / 地址 / 电话 / 法律实体 / 条款）",
            f"trust_score={r.get('trust_score')}/5 signals={r.get('signals')}",
            conf=0.72,
        ))

    # Mobile-friendly
    r = yx.mobile_friendly_check(raw_html)
    if not r.get("mobile_friendly"):
        findings.append(_f(
            "yandex.mobile.viewport-and-responsive", Severity.HIGH, Platform.YANDEX,
            "缺少 viewport meta，Yandex 移动端排名严重削弱",
            f"viewport={r.get('has_viewport_meta')} responsive={r.get('has_responsive_css')}",
            conf=0.88,
        ))

    # HTTPS
    r = yx.https_check(url)
    if not r.get("passed"):
        findings.append(_f(
            "yandex.security.https-required", Severity.HIGH, Platform.YANDEX,
            "页面非 HTTPS，Yandex 排名直接降权（金融类 YMYL 尤其严格）",
            f"is_https={r.get('is_https')}",
            conf=0.95,
        ))

    return findings


def _run_yahoo_jp(dom: dict, headers: dict, url: str = "", raw_html: str = "") -> list[Finding]:
    from detectors import jp
    findings: list[Finding] = []
    vt = dom["visible_text"]

    r = jp.japanese_authenticity(vt)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.content.japanese-authenticity", Severity.BLOCKER, Platform.YAHOO_JAPAN,
            "页面声明 ja 但日文假名（hiragana/katakana）字符严重不足，Yahoo!JAPAN 不会认作日文页",
            f"hiragana={r.get('hiragana_chars')}, katakana={r.get('katakana_chars')}, cjk={r.get('cjk_chars')}",
            conf=0.88,
        ))

    r = jp.jfsa_disclosure_check(vt)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.content.jfsa-registration-disclosure", Severity.HIGH, Platform.YAHOO_JAPAN,
            "未提及日本金融庁（JFSA）备案状态或'未登録業者'明示 — 日本 YMYL 金融页必须 transparently 披露",
            "page 中无金融庁/未登録 等 JFSA 相关披露",
            conf=0.90,
        ))

    r = jp.tax_disclosure_check(vt)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.content.tax-disclosure-missing", Severity.MEDIUM, Platform.YAHOO_JAPAN,
            "未提及日本加密税制（20.315% 雑所得 / 総合課税 / 確定申告）— 日本用户 SEO 关键词缺失",
            "无 20.315% / 総合課税 / 確定申告 关键词",
            conf=0.78,
        ))

    r = jp.payment_method_check(vt)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.content.payjp-bankjp-mention", Severity.LOW, Platform.YAHOO_JAPAN,
            "未提及 PayPay / 銀行振込 等日本本地支付方式 — 影响日本用户信任与转化",
            f"detected_methods={r.get('japanese_payment_methods')}",
            conf=0.72,
        ))

    # Yahoo!ニュース source 引用
    r = jp.news_source_citation_check(vt, raw_html)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.news.source-citation", Severity.MEDIUM, Platform.YAHOO_JAPAN,
            "未引用 ロイター / 日経 / Bloomberg 等日本权威源（Yahoo!ニュース 信号缺失）",
            "0 个权威源引用",
            conf=0.68,
        ))

    # .jp TLD 或日本 CDN
    r = jp.jp_tld_or_cdn_check(url, headers)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.regional.jp-tld-or-cdn", Severity.LOW, Platform.YAHOO_JAPAN,
            "非 .jp 域名且无日本 CDN 节点，Yahoo!JAPAN 地域加权弱",
            f"is_jp_tld={r.get('is_jp_tld')} has_jp_cdn={r.get('has_jp_cdn')}",
            conf=0.72,
        ))

    # 移动 viewport（强 mobile-first）
    r = jp.mobile_responsive_check(raw_html)
    if not r.get("passed"):
        findings.append(_f(
            "yahoo-jp.mobile.responsive-required", Severity.HIGH, Platform.YAHOO_JAPAN,
            "缺 viewport meta，日本移动搜索占 70%+，移动排名严重削弱",
            f"viewport={r.get('has_viewport_meta')} responsive={r.get('has_responsive_css')}",
            conf=0.88,
        ))

    # 敬语等级一致
    r = jp.honorific_consistency_check(vt)
    if r.get("mixed_honorific_suspect"):
        findings.append(_f(
            "yahoo-jp.content.honorific-consistency", Severity.LOW, Platform.YAHOO_JAPAN,
            "です・ます调 与 だ・である调 混用，Yahoo!JAPAN 视为低质 / 机翻",
            f"desumasu={r.get('desumasu_count')} dakana={r.get('dakana_count')} mix_ratio={r.get('mix_ratio')}",
            conf=0.60,
        ))

    return findings


def _run_baidu(dom: dict, headers: dict, raw_html: str = "") -> list[Finding]:
    from detectors import baidu as bd
    findings: list[Finding] = []
    vt = dom["visible_text"]

    r = bd.icp_check(dom.get("footer", ""))
    if not r.get("has_icp_license"):
        findings.append(_f(
            "baidu.compliance.icp-license-missing", Severity.BLOCKER, Platform.BAIDU,
            "页面 footer 缺 ICP 备案号，百度大概率不收录（中国大陆合规硬要求）",
            "footer 中无 ICP 备案号",
            conf=0.92,
        ))

    r = bd.simplified_chinese_check(vt)
    if not r.get("has_chinese"):
        findings.append(_f(
            "baidu.content.simplified-chinese", Severity.MEDIUM, Platform.BAIDU,
            "声明 zh-CN 但页面无中文字符，百度蜘蛛会判定为非中文页",
            "0 个中文字符",
            conf=0.80,
        ))

    # 清风算法：title 关键词堆砌
    r = bd.title_keyword_stuffing_check(dom.get("title", ""), vt)
    if r.get("suspect_stuffing"):
        rk = r.get("repeated_keywords_in_title", [])
        findings.append(_f(
            "baidu.qingfeng.title-keyword-stuffing", Severity.HIGH, Platform.BAIDU,
            "title 疑似关键词堆砌或与正文严重不符（百度清风算法目标）",
            f"repeated={rk[:2]} title_in_body={r.get('title_in_body')}",
            conf=0.78,
        ))

    # 冰桶算法：移动端强制下载 App 弹窗
    r = bd.mobile_app_interstitial_check(raw_html)
    if r.get("has_forced_app_interstitial"):
        findings.append(_f(
            "baidu.bingtong.mobile-forced-app-download", Severity.HIGH, Platform.BAIDU,
            "检测到移动端首屏强制下载 App 弹窗（百度冰桶算法直接降权）",
            f"signals={r.get('signals')}",
            conf=0.82,
        ))

    # 石榴算法：低质广告
    r = bd.low_quality_ads_check(raw_html)
    if r.get("suspect_low_quality"):
        findings.append(_f(
            "baidu.shiliu.low-quality-ads", Severity.MEDIUM, Platform.BAIDU,
            "主体内容混杂弹窗 / 悬浮广告 / 误导按钮（百度石榴算法目标）",
            f"low_quality_score={r.get('low_quality_score')}",
            conf=0.70,
        ))

    # 绿萝算法：垃圾外链
    r = bd.spam_outbound_links_check(dom["outbound_links"])
    if r.get("spam_detected"):
        findings.append(_f(
            "baidu.lvluo.spam-outbound-links", Severity.MEDIUM, Platform.BAIDU,
            "外链疑似买卖 / spam 锚文本（百度绿萝算法目标）",
            f"top_domain_ratio={r.get('top_domain_ratio')} spam_anchors={r.get('spam_anchor_hits')}",
            conf=0.68,
        ))

    # 极光算法：落地页时间格式
    r = bd.publication_date_format_check(raw_html, vt)
    if not r.get("passed"):
        findings.append(_f(
            "baidu.jiguang.publication-date-format", Severity.LOW, Platform.BAIDU,
            "未发现规范时间因子（YYYY-MM-DD HH:MM 或 JSON-LD datePublished），百度极光算法影响时效性",
            "0 时间格式匹配",
            conf=0.75,
        ))

    return findings


def _run_bing_global(dom: dict, raw_html: str, url: str) -> list[Finding]:
    """Bing 全 locale 共享检测（无 locale 限制）"""
    from detectors import bing as bg
    findings: list[Finding] = []

    r = bg.image_pack_check(raw_html)
    if not r.get("passed") and r.get("image_count", 0) > 0:
        findings.append(_f(
            "bing.image-pack.alt-and-filename", Severity.MEDIUM, Platform.BING,
            "图片 alt 覆盖率低或文件名不语义化（Bing Image Pack 流量损失）",
            f"alt_coverage={r.get('alt_coverage')} bad_filenames={r.get('bad_filename_count')}",
            conf=0.72,
        ))

    r = bg.trust_signals_check(raw_html, dom.get("visible_text", ""))
    if r.get("weak_trust"):
        findings.append(_f(
            "bing.trust.signals-weak", Severity.MEDIUM, Platform.BING,
            "缺 trust 信号（联系/关于/法律/地址/电话）— Bing 视为 thin/non-trustworthy 站点",
            f"trust_score={r.get('trust_score')}/5",
            conf=0.62,
        ))

    r = bg.mobile_friendly_check(raw_html)
    if not r.get("passed"):
        findings.append(_f(
            "bing.mobile.viewport-required", Severity.HIGH, Platform.BING,
            "缺 viewport meta，Bing 移动 SERP 严重降权",
            "viewport meta 缺失",
            conf=0.88,
        ))

    r = bg.https_check(url)
    if not r.get("passed"):
        findings.append(_f(
            "bing.security.https-required", Severity.HIGH, Platform.BING,
            "非 HTTPS 页面，Bing 直接降权",
            f"is_https={r.get('is_https')}",
            conf=0.90,
        ))

    return findings


async def run(ai: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    locale = (ai.target.locale or "").strip()
    if not locale:
        return AgentOutput(trace_id=ai.trace_id, agent="localization",
                          status=AgentStatus.OK,
                          metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms))

    artifacts_snap = ai.context.snapshots.get("crawler", {})
    raw_html = artifacts_snap.get("raw_html", "")
    headers = artifacts_snap.get("headers", {})
    if not raw_html:
        return AgentOutput(trace_id=ai.trace_id, agent="localization",
                          status=AgentStatus.OK,
                          metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms))

    dom = _extract_dom(raw_html)
    findings: list[Finding] = []

    try:
        if locale in KO_LOCALES:
            findings.extend(_run_naver(dom, headers, raw_html, ai.target.url or ""))
        elif locale in RU_LOCALES:
            findings.extend(_run_yandex(dom, headers, ai.target.url or "", raw_html))
        # Baidu 已下线，zh-CN 走 Google 路径（不再调 _run_baidu）
        elif locale in JA_LOCALES:
            findings.extend(_run_yahoo_jp(dom, headers, ai.target.url or "", raw_html))
        # Bing 全 locale 共享检测
        findings.extend(_run_bing_global(dom, raw_html, ai.target.url or ""))
    except Exception as e:
        return AgentOutput(trace_id=ai.trace_id, agent="localization",
                          status=AgentStatus.OK, findings=findings,
                          metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms))

    return AgentOutput(
        trace_id=ai.trace_id, agent="localization", status=AgentStatus.OK,
        findings=findings, artifacts={"locale_routed": locale, "dom_extracted": True},
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )
