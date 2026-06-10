# BYDFi SEO Audit Skill — V1 + V2 PRD

> 版本：v1.0
> 创建日期：2026-06-10
> Owner：Kelly (kelly@bydfi.com)
> 协作：Claude（设计 + 审查）+ Codex（编码执行）

---

## 0. 一句话概括

为 BYDFi 量身打造的「**SEO 风控 + 增长决策中台**」，覆盖 33 项业务能力 / 11 个框架模块 / 8 个搜索引擎平台规则库，目标是**永远不再发生 Google 人工处置**，同时跑通合约工具页 SEO MVP 增长闭环。

---

## 1. 背景与动机

### 1.1 触发事件

BYDFi 已经被 Google 人工处置过一次（MEXC 页面 + 原始来源 BlockchainReporter 转载事故）。事故复盘暴露了 7 类系统性问题：

1. 转载内容缺少足够原创增量
2. 自动识别 ticker 导致主题错配（PROS / Pharos 案例）
3. hreflang 与 robots/canonical 信号冲突
4. 结构化数据不反映页面真实内容
5. JSON-LD raw HTML 缺失，仅渲染后输出
6. 分类标签不准
7. E-E-A-T 信号弱（作者、来源、责任归属缺失）

### 1.2 现有 SEO 工具的局限

市面工具（Ahrefs / SEMrush / Screaming Frog / Surfer SEO）都是「采集 + 打勾」模式，**永远检测不出**：

- 语义错配（PROS / Pharos）
- 转载页 vs 原文的原创增量
- Schema 字段 vs 可见内容的语义偏差
- E-E-A-T 信号强度判断
- 多源抓取差异（Cloaking 风险）

### 1.3 战略价值

- **风控**：防止 Google 处置再次发生
- **增长**：跑通合约工具页 SEO MVP（liquidation calculator / futures calculator / funding rate）
- **沉淀**：建立 BYDFi 专属 SEO 规则库 = 6 个月不可复制的护城河
- **跨平台**：覆盖 Google + Bing + Naver + Yandex + LLM engines，韩国 / 俄罗斯流量纳入管理

---

## 2. 目标与范围

### 2.1 V1 目标（4 周内交付）

- 防风险闭环：单页审核 + 发布前卡审 + 修复 patch 生成
- 多平台规则库初始化（5 个平台）
- 规则同步管道运转（每日 pull + 自动更新）
- BYDFi 专属规则库初始化（含 MEXC 事故案例）
- 5 个 golden fixture + 测试覆盖

### 2.2 V2 目标（再 4-6 周）

- 增长闭环：内容生成 + ROI 预测 + 关键词矩阵主动发现
- 高级监控：Negative SEO / 合规 / 转化反哺 / 用户行为
- 跨 LLM 验证 + 内容生命周期管理
- 扩 3 个平台（Baidu / DuckDuckGo / Yahoo Japan）
- Multi-tenant 真实化（为未来扩项目）

### 2.3 非目标（明确不做）

- 不做通用 SEO 工具（市面已饱和）
- 不替代 Ahrefs / SEMrush 的数据采集（接 API / CSV 导入即可）
- 不做付费版商业化（V1+V2 阶段）
- 不做 SEO 培训 / 咨询服务

---

## 3. 业务能力清单（33 项 + 综合健康分）

### 3.1 V1 业务能力（16 项）

