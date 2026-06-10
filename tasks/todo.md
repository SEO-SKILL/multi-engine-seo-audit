# BYDFi SEO Audit Skill — 执行清单（V1 + V2）

> 按 CLAUDE.md「Task Management」规范：每完成一项立即勾选。
> 排期：V1 ≈ 4 周 / V2 ≈ 4-6 周
> 创建：2026-06-10

---

## 🚦 Phase 0 — 启动（Day 1-2）✅ 完成于 2026-06-10

- [x] Codex 调研：技术选型确认（playwright vs xcrawl 分工 / Python 版本 / 依赖列表）
- [x] Codex 调研：sub-agent 接口规范（输入/输出 JSON schema）
- [x] Claude 审 Codex 调研报告 → 5 项决策固化（PRD §13）
- [x] 写 `SKILL.md` 入口（Claude）
- [x] 写 `config.yaml` 默认配置（BYDFi 单租户）+ 成本预算调整
- [ ] 初始化 `pyproject.toml` + `uv.lock`（等 Codex quota 恢复）
- [x] **Will 知识库定位转向：benchmark to beat（PRD v1.2）**
- [x] **4 个元规则文件落地（rules/_system/）**
  - [x] `rule-schema.yaml`
  - [x] `severity-definition.yaml`
  - [x] `confidence-calibration.yaml`
  - [x] `conflict-resolution.yaml`
- [x] **10 条种子规则落地（Day 2-3 / 2026-06-10）**
  - [x] `bydfi/pros-ticker-blacklist.yaml`（3 条规则 + Ticker 黑白名单）
  - [x] `bydfi/fintech-compliance.yaml`（4 条规则 + 跨国合规黑名单）
  - [x] `bydfi/google-action-history.md`（MEXC 案例完整复盘）
  - [x] `platforms/google/_rules/e-e-a-t.yaml`（6 条规则）
  - [x] `platforms/google/_rules/canonical.yaml`（5 条规则）
  - [x] `platforms/google/_rules/structured-data-truthfulness.yaml`（6 条规则 — Will 没有）
  - [x] `platforms/google/_rules/cloaking-detection.yaml`（4 条规则 — Will 没有）
  - [x] `platforms/google/_rules/hreflang.yaml`（6 条规则）
  - [x] `platforms/naver/_rules/c-rank.yaml`（6 条规则 — Will 没有任何 Naver 维度）
  - [x] `platforms/llm-engines/_rules/perplexity.yaml`（7 条规则 — Will 没有任何 GEO 维度）
- [x] **合计：47 条结构化可执行规则**（V1 目标 300+，已完成 ~15%）
- [x] **Day 4 — self-knowledge 文档（超越 Will 版本）**
  - [x] `platforms/google/_knowledge/helpful-content-eat.md`（285 行）
    - BYDFi 频道级业务对齐（vs Will 仅列频道名）
    - AI Overview 维度（Will 完全没有）
    - GEO 维度（Will 完全没有）
- [x] **Day 5 — 补全 MEXC 事故剩余 2 类规则**
  - [x] `bydfi/republished-and-tagging.yaml`（3 条规则）
    - `bydfi.l01.republished-content-low-increment`（L01 转载原创增量）
    - `bydfi.l05.tagging-topic-mismatch`（L05 分类标签错配）
    - `bydfi.l05.tag-page-quality`（标签页质量）
- [x] **MEXC 事故 7 类问题对应规则：7/7 ✅ 全覆盖**
- [x] **W1 复盘已写入 lessons.md**

---

## 🚀 W2 — 平台规则扩展 + Fixture 落地（2026-06-10 同日推进）

### Bing 平台规则库（V1 必备 5 平台之一）
- [x] `platforms/bing/_rules/webmaster.yaml`（6 条规则）
- [x] `platforms/bing/_rules/ai-friendly.yaml`（5 条规则 — ChatGPT Search 后台优化）

### Yandex 平台规则库（俄罗斯市场 65%+）
- [x] `platforms/yandex/_rules/matrixnet.yaml`（6 条规则 — Will 完全没覆盖）

