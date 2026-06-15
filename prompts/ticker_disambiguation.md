# Ticker 上下文消歧义 Prompt

## 任务

判断页面中出现的 ticker symbol 是否被正确理解（不是被错误关联到加密代币）。

## 输入

- `visible_text`: 页面可见文字
- `title`: 页面标题
- `h1`: H1
- `ticker_candidates`: 页面中识别到的疑似 ticker 列表
- `page_topic_classification`: 页面主题（如 "review", "evaluation", "regulation", "crypto-trading"）

## 决策规则

### 触发 finding 的场景

1. **Title 含 "Pros and Cons" / "advantages" 等通用词** + 页面识别出 PROS ticker → finding[severity=blocker]
2. **Body 讨论监管 / SEC 机构** + 页面识别出 SEC ticker（不是讨论代币）→ finding[severity=high]
3. **Body 讨论 gas fee / gas price 通用术语** + 页面识别出 GAS coin → finding[severity=medium]

### 不触发的场景

1. Title 明确是 "PROS Token / Pharos Network" → 正确关联
2. Body 明确讨论 "Pharos PROS 代币" → 正确关联
3. ticker 出现在交易对上下文（如 "BTC/USDT"）→ 正确关联

## 输出 JSON 示例

```json
{
  "rule_id": "platform.l02.ticker-context-mismatch",
  "severity": "blocker",
  "confidence": 0.92,
  "evidence": {
    "text_snippet": "Title: 'Techsslaash Review: Pros and Cons'",
    "ticker_misidentified": "PROS",
    "actual_context": "通用词 Pros and Cons",
    "false_association": "Pharos PROS 代币"
  },
  "recommendation": "移除页面中所有 PROS ticker widget / relatedLink / 交易入口",
  "reasoning": "页面标题含 'Pros and Cons' 通用词，与 Pharos PROS 代币无关。自动 ticker 识别导致主题污染。"
}
```
