"""
Anthropic LLM Client — 统一封装 + 成本控制 + Prompt Caching
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

SKILL_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = SKILL_ROOT / "prompts"

# Model pricing (USD per million tokens) — 按 Codex 调研报告
PRICING = {
    "haiku":  {"input": 1.0,  "output": 5.0,  "cache_write_5m": 1.25, "cache_read": 0.10},
    "sonnet": {"input": 3.0,  "output": 15.0, "cache_write_5m": 3.75, "cache_read": 0.30},
    "opus":   {"input": 5.0,  "output": 25.0, "cache_write_5m": 6.25, "cache_read": 0.50},
}

MODEL_IDS = {
    "haiku":  "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-7",
}


class CostTracker:
    def __init__(self, budget_usd: float = 0.03) -> None:
        self.budget_usd = budget_usd
        self.spent_usd = 0.0
        self.calls: list[dict] = []

    def remaining(self) -> float:
        return max(0.0, self.budget_usd - self.spent_usd)

    def record(self, model: str, input_tokens: int, output_tokens: int,
               cache_write: int = 0, cache_read: int = 0) -> float:
        p = PRICING[model]
        cost = (
            input_tokens * p["input"] / 1_000_000
            + output_tokens * p["output"] / 1_000_000
            + cache_write * p["cache_write_5m"] / 1_000_000
            + cache_read * p["cache_read"] / 1_000_000
        )
        self.spent_usd += cost
        self.calls.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_write": cache_write,
            "cache_read": cache_read,
            "cost_usd": cost,
        })
        return cost


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {name}")
    return path.read_text()


async def judge(
    *,
    prompt_template: str,
    model: str = "haiku",
    inputs: dict[str, Any],
    cost_tracker: CostTracker | None = None,
    system_prompt: str | None = None,
) -> dict:
    """
    LLM Judge 调用封装

    返回结构化 JSON（finding 候选）
    """
    if cost_tracker and cost_tracker.remaining() <= 0:
        return {"skipped": True, "reason": "budget_exhausted"}

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("no_anthropic_api_key", using_stub=True)
        return {
            "stub": True,
            "rule_id": "stub.no-llm-key",
            "severity": "info",
            "confidence": 0.5,
        }

    try:
        from anthropic import AsyncAnthropic
    except ImportError:
        return {"skipped": True, "reason": "anthropic_sdk_not_installed"}

    template_text = load_prompt(prompt_template)
    system = system_prompt or load_prompt("_system")
    user_message = f"{template_text}\n\n## 输入数据\n```json\n{json.dumps(inputs, ensure_ascii=False, indent=2)}\n```"

    client = AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=MODEL_IDS[model],
        max_tokens=1024,
        system=[
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}},
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    usage = response.usage
    if cost_tracker:
        cost_tracker.record(
            model=model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_write=getattr(usage, "cache_creation_input_tokens", 0),
            cache_read=getattr(usage, "cache_read_input_tokens", 0),
        )

    content_text = response.content[0].text if response.content else ""
    try:
        # 提取 JSON 部分（LLM 可能带 ```json fence）
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0]
        return json.loads(content_text.strip())
    except (json.JSONDecodeError, IndexError):
        return {"raw_text": content_text, "parse_error": True}
