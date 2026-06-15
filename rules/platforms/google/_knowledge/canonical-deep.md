# Canonical 规范化深度指南（Platform 版）

> 对标 Will 知识库 `12-canonical规范化.md` 深做
> 来源：https://developers.google.com/search/docs/crawling-indexing/canonicalization
> 创建：2026-06-11

---

## 一、Canonical 的本质

**给 Google 一个"我的真身在哪里"的信号。**

Google 看到同一内容多个 URL（http/https / www/non-www / 大小写 / 参数 / 移动版 / 多语言）时，需要确定哪个是"主版本"参与排名。

---

## 二、Canonical 的 4 种声明方式（按优先级）

| 方式 | 优先级 | 示例 |
|---|---|---|
| HTTP Link header | 最高 | `Link: <https://example.com/btc>; rel="canonical"` |
| `<link rel="canonical">` in `<head>` | 高 | `<link rel="canonical" href="https://example.com/btc">` |
| Sitemap | 中 | `<loc>https://example.com/btc</loc>` |
| 301 重定向 | 高（但是另一种机制）| `Location: https://example.com/btc` |

---

## 三、5 种 Canonical 模式

### 1. Self-canonical（自指）

最常见，告诉 Google "this is the canonical"。
```html
<link rel="canonical" href="https://example.com/en/futures">
```

### 2. Cross-domain canonical（跨域）

⚠️ **MEXC 事故核心**：当 Platform 转载第三方文章时，必须 canonical 到原文。
```html
<!-- Platform /news/some-news 转载 BlockchainReporter -->
<link rel="canonical" href="https://blockchainreporter.net/the-original">
```

### 3. Locale variants（多语言）

每个语言版本应 canonical 到自己 + 用 hreflang 指向其他语言。
```html
<!-- example.com/ko/learn -->
<link rel="canonical" href="https://example.com/ko/learn">
<link rel="alternate" hreflang="en" href="https://example.com/en/learn">
```

❌ 错误：所有语言 canonical 到英文版（等于告诉 Google 其他语言都是重复）

### 4. AMP / Mobile variants（已逐步淘汰）

如有 AMP 版本：
```html
<!-- AMP page -->
<link rel="canonical" href="https://example.com/non-amp-version">
```

### 5. Pagination

分页页面建议每页 self-canonical（旧的 rel=prev/next 已弃用）。

---

## 四、Canonical 常见错误（MEXC 事故同类）

### 错误 1：CSR 注入 canonical
```javascript
// ❌ 错误 - Googlebot 抓取时看不到 canonical
window.addEventListener('DOMContentLoaded', () => {
  const link = document.createElement('link');
  link.rel = 'canonical';
  link.href = 'https://example.com/btc';
  document.head.appendChild(link);
});
```

应该 SSR 输出在原始 HTML 中。

### 错误 2：Canonical 链
```
Page A → canonical: B
Page B → canonical: C
Page C → canonical: D
```
Google 可能只跟随 1 跳。直接 canonical 到最终版。

### 错误 3：Canonical 指向 noindex 页
```html
<!-- 矛盾信号 -->
<link rel="canonical" href="/page-b">
<!-- page-b: -->
<meta name="robots" content="noindex">
```

### 错误 4：Self-canonical on 转载内容（MEXC 事故 L01）
```html
<!-- Platform /news/some-article 转载 BlockchainReporter -->
<!-- ❌ 错误：self-canonical 但内容是转载 -->
<link rel="canonical" href="https://example.com/news/some-article">
```
应：
- cross-domain canonical 到原文，OR
- 补足原创增量 ≥ 50%（编辑评审 / 风险边界 / FAQ）

### 错误 5：JS 改写 canonical 与 raw HTML 不一致
```html
<!-- raw HTML: -->
<link rel="canonical" href="https://example.com/v1">
<!-- JS 后改成: -->
<link rel="canonical" href="https://example.com/v2">
```
Google 选择哪个不确定 → 信号弱。

---

## 五、Platform 频道级 Canonical 策略

| 频道 | Canonical 策略 |
|---|---|
| `/en/futures` | self-canonical |
| `/ko/futures` | self-canonical（不指英文版） |
| `/news/{article}` | 如转载 → cross-domain 到原文；如原创 → self-canonical |
| `/price/{coin}` | self-canonical（多语言版各自 canonical）|
| `/learn/{topic}` | self-canonical |
| `/tools/{tool}/{pair}` | self-canonical |
| `/search?q=` | canonical 到无参数页（搜索结果不索引）|
| 参数化 URL（utm_ 等）| canonical 到无参版本 |

---

## 六、与我们 Skill 的对接

| 规则 | 检测什么 |
|---|---|
| `google.canonical.missing` | canonical 完全缺失 |
| `google.canonical.self-canonical-on-republished` | 转载页 self-canonical（MEXC 事故同类）|
| `google.canonical.chain-too-long` | canonical 跳链 > 1 |
| `google.canonical.points-to-noindex` | canonical 指向 noindex 页 |
| `google.canonical.disagrees-with-google` | GSC 显示 Google 选定的 canonical 与我们声明不同 |

跑 `audit <url>` 自动检测所有 5 条。

---

## 七、与 Will 知识库的关系

Will `12-canonical规范化.md` 是 Google 文档的中文版。
我们这版 = Will 内容 + Platform 频道级实操 + MEXC 事故案例对照 + 可执行规则 ID。
