"""
Rate Limit / Concurrency 控制 (V2)
"""
from __future__ import annotations

import asyncio
import time
from collections import deque


class TokenBucket:
    def __init__(self, requests_per_second: float, burst: int = 5) -> None:
        self.rps = requests_per_second
        self.burst = burst
        self.tokens = float(burst)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.burst, self.tokens + elapsed * self.rps)
            self.last_refill = now
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return
            wait = (1.0 - self.tokens) / self.rps
            await asyncio.sleep(wait)
            self.tokens = 0.0


class ConcurrencyLimiter:
    def __init__(self, max_concurrent: int) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self) -> "ConcurrencyLimiter":
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, *args: object) -> None:
        self.semaphore.release()


class DailyQuotaTracker:
    def __init__(self, daily_quota: int) -> None:
        self.daily_quota = daily_quota
        self.usage = deque(maxlen=daily_quota * 2)

    def can_proceed(self) -> bool:
        now = time.monotonic()
        cutoff = now - 86400
        while self.usage and self.usage[0] < cutoff:
            self.usage.popleft()
        return len(self.usage) < self.daily_quota

    def record(self) -> None:
        self.usage.append(time.monotonic())
