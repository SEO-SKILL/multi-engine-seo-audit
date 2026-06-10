"""
safety-agent — Web3 / 合规 / Ticker 消歧义
对应能力 #15 Web3-specific（V1）+ #18 合规（V1 基础）
"""
from __future__ import annotations

import time

import yaml

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
from detectors import compliance as comp_detect


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    findings: list[Finding] = []

    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")

    if not raw_html:
        return AgentOutput(
            trace_id=input_.trace_id,
            agent="safety",
            status=AgentStatus.SKIPPED,
        )

    findings += _check_banned_keywords(raw_html, input_.trace_id)
    findings += _check_pros_ticker_misuse(raw_html, input_.trace_id)

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = None
    for sev in severity_order:
        if any(f.severity == sev for f in findings):
            severity_max = sev
            break

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="safety",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _check_banned_keywords(raw_html: str, trace_id: str) -> list[Finding]:
    banned = [
        "guaranteed return", "guaranteed profit", "risk-free", "100% profit",
        "保证收益", "稳赚不赔", "零风险", "100% 盈利",
    ]
    hits = comp_detect.keyword_blacklist_check(raw_html, banned)
    findings: list[Finding] = []
    for hit in hits:
        findings.append(Finding(
            id="bydfi.compliance.banned-keywords-present",
            source=FindingSource.HARD_RULE,
            platform=Platform.BYDFI,
            severity=Severity.BLOCKER,
            confidence=0.99,
            evidence=Evidence(text_snippet=hit["first_match_context"]),
            recommendation=f"立即移除关键词 '{hit['keyword']}'，触发 US-SEC / EU-MiCA / JP-JFSA 多国监管风险",
            patch_hint=PatchHint(template="patches/remove_banned_keyword.diff.j2", priority="P0", requires_review=True),
        ))
    return findings


def _check_pros_ticker_misuse(raw_html: str, trace_id: str) -> list[Finding]:
    result = comp_detect.ticker_in_context(
        raw_html,
        "PROS",
        blacklist_contexts=["pros and cons", "advantages", "review"],
    )
    findings: list[Finding] = []
    if result["is_misidentification_likely"]:
        findings.append(Finding(
            id="bydfi.l02.ticker-context-mismatch",
            source=FindingSource.HARD_RULE,
            platform=Platform.BYDFI,
            severity=Severity.BLOCKER,
            confidence=0.90,
            evidence=Evidence(text_snippet=f"PROS 在 title/h1 含通用词 {result['matched_blacklist_contexts']}"),
            recommendation="移除 PROS ticker widget / relatedLink / 交易入口（MEXC 事故 L02 同类问题）",
            patch_hint=PatchHint(template="patches/remove_ticker_widget.diff.j2", priority="P0", requires_review=True),
        ))
    return findings
