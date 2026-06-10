"""
serp-agent — 真实 SERP + AI Overview 视角
对应能力 #2
V1：抽样模式（不全量爬 Google）
"""
from __future__ import annotations

import time

from agents._schema import AgentInput, AgentOutput, AgentStatus, Metrics


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    # V1 抽样模式：用户手动提供 SERP 截图 / DataForSEO API 接入待配置
    return AgentOutput(
        trace_id=input_.trace_id,
        agent="serp",
        status=AgentStatus.SKIPPED,
        next_actions=[
            "V1 SERP 数据通过用户手动采样或 CSV 导入",
            "V2 接入 DataForSEO API 自动采集",
        ],
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )
