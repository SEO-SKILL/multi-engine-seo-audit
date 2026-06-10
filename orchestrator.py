"""Main Orchestrator — 调度 10 个 sub-agent"""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog
import yaml

from agents._schema import (
    AgentInput,
    AgentOutput,
    AuditReport,
    Budget,
    Command,
    Context,
    FinalVerdict,
    Platform,
    Severity,
    Target,
)

logger = structlog.get_logger(__name__)

SKILL_ROOT = Path(__file__).parent
CONFIG_PATH = SKILL_ROOT / "config.yaml"


class Orchestrator:
    def __init__(self) -> None:
        self.config = yaml.safe_load(CONFIG_PATH.read_text())
        self.project = self.config.get("default_project", "bydfi")
        self.project_config = self.config["projects"][self.project]

    def _platforms_for_locale(self, locale: str | None) -> list[Platform]:
        routing = self.project_config.get("platform_routing", {})
        key = locale or "en"
        names = routing.get(key, routing.get("en", ["google"]))
        return [Platform(n) for n in names]

    async def audit(self, url: str, locale: str | None = None, no_cache: bool = False) -> AuditReport:
        run_id = f"audit-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"
        trace_id = str(uuid4())
        logger.info("audit_start", trace_id=trace_id, run_id=run_id, url=url)

        ai = AgentInput(
            trace_id=trace_id,
            run_id=run_id,
            project=self.project,
            command=Command.AUDIT,
            target=Target(url=url, locale=locale),
            platforms=self._platforms_for_locale(locale),
            budget=Budget(usd_remaining=0.03, timeout_ms=30000),
            context=Context(no_cache=no_cache),
        )

        outputs = await self._run_pipeline(ai)
        return self._aggregate(ai, outputs)

    async def _run_pipeline(self, ai: AgentInput) -> list[AgentOutput]:
        from agents import crawler, technical, semantic, safety, geo, lifecycle, report

        crawler_out = await crawler.run(ai)
        ai2 = ai.model_copy(update={
            "context": Context(snapshots={"crawler": crawler_out.artifacts})
        })

        parallel = await asyncio.gather(
            technical.run(ai2),
            safety.run(ai2),
            geo.run(ai2),
            lifecycle.run(ai2),
            return_exceptions=True,
        )

        outputs = [crawler_out] + [o for o in parallel if isinstance(o, AgentOutput)]

        # semantic 可选（需 ANTHROPIC_API_KEY）
        try:
            sem = await semantic.run(ai2)
            if isinstance(sem, AgentOutput):
                outputs.append(sem)
        except Exception as e:
            logger.warning("semantic_failed", error=str(e))

        report_input = ai2.model_copy(update={
            "context": Context(snapshots={
                **ai2.context.snapshots,
                **{o.agent: o.model_dump() for o in outputs},
            })
        })
        report_out = await report.run(report_input)
        outputs.append(report_out)
        return outputs

    def _aggregate(self, ai: AgentInput, outputs: list[AgentOutput]) -> AuditReport:
        all_findings = [f for o in outputs for f in o.findings]
        by_sev: dict[Severity, list] = {s: [] for s in Severity}
        for f in all_findings:
            by_sev[f.severity].append(f)

        if by_sev[Severity.BLOCKER]:
            verdict = FinalVerdict.BLOCKED
        elif by_sev[Severity.HIGH]:
            verdict = FinalVerdict.REVISE_AND_REVIEW
        elif len(by_sev[Severity.MEDIUM]) >= 5 or len(by_sev[Severity.LOW]) >= 15:
            verdict = FinalVerdict.REVISE_AND_REVIEW
        else:
            verdict = FinalVerdict.APPROVED

        score = 100.0
        score -= len(by_sev[Severity.BLOCKER]) * 40
        score -= len(by_sev[Severity.HIGH]) * 22.5
        score -= len(by_sev[Severity.MEDIUM]) * 10
        score -= len(by_sev[Severity.LOW]) * 2.5
        score = max(0.0, min(100.0, score))

        return AuditReport(
            trace_id=ai.trace_id,
            run_id=ai.run_id,
            project=ai.project,
            command=ai.command,
            target=ai.target,
            final_verdict=verdict,
            brand_seo_score=score,
            findings_by_severity={k: v for k, v in by_sev.items() if v},
            agent_outputs=outputs,
        )
