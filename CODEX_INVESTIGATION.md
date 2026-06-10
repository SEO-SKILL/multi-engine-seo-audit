# BYDFi SEO Audit Skill Phase 0 技术调研报告

> 日期：2026-06-10  
> 范围：只做技术调研，不写实现代码。  
> 依据：已按顺序阅读 `PRD.md`、`tasks/todo.md`、`SKILL.md`、`config.yaml`、`tasks/lessons.md`。  
> 说明：凡 PRD/todo/config/lessons 未明确的内容，均标注“PRD 未指定，建议方案”。

## 1. 技术栈选型

### Python 版本

推荐：**Python 3.12+，开发基线锁 3.12，CI 增加 3.13 兼容检查**。

理由：

- PRD 要求 V1 4 周交付，重点是稳定抓取、规则引擎、LLM 成本控制、测试覆盖，而不是追新语法（PRD §2.1、§9.1）。
- Python 官方状态页显示，截至 2026-05-27，3.12 已进入 security，3.13/3.14 是 bugfix；3.11 也是 security。3.12 比 3.11 生命周期更长，又比 3.13/3.14 的生态风险更低。来源：https://devguide.python.org/versions/
- 核心依赖均支持 3.12：Playwright、Anthropic SDK、Pydantic、pytest、structlog、tenacity、orjson、jsonschema 等在 PyPI 页面均声明支持 3.12。
- 3.12 提供更好的 typing 语法和性能改进，足够支撑 Pydantic schema、async orchestrator、structured logging。来源：https://docs.python.org/3.12/whatsnew/3.12.html

不推荐直接 3.13+ 作为唯一基线：

- PRD 验收含 `< 30s`、`< $0.02`、Prompt Caching 命中率和 90% 单测覆盖（PRD §9.1），先要减少变量。
- Playwright 浏览器二进制、解析库 wheel、CI 镜像在 3.13 上通常可用，但 V1 没有必要把兼容风险放到主路径。

### 核心依赖清单

版本以 2026-06-10 官方 PyPI/文档页面为准；实现时建议用 `~=x.y` 或 lockfile 固定补丁版本。

| 领域 | 推荐库与版本 | 选用理由 | 替代方案 |
|---|---:|---|---|
| 包/环境管理 | `uv` | 速度快，统一 virtualenv、lock、tool runner；适合 Codex/Claude 高频迭代。官方：https://docs.astral.sh/uv/ | `pip-tools` 简单可靠；`poetry` 功能完整但慢且项目迁移成本高 |
| HTTP 抓取 | `httpx 0.28.1` | async/sync 双接口，支持 HTTP/2、代理、严格 timeout；适合 crawler-agent 轻量抓取。PyPI：https://pypi.org/project/httpx/ | `aiohttp` 并发更强但 API 更重；`requests` 不适合 async |
| 浏览器渲染 | `playwright 1.60.0` | 官方 Python 包，支持 Chromium/Firefox/WebKit，适合 JS 渲染、UA/DOM diff、截图。PyPI：https://pypi.org/project/playwright/；文档：https://playwright.dev/python/docs/intro | Selenium 生态老但慢；Pyppeteer 维护弱 |
| HTML 解析 | `beautifulsoup4 4.15.0` + `lxml 6.1.1` | todo 明确 technical-agent 使用 BeautifulSoup；lxml 提供 XPath/XML/sitemap 解析性能。PyPI：https://pypi.org/project/beautifulsoup4/、https://pypi.org/project/lxml/ | `selectolax` 更快但 API 小众；`parsel` 适合 scrapy 生态 |
| Schema/DTO | `pydantic 2.13.4` | agent 输入输出、规则 YAML、报告 JSON 需要强校验；V2 保留 multi-tenant hook 也需要 typed config。PyPI：https://pypi.org/project/pydantic/ | `dataclasses` 轻但校验弱；`attrs` 成熟但 JSON schema 支持弱 |
| JSON Schema 校验 | `jsonschema 4.26.0` | 用于 sub-agent I/O contract、LLM 输出结构校验、fixture expected JSON。PyPI：https://pypi.org/project/jsonschema/ | 只用 Pydantic；但跨语言/文档化不如 JSON Schema |
| JSON 序列化 | `orjson 3.11.9` | 快速写 snapshot、cost log、trace log。PyPI：https://pypi.org/project/orjson/ | 标准库 `json` 零依赖但慢 |
| YAML | `PyYAML 6.0.3` | PRD 规则库是 YAML，Rule Sync 也要输出 YAML（PRD §7、todo Phase 3）。PyPI：https://pypi.org/project/PyYAML/ | `ruamel.yaml` 保留注释更好，但复杂度高 |
| 模板渲染 | `Jinja2 3.1.6` | PRD 文件布局已指定 `report.md.j2`、`dashboard.html.j2`、`patch.diff.j2`（PRD §7）。PyPI：https://pypi.org/project/Jinja2/ | f-string/Markdown 拼接不利于多格式输出 |
| LLM SDK | `anthropic 0.109.1` | 官方 Python SDK，支持 sync/async、usage、request ID、默认 retry、count_tokens。PyPI：https://pypi.org/project/anthropic/；文档：https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python | 直接 HTTP API，控制更细但重复造轮子 |
| Retry/熔断 | `tenacity 9.1.4` | PRD F3 要 retry/degrade/circuit breaker；tenacity 适合统一重试策略。PyPI：https://pypi.org/project/tenacity/ | 自写 retry；`backoff` 更轻 |
| 本地缓存 | `diskcache 5.6.3` | 无需 Redis，适合单租户 BYDFi 和本地抓取缓存；PRD 只要求 V1 单租户（PRD §4、SKILL 项目范围）。PyPI：https://pypi.org/project/diskcache/ | SQLite 自写；Redis 适合 V2 多租户/并发 |
| 结构化日志 | `structlog 26.1.0` | PRD F5 要 trace ID、agent 耗时、LLM 日志；structlog 原生 JSON/logfmt。PyPI：https://pypi.org/project/structlog/ | 标准库 logging + JSON formatter；OpenTelemetry 后续接入 |
| 测试 | `pytest 9.0.3` + `pytest-cov` | todo Phase 6 明确 pytest、覆盖率、e2e fixture。PyPI：https://pypi.org/project/pytest/ | `unittest` 可用但 fixture/snapshot 体验差 |
| 代码质量 | `ruff 0.15.16` + `mypy 2.1.0` | 快速 lint/format/type check，降低多 agent 协作回归。PyPI：https://pypi.org/project/ruff/、https://pypi.org/project/mypy/ | black/isort/flake8 组合更慢 |

