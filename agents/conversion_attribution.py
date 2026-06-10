"""
conversion-attribution (V2) — 转化反哺 + LTV 量化
对应能力 #19
"""
from __future__ import annotations

import time

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Metrics,
)


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)

    artifacts = {
        "seo_traffic_funnel": {},
        "page_ltv_estimates": {},
        "traffic_value_estimation_usd": 0.0,
        "brand_vs_non_brand_split": {},
    }

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="conversion_attribution",
        status=AgentStatus.SKIPPED,
        artifacts=artifacts,
        next_actions=[
            "需要 GA4 API 接入 (organic traffic → conversion)",
            "需要 BYDFi 后端 LTV 数据 (per landing page)",
            "需要 GSC API brand vs non-brand split",
            "需要 Google Ads CPC 数据估算流量等价价值",
        ],
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )
