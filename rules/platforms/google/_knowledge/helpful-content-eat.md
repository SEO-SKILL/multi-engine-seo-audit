# Helpful Content 与 E-E-A-T（Platform 深度版）

> 对标 Will 知识库 `01-帮助性内容与E-E-A-T.md`，**我们这版在 3 个维度做了实质增量**：
>
> 1. **Platform 频道级业务对齐**（Will 只列频道名，我们给到具体落地动作）
> 2. **加入 AI Overview / Google SGE 维度**（Will 完全没有）
> 3. **加入 GEO 时代的引用友好度策略**（Will 完全没有）
>
> 创建：2026-06-10 / 维护：kelly@example.com

---

## 一、Google 原文最关键的 5 条

源文档：<https://developers.google.com/search/docs/fundamentals/creating-helpful-content>（最后核实 2026-05-28）

1. Google 自动排名系统优先展示"让用户受益的实用可靠信息"，而非操纵排名的内容。
2. 自查不只看关键词和排名，要看是否有**原创信息、完整描述、独特洞察、清晰标题**，以及**是否比同 SERP 里的其他结果更有实质价值**。
3. 可信度不是一句"我们很专业"就够，Google 看可验证信号：**作者信息、来源、背景介绍、事实错误率、审核痕迹**。
4. E-E-A-T 在 YMYL 主题上权重更高，其中 **「可信度」最重要**。
5. **「对象、方式、原因」** 三问检查法：
   - 对象：谁写的，作者是否清楚、背景是否清楚
   - 方式：内容如何产出，是否说明测试、验证、采集或自动化方式
   - 原因：内容的主要目的是否是帮助用户，而不是吸引搜索流量

---

## 二、Platform 频道级落地动作（vs Will 的泛建议）

Will 在他的版本里只列了频道名（"price/how-to-buy/support/wiki/crypto-review"），但没给落地动作。我们这版到每个频道的**具体执行清单**。

### 2.1 `/price/*` 币种资产页

**Will**：「重点补事实与上下文，而不是泛解释」

**我们的具体动作**：

| 模块 | 必备 | E-E-A-T 信号点 |
|---|---|---|
| 实时价格 / 24h 涨跌 / 成交量 / 市值 | ✅ | 数据来源标 `CoinGecko / DefiLlama` |
| K 线图（多周期）| ✅ | 数据来源 + 时间戳精确到秒 |
| 项目简介 | ✅ | "Platform 加密研究团队整理" + 最后更新日期 |
| 市场数据（ATH / ATL / 流通量）| ✅ | 来源 |
| **风险提示**（PRD §12.4 模板）| ✅ | 必须有 |
| **价格预测免责声明** | ✅ | 不允许预测，必须用"参考资料"措辞 |
| 历史价格表 | ⚪ | 来源 |
| FAQ | ✅ | 答案有引用 |

**严格禁止**：

- 暗示"必涨 / 必跌"
- "保证收益"类措辞
- 与 CoinGecko 数据偏差 > 5%（数据质量问题）

### 2.2 `/how-to-buy/*` 买币教程

**Will**：「重点补地区限制、产品路径、风险提示、实际操作差异」

**我们的具体动作**：

| 模块 | 必备 | E-E-A-T 信号点 |
|---|---|---|
| 地区可用性矩阵 | ✅ | US-SEC / EU-MiCA / SG-MAS / JP-JFSA / HK-SFC 五区合规标 |
| 操作步骤截图 | ✅ | 真实 Platform UI 截图（不要 mockup）|
| 时长估算 | ✅ | 经验值（"通常 5-10 分钟"）|
| 支付方式（卡 / 银行 / OTC）| ✅ | 各方式手续费、限额、可用区域 |
| **常见错误处理** | ✅ | 来自 /support 真实工单的归纳 |
| **真实费率示例** | ✅ | 当前真实费率（非永久写死，cron 更新）|
| 风险提示 | ✅ | YMYL 强信号 |

**Experience 信号增强**：

- 截图必须含 Platform 真实 UI 元素（防 AI 生成误判）
- 步骤说明用第一人称视角（"你会看到..."）
- 引用真实 support 工单数据（"约 12% 用户在第 3 步出错"）

### 2.3 `/support/*` `/questions/*` 客服与问答

