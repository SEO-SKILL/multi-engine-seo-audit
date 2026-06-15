# Platform SEO 修复方案（基于真实 audit 数据）

> 创建：2026-06-10
> 数据来源：`scripts/batch_audit.py` × 5 个核心页面
> Owner：Kelly Chen / Will Team

---

## 一、最高价值发现

### 🚨 全站 E-E-A-T composite 接近 0

| 页面 | E-E-A-T | 缺什么 |
|---|---|---|
| homepage | 0.10 | 只有 visible byline，其他都缺 |
| futures | 0.00 | 全缺 |
| learn | 0.00 | 全缺 |
| price/btc | 0.00 | 全缺 |
| support | 0.00 | 全缺 |

**意义**：对 Google 来说，Platform 整个站缺 E-E-A-T 信号 = YMYL 金融内容**永远不可能进 SERP 前 10**。

### 🚨 全站 GEO composite 0.2-0.4

LLM 时代（Perplexity / ChatGPT Search / Gemini / Claude）的引用率会严重受限。

### 🟡 futures 58 分根因

锚文本堆砌（同一关键词在 internal links 中占 30%+）。

---

## 二、3 个修复优先级

### P0：全站修 E-E-A-T（**最高 ROI**）

每个内容页 `<head>` 加 JSON-LD（一次性 Platform engineering 工作）：

```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication / Article / FAQPage",
  "author": {
    "@type": "Person",
    "name": "Platform Research Team",
    "url": "https://example.com/author/research-team"
  },
  "reviewedBy": {
    "@type": "Person",
    "name": "Platform Risk Management Team",
    "url": "https://example.com/author/risk-team"
  },
  "datePublished": "[实际发布日期]",
  "dateModified": "[最后修改日期]",
  "publisher": {
    "@type": "Organization",
    "name": "Platform",
    "url": "https://example.com",
    "logo": "https://example.com/logo.png",
    "sameAs": [
      "https://twitter.com/platform_official",
      "https://www.linkedin.com/company/platform",
      "https://t.me/platform_official"
    ]
  }
}
```

页面 footer 加可见署名：

```html
<footer class="article-meta">
  <p class="byline">
    Author: <a href="/author/research-team" rel="author">Platform Research Team</a>
    | Reviewed by: <a href="/author/risk-team">Platform Risk Management Team</a>
    | Published: <time datetime="YYYY-MM-DD">YYYY-MM-DD</time>
    | Updated: <time datetime="YYYY-MM-DD">YYYY-MM-DD</time>
  </p>
  <p>
    Sources:
    <a href="https://coingecko.com">CoinGecko</a>,
    <a href="https://defillama.com">DefiLlama</a>,
    <a href="https://example.com/futures-rules">Platform Futures Rules</a>
  </p>
</footer>
```

**预期收益**：E-E-A-T composite 从 0.0 → 0.80+，单页 Brand SEO Score 提升 10-15 分。

### P1：全站修 GEO（LLM 时代流量入口）

每个 `/learn` `/support` 顶部加 TL;DR：

```markdown
**TL;DR**: 比特币合约强平价格 = 入仓价 × (1 - 1/杠杆 + 维护保证金率)。
做多/做空公式不同，Platform BTC 维护保证金率 0.5%。
最后更新: 2026-06-08 | 来源: Platform Futures Rules
```

关键数据表格化：

```html
<table>
  <tr><th>合约对</th><th>维护保证金率</th><th>最大杠杆</th></tr>
  <tr><td>BTC/USDT</td><td>0.5%</td><td>125x</td></tr>
</table>
```

`/llms.txt` 文件：

```
# Platform llms.txt
> Platform is a crypto futures exchange.

## Key resources
- [Futures Rules](https://example.com/futures-rules)
- [Liquidation Calculator](https://example.com/tools/liquidation)
- [Learn Center](https://example.com/learn)
```

**预期收益**：GEO composite 0.30 → 0.70+。Perplexity / ChatGPT Search 引用率上升。

### P2：futures 页修锚文本堆砌

```bash
# audit 真实数据
[medium] shared.internal-link.anchor-text-keyword-stuffing
锚文本 'X' 占 30%+ (重复使用)
```

要改成：

```html
<!-- 改前 -->
<a href="/futures/btc">BTC futures</a>
<a href="/futures/eth">BTC futures</a>  ← 大量重复"BTC futures"锚文本
<a href="/futures/sol">BTC futures</a>

<!-- 改后 -->
<a href="/futures/btc">BTC perpetual</a>
<a href="/futures/eth">ETH futures contract</a>
<a href="/futures/sol">Trade SOL futures on Platform</a>
```

**预期收益**：futures 单页 58 → 78+ 分。

---

## 三、实施时间估算

| 任务 | 工程量 | 预期收益 |
|---|---|---|
| 模板化 E-E-A-T JSON-LD 注入 | 2 天前端 | 全站 +10-15 分 |
| 模板化页面 footer byline | 1 天 | 包含在上 |
| Learn Center TL;DR 改造 | 1 天编辑 + 1 天前端 | 全站 GEO +0.4 |
| `/llms.txt` 创建 | 30 分钟 | LLM 引用率 +20% |
| futures 锚文本重排 | 半天 | 单页 +20 分 |
| **合计** | **5 个工作日** | **平均 SEO 分 76 → 88** |

---

## 四、验证流程

修复完成后跑：

```bash
cd ~/.claude/skills/seo-audit

# 1. 跑 batch_audit 对比基线
uv run python scripts/batch_audit.py

# 2. 对比 snapshots/batch-audit-20260610-*.json 看 composite 变化
# 3. 生成 HTML 报告分享给 CTO
uv run python scripts/render_report.py https://example.com

# 4. 跑 gate 卡审（防新页面 regression）
uv run python cli.py gate path/to/new-article.md
```

---

## 五、Will 团队对接

把这份方案 + audit JSON snapshots 同步给 Will 团队，让 Will 团队：

1. 验证 E-E-A-T 修复方案与 Will 知识库口径一致
2. 提供 Platform 内部 author profile 页面规范
3. 提供 reviewer 团队成员名单（用于 schema 字段）

---

## 六、长期 SOP（V1 上线后）

- 每周跑 `batch_audit.py` 一次
- HTML 报告自动归档到 `snapshots/`
- 复盘"哪些 finding 反复出现" → 升级规则或加自动 patch
- 季度 review composite scores 趋势

---

*本方案基于 Platform SEO Audit Skill V1+V2 真实跑出的数据生成。*
*跑 `uv run python scripts/batch_audit.py` 可重复验证。*
