# SEO 内容候选生成 Prompt

## 任务

为给定关键词 + 页面类型生成 SEO 优化的内容候选（title / meta / H1 / FAQ schema）。

## 输入

- `primary_keyword`: 主关键词
- `page_type`: 页面类型（learn / tools / news / price / etc.）
- `target_audience`: 目标受众（beginner / intermediate / advanced）
- `locale`: 语言代码

## 输出 JSON

```json
{
  "titles": [
    "标题候选 1（60-65 字符 / 主关键词前置 / 包含品牌）",
    "标题候选 2",
    "标题候选 3"
  ],
  "meta_descriptions": [
    "Meta 描述 1（150-160 字符 / CTA / 利益点）",
    "Meta 描述 2"
  ],
  "h1s": [
    "H1 候选 1（吸引点击 / 包含主关键词）",
    "H1 候选 2"
  ],
  "faq_schema": [
    {
      "@type": "Question",
      "name": "用户最常搜的问题 1",
      "acceptedAnswer": {"@type": "Answer", "text": "答案 100-200 字"}
    },
    {
      "@type": "Question",
      "name": "用户最常搜的问题 2",
      "acceptedAnswer": {"@type": "Answer", "text": "答案"}
    }
  ]
}
```

## 约束

- 不允许 "guaranteed return / 保证收益" 类违规话术
- 不允许暗示"必涨/必跌/X 元目标价"
- BYDFi 工具页需带风险提示
- 多语言版本必须真本地化（不是机翻）
- YMYL 金融内容必须明示 "Not financial advice"