**Will**：「重点补准确性、审核状态和失效管理」

**我们的具体动作**：

| 模块 | 必备 | E-E-A-T 信号点 |
|---|---|---|
| 答案作者 | ✅ | 必须有"答主：客服团队 - 张某 / 高级 KYC 专家" |
| **答案审核者** | ✅ | "审核：合规团队 - 李某" |
| 最后更新日期 | ✅ | 含日期 + 更新原因 |
| 答案适用范围 | ✅ | "适用于 KYC2 用户" / "仅 EU 可用"|
| **答案过期机制** | ✅ | 涉及费率 / 监管 / 产品的答案超过 6 个月自动标 "可能过期" |
| 相关问题链接 | ✅ | 内链权重传递 |
| 用户反馈入口 | ✅ | 收集"这个答案有帮助吗" |

**严格禁止**：

- UGC 答案不经审核直接进入索引
- 客服旧答案没有 archived 状态
- 答案内容与最新 Platform 产品功能不一致

### 2.4 `/learn/*` Learn Center

**Will**：（未细化）

**我们的具体动作**：

| 模块 | 必备 |
|---|---|
| 主题集群组织 | ✅（PRD §4.6 Learn Center 结构）|
| 受众标识 | ✅（新手 / 高频交易者 / 机构）|
| 学习路径 | ✅（前置知识 → 本文 → 下一步推荐）|
| 实际操作示例 | ✅（不是纯理论）|
| 风险提示 | ✅ |
| 作者 + 审核 + 更新 | ✅ |

### 2.5 `/tools/*` 工具页（PRD §5 合约工具页 MVP）

**Will**：（未覆盖）

**我们的具体动作**：

| 模块 | 必备 |
|---|---|
| 工具说明（一句话）| ✅ |
| 首屏工具模块（SSR 输出）| ✅ |
| 结果解释模块 | ✅ |
| **计算公式说明** | ✅ |
| **数据源说明** | ✅（实时价格 / 维护保证金率 / 资金费率来源）|
| 场景案例 | ✅ |
| **风险提示**（PRD §12.4 模板）| ✅（强制，否则触发 gate blocker）|
| FAQ | ✅ |
| 相关工具内链 | ✅ |

---

## 三、AI Overview 维度（Will 完全没有）

Google AI Overview 在 2024-2025 全量上线后，已经成为重要的"零点击流量"和"被引用入口"。

### 3.1 AI Overview 偏好什么内容

- **答案直接性**：能不能用 1-2 段话回答用户问题
- **结构清晰**：H1-H6 / 列表 / 表格清晰
- **数据可溯**：每个事实有来源
- **时效性**：金融 / 监管 / 价格类必须新鲜
- **权威性**：E-E-A-T 强信号

### 3.2 AI Overview 入选信号

```yaml
ai_overview_eligibility_signals:
  high_priority:
    - 第一段直接回答 query（前 100 字含答案核心）
    - 表格化关键数据
    - 明确日期 + 来源引用
    - 作者权威性强（authoritative author profile）
    - YMYL 类必须有审核状态
  medium_priority:
    - FAQ Schema（虽然 FAQ 富结果已弃用，但 AI Overview 仍参考）
    - HowTo Schema（步骤类）
    - Article Schema 完整字段
  red_flags_for_exclusion:
    - 营销 / 推销话术过重
    - 缺少明确受众
    - 关键事实无来源
    - 内容超过 6 个月未更新（金融类）
```

### 3.3 Platform 优化策略

每个 `/learn` `/support` 页面顶部添加 **「TL;DR」段落**：

```markdown
**TL;DR**: 比特币合约强平价格 = （入仓价 × 杠杆 - 入仓价） / 杠杆。
具体取决于做多/做空方向、保证金模式、维护保证金率。本工具实时计算。
来源：Platform 合约规则文档（2026-06 版）。
```

这种结构**最容易被 AI Overview 抓取并引用**，引用时会带 Platform 链接。

---

## 四、GEO（Generative Engine Optimization）维度（Will 完全没有）

不只是 AI Overview，还有 Perplexity / ChatGPT Search / Claude / Gemini 都在分流 SEO 流量。

### 4.1 通用 GEO 策略

#### Answerable Chunks（可独立回答片段）

每个 H2 下的段落应能**脱离上下文被引用**：