| # | 能力 | 档位 | 核心价值 |
|---|---|---|---|
| 1 | AI 原生语义检测（错配/原创增量/意图链/Schema 真实性）| 核心 | 防 PROS 事故 |
| 2 | 真实 SERP + AI Overview 视角 | 核心 | 真实流量预估 |
| 3 | 多源真实抓取 + Cloaking 检测 | 核心 | 防 Googlebot 看到错版本 |
| 4 | Pre-publish Gate（Final Verdict）| 风控 | 上线前卡审 |
| 5 | 决策闭环 + 修复 patch | 风控 | 不只检测还给改法 |
| 6 | Google 算法对标 + 死亡案例库 | 风控 | MEXC 事故沉淀 |
| 7 | 矩阵视角 + Cannibalization 合并建议 | 增长 | 工具页矩阵闭环 |
| 8 | 竞品深度情报快照 | 增长 | 对标 MEXC/Bybit/OKX |
| 9 | GEO（Generative Engine Optimization）| AI | 2026 新流量入口 |
| 10 | API/工具链集成核心（GSC/CrUX/Cloudflare/Slack）| 基础 | 数据通路 |
| 11 | 组织级知识沉淀 + 自进化 | 基础 | 护城河起点 |
| 12 | Log File SEO 分析 + Index Coverage 监控 | Crawl | Googlebot 真实行为 |
| 13 | URL 健康度 + Sitemap 健康度 | 架构 | hreflang 事故修复 |
| 14 | 多搜索引擎适配（Google/Bing/Naver/Yandex/LLM）| 渠道 | ko/ru 市场覆盖 |
| 15 | Web3-specific SEO（ticker 白名单/合约地址 link）| Web3 | PROS 事故防复发 |
| 16 | 综合健康分（Brand SEO Score, 0-100）| 增长 | CEO/CMO 单数字指标 |

### 3.2 V2 业务能力（18 项）

| # | 能力 | 档位 | 核心价值 |
|---|---|---|---|
| 17 | Negative SEO / 安全风险监控 | 风控 | 防被黑/被劫持 |
| 18 | 合规 / 法律自动同步（US/EU/SG/JP/HK）| 风控 | 跨国合规 |
| 19 | 转化反哺 + LTV 量化 | 商业 | CFO 听得懂的 ROI |
| 20 | 国际化深度（本地化质量/本地竞品/SERP feature）| 增长 | 9 语言市场深耕 |
| 21 | 内容深度评估（reading level/topical depth/AI 检测）| 增长 | Helpful Content 合规 |
| 22 | A/B 实验能力（Title/Meta/Schema）| 增长 | 数据驱动优化 |
| 23 | 跨 LLM 验证（GPT/Claude/Gemini 交叉）| AI | 高置信判断 |
| 24 | Crawl Budget 优化 | Crawl | 大站抓取效率 |
| 25 | Content Decay 检测 | 生命周期 | 流量下滑预警 |
| 26 | Pruning Candidates | 生命周期 | 薄内容清理 |
| 27 | Discover / News 入口 | 渠道 | 加密热点新闻流量 |
| 28 | Pogo-sticking 检测 | 用户行为 | 防降权 |
| 29 | Dwell time / Scroll depth | 用户行为 | 内容吸引力 |
| 30 | 链接质量谱 + Disavow 候选 | 链接 | 外链生态健康 |
| 31 | Entity SEO（知识图谱/Wikidata/sameAs）| 实体 | 2026 SEO 新主战场 |
| 32 | SEO ROI 预测器 | 主动能力 | 建页前的决策 |
| 33 | SEO 内容生成器（Title/Meta/H1/FAQ Schema）| 主动能力 | 跟 ContentForge 双向 |
| 34 | 关键词矩阵主动发现（GSC + Suggest + PAA + 竞品 diff）| 主动能力 | 找还没建的页面机会 |

> 注：上一轮讨论计 33 项业务能力，加上「综合健康分」实际 34 项。本 PRD 以此为准。

---

## 4. 框架支撑模块（11 个）

