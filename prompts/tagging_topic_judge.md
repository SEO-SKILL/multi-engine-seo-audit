# 分类标签语义匹配评估

## 任务

判断页面标签是否真实反映正文主题（防 MEXC L05 事故）。

## 输入

- `visible_text`
- `tags_assigned`: 当前页面标签
- `page_topic_classification`: LLM 分类的主题
- `source_article_tags`: 原文标签（如是转载）

## 决策规则

1. 标签 vs 正文主题重合度 < 40% → finding[severity=high]
2. 标签 vs 原文标签完全不一致（如原文 AI，本页 SEC）→ finding[severity=high]
3. 标签是 ticker 误识别产物（SEC ≠ 监管 SEC）→ finding[severity=blocker]

## 输出 JSON

```json
{
  "rule_id": "bydfi.l05.tagging-topic-mismatch",
  "severity": "high",
  "confidence": 0.85,
  "evidence": {
    "current_tags": ["SEC", "Lending"],
    "actual_topics": ["AI", "Fintech", "Creator Platform"],
    "source_article_tags": ["AI"],
    "match_score": 0.0
  },
  "recommendation": "标签改为 AI / Fintech / Tech Review / Guest Posting",
  "reasoning": "MEXC 事故 L05 同源问题：标签自动从 ticker 识别（SEC）但正文主题完全不同"
}
```