### Shared 跨平台通用规则
- [x] `shared/technical-baseline.yaml`（6 条规则 — HTTPS / HTTP 状态 / robots / viewport / duplicate / page size）
- [x] `shared/url-health.yaml`（8 条规则 — 重定向链 / 循环 / 参数 / 大小写 / orphan / broken link）
- [x] `shared/sitemap-quality.yaml`（7 条规则 — 含 MEXC L03 类似 sitemap-robots 冲突检测）

### Self-Knowledge 知识 MD（继续超越 Will）
- [x] `platforms/google/_knowledge/spam-policies-scale.md`（对照 Will 03，加加密行业案例 + AI 处置时间线 + BYDFi 程序化 SEO 红线）

### Golden Fixtures（V1 必备 5 个 HTML 测试样本）
- [x] `fixtures/mexc-incident.html`（MEXC 事故页 — 必须能检出 10+ 个 finding）
- [x] `fixtures/good-tools-page.html`（合格 BTC liquidation calculator 样板）
- [x] `fixtures/bad-hreflang.html`（hreflang 6 类问题集合）
- [x] `fixtures/cloaking-suspect.html`（多 UA diff + CSR 嫌疑 + 隐藏文字）
- [x] `fixtures/thin-content.html`（薄内容 + 缺 E-E-A-T）

### W2 增量
- **新增 38 条结构化规则**（V1 累计 ~88 / 300+ ≈ 29%）
- **新增 5 个 Golden Fixture**（V1 必备已完成 5/5 ✅）
- **新增 1 篇 self-knowledge MD**（spam-policies-scale）

---

## 🚀 W2 第二批 — A+B+C+D 全栈推进（2026-06-10）

### A. 规则扩展（11 个新文件）
- [x] `platforms/naver/_rules/dia-plus.yaml`（2 条）
- [x] `platforms/naver/_rules/view-search.yaml`（2 条）
- [x] `platforms/yandex/_rules/user-behavior.yaml`（3 条）
- [x] `platforms/llm-engines/_rules/chatgpt-search.yaml`（3 条 — Will 没有）
- [x] `platforms/llm-engines/_rules/claude-search.yaml`（2 条 — Will 没有）
- [x] `platforms/llm-engines/_rules/gemini.yaml`（3 条 — Will 没有）
- [x] `platforms/google/_rules/robots-noindex.yaml`（3 条）
- [x] `platforms/google/_rules/page-experience.yaml`（4 条 CWV）
- [x] `platforms/google/_rules/core-updates.yaml`（3 条）
- [x] `platforms/google/_rules/breadcrumb-and-navigation.yaml`（4 条）
- [x] `shared/eeat-baseline.yaml`（3 条）

### B. Self-Knowledge MDs（1 个新文件）
- [x] `platforms/google/_knowledge/ai-overview-eligibility.md`（Will 没有这个深度）

### C. 工程骨架（13 个新文件，Claude 直接接手）
- [x] `pyproject.toml`（依赖 + ruff/mypy 配置）
- [x] `agents/_schema.py`（Pydantic 统一 envelope）
- [x] `orchestrator.py`（主调度）
- [x] `cli.py`（4 个核心命令 typer 入口）
- [x] `agents/__init__.py`
- [x] `agents/crawler.py` stub
- [x] `agents/technical.py` stub
- [x] `agents/semantic.py` stub
- [x] `agents/serp.py` stub
- [x] `agents/competitor.py` stub
- [x] `agents/safety.py` stub
- [x] `agents/log.py` stub
- [x] `agents/lifecycle.py` stub
- [x] `agents/geo.py` stub
- [x] `agents/report.py` stub

### D. Patch Templates（10 个新模板）
- [x] `templates/patches/add_canonical.diff.j2`
- [x] `templates/patches/cross_domain_canonical.diff.j2`
- [x] `templates/patches/inject_risk_disclaimer.diff.j2`
- [x] `templates/patches/remove_ticker_widget.diff.j2`
- [x] `templates/patches/move_jsonld_to_ssr.diff.j2`
- [x] `templates/patches/remove_ungrounded_schema_fields.diff.j2`
- [x] `templates/patches/fix_hreflang_robots_conflict.diff.j2`
- [x] `templates/patches/remove_invalid_hreflang.diff.j2`
- [x] `templates/patches/add_author_metadata.diff.j2`
- [x] `templates/patches/add_breadcrumb_schema.diff.j2`
- [x] `templates/patches/allow_gptbot.diff.j2`

