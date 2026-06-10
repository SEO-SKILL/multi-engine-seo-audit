"""
lifecycle-agent — 矩阵视角 + Cannibalization（V1 基础版）
对应能力 #7
"""
from __future__ import annotations

import time
from collections import defaultdict

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


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")

    if not raw_html:
        return AgentOutput(trace_id=input_.trace_id, agent="lifecycle", status=AgentStatus.SKIPPED)

    findings: list[Finding] = []
    findings += _check_internal_link_anchor_distribution(raw_html, input_.trace_id)

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = next((s for s in severity_order if any(f.severity == s for f in findings)), None)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="lifecycle",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _check_internal_link_anchor_distribution(raw_html: str, trace_id: str) -> list[Finding]:
    """简化版：检查内链锚文本是否过度精确匹配（关键词堆砌）"""
    soup = BeautifulSoup(raw_html, "lxml")
    anchor_counts: dict[str, int] = defaultdict(int)
    total = 0
    for a in soup.find_all("a", href=True):
        text = a.get_text().strip().lower()
        if not text or text in {"了解更多", "more", "read more", "click here"}:
            continue
        anchor_counts[text] += 1
        total += 1

    findings: list[Finding] = []
    if total < 5:
        return findings

    # 找出占比 > 30% 的锚文本
    for anchor, count in anchor_counts.items():
        ratio = count / total
        if ratio > 0.30:
            findings.append(Finding(
                id="shared.internal-link.anchor-text-keyword-stuffing",
                source=FindingSource.HARD_RULE,
                platform=Platform.SHARED,
                severity=Severity.MEDIUM,
                confidence=0.85,
                evidence=Evidence(text_snippet=f"锚文本 '{anchor}' 占 {ratio:.0%} ({count}/{total})"),
                recommendation="混用品牌锚 / 关键词锚 / 通用锚，避免过度精确匹配",
            ))
    return findings