| # | 模块 | V1 | V2 | 说明 |
|---|---|---|---|---|
| F1 | Multi-Agent 编排（Orchestrator）| ✅ | — | 主调度 + 路由 + 聚合 |
| F2 | Cost / Token 控制 | ✅ | — | 预算护栏 + 模型分级 + Prompt Caching |
| F3 | Error / Retry / Degrade | ✅ | — | 失败重试 + 降级 + 熔断 |
| F4 | Secrets / Auth 统一 | ✅ | — | 多平台凭证管理 |
| F5 | Observability / Tracing | ✅ | — | trace ID + agent 耗时 + LLM 日志 |
| F6 | Testing / Fixture（含 MEXC golden）| ✅ | — | 硬规则单测 + LLM snapshot test |
| F7 | Feedback Loop（自进化数据通路）| ✅ | — | 用户标注 → rules/ 自动更新 |
| F8 | 规则同步管道（Rule Sync Pipeline）| ✅ | — | 每日 pull + LLM 提取 + 自动 PR |
| F9 | 平台路由层（Platform Router）| ✅ | — | 按语言版本路由到对应规则集 |
| F10 | Rate Limit / Concurrency | — | ✅ | 抓取速率 + IP 轮换 + 并发上限 |
| F11 | Plugin 扩展机制 | — | ✅ | 自定义规则 / agent / 输出格式 |

> Multi-tenant：V1 保留 hook（`get_project_path()` 拼接），V2 真实化。

---

## 5. 平台规则库（8 个）

### 5.1 V1（5 个）

| 平台 | 覆盖市场 | 关键差异 |
|---|---|---|
| **Google** | 全球 85%+ | 主战场，所有维度都做 |
| **Bing** | 全球 + ChatGPT Search 后台 | AI 友好度优化 |
| **Naver** | 韩国 60%+ | C-Rank / DIA / DIA+ 算法，本地化必须真韩文 |
| **Yandex** | 俄罗斯 65%+ | MatrixNet 算法，用户行为权重高 |
| **LLM engines** | Perplexity / ChatGPT Search / Claude / Gemini | answerable chunks + 引用友好 |

### 5.2 V2（3 个）

| 平台 | 覆盖市场 | 优先级 |
|---|---|---|
| Baidu | 中国大陆 | 需 ICP 备案，受限 |
| DuckDuckGo | 隐私敏感用户 | 加密圈占比中等 |
| Yahoo Japan | 日本（用 Google 索引）| 部分 SERP feature 不同 |

---

## 6. 系统架构

### 6.1 顶层架构

```
用户入口（Claude Code Skill）
  audit | gate | compare | watch
       │
       ▼
┌─────────────────────────┐
│  Orchestrator（主调度）  │
└──────────┬──────────────┘
           │
  ┌────────┴────────┐
  ▼                 ▼
Sub-Agents (10个)   Platform Router
  │                 │
  ▼                 ▼
Fetch / Parse / Analyze Layer
           │
           ▼
Rules Layer（bydfi/ + platforms/ + shared/）
           │
           ▼
Storage Layer（snapshots / patches / cache / fixtures）
           │
           ▼
Output Layer（MD / HTML / JSON / Slack / Git PR）
```

### 6.2 Sub-Agent 职责矩阵（10 个）

| Sub-Agent | 负责能力 | V1/V2 |
|---|---|---|
| crawler-agent | 多源抓取 / Cloaking 检测 / 多 IP 多 UA | V1 |
| technical-agent | Schema/hreflang/canonical/robots/sitemap/URL | V1 |
| semantic-agent | AI 语义检测 / E-E-A-T / 原创增量 / 意图链 | V1 |
| serp-agent | 真实 SERP / AI Overview / SERP feature | V1 |
| competitor-agent | 竞品快照 / Ahrefs CSV 导入 / diff | V1 |
| safety-agent | Negative SEO / Hacked / 合规 | V1（基础）+ V2（深度）|
| log-agent | Cloudflare/fly.io log / GSC API / Index Coverage | V1 |
| lifecycle-agent | Content Decay / Cannibalization / Pruning | V1（cannibalization）+ V2（decay/pruning）|
| geo-agent | GEO / LLM 引用率 / Entity SEO | V1（GEO）+ V2（Entity）|
| report-agent | 报告生成 / 修复 patch / Final Verdict | V1 |

### 6.3 4 个核心工作流

