# 结构化数据精通（Platform 防 某加密交易所案例 L04 复发版）

> 对标 Will 知识库 `18-结构化数据总览与通用规则.md`
> 来源：https://developers.google.com/search/docs/appearance/structured-data
> 创建：2026-06-11

---

## 一、为什么 Platform 必须把这个学透

**某加密交易所行业案例 L04 就是 schema 字段虚假触发的 manual action**。
Schema 不是"加个 JSON-LD 就行"，是"每个字段必须对应可见内容"。

---

## 二、Schema 三大原则（必须背下来）

### 原则 1：Grounded in Visible Content
**Schema 字段必须对应页面可见内容**。

❌ 某加密交易所行业案例同类违规：
```html
<!-- Schema 声明 AggregateRating -->
<script type="application/ld+json">
{"@type": "Article",
 "aggregateRating": {"ratingValue": "4.8", "reviewCount": "10234"}}
</script>

<!-- 但页面可见区域没有任何评分组件 -->
<article>... 文章内容 ...</article>
```

✅ 正确：
```html
<script type="application/ld+json">
{"@type": "Product",
 "aggregateRating": {"ratingValue": "4.2", "reviewCount": "127"}}
</script>

<section class="reviews">
  <div class="rating">4.2 / 5 (127 reviews)</div>
  <!-- 真实评论列表 -->
</section>
```

### 原则 2：SSR 而非 CSR

Schema 必须在 raw HTML 中，不能仅 JS 注入。

❌ 某加密交易所行业案例同类：
```javascript
window.addEventListener('DOMContentLoaded', () => {
  const s = document.createElement('script');
  s.type = 'application/ld+json';
  s.textContent = JSON.stringify({...});
  document.head.appendChild(s);
});
```

✅ 正确：在 SSR 输出 `<head>` 中直接含 `<script type="application/ld+json">`

### 原则 3：Match Page Purpose

Schema 类型必须匹配页面真实用途。

❌ 某加密交易所行业案例 L05 同类：
- Event schema 用在非活动页
- Recipe schema 用在非食谱页

✅ 正确映射：

| 页面类型 | 应用 schema |
|---|---|
| `/news/{id}` | NewsArticle |
| `/learn/{topic}` | Article + LearningResource |
| `/tools/{tool}` | SoftwareApplication / WebApplication |
| `/price/{coin}` | (无对应类型，用 Article + breadcrumb)|
| `/futures/{pair}` | Product（合约视为产品）|
| `/copy-trading/{trader}` | （慎用，监管风险）|
| `/learn/glossary` | DefinedTermSet |
| `/help/faq` | FAQPage（弃用但仍可加）|
| `/about` | AboutPage / Organization |
| `/security` | Organization 含 publicAccessLevel |

---

## 三、Platform 必备 Schema 清单（全站基线）

```html
<!-- 1. Organization (全站 footer 共享) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Platform",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "foundingDate": "2019",
  "sameAs": [
    "https://twitter.com/platform_official",
    "https://www.linkedin.com/company/platform",
    "https://t.me/platform_official"
  ],
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "...",
    "addressCountry": "..."
  }
}
</script>

<!-- 2. WebSite + SearchAction (首页) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "url": "https://example.com",
  "name": "Platform",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://example.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
</script>

<!-- 3. BreadcrumbList (所有非首页) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type":"ListItem","position":1,"name":"Home","item":"https://example.com/"},
    {"@type":"ListItem","position":2,"name":"Learn","item":"https://example.com/en/learn"},
    {"@type":"ListItem","position":3,"name":"BTC Liquidation","item":"https://example.com/en/learn/btc-liquidation"}
  ]
}
</script>
```

---

## 四、内容页应用模板（4 类）

### 4.1 Article (Learn / Blog / News)
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "image": "...",
  "datePublished": "2026-01-15",
  "dateModified": "2026-06-08",
  "author": {
    "@type": "Person",
    "name": "Platform Research",
    "url": "https://example.com/author/research"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Platform",
    "logo": {"@type": "ImageObject", "url": "..."}
  },
  "reviewedBy": {
    "@type": "Person",
    "name": "Platform Risk Management",
    "url": "https://example.com/author/risk"
  }
}
```

### 4.2 SoftwareApplication (Tools)
```json
{
  "@type": "SoftwareApplication",
  "name": "BTC Liquidation Calculator",
  "applicationCategory": "FinanceApplication",
  "operatingSystem": "Any",
  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
}
```

### 4.3 FAQPage (谨慎使用 — 富结果已弃用，但 AI Overview 仍读取)
```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is BTC liquidation?",
      "acceptedAnswer": {"@type": "Answer", "text": "..."}
    }
  ]
}
```

### 4.4 Product (合约 / 工具)
```json
{
  "@type": "Product",
  "name": "BTC/USDT Perpetual Futures",
  "description": "...",
  "brand": {"@type": "Brand", "name": "Platform"}
}
```

⚠️ Product 别加 `aggregateRating` 除非真有评分组件！

---

## 五、与我们 Skill 的对接

| 规则 ID | 检测 |
|---|---|
| `google.schema.field-not-grounded-in-visible-content` | 某加密交易所案例 L04 核心 - schema 字段虚假 |
| `google.schema.jsonld-csr-only` | 某加密交易所案例 L04 子问题 - CSR 注入 |
| `google.schema.aggregaterating-without-review-component` | AggregateRating 无可见评分 |
| `google.schema.copyrightnotice-inconsistent` | 邮箱不一致 |
| `google.schema.relatedlink-topic-mismatch` | relatedLink 主题不符 |
| `shared.schema.faqpage-deprecated` | FAQPage 弃用提醒 |
| `shared.schema.json-ld-syntax-error` | JSON 语法错 |
| `google.product.schema-incomplete` | Product 字段不全 |
| `google.kg.organization-incomplete` | Organization 字段不全 |

跑 `audit` 自动检测所有 schema 相关规则。

---

## 六、Will 知识库对照

Will `18-结构化数据总览与通用规则.md` 列了 schema 类型清单。
我们这版 = 类型清单 + Platform 频道映射 + 某加密交易所行业案例防复发 + 实操模板。
