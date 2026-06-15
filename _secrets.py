"""
F4 — Secrets / Auth 统一层
凭证管理 + 健康检查 + 日志脱敏
"""
from __future__ import annotations

import os
import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# 注册的 secret 环境变量（启动时检查）
REGISTERED_SECRETS = {
    "ANTHROPIC_API_KEY": {"required_for": ["semantic-agent", "rule_sync (LLM extract)", "content_generator"], "optional": True},
    "GSC_SERVICE_ACCOUNT_JSON": {"required_for": ["log-agent", "compare (real data)"], "optional": True},
    "GSC_OAUTH_TOKEN": {"required_for": ["log-agent (alt)"], "optional": True},
    "GOOGLE_APPLICATION_CREDENTIALS": {"required_for": ["log-agent (ADC alt — auto-detect ~/.config/gcloud/)"], "optional": True},
    "CLOUDFLARE_API_TOKEN": {"required_for": ["log-agent (server logs)"], "optional": True},
    "LARK_WEBHOOK": {"required_for": ["watch alerts (Platform uses Lark/飞书)"], "optional": True},
    "PLATFORM_SLACK_WEBHOOK": {"required_for": ["watch alerts (legacy)"], "optional": True},
    "PERPLEXITY_API_KEY": {"required_for": ["geo-agent (citation testing)"], "optional": True},
    "GA4_PROPERTY_ID": {"required_for": ["conversion_attribution"], "optional": True},
    "GA4_SERVICE_ACCOUNT_JSON": {"required_for": ["conversion_attribution"], "optional": True},
    "DATAFORSEO_API_KEY": {"required_for": ["serp-agent"], "optional": True},
    "AHREFS_API_TOKEN": {"required_for": ["competitor-agent (real API)"], "optional": True},
    "OPENAI_API_KEY": {"required_for": ["cross_llm (V2)"], "optional": True},
    "GOOGLE_AI_API_KEY": {"required_for": ["cross_llm Gemini (V2)"], "optional": True},
}


def health_check() -> dict:
    """启动时调用 — 检查所有 secret 状态"""
    status = {}
    for env_name, meta in REGISTERED_SECRETS.items():
        value = os.environ.get(env_name)
        status[env_name] = {
            "configured": bool(value),
            "length": len(value) if value else 0,
            "required_for": meta["required_for"],
            "optional": meta["optional"],
        }
    return status


def get_secret(name: str, default: str | None = None) -> str | None:
    """获取 secret + 自动 redact 日志"""
    value = os.environ.get(name, default)
    if value:
        logger.debug("secret_accessed", name=name, length=len(value))
    return value


def redact(text: str) -> str:
    """日志脱敏 — 任何看起来像 API key 的字符串都打码"""
    # API key 模式
    patterns = [
        (r"sk-[a-zA-Z0-9-_]{20,}", "sk-***REDACTED***"),
        (r"Bearer\s+[a-zA-Z0-9-_.]{20,}", "Bearer ***REDACTED***"),
        (r"AIza[0-9A-Za-z-_]{35}", "AIza***REDACTED***"),  # Google API key
        (r"ghp_[a-zA-Z0-9]{36}", "ghp_***REDACTED***"),  # GitHub
        (r'"key"\s*:\s*"[^"]+"', '"key": "***REDACTED***"'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def report_health(verbose: bool = False) -> dict:
    """给 doctor 命令用的健康报告"""
    status = health_check()
    summary = {
        "total_secrets": len(status),
        "configured": sum(1 for s in status.values() if s["configured"]),
        "missing": [name for name, s in status.items() if not s["configured"]],
    }
    if verbose:
        summary["detail"] = status
    return summary
