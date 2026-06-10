"""
log-agent — Log File + Index Coverage
对应能力 #12
V1：GSC API 占位（需 GSC OAuth 后接入）
"""
from __future__ import annotations

import time

from agents._schema import AgentInput, AgentOutput, AgentStatus, Metrics


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)
    # V1 stub: 等 GSC OAuth 配置完成后接入
    return AgentOutput(
        trace_id=input_.trace_id,
        agent="log",
        status=AgentStatus.SKIPPED,
        next_actions=[
            "需要 Kelly 在 GSC 添加我们的服务账号",
            "Cloudflare API token 待配置",
            "fly.io log 拉取接口待开发",
        ],
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )
