# AI Overview 入选信号深度分析（Platform 版）

> Will 知识库 `37-AI 功能与 AI 搜索呈现.md` 浅触及，我们这版深做。
> 2026 年 Google AI Overview 已成 SERP 首屏标配，零点击但带品牌曝光。
> 创建：2026-06-10

---

## 一、AI Overview 现状（2026-06）

- 覆盖率：全球 70%+ 的 informational query 触发 AI Overview
- 加密领域覆盖率：~85%（金融 / 投资 / 科技类高）
- 平均占首屏：1.5-2.5 屏（手机）/ 0.8-1.5 屏（桌面）
- 引用源数：3-7 个

---

## 二、入选 8 大信号（按权重排序）

### 信号 1：第一段直接回答（最关键）

❌ 反例：
```
比特币是一种神秘而有趣的数字资产。本文将详细介绍...
```

✅ 正例：
```
比特币（BTC）是 2009 年由匿名开发者中本聪发布的去中心化数字货币。
当前价格：$60,234（来源：CoinGecko, 2026-06-10）。
本文涵盖：定义、技术原理、如何购买、风险。
```

### 信号 2：TL;DR 模块

每个核心页面顶部放 TL;DR：

```markdown
**TL;DR**: 比特币合约强平价格 = 入仓价 × (1 - 1/杠杆 + 维护保证金率)。
做多/做空公式不同，Platform BTC 维护保证金率 0.5%。本工具实时计算。
最后更新：2026-06-08。
```

### 信号 3：表格化关键数据

AI Overview **极易**抓取表格内容：

```markdown
| 合约对 | 维护保证金率 | 最大杠杆 |
|---|---|---|
| BTC/USDT | 0.5% | 125x |
| ETH/USDT | 0.5% | 100x |
| SOL/USDT | 1.0% | 50x |
```

### 信号 4：列表化步骤

```markdown
如何在 Platform 买比特币：
1. 注册账户（30 秒）
2. 完成 KYC（5 分钟）
3. 选择支付方式（卡 / 银行 / OTC）
4. 输入金额并确认
```

### 信号 5：明确的事实 + 来源

```markdown
- BTC 24h 交易量：$320 亿（来源：CoinGecko, 2026-06-10）
- BTC 流通量：19,724,506 BTC（来源：CoinMarketCap）
- BTC 减半时间：约 4 年一次，下次约 2028-04
```

### 信号 6：E-E-A-T 强信号

- 作者权威（独立 author 页 + 历史内容）
- 审核状态（"经 Platform 风险管理团队审核"）
- 发布 + 更新日期
- 引用源

### 信号 7：YMYL 类必备审核

金融类 AI Overview 严格筛 YMYL 信号：

```markdown
本内容由 Platform 加密研究团队撰写，经合规与风险管理团队审核。
最后更新：2026-06-08。仅作信息参考，不构成投资建议。
```

### 信号 8：Schema 类型支持

支持的 schema：
- HowTo（步骤类）
- Article + author + reviewedBy
- FAQ（虽然富结果弃用，但 AI Overview 仍参考）
- WebApplication（工具类）

---

## 三、被排除的 4 类信号

### 排除 1：营销话术过重

❌ "Platform 是全球最好的加密交易所，零费率、超高杠杆、立即注册！"

### 排除 2：缺受众

❌ "本文适合任何对加密感兴趣的人。"
✅ "本文面向已开过合约交易但不熟悉强平机制的中级用户。"

### 排除 3：缺事实来源

❌ "BTC 价格暴涨。"
✅ "BTC 24h 涨幅 +5.2%（来源：CoinGecko，2026-06-10 10:00 UTC）。"

### 排除 4：内容过期

金融 / 监管 / 价格类超过 6 个月未更新 → 直接排除。

---

## 四、Platform AI Overview 优化矩阵（频道级）

| 频道 | AI Overview 入选目标 | 优化重点 |
|---|---|---|
| `/price/{coin}` | "What is the price of X" | 实时数据 + 来源 + 时间戳 |
| `/learn/what-is-{topic}` | "What is X" | TL;DR + 定义 + 来源 + FAQ |
| `/how-to-buy/{coin}` | "How to buy X" | 列表化步骤 + 地区限制表 + 风险提示 |
| `/tools/{tool}` | "How to calculate X" | 工具入口 + 公式说明 + 示例数据 |
| `/funding-rate/{pair}` | "Current funding rate for X" | 实时数据 + 历史趋势 + 解读 |
| `/learn/futures/{topic}` | "How does X work" | 概念 + 公式 + 示例 + FAQ |

---

## 五、AI Overview 流量价值评估

**误区**：AI Overview 零点击 → 没流量价值

**真相**：

1. **品牌曝光**：用户看到 AI Overview 中提到 Platform = 间接品牌建立
2. **引用流量**：~15% 用户会点击引用源（金融类高于平均，~25%）
3. **二次搜索**：AI Overview 看完用户再搜 "Platform" 品牌词 → 直接转化
4. **LLM 训练**：被 AI Overview 引用的内容更可能进 Gemini / Bard 训练数据

**估算 ROI**：

- Platform /learn/what-is-liquidation 每月 SERP 展示 10,000 次
- AI Overview 触发率 80% → 8,000 次曝光（前 3 引用源）
- 假设 Platform 排前 3 引用源中 → 1,500-2,500 次品牌曝光（无成本）
- 折算 CPM：相当于 $50-100 的免费品牌广告

---

## 六、AI Overview 监控（V2）

- 每月对 Platform 50 个核心页面手动查 Google 是否触发 AI Overview
- 记录是否被引用 + 引用位置
- 季度复盘哪些页面入选 → 反向优化未入选页面

---

## 七、联动阅读

- `01-helpful-content-eat.md`：E-E-A-T 基础
- `_rules/page-experience.yaml`：CWV 是 AI Overview 间接信号
- `../llm-engines/_rules/gemini.yaml`：Gemini 是 AI Overview 后台
- `../llm-engines/_rules/perplexity.yaml`：GEO 通用策略
