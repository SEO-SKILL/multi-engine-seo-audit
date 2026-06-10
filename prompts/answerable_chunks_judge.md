# GEO Answerable Chunks 评估

## 任务

判断页面内容是否能被切成"独立可回答片段"。

## 输入

- `visible_text`
- `h2_h3_structure`: H2/H3 标题列表
- `sections`: 各段落

## 评估信号

每个 H2/H3 下应：
1. 能独立回答一个问题（脱离前文也成立）
2. 段落 70-150 字最优
3. 关键数据用列表 / 表格 / 粗体
4. 第一句陈述核心结论

## 输出 JSON

```json
{
  "rule_id": "perplexity.geo.answerable-chunks",
  "severity": "medium",
  "confidence": 0.78,
  "evidence": {
    "total_sections": 12,
    "answerable_sections": 4,
    "answerable_ratio": 0.33,
    "problematic_sections": [
      {"h2": "强平价格", "issue": "段落以 '如前所述' 开头，无法独立"},
      {"h2": "...", "issue": "段落 > 400 字，AI 难抓取关键句"}
    ]
  },
  "recommendation": "重构为每 H2 段落独立可答 + 段首陈述结论",
  "reasoning": "ChatGPT Search / Perplexity 偏好抓 '短段落 + 独立可答' 内容"
}
```
