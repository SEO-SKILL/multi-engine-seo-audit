"""测试 Pydantic schema 的合法性"""
import pytest

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    AuditReport,
    Budget,
    Command,
    Evidence,
    Finding,
    FindingSource,
    Metrics,
    Platform,
    Severity,
    Target,
)


def test_agent_input_minimal():
    ai = AgentInput(
        run_id="test-001",
        command=Command.AUDIT,
        target=Target(url="https://example.com"),
    )
    assert ai.project == "platform"
    assert ai.budget.usd_remaining == 0.03


def test_finding_with_evidence():
    f = Finding(
        id="platform.l02.ticker-context-mismatch",
        source=FindingSource.LLM_JUDGE,
        platform=Platform.PLATFORM,
        severity=Severity.BLOCKER,
        confidence=0.92,
        evidence=Evidence(text_snippet="Pros and Cons"),
        recommendation="移除 PROS ticker widget",
    )
    assert f.confidence == 0.92


def test_audit_report_verdict():
    blocker_f = Finding(
        id="test.blocker",
        source=FindingSource.HARD_RULE,
        platform=Platform.GOOGLE,
        severity=Severity.BLOCKER,
        confidence=0.95,
        evidence=Evidence(),
        recommendation="fix it",
    )
    from agents._schema import FinalVerdict
    report = AuditReport(
        trace_id="t1",
        run_id="r1",
        project="platform",
        command=Command.AUDIT,
        target=Target(url="https://example.com"),
        final_verdict=FinalVerdict.BLOCKED,
        brand_seo_score=40.0,
        findings_by_severity={Severity.BLOCKER: [blocker_f]},
    )
    assert report.final_verdict == FinalVerdict.BLOCKED


def test_severity_ordering():
    levels = [Severity.BLOCKER, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    assert levels[0] == Severity.BLOCKER


def test_finding_confidence_range():
    with pytest.raises(ValueError):
        Finding(
            id="test.bad",
            source=FindingSource.HARD_RULE,
            platform=Platform.GOOGLE,
            severity=Severity.HIGH,
            confidence=1.5,  # 超出范围
            evidence=Evidence(),
            recommendation="...",
        )