PRD 未指定，建议暂不引入：

- FastAPI：V1 是 Claude Code Skill + CLI 命令，不是长驻 Web 服务（PRD §6.3、SKILL 4 个核心命令）。
- Scrapy：全站 watch 可以后续评估，但 V1 先用 async httpx + Playwright 足够，避免框架重量。
- Redis/Celery/Kafka：单租户、本地命令式运行，不需要先上分布式队列。

### 包管理推荐

推荐：**uv + `pyproject.toml` + lockfile**。

理由：

- todo Phase 0 要初始化 `requirements.txt` / `pyproject.toml`，没有指定包管理器。
- uv 更适合短周期 Codex 执行：创建环境、安装依赖、运行工具都快；lockfile 可复现。
- poetry 在发布库时体验好，但本项目是本地 Skill/CLI，不需要复杂 build/publish。
- pip 单独使用缺少 lock 与 workspace 体验；可输出 `requirements.txt` 给 Claude Code 环境兜底。

落地建议：以 `pyproject.toml` 为主，`uv.lock` 锁依赖，必要时生成 `requirements.txt` 给无 uv 环境。PRD 未指定，建议方案。

## 2. Sub-Agent 接口规范

### 统一输入 JSON Schema

PRD 已定义 10 个 sub-agent 职责（PRD §6.2），但未定义接口。建议所有 agent 使用同一 envelope，业务字段放 `payload`。

最小 schema：

```json
{
  "trace_id": "uuid",
  "run_id": "audit-20260610-001",
  "project": "bydfi",
  "command": "audit|gate|compare|watch",
  "target": {"url": "...", "locale": "ko", "content_path": null},
  "platforms": ["naver", "google", "bing", "llm-engines"],
  "budget": {"usd_remaining": 0.02, "timeout_ms": 30000},
  "context": {"snapshots": {}, "rules_version": "git-sha"},
  "payload": {}
}
```

### 统一输出 JSON Schema

```json
{
  "trace_id": "uuid",
  "agent": "semantic-agent",
  "status": "ok|partial|failed|skipped",
  "severity_max": "blocker|high|medium|low|info",
  "findings": [],
  "artifacts": {},
  "metrics": {"duration_ms": 0, "tokens": {}, "cost_usd": 0},
  "errors": [],
  "next_actions": []
}
```

统一 finding 字段：

- `id`：稳定规则 ID，如 `bydfi.L02.ticker-context-mismatch`。
- `source`：`hard_rule|llm|external_api|diff`。
- `platform`：`google|bing|naver|yandex|llm-engines|shared|bydfi`。
- `severity`：`blocker|high|medium|low|info`。
- `confidence`：0-1。
- `evidence`：URL、HTML selector、文本片段 hash、schema path、screenshot path。
- `recommendation`：修复建议。
- `patch_hint`：给 report-agent 生成 patch 的结构化输入。

### 10 个 agent 的 payload 约定

| Agent | 输入 payload | 输出 artifacts |
|---|---|---|
| crawler-agent | URL 列表、UA 列表、proxy 策略、render_required | raw HTML、rendered DOM、headers、status、screenshots、UA diff |
| technical-agent | crawler artifacts、sitemap/robots URL、platform rules | schema/hreflang/canonical/robots/sitemap findings |
| semantic-agent | visible text、title/H1/body/CTA、source/canonical text、ticker candidates | intent chain、原创增量、E-E-A-T、schema truthfulness |
| serp-agent | query、locale、device、platform | SERP features、AI Overview/引用、CTR estimate |
| competitor-agent | self URL、competitor URLs/CSV、metric config | competitor snapshot、diff、gap list |
| safety-agent | page text、links、ticker list、compliance regions | ticker/context、risk keyword、hacked/negative SEO basic |
| log-agent | GSC property、Cloudflare/fly log range、URL set | crawl stats、index coverage、Googlebot behavior |
| lifecycle-agent | URL inventory、internal links、GSC metrics | cannibalization、merge/prune/decay candidates |
| geo-agent | page chunks、entity list、LLM test queries | llms.txt、answerable chunks、LLM citation findings |
| report-agent | all agent outputs、rules version、template config | MD/HTML/JSON report、Final Verdict、patch diff、Brand SEO Score |

