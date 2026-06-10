"""
decay-agent (V2) — Content Decay 检测 + Pruning Candidates
对应能力 #24, #25
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
    Platform,
    Severity,
)
from detectors import freshness as freshness_detect


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")

    if not raw_html:
        return AgentOutput(trace_id=input_.trace_id, agent="decay", status=AgentStatus.SKIPPED)

    findings: list[Finding] = []
    findings += _check_staleness(raw_html, input_.trace_id)

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = next((s for s in severity_order if any(f.severity == s for f in findings)), None)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="decay",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _check_staleness(raw_html: str, trace_id: str) -> list[Finding]:
    from detectors.eeat import detect_publication_dates
    dates = detect_publication_dates(raw_html)
    date_modified = dates.get("dateModified") or dates.get("datePublished")
    if not date_modified:
        return []

    stale_info = freshness_detect.staleness_check(date_modified, max_age_days=180)
    findings: list[Finding] = []
    if stale_info.get("stale"):
        findings.append(Finding(
            id="shared.freshness.stale-content-no-update",
            source=FindingSource.HARD_RULE,
            platform=Platform.SHARED,
            severity=Severity.MEDIUM,
            confidence=0.88,
            evidence=Evidence(text_snippet=f"内容年龄 {stale_info.get('age_days')} 天 > 180"),
            recommendation="高变动主题（金融/监管/价格）建议每 6 个月更新",
        ))
    return findings
