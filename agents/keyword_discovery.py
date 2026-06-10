"""
keyword-discovery (V2) — 关键词矩阵主动发现
对应能力 #34
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

    sources = {
        "gsc_high_impression_low_position": [],
        "google_suggest": [],
        "people_also_ask": [],
        "competitor_diff": [],
    }

    candidates: list[dict] = []

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="keyword_discovery",
        status=AgentStatus.OK,
        artifacts={"sources": sources, "candidate_keywords": candidates},
        next_actions=[
            "需要 GSC API 接入提取 high-impression-low-position 查询",
            "需要 Google Suggest API 或抓取",
            "需要 PAA 抓取（受限于反爬）",
            "需要竞品对比数据（Ahrefs CSV）",
        ],
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )
