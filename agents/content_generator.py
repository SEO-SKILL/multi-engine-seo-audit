"""
content-generator (V2) — SEO 内容生成器
对应能力 #33
"""
from __future__ import annotations

import time

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Metrics,
)
from integrations.anthropic_client import CostTracker, judge


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)

    primary_keyword = input_.payload.get("primary_keyword", "")
    page_type = input_.payload.get("page_type", "learn")
    target_audience = input_.payload.get("target_audience", "intermediate")
    locale = input_.payload.get("locale", input_.target.locale or "en")

    if not primary_keyword:
        return AgentOutput(
            trace_id=input_.trace_id,
            agent="content_generator",
            status=AgentStatus.SKIPPED,
            next_actions=["payload.primary_keyword 必填"],
        )

    cost_tracker = CostTracker(budget_usd=input_.budget.usd_remaining)

    result = await judge(
        prompt_template="content_generation",
        model="sonnet",  # 生成任务需要 Sonnet
        inputs={
            "primary_keyword": primary_keyword,
            "page_type": page_type,
            "target_audience": target_audience,
            "locale": locale,
        },
        cost_tracker=cost_tracker,
    )

    artifacts: dict = {
        "primary_keyword": primary_keyword,
        "page_type": page_type,
        "locale": locale,
    }

    if result.get("stub") or result.get("skipped"):
        artifacts["candidates"] = _fallback_templates(primary_keyword, page_type, target_audience)
        artifacts["mode"] = "fallback_templates"
    elif result.get("parse_error"):
        artifacts["raw_llm_output"] = result.get("raw_text", "")
        artifacts["mode"] = "llm_parse_error"
    else:
        artifacts["candidates"] = result
        artifacts["mode"] = "llm_generated"

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="content_generator",
        status=AgentStatus.OK,
        artifacts=artifacts,
        metrics=Metrics(
            duration_ms=int(time.time() * 1000) - start_ms,
            cost_usd=cost_tracker.spent_usd,
        ),
    )


def _fallback_templates(keyword: str, page_type: str, audience: str) -> dict:
    """无 LLM 时的模板化候选"""
    templates_by_type = {
        "learn": {
            "titles": [
                f"{keyword} - Complete Guide | BYDFi",
                f"What Is {keyword}? {audience.title()} Guide for 2026",
                f"{keyword} Explained: Definition, Examples, Risks",
            ],
            "meta_descriptions": [
                f"Learn {keyword} on BYDFi. Complete guide with examples, calculator, and risk analysis.",
                f"Master {keyword} step by step. Designed for {audience} crypto traders.",
            ],
            "h1s": [
                f"{keyword}: Everything You Need to Know",
                f"Understanding {keyword} — A {audience.title()} Guide",
            ],
        },
        "tools": {
            "titles": [
                f"{keyword} Calculator | Free Online Tool | BYDFi",
                f"Calculate {keyword} - Instant, Accurate | BYDFi",
            ],
            "meta_descriptions": [
                f"Use BYDFi's free {keyword} calculator. Instant, accurate, no signup required.",
            ],
            "h1s": [f"{keyword} Calculator"],
        },
        "price": {
            "titles": [
                f"{keyword} Price Today | Live Chart | BYDFi",
                f"{keyword} Price: USD, Market Cap, Volume | BYDFi",
            ],
            "meta_descriptions": [
                f"Real-time {keyword} price, charts, and market data on BYDFi. Source: CoinGecko.",
            ],
            "h1s": [f"{keyword} Price"],
        },
    }
    fallback = templates_by_type.get(page_type, templates_by_type["learn"])
    fallback["faq_schema"] = [
        {
            "@type": "Question",
            "name": f"What is {keyword}?",
            "acceptedAnswer": {"@type": "Answer", "text": f"{keyword} is..."},
        },
        {
            "@type": "Question",
            "name": f"How to use {keyword}?",
            "acceptedAnswer": {"@type": "Answer", "text": f"Step 1..."},
        },
    ]
    return fallback
