# Schema 字段真实性评估 Prompt

## 任务

判断 JSON-LD 字段是否反映页面可见内容。

## 输入

- `jsonld_parsed`: 解析后的 JSON-LD
- `visible_text`: 页面可见文字
- `dom_screenshot`: 渲染后截图（如有）

## 检查项（按重要性）

1. **AggregateRating** → 页面是否有可见的评分组件 / 评论区？
2. **Article.author** → 页面是否有可见作者署名？
3. **Article.datePublished/dateModified** → 页面是否有可见日期？
4. **Product.offers.price** → 页面是否有可见价格？
5. **FAQ.mainEntity** → 页面是否有可见 FAQ 段落？
6. **copyrightNotice.email** → 是否与页面 footer 邮箱一致？

## 输出 JSON

```json
{
  "rule_id": "google.schema.field-not-grounded-in-visible-content",
  "severity": "blocker",
  "confidence": 0.90,
  "evidence": {
    "ungrounded_fields": [
      {
        "path": "aggregateRating.ratingValue",
        "value": "4.8",
        "missing_in_visible": true,
        "reason": "页面无评分组件，无评论区"
      }
    ]
  },
  "recommendation": "删除 aggregateRating 字段 或 添加可见评分组件",
  "reasoning": "AggregateRating 字段虚假 = Google 结构化数据人工处置高风险"
}
```
