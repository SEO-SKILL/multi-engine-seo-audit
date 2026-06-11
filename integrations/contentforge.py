"""
ContentForge 集成 hook（BYDFi 内部 SEO 内容工厂）
让 ContentForge 生成内容时自动跑 gate
对照 reference: ~/.claude/projects/-Users-coco/memory/reference_contentforge.md
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def is_configured() -> bool:
    return bool(os.environ.get("CONTENTFORGE_API_URL") or os.environ.get("CONTENTFORGE_WEBHOOK"))


async def pre_publish_check(content_md: str, locale: str = "en") -> dict:
    """
    ContentForge AI 写完内容 → 调用此 hook → 自动跑 BYDFi SEO Audit gate
    返回 pass/fail，让 ContentForge 决定是否打回 AI 重写
    """
    import tempfile
    from agents.gate import gate_md_file

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        f.write(content_md)
        tmp_path = f.name

    try:
        result = await gate_md_file(tmp_path, locale=locale, block_threshold="high")
        return {
            "pass": result["pass"],
            "verdict": result["verdict"],
            "score": result["score"],
            "blockers": result["blockers"],
            "highs": result["highs"],
            "feedback_to_ai": _format_feedback_for_ai(result),
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _format_feedback_for_ai(result: dict) -> str:
    """把 audit findings 转成 AI 能理解的修改提示"""
    if result["pass"]:
        return "✅ Content passed SEO gate. Safe to publish."

    msgs = ["❌ SEO Gate failed. Please revise:"]
    if result["blockers"]:
        msgs.append("\n🔴 MUST FIX (Blockers):")
        for b in result["blockers"]:
            msgs.append(f"  - {b['id']}: {b['rec']}")
    if result["highs"]:
        msgs.append("\n🟠 HIGH PRIORITY:")
        for h in result["highs"]:
            msgs.append(f"  - {h['id']}: {h['rec']}")
    msgs.append("\nPlease address the above and resubmit.")
    return "\n".join(msgs)


async def post_publish_audit(url: str, locale: str | None = None) -> dict:
    """ContentForge 发布后自动跑 audit（监控真实页面）"""
    from orchestrator import Orchestrator
    orch = Orchestrator()
    report = await orch.audit(url=url, locale=locale)
    return {
        "score": report.brand_seo_score,
        "verdict": report.final_verdict.value,
        "trace_id": report.trace_id,
    }


def webhook_payload(audit_result: dict) -> dict:
    """格式化成 ContentForge webhook 期望的 payload"""
    return {
        "tool": "bydfi-seo-audit",
        "version": "1.0",
        "audit_result": audit_result,
        "actionable": not audit_result.get("pass", False),
    }
