"""
gate-agent — Pre-publish Gate（发布前卡审）
对应能力 #4 + PRD §6.3 场景 2
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

from agents._schema import AgentInput, Command, Context, FinalVerdict, Severity, Target


async def gate_md_file(
    md_file: str | Path,
    locale: str | None = None,
    block_threshold: str = "high",  # blocker / high / medium
) -> dict:
    """
    用 audit pipeline 检查 MD 文件
    返回 {pass, verdict, score, blockers, highs, mediums, report_url}
    """
    md_path = Path(md_file)
    if not md_path.exists():
        return {"pass": False, "error": f"File not found: {md_file}"}

    md_content = md_path.read_text()
    rendered_html = _md_to_html(md_content)

    from orchestrator import Orchestrator
    orch = Orchestrator()

    # 注入虚拟 crawler artifacts（不抓网络，直接喂内容）
    from uuid import uuid4
    from datetime import datetime
    run_id = f"gate-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"
    trace_id = str(uuid4())

    ai = AgentInput(
        trace_id=trace_id,
        run_id=run_id,
        project="bydfi",
        command=Command.GATE,
        target=Target(url=None, locale=locale, content_path=str(md_path)),
        context=Context(snapshots={
            "crawler": {
                "raw_html": rendered_html,
                "rendered_html": rendered_html,
                "headers": {},
                "status_code": 200,
            }
        })
    )

    # 复用 audit pipeline（跳过 crawler stage）
    composite_scores = orch._compute_composite(ai.context.snapshots["crawler"], ai)
    ai.context.snapshots["crawler"]["composite_scores"] = composite_scores

    from agents import technical, safety, geo, lifecycle
    parallel = await asyncio.gather(
        technical.run(ai), safety.run(ai), geo.run(ai), lifecycle.run(ai),
        return_exceptions=True,
    )

    all_findings = []
    from agents._schema import AgentOutput
    for o in parallel:
        if isinstance(o, AgentOutput):
            all_findings.extend(o.findings)

    blockers = [f for f in all_findings if f.severity == Severity.BLOCKER]
    highs = [f for f in all_findings if f.severity == Severity.HIGH]
    mediums = [f for f in all_findings if f.severity == Severity.MEDIUM]

    if block_threshold == "blocker":
        pass_gate = len(blockers) == 0
    elif block_threshold == "high":
        pass_gate = len(blockers) == 0 and len(highs) == 0
    else:  # medium
        pass_gate = len(blockers) == 0 and len(highs) == 0 and len(mediums) < 5

    verdict = (
        FinalVerdict.BLOCKED if blockers
        else FinalVerdict.REVISE_AND_REVIEW if highs or len(mediums) >= 5
        else FinalVerdict.APPROVED
    )

    score = 100.0 - len(blockers) * 40 - len(highs) * 22.5 - len(mediums) * 10
    score = max(0.0, min(100.0, score))

    return {
        "pass": pass_gate,
        "verdict": verdict.value,
        "score": score,
        "blockers": [{"id": f.id, "rec": f.recommendation} for f in blockers],
        "highs": [{"id": f.id, "rec": f.recommendation} for f in highs],
        "mediums": [{"id": f.id, "rec": f.recommendation} for f in mediums],
        "composite_scores": {k: v.get("composite_score") for k, v in composite_scores.items() if isinstance(v, dict) and v.get("composite_score") is not None},
        "run_id": run_id,
    }


def _md_to_html(md: str) -> str:
    """简化 MD → HTML 转换（用于 gate 内部 audit）"""
    html = md
    # H1-H6
    for i in range(6, 0, -1):
        pat = r"^" + ("#" * i) + r"\s+(.+)$"
        html = re.sub(pat, lambda m: f"<h{i}>{m.group(1)}</h{i}>", html, flags=re.MULTILINE)
    # Bold / italic
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    # Links
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    # Paragraphs
    html = "<p>" + html.replace("\n\n", "</p><p>") + "</p>"
    # 包一层
    return f"<!DOCTYPE html><html><head><title>Gate Check</title></head><body>{html}</body></html>"