```
场景 1: audit <url>
  Orchestrator
    → crawler-agent（抓 raw + rendered + UA diff）
    → 并行 [technical-agent, semantic-agent, safety-agent, geo-agent]
    → Platform Router 按语言版本套规则
    → 应用 rules/bydfi/
    → report-agent → Final Verdict + 修复 patch

场景 2: gate <md_file>
  Git pre-commit hook
    → 临时渲染 MD → HTML
    → 跑场景 1 流程
    → 不通过 → exit 1
    → 通过 → 写 .seo-passed 标记

场景 3: compare <self> <competitors...>
  Orchestrator
    → crawler-agent 并行抓取
    → competitor-agent 加载 Ahrefs CSV
    → geo-agent 跑 LLM 引用率对比
    → report-agent → HTML 仪表盘（橙白配色 + 左侧导航）

场景 4: watch <site>
  Cron 每周
    → crawler-agent 全站抓取
    → log-agent 拉取 GSC + server log
    → lifecycle-agent 检测 cannibalization
    → safety-agent 检测 negative SEO
    → diff 上周 snapshot
    → report-agent → 周报 + Slack 推送
```

---

## 7. 文件系统布局

```
~/.claude/skills/seo-audit/
├── SKILL.md                          # Skill 入口
├── PRD.md                            # 本文件
├── config.yaml                       # 全局配置（BYDFi 默认）
├── orchestrator.py                   # 主调度
├── agents/
│   ├── crawler.py
│   ├── technical.py
│   ├── semantic.py
│   ├── serp.py
│   ├── competitor.py
│   ├── safety.py
│   ├── log.py
│   ├── lifecycle.py
│   ├── geo.py
│   └── report.py
├── rules/
│   ├── bydfi/
│   │   ├── pros-ticker-blacklist.yaml
│   │   ├── fintech-compliance.yaml
│   │   ├── google-action-history.md   # MEXC 案例 + 后续积累
│   │   ├── seo-final-review-rules.yaml
│   │   └── sensitive-tickers.yaml
│   ├── platforms/
│   │   ├── google/
│   │   │   ├── core-updates.yaml
│   │   │   ├── helpful-content.yaml
│   │   │   ├── spam-policies.yaml
│   │   │   ├── e-e-a-t.yaml
│   │   │   ├── ai-overview-rules.yaml
│   │   │   └── manual-actions.yaml
│   │   ├── bing/
│   │   ├── naver/
│   │   ├── yandex/
│   │   └── llm-engines/
│   └── shared/
│       ├── technical-baseline.yaml
│       ├── schema-org.yaml
│       └── eeat-baseline.yaml
├── integrations/
│   ├── gsc.py                        # Google Search Console API
│   ├── crux.py                       # Chrome UX Report
│   ├── cloudflare.py                 # Server log
│   ├── slack.py                      # Webhook 告警
│   ├── ahrefs.py                     # CSV 导入（V1）+ API（V2）
│   └── contentforge.py               # ContentForge 双向钩子
├── templates/
│   ├── report.md.j2
│   ├── dashboard.html.j2             # 橙白配色 + 左侧导航
│   ├── patch.diff.j2
│   └── slack-alert.j2
├── snapshots/                        # 时间维度全量快照
├── cache/                            # 抓取缓存
├── fixtures/                         # Golden test fixtures
│   ├── mexc-incident.html            # MEXC 事故页（V1 必备）
│   ├── good-tools-page.html
│   ├── bad-hreflang.html
│   ├── cloaking-suspect.html
│   └── thin-content.html
├── tests/
│   ├── test_technical.py
│   ├── test_semantic.py
│   └── test_e2e.py
└── tasks/
    ├── todo.md                       # 可勾选执行清单
    └── lessons.md                    # 经验沉淀
```

---

## 8. 工程量 & 排期

### 8.1 V1 排期（3-4 周）

