"""Slack Webhook 告警"""
from __future__ import annotations

import json
import os

import httpx


async def send_alert(payload: dict, webhook_env: str = "BYDFI_SLACK_WEBHOOK") -> bool:
    webhook_url = os.environ.get(webhook_env)
    if not webhook_url:
        return False
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(webhook_url, json=payload)
            return resp.status_code == 200
        except Exception:
            return False