### W2 第二批增量
- **新增 32 条结构化规则**（V1 累计 ~120 / 300+ ≈ 40%）
- **新增 1 篇 self-knowledge MD**（累计 3 篇）
- **工程骨架就位**（pyproject + schema + orchestrator + cli + 10 agent stubs）
- **11 个 patch 模板**（report-agent 可以开始 render patch）

---

## 🏗️ Phase 1 — V1 框架骨架（W1）

### 框架支撑模块（V1 必备 9 个）

- [ ] F1: Multi-Agent Orchestrator（主调度 + 路由 + 聚合）
- [ ] F2: Cost / Token 控制层
  - [ ] 预算护栏（单次 / 每周 / 每月上限）
  - [ ] 模型分级路由（Haiku / Opus）
  - [ ] Prompt Caching 接入（claude-api skill）
- [ ] F3: Error / Retry / Degrade 层
  - [ ] 抓取失败重试（3 次 + 切 IP）
  - [ ] LLM 失败降级到硬规则
  - [ ] 单 agent 超时熔断
- [ ] F4: Secrets / Auth 统一
  - [ ] `.env` 模板 + 凭证健康检查
  - [ ] 日志脱敏
- [ ] F5: Observability / Tracing
  - [ ] trace ID
  - [ ] agent 耗时/成本日志
  - [ ] LLM input/output 日志（debug 模式）
- [ ] F6: Testing / Fixture
  - [ ] pytest 框架
  - [ ] LLM snapshot test 工具
- [ ] F7: Feedback Loop
  - [ ] 报告里 [👍 准/👎 误报/➕ 补充] 按钮
  - [ ] 反馈 → rules/ 自动更新
- [ ] F8: 规则同步管道（Rule Sync Pipeline）
  - [ ] daily-pull-agent
  - [ ] rule-extract-agent（LLM 提取）
  - [ ] diff-engine
  - [ ] alert-agent（Slack）
  - [ ] version-manager（Git 化）
- [ ] F9: 平台路由层（Platform Router）
  - [ ] 按语言版本路由
  - [ ] 多平台规则集组合

---

## 🤖 Phase 2 — V1 Sub-Agents（W1-W2）

### 10 个 V1 sub-agent

- [ ] **crawler-agent**（能力 #3 多源真实抓取 + Cloaking）
  - [ ] xcrawl 集成
  - [ ] playwright 集成
  - [ ] 多 IP 池
  - [ ] 多 UA 对比（Googlebot Desktop/Mobile/真实浏览器）
  - [ ] raw HTML vs 渲染后 DOM diff

- [ ] **technical-agent**（能力 #13 URL/Sitemap + 部分 #1）
  - [ ] HTML 解析（BeautifulSoup）
  - [ ] JSON-LD 解析 + 校验
  - [ ] hreflang 解析 + 互查
  - [ ] canonical/robots/sitemap 一致性检查
  - [ ] URL 健康度（参数 / 大小写 / trailing slash）
  - [ ] 重定向链路追踪

- [ ] **semantic-agent**（能力 #1 AI 原生语义检测）
  - [ ] 语义错配检测（PROS 案例）
  - [ ] 原创增量评分（vs canonical 来源）
  - [ ] 意图链一致性（title→H1→正文→CTA）
  - [ ] Schema 真实性校验（字段 vs 可见内容）
  - [ ] E-E-A-T 信号评分

- [ ] **serp-agent**（能力 #2 真实 SERP + AI Overview）
  - [ ] Google 真实搜索抓取
  - [ ] SERP feature 识别（AI Overview / Featured Snippet / PAA / 视频 / 图片）
  - [ ] CTR 真实预估
  - [ ] AI Overview 引用检测

- [ ] **competitor-agent**（能力 #8 竞品深度对比）
  - [ ] Ahrefs CSV 导入
  - [ ] 6 家竞品定时抓取（MEXC/WEEX/Binance/Bybit/OKX/CoinGlass）
  - [ ] diff 引擎
  - [ ] HTML 仪表盘渲染（橙白配色 + 左侧导航）

