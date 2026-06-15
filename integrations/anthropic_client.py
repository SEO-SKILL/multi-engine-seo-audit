"""
Anthropic LLM Client — 统一封装 + 成本控制 + Prompt Caching + 本地结果 Cache
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import structlog

# 本地 diskcache: 30 分钟 TTL 防 LLM 输出抖动 + 节省成本
_LLM_CACHE_DIR = Path("/tmp/seo-llm-cache")
_LLM_CACHE_TTL = 1800  # 30 分钟
_llm_cache = None


def _get_cache():
    global _llm_cache
    if _llm_cache is None:
        try:
            from diskcache import Cache
            _LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            _llm_cache = Cache(str(_LLM_CACHE_DIR))
        except Exception as e:
            logger.warning("llm_cache_init_failed", error=str(e))
            _llm_cache = False  # 标记不可用
    # diskcache.Cache.__bool__ uses __len__ → 空 cache 会被当 False
    # 必须用 is False / is not None 显式检查
    return _llm_cache if _llm_cache is not False else None


def _cache_key(model: str, prompt_template: str, inputs: dict, system_prompt_hash: str) -> str:
    payload = {
        "m": model, "p": prompt_template, "i": inputs, "s": system_prompt_hash[:16],
        "v": 1,  # 升级 → 整体 invalidate
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

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


async def _gemini_fallback(system_prompt: str, user_message: str) -> dict | None:
    """Gemini 免费层 fallback（1500 req/day · 15 req/min）"""
    api_key = os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        import httpx
    except ImportError:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": user_message}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "maxOutputTokens": 4096,
            "thinkingConfig": {"thinkingBudget": 0},  # 关 thinking 避免 token 浪费在 reasoning
        },
    }
    # 使用 sync httpx 在 asyncio.to_thread 中调用，避开嵌套 asyncio.run 的 Event loop closed 问题
    import asyncio
    def _do_sync():
        try:
            r = httpx.post(url, json=payload, timeout=30)
            if r.status_code != 200:
                logger.warning("gemini_fallback_failed", status=r.status_code, body=r.text[:200])
                return None
            data = r.json()
            cand = data.get("candidates", [{}])[0]
            text = cand.get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text:
                logger.warning("gemini_empty_text", finish_reason=cand.get("finishReason"))
                return None
            try:
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                return json.loads(text.strip())
            except (json.JSONDecodeError, IndexError):
                logger.warning("gemini_parse_failed", text_len=len(text), finish_reason=cand.get("finishReason"))
                return {"raw_text": text[:500], "parse_error": True}
        except Exception as e:
            logger.warning("gemini_fallback_exception", error=str(e)[:200])
            return None
    return await asyncio.to_thread(_do_sync)


async def judge(
    *,
    prompt_template: str,
    model: str = "haiku",
    inputs: dict[str, Any],
    cost_tracker: CostTracker | None = None,
    system_prompt: str | None = None,
    no_cache: bool = False,
) -> dict:
    """
    LLM Judge 调用封装

    返回结构化 JSON（finding 候选）

    确定性 + 缓存：
    - temperature=0 让同 prompt 出同 finding
    - diskcache TTL=30min，key=hash(model+prompt+inputs)
    - no_cache=True 强制走真 LLM
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

    # === 本地 cache 查询 ===
    sys_hash = hashlib.sha256(system.encode()).hexdigest()
    ck = _cache_key(model, prompt_template, inputs, sys_hash)
    cache = None if no_cache else _get_cache()
    if cache is not None:
        hit = cache.get(ck)
        if hit is not None:
            hit_copy = dict(hit)
            hit_copy["_cache_hit"] = True
            return hit_copy

    # === Anthropic 失败时自动 fallback 到 Gemini 免费层 ===
    client = AsyncAnthropic(api_key=api_key)
    try:
        response = await client.messages.create(
            model=MODEL_IDS[model],
            max_tokens=1024,
            temperature=0,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as anthropic_err:
        err_str = str(anthropic_err).lower()
        # 余额耗尽 / rate limit / 认证失败 → fallback Gemini
        if any(s in err_str for s in ["credit balance", "insufficient", "rate limit", "401", "402", "429"]):
            gemini_result = await _gemini_fallback(system, user_message)
            if gemini_result is not None:
                if cache is not None:
                    try: cache.set(ck, gemini_result, expire=_LLM_CACHE_TTL)
                    except Exception: pass
                out = dict(gemini_result); out["_cache_hit"] = False; out["_provider"] = "gemini"
                return out
        logger.warning("llm_judge_failed", error=str(anthropic_err)[:200])
        return {"skipped": True, "reason": "llm_failed", "error": str(anthropic_err)[:200]}

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
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0]
        result = json.loads(content_text.strip())
    except (json.JSONDecodeError, IndexError):
        result = {"raw_text": content_text, "parse_error": True}

    # === 写 cache（TTL=30min）===
    if cache is not None and not result.get("parse_error"):
        try:
            cache.set(ck, result, expire=_LLM_CACHE_TTL)
        except Exception as ce:
            logger.warning("llm_cache_set_failed", error=str(ce))

    result_out = dict(result)
    result_out["_cache_hit"] = False
    return result_out
