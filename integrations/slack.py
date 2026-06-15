"""Webhook 告警 — 支持 Slack 和飞书 Lark（按 URL 自动识别）"""
from __future__ import annotations

import os

import httpx


def _is_lark(url: str) -> bool:
    return "larksuite.com" in url or "feishu.cn" in url


def _to_lark_payload(payload: dict) -> dict:
    """把 Slack 风格 payload 转成 Lark 文本消息"""
    text = payload.get("text") or ""
    blocks = payload.get("blocks") or payload.get("attachments")
    if blocks and not text:
        lines = []
        for b in blocks:
            t = b.get("text")
            if isinstance(t, dict):
                lines.append(t.get("text", ""))
            elif isinstance(t, str):
                lines.append(t)
        text = "\n".join(filter(None, lines))
    return {"msg_type": "text", "content": {"text": text or "(empty alert)"}}


async def send_alert(payload: dict, webhook_env: str | None = None) -> bool:
    # 优先 LARK_WEBHOOK，兼容旧的 PLATFORM_SLACK_WEBHOOK
    candidates = [webhook_env] if webhook_env else ["LARK_WEBHOOK", "PLATFORM_SLACK_WEBHOOK"]
    webhook_url = next((os.environ.get(c) for c in candidates if c and os.environ.get(c)), None)
    if not webhook_url:
        return False
    body = _to_lark_payload(payload) if _is_lark(webhook_url) else payload
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(webhook_url, json=body)
            return resp.status_code == 200
        except Exception:
            return False