❌ 反例：
```markdown
## 强平价格
如前所述，影响因素很多...
```

✅ 正例：
```markdown
## BTC 合约强平价格如何计算
比特币永续合约的强平价格 = 入仓价 × (1 - 1/杠杆 + 维护保证金率)。
做多和做空公式不同。Platform 当前 BTC 维护保证金率为 0.5%。
```

#### Fact Verifiability（事实可验证）

每个关键事实带来源：

❌ 反例：
```markdown
BTC 24h 交易量超过 300 亿美元。
```

✅ 正例：
```markdown
BTC 24h 交易量超过 300 亿美元（来源：CoinGecko, 2026-06-10）。
```

#### Citation-Friendly Structure（引用友好结构）

- 关键数据用表格（LLM 抓取概率 +60%）
- 关键结论用列表
- 段落长度 70-150 字最易被引用
- 用陈述句而非问句开头

### 4.2 跨 LLM 引用率追踪

V1 抽样测试：
- 每月对 Platform 50 个核心页面，跑 Perplexity / ChatGPT Search / Claude / Gemini
- 记录是否被引用 + 引用位置
- 季度复盘哪些页面被引用最多 → 反向优化其他页面

V2 自动化：
- geo-agent 每周自动跑
- Slack 周报

---

## 五、Platform 与 Will 知识库的关系

| 维度 | Will 版 | 我们 Platform 版 |
|---|---|---|
| Google 原文蒸馏 | ✅ 蒸馏到位 | ✅ 同样蒸馏 + 引用 Will 的核心结论 |
| Platform 频道对齐 | 列频道名 | 每频道给到字段级清单 |
| AI Overview | ❌ 未覆盖 | ✅ 3.1-3.3 节 |
| GEO（Perplexity/LLM 引擎）| ❌ 未覆盖 | ✅ 第 4 节 |
| 实际审核可执行性 | ❌ 文字描述 | ✅ 对应 `e-e-a-t.yaml` 6 条结构化规则可直接 audit |
| 与 fixture 关联 | ❌ 无 | ✅ 每条规则有 positive/negative fixture |
| YMYL 严格度 | 通用 | 加密 / 金融特化 |
| 更新机制 | 月度人工 | daily-pull-agent 同步 |

---

## 六、AI 调用判断规则（给 agent 用）

semantic-agent 在判断"是否符合 E-E-A-T"时使用以下决策树：

```
1. 检查页面是否属于 YMYL（金融/资产/安全/出入金/产品评价/合规）
   ↓
2. YMYL 必备五件套：作者 / 审核 / 发布日期 / 最后更新 / 来源
   ↓
3. 任一缺失 → finding[severity=high, rule=google.eeat.author-attribution-missing]
   ↓
4. 检查 Experience 信号：第一人称叙述 / 实操截图 / 平台特定数据
   ↓
5. 全部缺失 → finding[severity=medium, rule=google.eeat.first-hand-experience-missing]
   ↓
6. 检查 vs SERP：本页是否比同 SERP 其他结果有实质增量
   ↓
7. 增量低于 30% → finding[severity=medium, rule=google.eeat.thin-content-vs-serp]
   ↓
8. 检查 AI Overview 入选信号（见 3.2）
   ↓
9. TL;DR 段落缺失 → finding[severity=low, rule=google.ai-overview.tldr-missing]
   ↓
10. 检查 GEO 引用友好度
    ↓
11. answerable chunks 不足 3 → finding[severity=low, rule=perplexity.geo.answerable-chunks]
```

---

## 七、联动阅读

- `_rules/e-e-a-t.yaml`：本文档对应的结构化规则
- `_rules/structured-data-truthfulness.yaml`：Schema 真实性（E-E-A-T 信号之一）
- `../../platform/fintech-compliance.yaml`：YMYL 金融合规规则
- `../../platform/google-action-history.md`：MEXC 事故起因之一就是 E-E-A-T 信号弱
- `../llm-engines/_rules/perplexity.yaml`：GEO 对应规则

---

## 八、维护原则

- 每次 Google Search Central 更新本文档时同步更新（daily-pull-agent 检测）
- 每次 Platform 实际审核发现新模式时回写本文档
- 季度回顾"哪些建议被反复触发" → 升级为 `_rules/*.yaml` 硬规则
