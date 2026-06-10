# Google AI Overview 入选评估

## 任务

判断页面是否符合 AI Overview 入选信号。

## 输入

- `visible_text`
- `jsonld`
- `page_structure`

## 入选信号（≥ 5 项算 high eligibility）

1. 第一段直接回答 query（前 100 字含核心答案）
2. TL;DR 模块
3. 关键数据表格化
4. 列表化步骤
5. 明确事实 + 来源
6. E-E-A-T 强信号（作者 / 审核 / 日期）
7. YMYL 类有审核状态
8. Schema 类型支持（HowTo / Article / FAQ）

## 排除信号（任一即低 eligibility）

- 营销话术过重
- 缺受众
- 缺事实来源
- 金融类 > 6 个月未更新

## 输出 JSON

```json
{
  "rule_id": "gemini.ai-overview.eligibility",
  "severity": "low",
  "confidence": 0.80,
  "evidence": {
    "eligibility_signals_found": 3,
    "eligibility_signals_missing": ["TL;DR", "data tables", "structured citations"],
    "exclusion_signals": [],
    "eligibility_score": 0.40
  },
  "recommendation": "添加 TL;DR 段落 + 关键数据表格化 + 引用来源",
  "reasoning": "AI Overview 入选概率低，错失零点击品牌曝光"
}
```
