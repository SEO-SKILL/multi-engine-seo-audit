"""Sub-Agent 统一 I/O Schema"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Command(str, Enum):
    AUDIT = "audit"
    GATE = "gate"
    COMPARE = "compare"
    WATCH = "watch"


class Platform(str, Enum):
    GOOGLE = "google"
    BING = "bing"
    NAVER = "naver"
    YANDEX = "yandex"
    BAIDU = "baidu"
    YAHOO_JAPAN = "yahoo-japan"
    DUCKDUCKGO = "duckduckgo"
    LLM_ENGINES = "llm-engines"
    SHARED = "shared"
    PLATFORM = "platform"


class Severity(str, Enum):
    BLOCKER = "blocker"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AgentStatus(str, Enum):
    OK = "ok"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"
    SKIPPED_BUDGET = "skipped_budget"


class FindingSource(str, Enum):
    HARD_RULE = "hard_rule"
    LLM_JUDGE = "llm_judge"
    EXTERNAL_API = "external_api"
    DIFF = "diff"


class FinalVerdict(str, Enum):
    APPROVED = "上线"
    REVISE_AND_REVIEW = "改后再审"
    BLOCKED = "暂不上线"


class Target(BaseModel):
    url: str | None = None
    locale: str | None = None
    content_path: str | None = None
    page_type: str | None = None


class Budget(BaseModel):
    usd_remaining: float = Field(default=0.03)
    timeout_ms: int = Field(default=30000)


class Context(BaseModel):
    snapshots: dict[str, Any] = Field(default_factory=dict)
    rules_version: str | None = None
    no_cache: bool = False


class AgentInput(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    project: str = "platform"
    command: Command
    target: Target
    platforms: list[Platform] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    context: Context = Field(default_factory=Context)
    payload: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    url: str | None = None
    selector: str | None = None
    text_snippet: str | None = None
    text_hash: str | None = None
    schema_path: str | None = None
    screenshot_path: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class PatchHint(BaseModel):
    template: str
    priority: str = "P2"
    auto_apply: bool = False
    requires_review: bool = False
    diff_preview: str | None = None


class Finding(BaseModel):
    id: str
    source: FindingSource
    platform: Platform
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Evidence
    recommendation: str
    patch_hint: PatchHint | None = None
    rule_git_sha: str | None = None


class Metrics(BaseModel):
    duration_ms: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_cache_creation: int = 0
    tokens_cache_read: int = 0
    cost_usd: float = 0.0
    cache_hit_rate: float | None = None


class AgentError(BaseModel):
    type: str
    message_sanitized: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentOutput(BaseModel):
    trace_id: str
    agent: str
    status: AgentStatus
    severity_max: Severity | None = None
    findings: list[Finding] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    metrics: Metrics = Field(default_factory=Metrics)
    errors: list[AgentError] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class AuditReport(BaseModel):
    trace_id: str
    run_id: str
    project: str
    command: Command
    target: Target
    final_verdict: FinalVerdict
    brand_seo_score: float = Field(ge=0.0, le=100.0)
    findings_by_severity: dict[Severity, list[Finding]] = Field(default_factory=dict)
    skipped_rules: list[dict] = Field(default_factory=list)
    agent_outputs: list[AgentOutput] = Field(default_factory=list)
    total_metrics: Metrics = Field(default_factory=Metrics)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
