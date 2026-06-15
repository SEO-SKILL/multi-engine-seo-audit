"""
semantic-agent — AI 语义检测（语义错配/原创增量/意图链/Schema 真实性）
对应能力 #1
"""
from __future__ import annotations

import time

from bs4 import BeautifulSoup

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Evidence,
    Finding,
    FindingSource,
    Metrics,
    Platform,
    Severity,
)
from detectors.schema import extract_jsonld
from integrations.anthropic_client import CostTracker, judge


SEMANTIC_JUDGES = [
    # (prompt_template, default_rule_id, default_platform)
    ("schema_grounding_judge", "google.schema.field-not-grounded-in-visible-content", "google"),
    ("eeat_author_judge", "google.eeat.author-attribution-missing", "google"),
    ("thin-content-vs-serp", "google.eeat.thin-content-vs-serp", "google"),
    ("helpful_content_signal_judge", "google.helpful-content.signal-weak", "google"),
    ("republished_originality_judge", "google.duplicate-content.plagiarism-no-value-add", "google"),
]

# 按 locale 路由的本地化 LLM judge
LOCALE_LLM_JUDGES = {
    "ko": [
        ("naver_korean_authenticity_judge", "naver.content.korean-honorific-usage", "naver"),
        ("naver_korean_authenticity_judge", "naver.dia.content-completeness", "naver"),
    ],
    "ja": [
        ("republished_originality_judge", "yahoo-jp.content.japanese-financial-context", "yahoo-japan"),
    ],
    "ru": [
        ("republished_originality_judge", "yandex.y1.content-quality-low", "yandex"),
    ],
    # zh-CN：Baidu 已下线，走 Google 路径，无 locale-specific judge
}


_PLATFORM_MAP = {
    "google": Platform.GOOGLE,
    "naver": Platform.NAVER,
    "yandex": Platform.YANDEX,
    "baidu": Platform.BAIDU,
    "yahoo-japan": Platform.YAHOO_JAPAN,
    "bing": Platform.BING,
}


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")

    if not raw_html:
        return AgentOutput(trace_id=input_.trace_id, agent="semantic", status=AgentStatus.SKIPPED)

    soup = BeautifulSoup(raw_html, "lxml")
    visible_text = soup.get_text(separator=" ", strip=True)
    title = soup.title.get_text() if soup.title else ""
    h1 = soup.find("h1")
    h1_text = h1.get_text() if h1 else ""
    jsonld = extract_jsonld(raw_html)

    cost_tracker = CostTracker(budget_usd=input_.budget.usd_remaining)

    inputs = {
        "title": title,
        "h1": h1_text,
        "visible_text": visible_text[:4000],
        "jsonld": jsonld,
        "page_url": input_.target.url,
    }

    findings: list[Finding] = []

    # 通用 Google judges + locale-aware judges 合并
    locale = (input_.target.locale or "").strip()
    judges_to_run = list(SEMANTIC_JUDGES)
    if locale in LOCALE_LLM_JUDGES:
        judges_to_run.extend(LOCALE_LLM_JUDGES[locale])

    for entry in judges_to_run:
        if cost_tracker.remaining() < 0.005:
            # Gemini 免费层不扣 anthropic budget，但保留 budget 检查作为安全阀
            pass  # 不 break，让 Gemini 跑
        judge_name, default_rule_id, default_platform_str = entry
        default_platform = _PLATFORM_MAP.get(default_platform_str, Platform.GOOGLE)
        result = await judge(
            prompt_template=judge_name,
            model="haiku",
            inputs={**inputs, "_target_rule_id": default_rule_id, "_target_platform": default_platform_str},
            cost_tracker=cost_tracker,
            no_cache=input_.context.no_cache,
        )
        if result.get("skipped") or result.get("stub") or result.get("parse_error"):
            continue
        if result.get("severity") and result.get("severity") != "info":
            try:
                # 优先用 LLM 返回的 rule_id，否则用 default
                returned_rid = result.get("rule_id") or default_rule_id
                # 如果 returned_rid 跟 default_platform 不匹配，用 default
                if not returned_rid.startswith(default_platform_str + ".") and default_platform_str != "google":
                    returned_rid = default_rule_id
                findings.append(Finding(
                    id=returned_rid,
                    source=FindingSource.LLM_JUDGE,
                    platform=default_platform,
                    severity=Severity(result["severity"]),
                    confidence=float(result.get("confidence", 0.5)),
                    evidence=Evidence(text_snippet=str(result.get("evidence", {}))[:300]),
                    recommendation=result.get("recommendation", ""),
                ))
            except (ValueError, KeyError):
                continue

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = next((s for s in severity_order if any(f.severity == s for f in findings)), None)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="semantic",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(
            duration_ms=int(time.time() * 1000) - start_ms,
            cost_usd=cost_tracker.spent_usd,
        ),
    )
