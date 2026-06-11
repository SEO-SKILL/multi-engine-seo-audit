"""
F3 — Error / Retry / Degrade 统一层
基于 tenacity 实现重试 + 熔断 + 降级
"""
from __future__ import annotations

import asyncio
import functools
from typing import Any, Callable

import structlog
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger(__name__)


class AgentTimeout(Exception):
    """Agent 超过预算 / 时间上限"""


class CircuitBreaker:
    """简单的熔断器：N 次连续失败后开路 X 秒"""

    def __init__(self, name: str, fail_threshold: int = 5, reset_seconds: int = 60) -> None:
        self.name = name
        self.fail_threshold = fail_threshold
        self.reset_seconds = reset_seconds
        self.failures = 0
        self.opened_at: float | None = None

    def can_proceed(self) -> bool:
        import time
        if self.opened_at is None:
            return True
        if time.monotonic() - self.opened_at >= self.reset_seconds:
            self.opened_at = None
            self.failures = 0
            return True
        return False

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        import time
        self.failures += 1
        if self.failures >= self.fail_threshold:
            self.opened_at = time.monotonic()
            logger.warning("circuit_breaker_opened", name=self.name)


_BREAKERS: dict[str, CircuitBreaker] = {}


def get_breaker(name: str) -> CircuitBreaker:
    if name not in _BREAKERS:
        _BREAKERS[name] = CircuitBreaker(name)
    return _BREAKERS[name]


def with_retry(max_attempts: int = 3, min_wait: float = 1.0, max_wait: float = 8.0):
    """async retry decorator (exponential backoff)"""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=min_wait, max=max_wait),
                retry=retry_if_exception_type((TimeoutError, ConnectionError, asyncio.TimeoutError)),
                reraise=True,
            ):
                with attempt:
                    return await fn(*args, **kwargs)

        return wrapper

    return decorator


async def with_degrade(primary: Callable, fallback: Callable, breaker_name: str | None = None) -> Any:
    """主调用失败 → 降级到 fallback"""
    breaker = get_breaker(breaker_name) if breaker_name else None
    if breaker and not breaker.can_proceed():
        logger.info("circuit_open_using_fallback", breaker=breaker_name)
        return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()

    try:
        result = await primary() if asyncio.iscoroutinefunction(primary) else primary()
        if breaker:
            breaker.record_success()
        return result
    except Exception as e:
        logger.warning("primary_failed_degrading", error=str(e))
        if breaker:
            breaker.record_failure()
        return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()


async def with_budget(coro_fn: Callable, budget_usd_remaining: float, agent_name: str) -> Any:
    """预算检查 wrapper"""
    if budget_usd_remaining <= 0:
        from agents._schema import AgentOutput, AgentStatus
        logger.info("budget_exhausted_skipping", agent=agent_name)
        return AgentOutput(trace_id="budget-skipped", agent=agent_name, status=AgentStatus.SKIPPED_BUDGET)
    return await coro_fn() if asyncio.iscoroutinefunction(coro_fn) else coro_fn()