### Orchestrator 调度、聚合、容错

调度建议：

1. 初始化 `run_id/trace_id`，加载 `config.yaml` 项目配置和 platform routing（config `projects.bydfi.platform_routing`）。
2. 先跑 crawler-agent；没有抓取产物时，technical/semantic/geo/safety 都缺输入。
3. 按命令选择 agent graph：`audit/gate` 走单页风险；`compare` 加 competitor；`watch` 加 log/lifecycle/safety diff（PRD §6.3、SKILL 4 个核心命令）。
4. Platform Router 先基于 locale 选择规则集，再把规则集传给各 agent。
5. 聚合时按 severity、confidence、平台权重、BYDFi 专属规则优先级计算 Final Verdict。
6. report-agent 是唯一允许生成最终用户输出和 patch 的 agent，避免多 agent 输出风格不一致。

容错建议：

- `crawler-agent` 失败：若缓存未过期，允许 `partial` 继续；无缓存则 audit/gate 直接 `failed`。
- `semantic-agent` LLM 超时：降级为硬规则 + `needs_human_review`，gate 对 blocker 风险默认不放行。
- `serp-agent` 外部 SERP 被限流：audit 不阻塞，compare/watch 标为 partial。
- `log-agent` GSC/Cloudflare 凭证缺失：watch partial，不影响 audit/gate。
- 任一 agent 超过预算：返回 `skipped_budget`，report-agent 必须披露缺失维度。

### 数据依赖与 message bus

结论：**V1 不需要 message bus；用 in-process async task graph + 文件 artifacts 即可**。

理由：

- PRD 指定单租户 BYDFi，multi-tenant 只保留 hook（PRD §4、SKILL 项目范围）。
- V1 验收是单页审核 `< 30s` 和 5 个 fixture e2e（PRD §9.1），引入 message bus 会增加运维面。
- agent 依赖主要是 crawler 产物和 rule set，不是持续事件流。

V2 触发条件：

- watch 全站抓取超过 10k URL；
- 多租户真实化；
- 需要跨机器调度或任务恢复；
- 规则同步与 crawl/watch 要独立部署。

低成本 V2 替代：SQLite job table + file lock；再升级 Redis Queue/RQ；最后才考虑 Kafka/NATS。

### 并行 vs 串行判定规则

串行硬依赖：

- crawler-agent 必须先于 technical/semantic/safety/geo。
- Platform Router 必须先于规则执行。
- report-agent 必须最后。
- gate 必须等待 Final Verdict。

可并行：

- technical、semantic、safety、geo 在 crawler 产物可用后并行。
- compare 的多个 URL 抓取并行，但每个域名限速。
- rules 同步中各平台官方源抓取并行；LLM 提取可按源并行；diff/PR 串行。

半串行：

- semantic 的“原创增量 vs canonical 来源”依赖 canonical/source 抓取；若 source 抓取失败，先跑页面内 E-E-A-T/intent，原创增量标 partial。
- serp-agent 不应阻塞 audit 的风险结论，但 compare/watch 需要等待 SERP 指标。

## 3. 抓取层架构（crawler-agent）

### xcrawl vs Playwright 分工

PRD/todo 明确 crawler-agent 需要 xcrawl、playwright、多 IP、多 UA、raw HTML vs rendered DOM diff（todo Phase 2 crawler-agent）。PRD 未指定 xcrawl API 细节，建议如下：

| 场景 | 用 xcrawl | 用 Playwright |
|---|---|---|
| 普通 HTML、headers、status、robots、sitemap | 首选 | 不用 |
| raw HTML 抓取、canonical、SSR JSON-LD | 首选 | 不用 |
| 页面强 JS、CSR JSON-LD、懒加载正文 | 先 xcrawl 探测 | 必须 |
| Cloaking 多 UA 对比 | 先 xcrawl 多 UA | 对差异页 Playwright 复核 |
| 截图、可见文本、DOM after hydration | 不适合 | 必须 |
| SERP 页面渲染 | 谨慎，限速 | 必要时用，但优先官方 API/手动导入 |

核心策略：**默认轻量，证据不足再渲染**。这样满足 PRD `< 30s` 和成本要求，同时能防 lessons L04 的“JSON-LD raw HTML 缺失，仅渲染后输出”。

### 何时判定 JS 渲染必须

触发 Playwright 的条件：

- raw HTML 正文长度低于阈值，如 visible text `< 800 chars`，但页面 title/meta 表示是内容页。
- raw HTML 没有 JSON-LD，但 rendered DOM 有 JSON-LD，命中 lessons L04。
- canonical/hreflang/robots/schema 在 raw 与 rendered 不一致。
- HTTP body 存在 `__NEXT_DATA__`/hydration bundle 且主体内容由 JS 注入。
- 多 UA raw 抓取存在高风险差异，需截图和 DOM 证据。

### 多 UA 对比

UA 组合：

- Googlebot Desktop
- Googlebot Mobile
- 真实 Chrome Desktop
- 真实 Chrome Mobile

对比维度：

- status code、redirect chain、canonical、robots meta、hreflang 数量/目标、JSON-LD 类型、visible text hash、主要 heading、主要 CTA、内部链接数量。
- 差异分级：`expected_device_diff`（布局/图片）、`seo_signal_diff`（canonical/robots/hreflang/schema）、`content_diff`（正文/CTA/链接）、`blocker_cloaking`（Googlebot 与真实用户内容主题不同）。

