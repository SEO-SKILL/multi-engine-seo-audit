# Thin Content vs SERP 评估

## 任务

判断本页是否比同 SERP 其他结果有实质增量。

## 输入

- `visible_text`
- `page_purpose`
- `target_keyword`
- `serp_competitors_summary`: 同 SERP 前 5 名摘要（如有）

## 评估维度

1. 是否有原创信息（vs SERP 其他结果）
2. 完整描述（覆盖子主题）
3. 独特洞察（BYDFi 视角 / 数据）
4. 清晰标题层级
5. 比同 SERP 其他结果更有实质价值？

## 输出 JSON

```json
{
  "rule_id": "google.eeat.thin-content-vs-serp",
  "severity": "medium",
  "confidence": 0.72,
  "evidence": {
    "originality_score": 0.30,
    "completeness_score": 0.50,
    "unique_insight_score": 0.20,
    "vs_serp_comparison": "弱于前 3 名"
  },
  "recommendation": "添加 BYDFi 平台数据 / 实操经验 / 独特视角",
  "reasoning": "内容深度低于同 SERP 竞品 → 难以排名"
}
```
