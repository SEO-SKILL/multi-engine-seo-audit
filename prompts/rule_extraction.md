# Rule Extraction Prompt

从搜索引擎官方文档/blog/状态页中提取 SEO 规则候选。

## 输入
- `source_name`: 来源名称（如 google_search_central_blog）
- `text`: 文档正文（最多 8000 字符）

## 输出格式（严格 JSON）

```json
{
  "candidates": [
    {
      "id_suggestion": "google.feature.short-name",
      "title": "规则简短标题",
      "description": "Google 文档原文表达",
      "severity_suggestion": "blocker | high | medium | low | info",
      "applies_to_pages": ["all", "news", "learn", ...],
      "is_new_signal": true,
      "evidence_snippet": "原文 1-2 句话",
      "confidence": 0.0-1.0
    }
  ]
}
```

## 提取标准

只提取明确表达"应该 / 必须 / 不应"的规则，不要提取一般描述。

## 严重程度判定

- `blocker`: Google 明确说"违反 = manual action" 或"不索引"
- `high`: Google 说"严重影响排名"
- `medium`: 建议但不强制
- `low`: 最佳实践
- `info`: 数据点
