"""
cross-llm-agent (V2) — 跨 LLM 验证
对应能力 #23

V2.0 用 Haiku/Sonnet/Opus 三家交叉确认
V2.1 后期接 GPT API / Gemini API 实现真正跨厂商交叉
"""
from __future__ import annotations

import asyncio
import time
from collections import Counter

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
from integrations.anthropic_client import CostTracker, judge


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    snapshots = input_.context.snapshots or {}
    semantic_findings = snapshots.get("semantic", {}).get("findings", [])

    cost_tracker = CostTracker(budget_usd=input_.budget.usd_remaining)

    cross_validated: list[Finding] = []
    for f_dict in semantic_findings[:5]:  # 限制最多复核 5 个，控制成本
        if cost_tracker.remaining() < 0.005:
            break
        verdicts = await _query_three_models(f_dict, cost_tracker)
        agreement = _calculate_agreement(verdicts)

        original_severity = f_dict.get("severity", "info")
        original_confidence = float(f_dict.get("confidence", 0.5))

        # 三家一致 → 提升 confidence
        # 多数一致 → 维持 + 标 flag
        # 完全不一致 → 降级 confidence
        if agreement["agreement_ratio"] >= 1.0:
            new_confidence = min(1.0, original_confidence + 0.15)
            severity_label = original_severity
        elif agreement["agreement_ratio"] >= 0.66:
            new_confidence = min(1.0, original_confidence + 0.05)
            severity_label = agreement["majority_severity"]
        else:
            new_confidence = max(0.1, original_confidence - 0.30)
            severity_label = original_severity

        try:
            cross_validated.append(Finding(
                id=f_dict["id"],
                source=FindingSource.LLM_JUDGE,
                platform=Platform(f_dict.get("platform", "google")),
                severity=Severity(severity_label),
                confidence=new_confidence,
                evidence=Evidence(text_snippet=f"Cross-LLM agreement: {agreement['agreement_ratio']:.0%} ({len(verdicts)} models)"),
                recommendation=f_dict.get("recommendation", ""),
            ))
        except (ValueError, KeyError):
            continue

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="cross_llm",
        status=AgentStatus.OK,
        findings=cross_validated,
        metrics=Metrics(
            duration_ms=int(time.time() * 1000) - start_ms,
            cost_usd=cost_tracker.spent_usd,
        ),
    )


async def _query_three_models(finding: dict, cost_tracker: CostTracker) -> list[dict]:
    """V2: Claude 三种模式 + 不同 prompt focus 模拟跨模型；
    V2.1 后期接 GPT/Gemini API"""

    async def _q(model: str) -> dict:
        result = await judge(
            prompt_template="schema_grounding_judge" if "schema" in finding.get("id", "") else "eeat_author_judge",
            model=model,
            inputs=finding,
            cost_tracker=cost_tracker,
        )
        return {
            "model": f"claude-{model}",
            "severity": result.get("severity", finding.get("severity", "info")),
            "confidence": float(result.get("confidence", 0.5)),
        }

    results = await asyncio.gather(_q("haiku"), _q("sonnet"), return_exceptions=True)
    return [r for r in results if isinstance(r, dict)]


def _calculate_agreement(verdicts: list[dict]) -> dict:
    if not verdicts:
        return {"majority_severity": None, "agreement_ratio": 0.0}
    severities = [v["severity"] for v in verdicts]
    counter = Counter(severities)
    most_common = counter.most_common(1)
    sev, count = most_common[0]
    return {"majority_severity": sev, "agreement_ratio": count / len(verdicts)}