MEXC 事故防护：

- lessons L03 要求 hreflang alternate 必须真实存在、可抓取、可索引、语言匹配。
- lessons L04 要求 JSON-LD 字段与可见内容一致且 SSR 输出关键字段。
- 多 UA diff 直接覆盖 PRD 能力 #3 多源真实抓取 + Cloaking 检测（PRD §3.1）。

### 多 IP 池接入

V1 推荐：**本地出口 + 1-2 个低成本代理，不上大型住宅 IP 池**。

理由：

- PRD V1 验收重点是 BYDFi 自有页面 audit/gate，不是大规模竞品爬取（PRD §2.1、§9.1）。
- config crawler 限速是 `requests_per_second: 2`、`max_concurrent: 5`，说明默认不是高并发采集。
- 抓竞品要遵守 robots.txt 和限速（PRD §10.3）。

接入方式：

- proxy profile：`direct`、`proxy_a`、`proxy_b`。
- 每个 fetch attempt 记录 `proxy_id`、出口国家、失败原因。
- 只有 403/429/timeout 或 Googlebot UA 被异常阻断时切代理。
- 不把代理凭证写日志，符合 PRD F4 secrets/log 脱敏（todo Phase 1 F4）。

免费/低成本替代：

- 本地网络 direct + Cloudflare/GSC 官方数据补证。
- 用户手动导入 Ahrefs CSV（PRD/todo 已指定 V1 CSV，API V2）。
- SERP 先用低频人工采样/CSV，不把搜索引擎页面爬取作为 V1 主路径。
- 代理供应商仅用按量 datacenter proxy；住宅 proxy 作为 V2 风险项，不默认采购。

### raw HTML vs rendered DOM diff

实现方案（工程设计，不写代码）：

- 保存 `raw.html`、`rendered.html`、`visible_text.txt`、`seo_signals.json`。
- 对 HTML 先做规范化：移除 script/style/noscript hash 噪音、排序 JSON-LD key、规范化空白。
- 生成两类 diff：结构化 SEO signal diff 与文本/DOM hash diff。
- SEO signal diff 优先级高于全文 diff，因为 gate 需要可解释 finding。
- 每条差异都要有 selector/path/evidence hash，避免 LLM 只能给模糊结论。

快照命名建议见第 7 章。

## 4. LLM 成本控制

### Anthropic SDK 集成方式

推荐使用官方 Python SDK `anthropic 0.109.1` 的 async client：

- 官方 SDK 支持 sync/async、streaming、usage、count_tokens、request ID、默认 retry。来源：https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
- 每次 LLM 调用都通过统一 `LLMClient` 包装：注入 trace_id、model route、timeout、max_tokens、cache_control、budget guard、usage log。
- 只允许 semantic-agent、geo-agent、report-agent、rule-extract-agent 调 LLM；technical/crawler/safety 的硬规则优先。
- SDK 默认 retry 是 2 次；外层 tenacity 只处理业务级 retry，避免重复重试放大成本。

### Prompt Caching 命中率 80%

Anthropic 官方价格页说明 Prompt Caching 可缓存大型 system prompt、文档、对话历史；5 分钟 cache write 为 1.25x，1 小时为 2x，cache read 为 0.1x。来源：https://platform.claude.com/docs/en/about-claude/pricing

要达到 80% 命中率，缓存必须放在稳定前缀：

缓存内容：

- 固定 system prompt：BYDFi SEO 审核口径、输出 schema、severity 定义。
- BYDFi 专属规则摘要：MEXC 7 类事故、ticker 白名单/黑名单、E-E-A-T 风控口径（lessons L01-L06、PRD §1.1）。
- 平台规则摘要：Google/Bing/Naver/Yandex/LLM 规则集当前版本。
- JSON output schema 与 few-shot fixture 摘要。

不缓存内容：

- 当前页面 HTML/visible text。
- 当前 URL、当前 SERP、当前 competitor diff。
- 用户临时 override。

命中率工程规则：

- 同一次 `audit` 内 semantic/schema/E-E-A-T/patch synthesis 复用同一个 cached prefix。
- `watch` 周报同一批 URL 使用 1 小时缓存。
- 规则库变更后 cache key 包含 `rules_git_sha`，避免旧规则污染。
- 对单页零散 audit，5 分钟缓存命中率可能不足；对 gate 批量提交和 watch 可超过 80%。报告中应披露按 workload 统计，而不是全局平均。

### 模型分级路由

config 已给出 `simple_classification: haiku`、`semantic_judgment: opus`、`report_synthesis: sonnet`。PRD §10.1 写“Haiku/Opus”，但 Anthropic 官方成本建议是简单任务 Haiku、生产主力 Sonnet、复杂推理 Opus。来源：https://platform.claude.com/docs/en/about-claude/pricing

建议路由：

| 任务 | 默认模型 | 升级/降级规则 |
|---|---|---|
| 规则 YAML 提取初筛 | Haiku 4.5 | 只做分类/字段抽取；重大 diff 再 Sonnet |
| ticker 上下文初判 | Haiku 4.5 | confidence 0.4-0.8 交 Sonnet |
| 原创增量/E-E-A-T/意图链 | Sonnet 4.6 | 涉及金融/人工处置/高相似转载且 gate 阻断时升 Opus |
| Schema 真实性解释 | Sonnet 4.6 | 硬规则证据充分时不用 LLM |
| Final report synthesis | Sonnet 4.6 | 只合并 finding，不重新判断事实 |
| 规则重大变化审核摘要 | Sonnet 4.6 | 政策变化影响 gate 规则时升 Opus |
| Opus | Opus 4.8 | 仅用于“会决定上线/暂不上线”的高风险争议项 |

