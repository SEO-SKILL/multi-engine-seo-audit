# 垃圾内容政策与规模化内容（Platform 深度版）

> 对标 Will 知识库 `03-垃圾内容政策与规模化内容.md`。**我们这版增量**：
>
> 1. **加密 / Web3 行业风险案例库**（Will 没有）
> 2. **AI 生成内容的 Google 处置历史时间线**
> 3. **Platform 程序化 SEO 红线**（具体到 URL 模式 + 触发举报的实操示例）
>
> 创建：2026-06-10 / 维护：kelly@example.com

---

## 一、Google 原文最关键的 3 条更新（2026-05-15 起）

源文档：<https://developers.google.com/search/docs/essentials/spam-policies>（最后核实 2026-05-28）

1. **「滥用规模化内容」定义升级**：关注**结果和意图**，不再关注技术手段。AI / 脚本 / 翻译 / 拼接 / 多站分发——任何主要为排名而生的低增量内容都算。
2. **垃圾政策适用生成式 AI 回答**：想进入 AI 概览 / AI 模式不能用低价值规模化页面"喂"系统。
3. **垃圾信息举报可触发人工处置**（2026-04-23 更新）：举报不再是"反馈入口"，可能直接导致 manual action。

---

## 二、Google 列举的 5 类规模化高风险（Will 提到，但我们加案例）

### 2.1 AI 大量生成无增量页面

**Will 提到**：使用 AI 或类似工具生成大量页面，但没有给用户增加价值。

**加密行业真实案例**：

| 案例 | 时间 | Google 动作 |
|---|---|---|
| 某交易所用 AI 生成 5000+ "What is X coin" 页面 | 2024-Q2 | 全站去索引 |
| 某 DeFi 项目模板化生成 200+ "How to stake on X chain" | 2024-Q4 | 主域 PageRank 大跌 |
| 某加密交易所案例 转载页（Platform 事故同源）| 2026-Q1 | 单页人工处置 |

**Platform 红线**：

- 不能用 AI 模板生成币种页（除非每页有独立的研究 / 数据 / 风险视角）
- 不能用 AI 翻译填充 9 语言版本（必须真本地化）
- 程序化 SEO 必须设计每类页面的"独特信息层"

### 2.2 爬取 + 改写

**Will 提到**：转载、轻改写、照搬 feed、媒体聚合但没有独特价值。

**加密行业陷阱**：

- 转载 CoinDesk / CoinTelegraph / The Block 文章直接发自家 /news/
- 抓 CoinGecko 数据填充 /price/ 页（必须加增量解读）
- 抓 Etherscan 信息填充合约页

**Platform 红线**：

- `/news/*` 任何转载必须满足以下任一：
  1. cross-domain canonical 到原文
  2. noindex
  3. 原创增量 ≥ 50%（编辑评审 + 风险边界 + 独立段落）
- `/price/*` 抓 CoinGecko 数据 OK，但必须加 Platform 增量（K 线分析 / 用户讨论 / 工具入口）

### 2.3 拼贴（content aggregation）

**Will 提到**：不同页面的内容拼贴在一起但没有附加价值。

**Platform 红线**：

- `/learn` 不能是"Google 搜 'crypto futures' 把前 5 篇拼起来"
- 必须有 Platform 视角 / 平台具体数据 / 实操截图

### 2.4 多站隐藏规模化痕迹

**Will 提到**：为了隐藏规模化痕迹而创建多个站点。

**加密行业陷阱**：

- Platform 做了 example.com + Platform.io + 多个微站
- 内容互相重复或机械化分发

**Platform 红线**：

- 任何 Platform 子站 / 微站 / 二级域必须有独立价值定位
- 不能是同一批内容换域名分发

### 2.5 关键词堆砌空内容

**Will 提到**：大量几乎没有实际意义、但塞满关键词的页面。

**Platform 红线**：

- 不能为了覆盖 "BTC/ETH/SOL/XRP/..." 数百个币种关键词，做模板化的空壳币种页
- 每个币种页必须有真实数据 + 用户决策价值

---

## 三、AI 生成内容的 Google 处置时间线

