"""
negative-seo-agent (V2) — Negative SEO / 安全风险监控
对应能力 #17
"""
from __future__ import annotations

import re
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

# Hacked content 关键词模式
HACKED_PATTERNS = [
    r"\b(?:viagra|cialis|levitra)\b",
    r"\b(?:porn|xxx|adult)\s+(?:site|video)\b",
    r"\b(?:casino|gambling|poker|baccarat)\b",
    r"\b(?:cheap\s+jerseys?|replica\s+(?:watch|bag))\b",
]


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")

    if not raw_html:
        return AgentOutput(trace_id=input_.trace_id, agent="negative_seo", status=AgentStatus.SKIPPED)

    findings: list[Finding] = []
    findings += _check_hacked_content(raw_html, input_.trace_id)
    findings += _check_brand_hijack_keywords(raw_html, input_.trace_id)

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = next((s for s in severity_order if any(f.severity == s for f in findings)), None)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="negative_seo",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _check_hacked_content(raw_html: str, trace_id: str) -> list[Finding]:
    soup = BeautifulSoup(raw_html, "lxml")
    text = soup.get_text()
    hits = []
    for pattern in HACKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(pattern)

    findings: list[Finding] = []
    if hits:
        findings.append(Finding(
            id="shared.security.hacked-content",
            source=FindingSource.HARD_RULE,
            platform=Platform.SHARED,
            severity=Severity.BLOCKER,
            confidence=0.90,
            evidence=Evidence(text_snippet=f"检测到 hacked content 关键词: {hits}"),
            recommendation="立即调查站点是否被入侵，扫描所有页面 + 清理 + Google reconsideration request",
        ))
    return findings


def _check_brand_hijack_keywords(raw_html: str, trace_id: str) -> list[Finding]:
    return []