截至官方价格页：

- Claude Haiku 4.5：input $1/MTok，cache hit $0.10/MTok，output $5/MTok。
- Claude Sonnet 4.6：input $3/MTok，cache hit $0.30/MTok，output $15/MTok。
- Claude Opus 4.8：input $5/MTok，cache hit $0.50/MTok，output $25/MTok。
- Prompt cache write/read 价格同官方表，5m write 1.25x，1h write 2x，read 0.1x。来源：https://platform.claude.com/docs/en/about-claude/pricing

### 单次 audit 成本 < $0.02 可行性

用户写的“< /bin/zsh.02”应为 `< $0.02`；PRD §9.1 明确单页审核成本 `< $0.02`。config 当前 `per_audit: 0.05`，与 PRD 验收冲突；建议按 PRD 更严格目标执行，config 后续改为 warn 0.015 / hard stop 0.02。

可行模型：**可行，但必须限制 Opus 触发率，并把 LLM 输入做摘要化**。

预算估算（单页 audit，常规页面）：

| 调用 | 模型 | 输入 | 输出 | 成本估算 |
|---|---|---:|---:|---:|
| ticker/分类初筛 | Haiku | 2k uncached + 8k cache hit | 500 | $0.0025 + $0.0008 + $0.0025 = $0.0058 |
| semantic 主判 | Sonnet | 4k uncached + 12k cache hit | 700 | $0.0120 + $0.0036 + $0.0105 = $0.0261 |
| report synthesis | Sonnet | 2k uncached + 8k cache hit | 900 | $0.0060 + $0.0024 + $0.0135 = $0.0219 |

以上“三次 LLM 全开”会超预算。因此 V1 成本控制必须改成：

- semantic 主判合并 ticker/E-E-A-T/intent/schema truthfulness，一次 Sonnet 调用解决。
- report-agent 默认模板化，不再 LLM synthesis；只有用户要求 narrative report 才调用 Sonnet。
- Haiku 只在页面复杂或 ticker candidates 多时调用；硬规则可直接跳过。

压缩后常规成本：

| 调用 | 模型 | 输入 | 输出 | 成本 |
|---|---|---:|---:|---:|
| semantic 合并判定 | Sonnet | 3k uncached + 12k cache hit | 800 | $0.009 + $0.0036 + $0.012 = $0.0246 |

仍略超。要稳定 `< $0.02`，需采用：

- 默认 Haiku 先判：3k uncached + 12k cache hit + 600 output ≈ $0.003 + $0.0012 + $0.003 = $0.0072。
- 仅当 Haiku 输出 `risk_score >= 0.65` 或 `confidence < 0.75` 时升 Sonnet。
- Sonnet 只接收 1.5k evidence 摘要，不接全文：1.5k uncached + 12k cache hit + 500 output ≈ $0.0045 + $0.0036 + $0.0075 = $0.0156。
- 常规页只 Haiku，成本约 $0.007；高风险页 Haiku+Sonnet 约 $0.023，允许触发 gate blocker，但计入“需人工复核”成本例外。

结论：

- 若要求所有页面、所有风险级别都 `< $0.02`，不可稳定保证。
- 若按 V1 目标“单页常规 audit 平均成本 `< $0.02`，高风险阻断可超预算但必须记录”，可行。
- Kelly 需要拍板：成本 KPI 是平均值、P95，还是每次 hard cap。建议：V1 hard cap $0.03、平均 <$0.02；V2 优化到 hard cap $0.02。

## 5. 规则同步管道

PRD F8 要每日 pull + LLM 提取 + 自动 PR（PRD §4、§9.1）；config 已列出 Google/Bing/Naver/Yandex 和第三方源，但 PRD 平台规则 V1 还包含 LLM engines（PRD §5.1）。建议补 LLM engine 官方源，不依赖第三方新闻作为硬规则来源。

### 每日 pull → YAML 流程

流程：

1. `daily-pull-agent` 读取 config `framework.rule_sync.sources`，按平台抓取官方源。
2. 抓取后保存 raw page、ETag/Last-Modified、content hash。
3. 仅 hash 变化的文档进入 LLM extract；无变化跳过。
4. `rule-extract-agent` 用 Haiku 提取候选：规则标题、适用平台、影响页面类型、禁止/建议动作、证据 URL、发布日期。
5. Sonnet 对候选去重、归并到 YAML schema。
6. `diff-engine` 与上一版 YAML 对比，输出 `minor|major|breaking|uncertain`。
7. `alert-agent` 对 major/breaking/uncertain 发 Slack，minor 可自动 PR。
8. `version-manager` 创建 branch、commit、PR；不直接改 main。

YAML rule 字段建议：

- `id`、`platform`、`source_url`、`source_published_at`、`pulled_at`、`rule_type`、`severity_default`、`applies_to`、`detector_hint`、`human_review_required`、`supersedes`、`confidence`。

### 重大变化判定

判定为 major/breaking：