| 周次 | 任务 | 负责 |
|---|---|---|
| W1 | 框架骨架 + 5 个核心 sub-agent + BYDFi 规则库初始化 | Codex 写 / Claude 审 |
| W2 | 5 个剩余 sub-agent + 5 个平台规则库 + 规则同步管道 | Codex 写 / Claude 审 |
| W3 | 4 个核心工作流串联 + golden fixture + 测试 | Codex 写 / Claude 审 |
| W4 | 文档 + Slack/Git 集成 + BYDFi 真实页面试跑 + 修 bug | Claude 主导 |

### 8.2 V2 排期（4-6 周）

| 周次 | 任务 |
|---|---|
| W5 | V1 真实数据反馈 + 规则库迭代 + V2 详细 PRD |
| W6-7 | 高级 sub-agent（lifecycle/safety/geo 深度）+ 主动能力（ROI/生成/发现）|
| W8 | A/B 实验 + 跨 LLM 验证 + Rate Limit/Plugin |
| W9 | 扩 3 个平台规则库 + Multi-tenant 真实化 |
| W10 | 文档 + 验收 + case study |

### 8.3 关键里程碑

- **M1（W4 末）**：V1 上线，跑通 audit 单页流程
- **M2（W5 末）**：BYDFi 真实页面跑过 50+ 次审核，规则库初步沉淀
- **M3（W8 末）**：V2 核心能力上线
- **M4（W10 末）**：V2 全量交付 + case study

---

## 9. 验收标准

### 9.1 V1 验收

**功能验收：**

- [ ] `audit <url>` 能输出 Final Verdict（上线 / 暂不上线 / 改后再审）
- [ ] `gate <md>` 能阻止有问题的 commit
- [ ] `compare <urls>` 能输出 HTML 仪表盘
- [ ] `watch <site>` 能跑周报
- [ ] 5 个 golden fixture 全部能复现已知问题（含 MEXC 事故页）
- [ ] 5 个平台规则库各有至少 10 条规则
- [ ] 规则同步管道能每日自动跑

**质量验收：**

- [ ] MEXC 事故 7 类问题 100% 被检出
- [ ] 单页审核成本 < $0.02
- [ ] 单页审核耗时 < 30 秒
- [ ] Prompt Caching 命中率 ≥ 80%
- [ ] 硬规则单测覆盖率 ≥ 90%

**沉淀验收：**

- [ ] BYDFi 规则库 ≥ 30 条初始规则
- [ ] 文档完整（SKILL.md + PRD.md + tasks/）
- [ ] Slack 告警通道打通
- [ ] Git pre-commit hook 可用

### 9.2 V2 验收

- [ ] 全 34 项业务能力可用
- [ ] 8 个平台规则库各有至少 20 条规则
- [ ] Brand SEO Score 0-100 评分输出
- [ ] BYDFi 4 周真实数据沉淀（≥ 200 次审核记录）
- [ ] case study 文档（"防住 X 次风险 + 涨 Y 流量"）

---

## 10. 风险与对策

### 10.1 技术风险

| 风险 | 对策 |
|---|---|
| LLM 成本失控 | 硬规则前置过滤 + 模型分级（Haiku/Opus）+ Prompt Caching |
| 抓取被反爬 | 多 IP 池 + 速率控制 + 真实 UA + xcrawl/playwright 混用 |
| LLM 判断不稳 | snapshot test + 跨模型验证（V2）+ 人工反馈通路 |
| 规则同步出错 | 重大变化必须人工审核 + Git 化可回滚 |

### 10.2 业务风险

| 风险 | 对策 |
|---|---|
| 误报多用户不信任 | Feedback Loop 闭环 + 每条 Finding 带置信度 |
| 漏报关键问题 | Golden fixture 必跑通 + 每月扩 fixture |
| 规则库被滥用 | rules/ Git 化 + 重大变更需 owner 审批 |

### 10.3 合规风险

| 风险 | 对策 |
|---|---|
| 抓取竞品被投诉 | 严格遵守 robots.txt + 限速 |
| 数据隐私 | secrets 单独管理 + 不进日志 |
| AI 生成内容版权 | 修复 patch 仅提供建议，最终由人工 commit |

---

## 11. 实施分工（Claude + Codex 流程）

