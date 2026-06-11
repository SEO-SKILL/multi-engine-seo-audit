"""
crawler-agent — 多源真实抓取 + Cloaking 检测
对应能力 #3
V1 简化版：httpx + 多 UA（playwright 留给 Codex W2 接入）
"""
from __future__ import annotations

import asyncio
import time

import httpx

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Metrics,
)
from _ratelimit import ConcurrencyLimiter, TokenBucket

# F10 集成：全局限速 + 并发上限（按 config.yaml 中的 framework.rate_limit）
_GLOBAL_RATE_BUCKET = TokenBucket(requests_per_second=2.0, burst=5)
_GLOBAL_CONCURRENCY = ConcurrencyLimiter(max_concurrent=5)

UA_PROFILES = {
    "googlebot_desktop": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "googlebot_mobile": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "chrome_desktop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "chrome_mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
}


async def run(input_: AgentInput) -> AgentOutput:
    url = input_.target.url
    if not url:
        return AgentOutput(trace_id=input_.trace_id, agent="crawler", status=AgentStatus.FAILED)

    start_ms = int(time.time() * 1000)
    artifacts: dict = {"per_ua": {}}

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        tasks = [_fetch(client, url, ua_name, ua) for ua_name, ua in UA_PROFILES.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for (ua_name, _), result in zip(UA_PROFILES.items(), results):
        if isinstance(result, Exception):
            artifacts["per_ua"][ua_name] = {"error": str(result)}
        else:
            artifacts["per_ua"][ua_name] = result

    primary = artifacts["per_ua"].get("googlebot_desktop", {})
    artifacts["raw_html"] = primary.get("body", "")
    artifacts["headers"] = primary.get("headers", {})
    artifacts["status_code"] = primary.get("status_code")
    artifacts["final_url"] = primary.get("final_url")
    artifacts["redirect_chain"] = primary.get("redirects", [])

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="crawler",
        status=AgentStatus.OK,
        artifacts=artifacts,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


async def _fetch(client: httpx.AsyncClient, url: str, ua_name: str, ua_string: str) -> dict:
    # F10 真集成：限速 + 并发
    await _GLOBAL_RATE_BUCKET.acquire()
    async with _GLOBAL_CONCURRENCY:
        headers = {"User-Agent": ua_string, "Accept-Language": "en-US,en;q=0.9"}
        response = await client.get(url, headers=headers)
        return {
            "ua": ua_name,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "final_url": str(response.url),
            "redirects": [str(r.url) for r in response.history],
        }