- 官方源包含 manual action、spam policy、helpful content、structured data eligibility、AI Overview inclusion/exclusion。
- 规则 severity 从建议变为禁止，或影响 gate blocker。
- 改变 canonical/hreflang/robots/schema 的硬规则。
- 影响 BYDFi 9 语言路由或金融/crypto 合规口径。
- LLM 抽取 confidence < 0.8 或同一文档中存在冲突描述。

必须人工审核：

- Google manual actions/spam policies；
- Naver/Yandex 本地化质量/用户行为规则；
- 合规/法律同步（V2 能力 #18）；
- 任何会新增 gate blocker 的规则。

### Git 化版本管理

PRD §10.1 要“重大变化必须人工审核 + Git 化可回滚”。建议：

- 每日 branch：`rule-sync/YYYY-MM-DD/<platform>`。
- commit message：`rule-sync(google): update spam policies 2026-06-10`。
- PR 内容包含：源 URL、diff summary、LLM confidence、影响规则、是否需要 owner approval。
- minor 变更自动 PR 不自动 merge；major/breaking 标 `requires-kelly-review`。
- 每次 audit 记录 `rules_git_sha`，报告可追溯。

免费/低成本替代：

- 不买第三方政策 API，先用官方 RSS/blog/status + GitHub Actions/本地 cron。
- Search Engine Journal/Seroundtable 只能作为 alert 信号，不作为规则事实源。

## 6. 平台路由层

### 语言 → 多平台规则集组合

config 已明确 BYDFi locales 与 platform routing：

- en/pt/es/vi/tr/zh-CN：Google + Bing + LLM engines。
- ja：Google + Bing + LLM engines；注释说明 Yahoo Japan 用 Google 索引。
- ko：Naver + Google + Bing + LLM engines。
- ru：Yandex + Google + Bing + LLM engines。

建议规则组合顺序：

1. shared baseline：technical/schema/E-E-A-T。
2. bydfi：MEXC 事故、ticker、fintech compliance、final review。
3. platform rules：按 locale routing 组合。
4. command-specific rules：gate 比 audit 更严格；watch 加 lifecycle/safety。

冲突处理：

- BYDFi 风控规则优先于平台增长建议。
- 平台硬规则优先于 shared 建议。
- Google manual action/spam policy 优先级最高，因为 PRD 一句话目标是“不再发生 Google 人工处置”（PRD §0）。
- locale 平台规则只增加检查，不减少 Google 基线；ko/ru 仍跑 Google/Bing/LLM。

### ko 页面示例

`ko` 页面路由：`[naver, google, bing, llm-engines]`（config `platform_routing.ko`）。

执行建议：

- 串行：locale detection → route resolve → crawler。
- 并行：technical-agent 同时应用 shared + google/bing/naver hard rules；semantic-agent 应用 BYDFi + Naver Korean content + Google helpful content；geo-agent 应用 LLM rules。
- 串行聚合：report-agent 合并平台 findings，若 Naver 本地化低质但 Google 无 blocker，Final Verdict 可为“改后再审”而不是“暂不上线”；若 Google/BYDFi 命中 blocker，则 gate 阻断。

原因：

- PRD 指出 Naver 覆盖韩国 60%+，本地化必须真韩文（PRD §5.1）。
- lessons L03 指出本地化 alternate 不能 404、不能 robots 禁止、语言必须匹配。
- Naver 内容质量与 Google manual action 风险都要看，但上线卡口应以最高风险平台为准。

## 7. Storage & Cache

### snapshots/ 目录组织

PRD §7 只给目录，未指定时间组织。建议按项目、命令、日期、run_id 组织：

- `snapshots/bydfi/audit/2026/06/10/<run_id>/`
- `snapshots/bydfi/gate/2026/06/10/<run_id>/`
- `snapshots/bydfi/compare/2026/06/10/<run_id>/`
- `snapshots/bydfi/watch/2026-W24/<run_id>/`

每次跑都存 metadata 与 finding JSON；HTML/DOM 采用策略化存储：

- audit/gate：每次存 raw/rendered signal JSON；只有 blocker/high 或 debug 才存完整 HTML。
- compare：存 competitor summary 和 diff，不默认存全部 HTML。
- watch：每周全量 snapshot，日内失败重试只存 delta。

保留策略：

- blocker/high：保留 180 天。
- 普通 audit：保留 30 天。
- watch weekly baseline：保留 52 周。
- fixture 相关：永久保留。

### cache/ 抓取缓存策略

建议 cache key：

`project + url + ua_profile + render_mode + proxy_region + accept_language + rules_irrelevant_version`

TTL：

- BYDFi 自有页面 audit/gate：10 分钟，gate 可强制 bypass。
- competitor 页面：24 小时。
- robots.txt/sitemap：6 小时。
- official rule source：24 小时或 ETag/Last-Modified 控制。
- canonical source/original article：7 天，但若 page hash 变化立即失效。

失效条件：

- URL 内容 hash 改变。
- status/redirect/canonical 变化。
- robots/hreflang/schema 变化。
- 用户传 `--no-cache`。
- rules_git_sha 变化不必清抓取缓存，但要重新跑规则判断。

### fixtures/ golden test 准备方案

todo Phase 6 已列 5 个 fixture：