- [ ] **safety-agent** V1 基础（能力 #15 Web3-specific）
  - [ ] Ticker 白名单（防 PROS 案例）
  - [ ] 合约地址识别 + link 化
  - [ ] 链名识别
  - [ ] 基础合规检测（风险提示存在性）

- [ ] **log-agent**（能力 #12 Log + Index Coverage）
  - [ ] Cloudflare log API 拉取
  - [ ] fly.io log 拉取
  - [ ] GSC API（已索引 / 已抓取未索引 / 已发现未抓取）
  - [ ] Googlebot 抓取行为分析

- [ ] **lifecycle-agent** V1 基础（能力 #7 矩阵 + Cannibalization）
  - [ ] 内链图谱构建
  - [ ] Cannibalization 检测
  - [ ] 合并建议生成

- [ ] **geo-agent**（能力 #9 GEO）
  - [ ] `llms.txt` 检测
  - [ ] answerable chunks 检测
  - [ ] Perplexity API 引用率测试
  - [ ] ChatGPT Search 引用率测试
  - [ ] Claude / Gemini 引用率测试

- [ ] **report-agent**（能力 #5 决策闭环 + #16 健康分）
  - [ ] Final Verdict 生成（上线 / 暂不上线 / 改后再审）
  - [ ] Findings 三级分类（必须修 / 建议修 / 可忽略）
  - [ ] 修复 patch 生成（HTML diff / MD 替换块）
  - [ ] 优先级排序（流量 × 难度 × 风险）
  - [ ] Brand SEO Score 计算（0-100）
  - [ ] 多格式渲染（MD / HTML / JSON）

---

## 📚 Phase 3 — 规则库初始化（W2）

### BYDFi 专属规则（能力 #11 知识沉淀起点）

- [ ] `rules/bydfi/pros-ticker-blacklist.yaml`（PROS / SEC / BTC 等敏感 ticker）
- [ ] `rules/bydfi/fintech-compliance.yaml`（风险提示模板 + 黑名单词）
- [ ] `rules/bydfi/google-action-history.md`（MEXC 事故复盘 + 后续案例）
- [ ] `rules/bydfi/seo-final-review-rules.yaml`（byd-google-seo-final-review 口径）
- [ ] `rules/bydfi/sensitive-tickers.yaml`（加密 ticker 消歧义白名单）

### 5 个平台规则库

- [ ] `rules/platforms/google/`
  - [ ] core-updates.yaml（算法历史）
  - [ ] helpful-content.yaml
  - [ ] spam-policies.yaml
  - [ ] e-e-a-t.yaml
  - [ ] ai-overview-rules.yaml
  - [ ] manual-actions.yaml
- [ ] `rules/platforms/bing/`
  - [ ] webmaster-guidelines.yaml
  - [ ] ai-friendly-rules.yaml
- [ ] `rules/platforms/naver/`
  - [ ] c-rank.yaml
  - [ ] dia-plus.yaml
  - [ ] view-search.yaml
  - [ ] naver-blog-cafe.yaml
  - [ ] korean-content.yaml
- [ ] `rules/platforms/yandex/`
  - [ ] matrixnet.yaml
  - [ ] user-behavior.yaml
  - [ ] regional-signals.yaml
- [ ] `rules/platforms/llm-engines/`
  - [ ] perplexity.yaml
  - [ ] chatgpt-search.yaml
  - [ ] claude-search.yaml
  - [ ] gemini-overview.yaml

### Shared 通用规则

- [ ] `rules/shared/technical-baseline.yaml`
- [ ] `rules/shared/schema-org.yaml`
- [ ] `rules/shared/eeat-baseline.yaml`

---

## 🔗 Phase 4 — 集成（W3）

- [ ] `integrations/gsc.py` — Google Search Console API
- [ ] `integrations/crux.py` — Chrome UX Report
- [ ] `integrations/cloudflare.py` — Server log
- [ ] `integrations/slack.py` — Webhook 告警
- [ ] `integrations/ahrefs.py` — CSV 导入
- [ ] `integrations/contentforge.py` — ContentForge 钩子