按全局 CLAUDE.md 规则执行：

```
任务进来
  ↓
①Codex 调研出方案（codex exec, 只分析不写码）
  ↓
②Claude 审批 ←→ 不同意打回修正，直到对齐
  ↓
③Codex 写代码（codex exec --full-auto）
  ↓
④Codex 自审（codex exec review）
  ↓
⑤Claude 终审 + 合并
  ↓
⑥有问题？→ 打回 Codex 修 → 回到 ④
  ↓
⑦向用户交付
```

每个 sub-agent 作为独立任务走这个流程。Claude 不下场写 ≥ 30 行的代码。

---

## 12. 配套文档

- `tasks/todo.md` — 可勾选执行清单
- `tasks/lessons.md` — 经验沉淀（每次纠错后更新）
- `SKILL.md` — Skill 入口（Claude 读这个识别能力）— 待写
- 各 sub-agent 单独 README — 待写

---

## 13. V1 决策固化（Phase 0 Codex 调研后）

经 Codex 技术调研 + Kelly 拍板，V1 细化为：

### 13.1 决策点

| 决策 | 结论 |
|---|---|
| 单页 audit 成本 KPI | V1 hard cap $0.03 / 平均 < $0.02；V2 优化到 hard cap $0.02 |
| SERP 实时采集 | V1 降级为采样 + CSV 导入 + partial；自动采集放 V2 |
| GEO 跨 LLM 引用率 | V1 静态检查 + 抽样真实测试；全量自动测试放 V2 |
| 规则自动合并 | minor 变化自动 PR，major/breaking 必须 Kelly 人工 review |
| 自进化机制 | V1 只记录 feedback JSON，不自动改 rules；自动更新需人工 PR |

### 13.2 V1 不能降级的硬要求

1. MEXC 事故 7 类问题 100% 检出
2. Pre-publish Gate blocker 机制
3. raw HTML vs rendered DOM 的 JSON-LD/Schema 差异检测
4. ticker 上下文判断（防 PROS 案例）
5. hreflang/robots/canonical 一致性

### 13.3 技术栈定稿

- Python 3.12+ / uv + pyproject.toml
- httpx 0.28+ / playwright 1.60+ / beautifulsoup4 4.15+ / lxml 6.1+
- pydantic 2.13+ / jsonschema 4.26+ / orjson 3.11+ / PyYAML 6.0+
- Jinja2 3.1+ / anthropic SDK / tenacity 9.1+ / diskcache 5.6+
- structlog 26.1+ / pytest 9.0+ + pytest-cov / ruff + mypy

### 13.4 LLM 路由

- 规则提取初筛 / ticker 上下文初判 → Haiku
- 原创增量 / E-E-A-T / 意图链 / Schema 真实性 → Sonnet
- 上线阻断争议 / 重大规则审核 → Opus
- Report synthesis → 默认模板化，仅 narrative 需求才调 Sonnet

### 13.5 抓取层

- 默认 httpx 轻量抓取；JS/Schema/raw-render 差异时升级 Playwright
- 多 UA：Googlebot Desktop / Googlebot Mobile / 真实 Chrome Desktop / 真实 Chrome Mobile
- V1 不买大型住宅 IP 池，本地出口 + 1-2 个低成本代理足够

---

## 14. 「碾压 Will 知识库」设计目标（v1.2 加入）

### 14.1 战略定位

Will 团队的 `Google SEO 知识库`（76 份 MD / 5 字段结构 / 月度人工巡检）是 **benchmark to beat，不是上游依赖**。最终目标：**Will 主动放弃他自己的工作流，转用我们这个 skill**。

### 14.2 量化超越目标

