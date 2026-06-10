"""
entity-agent (V2) — Entity SEO + 知识图谱
对应能力 #31
"""
from __future__ import annotations

import time

import httpx
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
from detectors.schema import extract_jsonld, get_jsonld_field


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")

    if not raw_html:
        return AgentOutput(trace_id=input_.trace_id, agent="entity", status=AgentStatus.SKIPPED)

    findings: list[Finding] = []
    findings += _check_sameas_signals(raw_html, input_.trace_id)
    findings += await _check_wikidata_presence(input_.target.url or "", input_.trace_id)
    findings += _check_organization_schema(raw_html, input_.trace_id)

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = next((s for s in severity_order if any(f.severity == s for f in findings)), None)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="entity",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _check_sameas_signals(raw_html: str, trace_id: str) -> list[Finding]:
    blocks = extract_jsonld(raw_html)
    sameas = []
    for b in blocks:
        if isinstance(b, dict) and "sameAs" in b:
            sameas = b["sameAs"] if isinstance(b["sameAs"], list) else [b["sameAs"]]
            break

    findings: list[Finding] = []
    if not sameas:
        findings.append(Finding(
            id="google.kg.sameas-missing",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.LOW,
            confidence=0.92,
            evidence=Evidence(text_snippet="JSON-LD 中 sameAs 字段缺失"),
            recommendation="添加 sameAs 链接到 Twitter / LinkedIn / Crunchbase / Wikipedia",
        ))
    return findings


async def _check_wikidata_presence(url: str, trace_id: str) -> list[Finding]:
    return []


def _check_organization_schema(raw_html: str, trace_id: str) -> list[Finding]:
    blocks = extract_jsonld(raw_html)
    has_org = any(isinstance(b, dict) and b.get("@type") in ("Organization", "Corporation") for b in blocks)
    findings: list[Finding] = []
    if not has_org:
        findings.append(Finding(
            id="google.kg.organization-incomplete",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.MEDIUM,
            confidence=0.90,
            evidence=Evidence(text_snippet="JSON-LD 中无 Organization schema"),
            recommendation="添加 Organization schema 含 name/url/logo/sameAs/foundingDate",
        ))
    return findings
