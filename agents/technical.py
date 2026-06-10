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