| 维度 | Will 知识库 | 我们 V1 | 我们 V2 | 倍数 |
|---|---|---|---|---|
| 平台数 | 1 (Google) | 5 | 8 | 8x |
| 可执行规则条目 | ~150 文字 | 300+ YAML | 600+ | 4x |
| 语言覆盖 | 中文 | 9 语言路由 | 9 语言深度 | 9x |
| 更新频率 | 月度人工 | 每日 auto-pull | 每日 + 实时 | 30x |
| 输出形式 | MD 静态 | MD/HTML/JSON/Slack/PR | + Looker | 5x |
| 可执行性 | 0 | Pre-publish Gate + CI | + ContentForge | ∞ |
| 修复建议 | 文字描述 | 自动 patch | A/B 测试 | 自动化 |
| 历史追溯 | 文档 git log | 时间序列快照 | + 算法对标 | 数据化 |
| 反馈闭环 | 单向 | 用户反馈→规则迭代 | 自进化 | 双向 |
| 跨 LLM 验证 | 无 | 抽样 | 全量交叉 | 独有 |
| GEO 维度 | 无 | llms.txt + 引用率 | 全 LLM 覆盖 | 独有 |
| Cloaking 检测 | 无 | 多 UA diff | 多 IP diff | 独有 |
| Cannibalization | 无 | 检测 + 合并建议 | 自动 patch | 独有 |
| Web3 专属 | 无 | Ticker / 合约地址 | + 全链整合 | 独有 |
| 商业价值量化 | 无 | Brand SEO Score | ROI 预测 | 独有 |
| 竞品对比 | 无 | 6 家快照 | + 实时 diff | 独有 |

### 14.3 规则体系 4 层架构（自研，不抄 Will）

```
rules/
├── bydfi/                    # BYDFi 专属（核心护城河）
├── platforms/<engine>/
│   ├── _knowledge/           # 自研知识层（比 Will 深 BYDFi 对齐）
│   ├── _rules/               # 结构化可执行 YAML 规则
│   ├── _checklists/          # 可执行检查清单（detector 化）
│   └── _meta/                # 来源追溯 + 更新日志
├── shared/                   # 跨平台通用
└── _system/                  # 元规则（schema / severity / confidence / conflict）
```

### 14.4 与 Will 的 3 个"兼容点"（让他愿意切过来）

1. **报告默认输出 MD 格式**，文件结构可直接放进他知识库
2. **daily-pull-agent 输出兼容他的更新日志格式**
3. **audit 命令输出包含他清单格式的检查结果**

### 14.5 Will 知识库的正确用法（不是消费）

- 不 fork、不 symlink、不直接消费
- 参考结构（5 字段 / 76 主题 / BYDFi 业务对齐方式）
- 自己写更深的 _knowledge MD（加 BYDFi 业务对齐 + GEO + AI Overview）
- 自己写可执行的 _rules YAML（每条带 detector + LLM judge + fixture）

### 14.6 让 Will 看了愿意切换的杀手锏

- ✅ 兼容他工作流（输出格式 = 他的写作格式）
- ✅ 覆盖他做不到的（韩国 / 俄罗斯 / GEO / 多 LLM / Cloaking / Web3）
- ✅ 自动化他正在做的（流量下跌 SOP / HTML 头部检查 / 多语言上线 / Search Console 巡检）

---

## 15. 元规则文件（已落地）

V1 Day 1 已交付 4 个元规则文件：

- `rules/_system/rule-schema.yaml` — 规则本身的 schema 定义
- `rules/_system/severity-definition.yaml` — 5 级 severity 标准 + Final Verdict 决策树
- `rules/_system/confidence-calibration.yaml` — 3 个 bucket + 升级策略 + 校准反馈
- `rules/_system/conflict-resolution.yaml` — 规则冲突解决 + 聚合 dedup

这 4 份元规则是所有业务规则的"宪法"，必须先于业务规则建立。

---

## 16. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2026-06-10 | 初稿，定义 V1+V2 全量范围 |
| v1.1 | 2026-06-10 | Codex Phase 0 调研后 5 项决策固化 + 技术栈定稿 |
| v1.2 | 2026-06-10 | 加入「碾压 Will 知识库」战略定位 + 4 层规则架构 + 4 个元规则文件落地 |
