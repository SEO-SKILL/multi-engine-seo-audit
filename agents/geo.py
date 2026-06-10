"""
geo-agent — GEO（Generative Engine Optimization）+ 跨 LLM 引用率
对应能力 #9
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


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    crawler_artifacts = snapshots.get("crawler") or {}
    raw_html = crawler_artifacts.get("raw_html", "")
    url = input_.target.url

    if not raw_html or not url:
        return AgentOutput(trace_id=input_.trace_id, agent="geo", status=AgentStatus.SKIPPED)

    findings: list[Finding] = []

    findings += await _check_llms_txt(url, input_.trace_id)
    findings += _check_answerable_chunks(raw_html, input_.trace_id)
    findings += _check_robots_for_ai_bots(crawler_artifacts, input_.trace_id)

    severity_order = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    severity_max = next((s for s in severity_order if any(f.severity == s for f in findings)), None)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="geo",
        status=AgentStatus.OK,
        severity_max=severity_max,
        findings=findings,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


async def _check_llms_txt(url: str, trace_id: str) -> list[Finding]:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"

    findings: list[Finding] = []
    async with httpx.AsyncClient(timeout=10) as client:
        for path in ["/llms.txt", "/llms-full.txt"]:
            try:
                resp = await client.get(domain + path)
                if resp.status_code == 200:
                    return findings  # 找到一个即可
            except Exception:
                continue

    findings.append(Finding(
        id="perplexity.geo.llms-txt-missing",
        source=FindingSource.HARD_RULE,
        platform=Platform.LLM_ENGINES,
        severity=Severity.LOW,
        confidence=0.99,
        evidence=Evidence(text_snippet=f"未发现 {domain}/llms.txt 或 /llms-full.txt"),
        recommendation="创建 llms.txt 声明站点结构和重点页面",
    ))
    return findings


def _check_answerable_chunks(raw_html: str, trace_id: str) -> list[Finding]:
    """简化版：检查 H2 数量 + 段落长度分布"""
    soup = BeautifulSoup(raw_html, "lxml")
    h2_count = len(soup.find_all("h2"))
    paragraphs = soup.find_all("p")
    short_paragraphs = sum(1 for p in paragraphs if 70 <= len(p.get_text()) <= 150)

    findings: list[Finding] = []
    if h2_count < 3 or short_paragraphs < 3:
        findings.append(Finding(
            id="perplexity.geo.answerable-chunks",
            source=FindingSource.HARD_RULE,
            platform=Platform.LLM_ENGINES,
            severity=Severity.MEDIUM,
            confidence=0.75,
            evidence=Evidence(text_snippet=f"H2={h2_count}, short-paragraphs={short_paragraphs}"),
            recommendation="重构为每 H2 段落独立可答 + 段首陈述结论",
        ))
    return findings


def _check_robots_for_ai_bots(crawler_artifacts: dict, trace_id: str) -> list[Finding]:
    return []