1. `mexc-incident.html`：覆盖 lessons L01-L06 和 PRD §1.1 七类事故。
2. `good-tools-page.html`：合格工具页，验证低误报。
3. `bad-hreflang.html`：robots/canonical/hreflang 冲突，覆盖 lessons L03。
4. `cloaking-suspect.html`：UA 差异、raw/rendered 差异，覆盖 PRD 能力 #3。
5. `thin-content.html`：低原创增量/E-E-A-T 弱，覆盖 lessons L01/L06。

每个 fixture 需要配套：

- `input.json`：URL、locale、command、platform routing。
- `expected_findings.json`：必须检出的 rule IDs。
- `expected_verdict.json`：Final Verdict 和 blocker/high 数量。
- `raw.html` 与必要时 `rendered.html`。

## 8. 测试策略

### 硬规则单测覆盖率 ≥ 90%

PRD §9.1 要硬规则单测覆盖率 ≥ 90%；todo Phase 6 指定 pytest。

建议：

- 每条 YAML hard rule 必须有至少 1 个 positive fixture 和 1 个 negative fixture。
- technical-agent 的 canonical/hreflang/robots/schema/sitemap 走纯函数单测。
- safety-agent 的 ticker 白名单/上下文前置规则走参数化测试。
- rule loader/schema validator 覆盖所有 YAML 规则文件。
- 覆盖率口径只统计硬规则模块，不把 Playwright/外部 API wrapper 纳入 90% 主 KPI。

MEXC 事故验收：

- lessons L01-L06 + PRD §1.1 7 类问题做成 `test_mexc_incident_detects_all_required_findings`。
- 任何一个必检 finding 丢失，CI fail。

### LLM 判断 snapshot test

问题：LLM 输出不稳定。PRD §10.1 已列“LLM 判断不稳 → snapshot test + 跨模型验证（V2）+ 人工反馈”。

工程方案：

- LLM 输出必须是结构化 JSON，不 snapshot 整段自然语言。
- snapshot 存字段：`rule_id`、`severity`、`confidence_bucket`、`evidence_hashes`、`verdict`。
- confidence 不比精确小数，只比 bucket：`low <0.5`、`medium 0.5-0.8`、`high >=0.8`。
- snapshot diff 分三类：新增 finding、丢失 blocker、severity 变化。
- 丢失 blocker 自动 fail；新增 low/info 只 warning；severity 从 high 降 medium 需要人工 approve。

存储建议：

- `tests/snapshots/llm/<fixture>/<agent>.json`
- `tests/snapshots/llm/<fixture>/prompt_version.txt`
- 每次规则变更导致 snapshot 更新，PR 必须解释原因。

### 端到端 CI

CI 阶段：

1. lint/type/schema check。
2. hard rule unit tests。
3. 5 个 golden fixture e2e，禁用真实网络，使用 fixtures HTML/cache。
4. LLM snapshot tests 默认 mock；夜间可跑真实 LLM 采样但不作为 PR blocker。
5. cost simulation：用 token counter 或固定估算，确保常规 fixture 预算 `< $0.02`。

低成本原则：

- PR CI 不调用 Anthropic API。
- nightly 才调用少量真实 LLM，并记录 cost。
- SERP/GSC/Cloudflare 集成用 recorded response。

## 9. Observability

### trace ID 贯穿 10 个 sub-agent

建议：

- orchestrator 创建 `trace_id` 和 `run_id`。
- 每个 agent 输入/输出都必须包含 `trace_id`。
- 每个 external call 生成 `span_id`：fetch、playwright render、LLM call、GSC call、rule sync fetch。
- Anthropic SDK response 的 `_request_id` 写入 LLM cost log，方便排查。官方 SDK 支持 request ID 属性。来源：https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python

ID 结构：

- `trace_id`：跨整个命令。
- `run_id`：一次 audit/gate/compare/watch。
- `agent_run_id`：单 agent 执行。
- `artifact_id`：snapshot/cache 产物。

### 日志格式

推荐 `structlog 26.1.0` 输出 JSON Lines。

字段：

- `ts`、`level`、`trace_id`、`run_id`、`agent`、`event`。
- `url_hash` 而非完整敏感 URL 参数。
- `duration_ms`、`status`、`retry_count`、`proxy_id`。
- `rules_git_sha`、`platforms`、`locale`。
- `error_type`、`error_message_sanitized`。

PRD/todo 要求 secrets/auth 统一和日志脱敏（todo Phase 1 F4），因此：

- 不记录 API key、Slack webhook、proxy credentials。
- LLM input/output 仅 debug 模式开启，且默认 false（config `observability.llm_io_log: false`）。

### 成本日志

每个 LLM call 记录：

- `model`
- `input_tokens`
- `output_tokens`
- `cache_creation_input_tokens`
- `cache_read_input_tokens`
- `price_table_version`
- `cost_usd`
- `budget_before/budget_after`
- `cache_hit_rate`
- `anthropic_request_id`

聚合：

- per agent cost
- per run cost
- daily/monthly project cost
- by model cost
- cache hit rate by workload：audit/gate/watch/rule-sync

触发告警：

- 单次 audit 预计超过 PRD `$0.02`。
- 每日超过 config `per_day: 10.00`。
- 月度超过 config `per_month: 200.00`。
- cache hit rate 连续 3 天低于 80%。

## 10. 风险与不确定性

### 最大 3 个技术未知数

