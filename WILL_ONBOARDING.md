# Will 团队接入指南

> 创建：2026-06-11
> 受众：Will + BYDFi SEO 团队
> 目的：让 Will 团队 1 小时上手用 skill 替代手工对照清单

---

## 一、5 分钟快速上手

```bash
# 1. clone skill
cd ~/.claude/skills && cp -r seo-audit ./

# 2. 装依赖（一次性）
cd seo-audit
uv sync

# 3. 健康检查
uv run python cli.py doctor
# 应看到：371 rules / 100% detector coverage / 12 secrets pending

# 4. 跑第一次 audit
uv run python cli.py audit https://bydfi.com
# 30 秒出结果，含 Final Verdict + Brand SEO Score + 8 composite scores
```

---

## 二、4 个核心命令对应你的日常

| 你以前手工做 | 现在用什么命令 |
|---|---|
| 对照 15 份清单查文章 | `audit <url>` 一键查 |
| 流量下跌排查 SOP | `audit <url>` + `watch <site>` |
| 多语言上线检查 | `audit <url> --locale ko` |
| 竞品对比研究 | `compare <self> <competitor1> ...` |
| 月度巡检 | `watch <site>` 周报 |
| 发布前内容审核 | `gate <md_file>`（git pre-commit）|

---

## 三、关键能力对照（你以前 vs 现在）

| 维度 | 你以前手工 | Skill 自动 |
|---|---|---|
| 单页审核耗时 | 30 分钟 | < 30 秒 |
| Google E-E-A-T 检查 | 文字描述对照 | 8 维度 composite + 最弱环节定位 |
| Schema 真实性 | 看 schema 字段 | 字段 vs 可见内容语义比对 |
| Cloaking 检测 | 不查 | 多 UA 自动 diff |
| MEXC 事故防复发 | 经验判断 | 7 类问题硬规则全覆盖 + e2e 测试 |
| 跨语言审核 | 单语言 | 9 语言路由 + Naver/Yandex 专属 |
| GEO（LLM 引用率）| 不查 | Perplexity/ChatGPT/Claude/Gemini |
| Negative SEO 监控 | 不查 | hacked content + 品牌词检测 |

---

## 四、你的知识库 vs 我们规则库（关系）

**Will 的 Google SEO 知识库 = 我们规则库的灵感源**：
- 76 份 MD 文档 → 我们已转 16+ 篇为可执行规则
- 5 字段结构（链接/更新时间/AI 判断规则）→ 我们 yaml schema 沿用

**我们规则库 = 你的工具**：
- 371 条结构化规则
- 8 平台（你只覆盖 Google）
- 100% detector 实现
- 365×7 自动跑 vs 你月度手工

---

## 五、典型使用场景

### 场景 1：写完一篇 BYDFi /learn 文章
```bash
# 发布前卡审
uv run python cli.py gate /path/to/article.md --locale en
# Output: ✅ Gate PASSED. Safe to publish.
# 或: ❌ BLOCKERS: bydfi.compliance.banned-keywords-present
```

### 场景 2：每周 Google 流量下跌排查
```bash
uv run python scripts/batch_audit.py
# 自动跑 10 个核心页 + diff 上周 snapshot
# Output: snapshots/batch-audit-YYYYMMDD-HHMMSS.json
```

### 场景 3：判断要不要按 MEXC 事故口径处置某页
```bash
uv run python cli.py audit https://bydfi.com/news/some-news
# 看 Final Verdict
# 看 8 个 composite scores
# 看 Findings 按 severity 排序
```

### 场景 4：竞品对比
```bash
uv run python cli.py compare \
  https://bydfi.com/futures \
  https://www.binance.com/en/futures \
  https://www.bybit.com/en/trade
# 输出 HTML 仪表盘 + 终端 Score 对比
```

### 场景 5：每月规则更新追踪
```bash
uv run python3 -c "import asyncio; from agents.rule_sync import run_sync; print(asyncio.run(run_sync()))"
# 自动抓 6 个官方源（Google/Bing/Naver/Yandex blog/dashboard）
# diff 已有 371 条规则
# minor 变化自动 PR / major 推 Slack
```

---

## 六、你需要的 3 个秘密配置（一次性）

```bash
# ~/.bashrc 或 ~/.zshrc

# 必须：让 LLM judges 真用 Claude
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# 必须：让 GSC 数据接入
export GSC_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# 可选：让 Slack 收警报
export BYDFI_SLACK_WEBHOOK="https://hooks.slack.com/services/..."
```

跑 `uv run python cli.py doctor` 看哪些配好了。

---

## 七、当我们规则出错时（误报 / 漏报）

### 误报反馈
```bash
uv run python3 -c "
from agents.feedback import record_feedback
record_feedback('bydfi.compliance.banned-keywords-present', 'audit-xxx', 'false_positive', '这是教育内容，'guaranteed' 是引用监管原文不是承诺')
"
```

### 漏报反馈
```bash
record_feedback('rule-id', 'trace-id', 'missed', '应该检出 X 问题但没检出')
```

### 季度看反馈累积
```bash
uv run python3 -c "from agents.feedback import quarterly_review; import json; print(json.dumps(quarterly_review(), indent=2))"
```

精度低的规则会自动降低 confidence_default。

---

## 八、你给我们做的 3 件最重要事

1. **每周抽 5 个 finding 标"准 / 误报"**（10 分钟 → 帮我们校准规则）
2. **每月跑一次 rule_sync 看变化**（自动同步 Google 官方更新）
3. **新发现的事故案例写到 `rules/bydfi/google-action-history.md`**（沉淀给后人）

---

## 九、文档导航

| 想了解 | 看哪份 |
|---|---|
| 整体设计 | `PRD.md` |
| V1+V2 对比 | `V1_MILESTONE_REPORT.md` / `V2_MILESTONE_REPORT.md` |
| 与你团队对比 | `COMPARISON_WITH_WILL.md` |
| BYDFi 修复方案 | `BYDFI_REMEDIATION_PLAN.md` |
| Manual Actions SOP | `rules/platforms/google/_knowledge/manual-actions-reconsideration.md` |
| 网站迁移 SOP | `rules/platforms/google/_knowledge/site-migration-sop.md` |
| 高管汇报版 | `EXECUTIVE_SUMMARY.md` |
| 经验沉淀 | `tasks/lessons.md` |

---

## 十、有问题找谁

- Kelly（owner，kelly@bydfi.com）
- 内部 issue：在 BYDFi 仓库 git 化后开 issue
- 紧急（manual action 风险）：Slack `#seo-emergency`

---

*Skill 已在 `~/.claude/skills/seo-audit/` 落地，9 个 git commits 在本地，等你 onboarding 完成后推到 BYDFi 远程仓库。*
