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
    ("schema_grounding_judge", "google.schema.field-not-grounded-in-visible-content"),
    ("eeat_author_judge", "google.eeat.author-attribution-missing"),
    ("thin-content-vs-serp", "google.eeat.thin-content-vs-serp"),
    ("helpful_content_signal_judge", "google.helpful-content.signal-weak"),
]


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
    for judge_name, default_rule_id in SEMANTIC_JUDGES:
        if cost_tracker.remaining() < 0.005:
            break
        result = await judge(
            prompt_template=judge_name,
            model="haiku",
            inputs=inputs,
            cost_tracker=cost_tracker,
        )
        if result.get("skipped") or result.get("stub") or result.get("parse_error"):
            continue
        if result.get("severity") and result.get("severity") != "info":
            try:
                findings.append(Finding(
                    id=result.get("rule_id", default_rule_id),
                    source=FindingSource.LLM_JUDGE,
                    platform=Platform.GOOGLE,
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
