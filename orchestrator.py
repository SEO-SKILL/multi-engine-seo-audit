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
        self.project = self.config.get("default_project", "platform")
        self.project_config = self.config["projects"][self.project]

    def _platforms_for_locale(self, locale: str | None) -> list[Platform]:
        routing = self.project_config.get("platform_routing", {})
        key = locale or "en"
        names = routing.get(key, routing.get("en", ["google"]))
        return [Platform(n) for n in names]

    async def audit(self, url: str, locale: str | None = None, no_cache: bool = False, page_type: str | None = None) -> AuditReport:
        from _page_type import infer_page_type
        run_id = f"audit-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"
        trace_id = str(uuid4())
        page_type = page_type or infer_page_type(url)
        logger.info("audit_start", trace_id=trace_id, run_id=run_id, url=url, page_type=page_type)

        ai = AgentInput(
            trace_id=trace_id,
            run_id=run_id,
            project=self.project,
            command=Command.AUDIT,
            target=Target(url=url, locale=locale, page_type=page_type),
            platforms=self._platforms_for_locale(locale),
            budget=Budget(usd_remaining=0.03, timeout_ms=30000),
            context=Context(no_cache=no_cache),
        )

        outputs = await self._run_pipeline(ai)
        return self._aggregate(ai, outputs)

    async def _run_pipeline(self, ai: AgentInput) -> list[AgentOutput]:
        from agents import crawler, technical, semantic, safety, geo, lifecycle, report, localization

        crawler_out = await crawler.run(ai)
        composite_scores = self._compute_composite(crawler_out.artifacts, ai)
        crawler_out.artifacts["composite_scores"] = composite_scores
        ai2 = ai.model_copy(update={
            "context": Context(snapshots={"crawler": crawler_out.artifacts}, no_cache=ai.context.no_cache)
        })

        parallel = await asyncio.gather(
            technical.run(ai2),
            safety.run(ai2),
            geo.run(ai2),
            lifecycle.run(ai2),
            localization.run(ai2),
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
            }, no_cache=ai2.context.no_cache)
        })
        report_out = await report.run(report_input)
        outputs.append(report_out)
        return outputs

    def _compute_composite(self, artifacts: dict, ai: AgentInput) -> dict:
        """按 locale 路由到对应平台 composite — 每个搜索引擎用各自的核心维度

        - ko → Naver C-Rank / 韩文真实性 / Naver 生态（不套 Google）
        - ru → Yandex MatrixNet / 俄文真实性 / Metrica
        - zh-CN → Baidu ICP / 简体中文 / Baidu 生态
        - 其他 (en/ja/vi/tr/pt/es) → Google E-E-A-T / Schema / 内链
        - 共享 (所有平台): crawlability / performance / multilingual / image
        """
        from detectors import composite as comp
        raw_html = artifacts.get("raw_html", "")
        rendered_html = artifacts.get("rendered_html") or raw_html
        headers = artifacts.get("headers", {})
        locale = ai.target.locale
        if not raw_html:
            return {}

        result: dict = {"_primary_engine": None}
        try:
            # 共享维度（技术层 — 所有引擎共用）
            result["crawlability"] = comp.crawlability_composite(raw_html, headers)
            result["performance"] = comp.performance_composite_quality(raw_html, http_headers=headers)
            result["image"] = comp.image_composite_quality(raw_html, rendered_html)
        except Exception as e:
            logger.warning("composite_shared_failed", error=str(e))

        # 平台专属（每个引擎用自己的核心维度）
        try:
            if locale == "ko":
                result["_primary_engine"] = "naver"
                result["naver_korean"] = comp.naver_composite_quality(raw_html, locale=locale)
                result["geo"] = comp.geo_composite_quality(raw_html)
            elif locale == "ru":
                result["_primary_engine"] = "yandex"
                result["yandex_russian"] = comp.yandex_composite_quality(raw_html, locale=locale, headers=headers)
                result["geo"] = comp.geo_composite_quality(raw_html)
            elif locale == "zh-CN":
                # 已去掉 Baidu — zh-CN 走 Google 海外华人路径
                result["_primary_engine"] = "google"
                result["eeat"] = comp.eeat_composite_quality(raw_html)
                result["schema"] = comp.schema_composite_quality(raw_html, rendered_html)
                result["internal_linking"] = comp.internal_linking_composite_quality(raw_html)
                result["multilingual"] = comp.multilingual_composite_quality(raw_html, locale=locale)
                result["geo"] = comp.geo_composite_quality(raw_html)
            elif locale == "ja":
                # 日本：Google 76% 主导，Yahoo!JAPAN 13% 用 Google 索引但有专属信号
                result["_primary_engine"] = "google+yahoo-jp"
                result["eeat"] = comp.eeat_composite_quality(raw_html)
                result["schema"] = comp.schema_composite_quality(raw_html, rendered_html)
                result["internal_linking"] = comp.internal_linking_composite_quality(raw_html)
                result["multilingual"] = comp.multilingual_composite_quality(raw_html, locale=locale)
                result["geo"] = comp.geo_composite_quality(raw_html)
            else:
                # Google 主战场（en/vi/tr/pt/es）
                result["_primary_engine"] = "google"
                result["eeat"] = comp.eeat_composite_quality(raw_html)
                result["schema"] = comp.schema_composite_quality(raw_html, rendered_html)
                result["internal_linking"] = comp.internal_linking_composite_quality(raw_html)
                result["multilingual"] = comp.multilingual_composite_quality(raw_html, locale=locale)
                result["geo"] = comp.geo_composite_quality(raw_html)
        except Exception as e:
            logger.warning("composite_platform_failed", error=str(e), locale=locale)

        return result

    def _aggregate(self, ai: AgentInput, outputs: list[AgentOutput]) -> AuditReport:
        from _page_type import is_rule_applicable
        from _router import get_router
        from _scope import collect_skipped_rules

        rules_map = get_router().load_all_rules()
        page_type = ai.target.page_type
        platforms = {p.value for p in ai.platforms} | {"shared", "platform"}
        skipped_rules = collect_skipped_rules(rules_map, page_type=page_type, platforms=platforms)

        raw_findings = [f for o in outputs for f in o.findings]
        # rule_id 去重：保留 confidence 最高的 finding（多 agent 检测同条规则时）
        dedup: dict[str, "object"] = {}
        for f in raw_findings:
            ex = dedup.get(f.id)
            if ex is None or (f.confidence or 0) > (ex.confidence or 0):
                dedup[f.id] = f
        all_findings = []
        for f in dedup.values():
            rule = rules_map.get(f.id, {})
            if not is_rule_applicable(rule, page_type):
                logger.debug("finding_filtered_by_page_type", rule_id=f.id, page_type=page_type)
                continue
            rule_platforms = (rule.get("applies_to", {}) or {}).get("platforms", []) or []
            if rule_platforms and not (set(rule_platforms) & platforms):
                logger.debug("finding_filtered_by_platform", rule_id=f.id, platforms=list(platforms))
                continue
            all_findings.append(f)

        by_sev: dict[Severity, list] = {s: [] for s in Severity}
        for f in all_findings:
            by_sev[f.severity].append(f)

        # 非线性扣分（log + 加权差异）— 防多 finding 一刀切归 0
        # blocker 是硬扣分，high/medium/low 用对数平滑
        import math
        b = len(by_sev[Severity.BLOCKER])
        h = len(by_sev[Severity.HIGH])
        m = len(by_sev[Severity.MEDIUM])
        l = len(by_sev[Severity.LOW])
        # blocker 仍硬扣（第 1 个扣 30 ， 之后每个 +10）
        blocker_penalty = (30 + 10 * (b - 1)) if b > 0 else 0
        blocker_penalty = min(blocker_penalty, 50)  # blocker 类上限 50
        # high/medium/low 用 log 平滑（首条扣最多，后续递减）
        high_penalty = 20 * math.log1p(h) if h > 0 else 0      # 1 high≈14, 5 high≈36
        medium_penalty = 8 * math.log1p(m) if m > 0 else 0      # 1 m≈5.5, 5 m≈14
        low_penalty = 3 * math.log1p(l) if l > 0 else 0          # 5 l≈5.4
        score = 100.0 - blocker_penalty - high_penalty - medium_penalty - low_penalty
        score = max(0.0, min(100.0, round(score, 1)))

        # verdict: score 兜底 + severity 联合判定
        if by_sev[Severity.BLOCKER] or score < 50:
            verdict = FinalVerdict.BLOCKED
        elif by_sev[Severity.HIGH] or score < 70:
            verdict = FinalVerdict.REVISE_AND_REVIEW
        elif len(by_sev[Severity.MEDIUM]) >= 5 or len(by_sev[Severity.LOW]) >= 15:
            verdict = FinalVerdict.REVISE_AND_REVIEW
        else:
            verdict = FinalVerdict.APPROVED

        return AuditReport(
            trace_id=ai.trace_id,
            run_id=ai.run_id,
            project=ai.project,
            command=ai.command,
            target=ai.target,
            final_verdict=verdict,
            brand_seo_score=score,
            findings_by_severity={k: v for k, v in by_sev.items() if v},
            skipped_rules=skipped_rules,
            agent_outputs=outputs,
        )
