"""
HTML 报告渲染器
跑 audit 后生成橙白配色 HTML dashboard 文件
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402

from agents._schema import Severity  # noqa: E402
from orchestrator import Orchestrator  # noqa: E402


async def render(url: str, locale: str | None = None, output_path: str | None = None) -> str:
    orch = Orchestrator()
    report = await orch.audit(url=url, locale=locale)

    # 提取 composite scores
    composite_scores = {}
    for o in report.agent_outputs:
        if o.agent == "crawler" and o.artifacts.get("composite_scores"):
            composite_scores = o.artifacts["composite_scores"]
            break

    env = Environment(
        loader=FileSystemLoader(SKILL_ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
    )

    # 用现有 dashboard 模板 + 加 composite 数据
    template = env.get_template("dashboard.html.j2")
    html = template.render(
        target=report.target,
        run_id=report.run_id,
        trace_id=report.trace_id,
        project=report.project,
        command=report.command,
        final_verdict=report.final_verdict,
        brand_seo_score=report.brand_seo_score,
        findings_by_severity={k.value: v for k, v in report.findings_by_severity.items()},
        total_metrics=report.total_metrics,
        generated_at=report.generated_at.isoformat() if hasattr(report.generated_at, 'isoformat') else str(report.generated_at),
        composite_scores=composite_scores,
    )

    if not output_path:
        slug = url.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")[:80]
        output_path = SKILL_ROOT / "snapshots" / f"report-{slug}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.html"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"📄 Report saved: {output_path.relative_to(SKILL_ROOT)}")
    print(f"   Score: {report.brand_seo_score:.1f}/100  Verdict: {report.final_verdict.value}")
    return str(output_path)


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://bydfi.com"
    locale = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(render(url=target_url, locale=locale))