1. **LLM 成本与质量是否能同时满足 `< $0.02`**
   - 依据：PRD §9.1 成本 `< $0.02`，config 却写 `per_audit: 0.05`。
   - 风险：Sonnet/Opus 对语义错配、原创增量、E-E-A-T 更稳，但成本容易超。
   - 缓解：Haiku 初筛 + Sonnet 争议复核 + Opus 只处理上线阻断争议；report 默认模板化；成本 KPI 采用平均/P95 需 Kelly 拍板。

2. **SERP/AI Overview/LLM 引用率真实采集稳定性**
   - 依据：PRD 能力 #2、#9；todo serp-agent/geo-agent 要 Google 真实搜索、AI Overview、Perplexity/ChatGPT Search/Claude/Gemini 引用率。
   - 风险：搜索页面反爬、地域差异、API 不稳定或成本高。
   - 缓解：V1 audit 不把 SERP 作为 gate blocker；compare/watch 可 partial；先支持 CSV/人工采样/低频 API，真实自动采集放 V1 后半或 V2。

3. **规则同步 LLM 提取误判**
   - 依据：PRD F8 和 §10.1 要每日 pull + LLM 提取 + 重大变化人工审核。
   - 风险：LLM 将新闻/第三方解读误写成硬规则，导致 gate 误杀。
   - 缓解：官方源优先；第三方只做 alert；major/breaking 必须人工审核；每条规则保留 source URL、confidence、rules_git_sha 可回滚。

### V1 难度可能超预期的能力

建议降级项：

- 能力 #2 真实 SERP + AI Overview：V1 先做“采样 + 外部数据导入 + 可 partial”，不作为 gate 必需。
- 能力 #8 竞品深度情报快照：V1 先支持 6 家竞品低频抓取 + Ahrefs CSV diff，不做大规模爬取。
- 能力 #9 GEO：V1 先做 llms.txt、answerable chunks、引用友好度静态检查；真实跨 LLM 引用率测试抽样。
- 能力 #12 Log File SEO + Index Coverage：V1 先接 GSC/Cloudflare 基础字段；fly.io log 若 BYDFi 不实际使用则标 optional。
- 能力 #11 自进化：V1 先记录 feedback JSON，不自动改 rules；自动 rules 更新需人工 PR。

不能降级项：

- MEXC 事故 7 类问题 100% 检出（PRD §9.1）。
- Pre-publish Gate blocker 机制（PRD 能力 #4、lessons L06）。
- raw HTML vs rendered DOM 的 JSON-LD/Schema 差异检测（lessons L04）。
- ticker 上下文判断（lessons L02）。
- hreflang/robots/canonical 一致性（lessons L03）。

## 11. W1 第一周可立即开工的 Day-by-Day 任务表

按 PRD §8.1，W1 是“框架骨架 + 5 个核心 sub-agent + BYDFi 规则库初始化”，负责方式是 Codex 写 / Claude 审。考虑 Phase 0 仍需 Claude 审报告，W1 建议如下。

| 天 | 任务 | 负责人 | 交付物 |
|---|---|---|---|
| Day 1 | Claude 审本调研报告；Kelly 拍板 Python 3.12、uv、成本 KPI、SERP/GEO 降级边界 | Claude + Kelly | 审批意见；需要改的决策项 |
| Day 1 | Codex 初始化工程骨架方案，不写业务逻辑前先确认目录、pyproject、基础 schema | Codex | pyproject/目录/contract 设计 PR |
| Day 2 | 实现/审查 sub-agent 统一 I/O schema、orchestrator task graph、trace/cost/log envelope | Codex 写，Claude 审 | F1/F2/F5 基础可运行 |
| Day 3 | crawler-agent MVP：xcrawl/httpx 轻量抓取、Playwright 渲染接口、UA profiles、raw/rendered artifact 规范 | Codex 写，Claude 审 | crawler 产物 JSON + cache 设计 |
| Day 4 | technical-agent MVP：schema/hreflang/canonical/robots/sitemap/url health 硬规则；MEXC L03/L04 先覆盖 | Codex 写，Claude 审 | hard rules + unit tests 初版 |
| Day 5 | semantic/safety/report MVP：ticker 上下文、原创增量接口、Final Verdict 合并；5 fixture 的 expected schema 定稿 | Codex 写，Claude 审 | audit 单页离线 fixture 跑通 |

W1 不建议做：

- 真实 SERP 大规模采集。
- 多 IP 池采购。
- 自动 rules PR 合并。
- Slack/GSC/Cloudflare 完整集成。

W1 验收建议：

- `mexc-incident` 离线 fixture 能检出 L01-L06 对应 finding。
- audit 离线流程不调用外部网络也能跑通。
- 每个 agent 输出符合 JSON Schema。
- cost log 即使 mock LLM 也能记录模型、tokens、预算。

## 执行摘要

建议 V1 基线选 Python 3.12 + uv + async httpx/Playwright + Pydantic schema + structlog；V1 不上 message bus、Redis、Kafka，先用 in-process task graph 和文件 artifacts。抓取层默认 xcrawl/httpx，遇 JS/Schema/raw-render 差异再 Playwright。LLM 采用 Haiku 初筛、Sonnet 复核、Opus 只处理上线阻断争议；`< $0.02` 若按每次 hard cap 不稳，建议 Kelly 拍板改成平均 `< $0.02`、P95/高风险例外可到 `$0.03`。SERP/GEO 真实采集、自动规则合并、多 IP 池采购建议降级为 V1 partial，优先确保 MEXC 7 类事故 100% 检出、gate 可阻断、5 个 golden fixture 跑通。