---

## 🔄 Phase 5 — 4 个核心工作流（W3）

- [ ] `audit <url>` 命令（能力 #4 Pre-publish Gate）
- [ ] `gate <md_file>` 命令（含 Git pre-commit hook）
- [ ] `compare <self> <competitors>` 命令
- [ ] `watch <site>` 命令（含 cron 周报）

---

## 🧪 Phase 6 — 测试 & Fixture（W3-W4）

- [ ] `fixtures/mexc-incident.html`（MEXC 事故页 — V1 必备 golden）
- [ ] `fixtures/good-tools-page.html`（合格的工具页样板）
- [ ] `fixtures/bad-hreflang.html`（hreflang 错配样例）
- [ ] `fixtures/cloaking-suspect.html`（Cloaking 嫌疑样例）
- [ ] `fixtures/thin-content.html`（薄内容样例）
- [ ] 硬规则单测覆盖率 ≥ 90%
- [ ] LLM 判断 snapshot test
- [ ] 端到端测试：5 个 fixture 全跑通

---

## 📖 Phase 7 — 文档 & 上线（W4）

- [ ] `SKILL.md` 入口文档
- [ ] 各 sub-agent README
- [ ] 用户使用指南（命令 + 配置 + 故障排查）
- [ ] BYDFi 真实页面试跑 ≥ 10 次
- [ ] 根据反馈调整规则库
- [ ] V1 验收 checklist 全过

---

## 🌟 V2 — Phase 8 起（W5-W10）

### V2 业务能力（18 项）

- [ ] 17. Negative SEO / 安全风险监控
- [ ] 18. 合规 / 法律自动同步（US/EU/SG/JP/HK）
- [ ] 19. 转化反哺 + LTV 量化
- [ ] 20. 国际化深度
- [ ] 21. 内容深度评估
- [ ] 22. A/B 实验能力
- [ ] 23. 跨 LLM 验证
- [ ] 24. Crawl Budget 优化
- [ ] 25. Content Decay 检测
- [ ] 26. Pruning Candidates
- [ ] 27. Discover / News 入口
- [ ] 28. Pogo-sticking 检测
- [ ] 29. Dwell time / Scroll depth
- [ ] 30. 链接质量谱 + Disavow 候选
- [ ] 31. Entity SEO
- [ ] 32. SEO ROI 预测器
- [ ] 33. SEO 内容生成器
- [ ] 34. 关键词矩阵主动发现

### V2 框架支撑

- [ ] F10: Rate Limit / Concurrency
- [ ] F11: Plugin 扩展机制
- [ ] Multi-tenant 真实化

### V2 平台扩展

- [ ] `rules/platforms/baidu/`
- [ ] `rules/platforms/duckduckgo/`
- [ ] `rules/platforms/yahoo-japan/`

### V2 验收

- [ ] 34 项业务能力全部可用
- [ ] 8 个平台规则库各 ≥ 20 条规则
- [ ] 4 周真实数据沉淀（≥ 200 次审核）
- [ ] case study 文档

---

## 📊 复盘章节（每周更新）

### Week 1 复盘
（W1 结束后填）

### Week 2 复盘
（W2 结束后填）

### Week 3 复盘
（W3 结束后填）

### Week 4 复盘（V1 上线）
（W4 结束后填）

### Week 5-10 复盘（V2）
（V2 阶段填）

---

## 🎯 关键指标追踪

| 指标 | V1 目标 | 当前 | V2 目标 |
|---|---|---|---|
| 业务能力数 | 16 | 0 | 34 |
| 框架模块数 | 9 | 0 | 11 |
| 平台规则库 | 5 | 0 | 8 |
| BYDFi 规则数 | ≥ 30 | 0 | ≥ 100 |
| 单页审核成本 | < $0.02 | — | < $0.01 |
| 单页审核耗时 | < 30s | — | < 20s |
| Prompt Caching 命中率 | ≥ 80% | — | ≥ 90% |
| 硬规则单测覆盖率 | ≥ 90% | — | ≥ 95% |
| 真实页面审核次数 | ≥ 50 | 0 | ≥ 500 |
| 防住的潜在风险数 | — | — | 量化记录 |
