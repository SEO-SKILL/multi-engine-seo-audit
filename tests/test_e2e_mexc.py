"""E2E 测试：MEXC 事故 fixture 必须能检出 7 类问题"""
import pytest


REQUIRED_FINDINGS_ON_MEXC = [
    "bydfi.l01.republished-content-low-increment",
    "bydfi.l02.ticker-context-mismatch",
    "bydfi.l02.related-link-schema-pollution",
    "google.hreflang.alternate-blocked-by-robots",
    "google.hreflang.alternate-returns-404",
    "google.schema.field-not-grounded-in-visible-content",
    "google.schema.jsonld-csr-only",
    "google.schema.copyrightnotice-inconsistent",
    "google.schema.relatedlink-topic-mismatch",
    "bydfi.l05.tagging-topic-mismatch",
]


@pytest.mark.skip(reason="Pending agent implementation (Codex W1 Day 3-5)")
def test_mexc_incident_detects_all_required_findings(mexc_incident_html: str):
    """
    本测试是 V1 验收的硬指标：
    MEXC 事故 7 类问题对应的规则必须 100% 检出，否则 CI fail。
    """
    # TODO: orchestrator.audit(fixture_url) 实现后填充
    findings_ids = []  # placeholder

    missing = set(REQUIRED_FINDINGS_ON_MEXC) - set(findings_ids)
    assert not missing, f"MEXC fixture missing required findings: {missing}"


@pytest.mark.skip(reason="Pending agent implementation")
def test_good_tools_page_no_blocker(good_tools_page_html: str):
    """合格的工具页不应触发任何 blocker / high"""
    findings = []  # placeholder
    blockers = [f for f in findings if f.get("severity") == "blocker"]
    highs = [f for f in findings if f.get("severity") == "high"]
    assert not blockers
    assert not highs


@pytest.mark.skip(reason="Pending agent implementation")
def test_bad_hreflang_detects_all_hreflang_rules(bad_hreflang_html: str):
    expected_rule_ids = [
        "google.hreflang.alternate-returns-404",
        "google.hreflang.alternate-blocked-by-robots",
        "google.hreflang.language-mismatch",
        "google.hreflang.canonical-not-self",
    ]
    findings_ids = []  # placeholder
    for rid in expected_rule_ids:
        assert rid in findings_ids, f"Missing {rid}"


@pytest.mark.skip(reason="Pending agent implementation (requires multi-UA crawling)")
def test_cloaking_suspect_detects_ua_diff(cloaking_suspect_html: str):
    """需要 crawler-agent 配合多 UA 抓取"""
    findings_ids = []
    assert "google.cloaking.googlebot-vs-user-content-diff" in findings_ids \
        or "google.cloaking.csr-renders-different-content" in findings_ids


@pytest.mark.skip(reason="Pending agent implementation")
def test_thin_content_detects_eeat_issues(thin_content_html: str):
    expected_rule_ids = [
        "google.eeat.author-attribution-missing",
        "google.eeat.publication-date-missing-or-stale",
        "bydfi.compliance.risk-disclaimer-required",
    ]
    findings_ids = []
    for rid in expected_rule_ids:
        assert rid in findings_ids
