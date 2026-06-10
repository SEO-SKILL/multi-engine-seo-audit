"""
report-agent — 报告生成 + 修复 patch + Final Verdict
对应能力 #5 决策闭环 + #16 健康分
"""
from __future__ import annotations

import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Metrics,
)

SKILL_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)

    snapshots = input_.context.snapshots or {}
    all_findings = []
    for agent_name, agent_data in snapshots.items():
        if agent_name == "crawler":
            continue
        if isinstance(agent_data, dict):
            for f in agent_data.get("findings", []):
                all_findings.append(f)

    artifacts = {
        "total_findings": len(all_findings),
        "report_md_template_used": "report.md.j2",
        "report_html_template_used": "dashboard.html.j2",
    }

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="report",
        status=AgentStatus.OK,
        artifacts=artifacts,
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def render_md(report_data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("report.md.j2")
    return template.render(**report_data)


def render_html_dashboard(report_data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("dashboard.html.j2")
    return template.render(**report_data)