| 时间 | 事件 |
|---|---|
| 2023-02 | Google 明确"AI 生成内容不违反 spam policy，前提是内容有用" |
| 2023-09 | Helpful Content Update 加强，targeting "为搜索引擎而非用户生产的内容" |
| 2024-03 | Spam Update + Core Update 同时上线，大量 AI 内容站点流量 -90% |
| 2024-08 | 政策更新："滥用规模化内容"定义升级，关注意图 / 结果 |
| 2025-Q2 | 多个加密 / fintech 站点因 AI 内容被 manual action |
| 2026-05-15 | 垃圾政策适用于生成式 AI 回答（AI Overview / SGE）|
| 2026-04-23 | 垃圾信息举报可触发 manual action |

**对 Platform 的启示**：

- AI 生成必须人工审核 + 编辑润色
- AI 生成的 schema / 标题 / 描述 / alt 也要校验
- 对可能让用户关心"怎么写的"的内容，**披露 AI 参与方式**
- 批量页面必须先定义独特价值层，再开始生产

---

## 四、Platform 程序化 SEO 红线（具体到 URL 模式）

### 4.1 允许的程序化模式

✅ **币种页**：`/price/{symbol}` — 每个币有独立的实时数据 + 历史 + 用户讨论

✅ **交易对工具页**：`/liquidation-calculator/{pair}` — 工具 + 真实计算逻辑 + 风险提示

✅ **资金费率页**：`/funding-rate/{pair}` — 真实数据 + 历史图表 + 解读

### 4.2 高风险程序化模式（必须人工增量审核）

⚠️ **比较页**：`/compare/platform-vs-{competitor}` — 必须有事实核验 + 不能 Best 类话术

⚠️ **区域页**：`/region/{country}` — 必须有真实可用性 + 合规说明

⚠️ **新闻 tag 页**：`/news/tag/{tag}` — 必须有 ≥ 5 篇高质量文章

### 4.3 禁止的程序化模式

❌ **What is X 模板页**：`/learn/what-is-{coin}` — 除非每页有独特研究角度

❌ **How to buy X 模板页**：`/buy/{coin}` — 除非每页有真实流程差异 + 地区说明

❌ **{Coin} Price Prediction**：完全禁止（Google YMYL 高风险 + 监管风险）

❌ **任何含 "Best" 的批量页**：`/best-crypto-{category}` — 合规 + 内容真实性双高风险

---

## 五、垃圾信息举报实战防御

2026-04-23 后举报可触发 manual action。Platform 需要：

### 5.1 防御自身被举报

- 定期 audit 所有程序化页面
- 维护"举报常见原因"列表，自查
- 客服 / 社区接到用户抱怨"内容像 AI 写的"立即排查

### 5.2 防御被竞品恶意举报

- 维护一份"高质量证据"清单：作者真人证明 / 编辑流程截图 / 引用源
- Google Search Console 监控异常流量下跌
- 一旦收到 manual action 通知，立即 reconsideration request

### 5.3 主动观察行业事故

- 关注 Twitter @googlesearchc + @searchliaison
- 监控 r/SEO 上的 manual action 报告
- 定期复盘行业事故（详见 `rules/platform/google-action-history.md`）

---

## 六、AI 调用判断规则（给 safety-agent 用）

```
1. 页面是否为程序化生成（URL 模式 + 数据库驱动）
   ↓
2. 程序化生成 → 检查每页"独特信息层"是否存在
   ↓
3. 信息层为空 → finding[severity=blocker, rule=google.spam.scaled-low-value]
   ↓
4. 检查内容相似度（vs 站内其他同模板页）
   ↓
5. 相似度 > 80% → finding[severity=high, rule=google.spam.scaled-duplicate]
   ↓
6. 检查是否为转载（外部 source link + 内容相似度 > 70%）
   ↓
7. 是转载 + self-canonical → finding[severity=blocker, rule=platform.l01]
   ↓
8. 检查 AI 生成痕迹（重复模板 / 缺事实 / 无第一手经验）
   ↓
9. 强 AI 痕迹 → finding[severity=high, rule=google.spam.ai-scaled]
```

---

## 七、联动阅读

- `_rules/structured-data-truthfulness.yaml`：schema 真实性（spam 防御一环）
- `../../platform/republished-and-tagging.yaml`：转载原创增量规则
- `../../platform/fintech-compliance.yaml`：金融合规黑名单
- `../../platform/google-action-history.md`：行业 + 自家事故案例库
- `01-helpful-content-eat.md`：E-E-A-T 信号（与 spam 防御互补）
