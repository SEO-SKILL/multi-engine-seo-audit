"""
F5 — Observability / Tracing 统一层
trace_id 贯穿全 agent + 结构化日志 + 成本追踪
"""
from __future__ import annotations

import contextvars
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)

# ContextVar 让 trace_id 在 async 调用中自动传递
_trace_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)
_run_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("run_id", default=None)


def set_trace(trace_id: str, run_id: str | None = None) -> None:
    _trace_ctx.set(trace_id)
    if run_id:
        _run_ctx.set(run_id)


def get_trace() -> str | None:
    return _trace_ctx.get()


def get_run_id() -> str | None:
    return _run_ctx.get()


@dataclass
class SpanRecord:
    name: str
    trace_id: str
    span_id: str = field(default_factory=lambda: uuid4().hex[:12])
    start_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    end_ms: int = 0
    duration_ms: int = 0
    status: str = "ok"
    metadata: dict = field(default_factory=dict)


class TracedSpan:
    """async context manager for tracing"""

    def __init__(self, name: str, **metadata: Any) -> None:
        self.record = SpanRecord(name=name, trace_id=get_trace() or "no-trace", metadata=metadata)

    async def __aenter__(self) -> SpanRecord:
        logger.debug("span_start", span=self.record.name, trace_id=self.record.trace_id, **self.record.metadata)
        return self.record

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.record.end_ms = int(time.time() * 1000)
        self.record.duration_ms = self.record.end_ms - self.record.start_ms
        if exc_type:
            self.record.status = "failed"
            logger.warning("span_failed", span=self.record.name, error=str(exc_val), duration_ms=self.record.duration_ms)
        else:
            logger.debug("span_end", span=self.record.name, duration_ms=self.record.duration_ms, status=self.record.status)


class CostLog:
    """累积 LLM 成本到 trace"""

    def __init__(self) -> None:
        self._totals: dict = {}

    def record_llm_call(self, agent: str, model: str, input_tokens: int, output_tokens: int,
                        cache_creation: int = 0, cache_read: int = 0, cost_usd: float = 0.0,
                        request_id: str | None = None) -> None:
        entry = {
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_creation": cache_creation,
            "cache_read": cache_read,
            "cost_usd": cost_usd,
            "request_id": request_id,
            "trace_id": get_trace(),
        }
        logger.info("llm_call", **entry)
        agent_total = self._totals.setdefault(agent, {"cost_usd": 0.0, "calls": 0})
        agent_total["cost_usd"] += cost_usd
        agent_total["calls"] += 1

    def summary(self) -> dict:
        return self._totals


# 全局 CostLog
GLOBAL_COST_LOG = CostLog()


def configure_logging(log_level: str = "info", io_log: bool = False) -> None:
    """配置 structlog 输出"""
    import logging
    logging.basicConfig(level=log_level.upper())
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if log_level == "debug" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level.upper())),
    )
