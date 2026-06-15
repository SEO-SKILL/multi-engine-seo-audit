# Google Helpful Content 信号评估

## 任务

判断页面是否符合 Google Helpful Content 标准。

## 输入

- `visible_text`
- `page_purpose`: 页面类型
- `author_metadata`
- `sources`: 引用源

## "对象、方式、原因" 三问

1. **对象**：谁写的？背景是否清楚？
2. **方式**：内容如何产出？是否说明测试 / 验证 / 数据来源？
3. **原因**：内容主要目的是帮助用户还是吸引流量？

## 高风险信号

- 跨主题大量铺内容
- 广泛自动化
- 只做别人内容摘要
- 不为现有受众写内容
- 制造"假新鲜"
- 追逐没有答案的话题（如价格预测）

## 输出 JSON

```json
{
  "rule_id": "google.helpful-content.signal-weak",
  "severity": "high",
  "confidence": 0.80,
  "evidence": {
    "three_questions_score": {
      "who": 0.4,
      "how": 0.3,
      "why": 0.5
    },
    "risk_signals": ["缺作者背景", "无 Platform 自有数据", "改写自其他文章"]
  },
  "recommendation": "补 Platform 自有数据 / 经验 / 风险分析；明确作者背景",
  "reasoning": "Helpful Content 信号弱，Core Update 时易被打击"
}
```
