# Naver 韩文本地化质量评估

## 任务

判断韩文内容是否真本地化（vs 机翻）。

## 输入

- `visible_text` (Korean)
- `machine_translation_signals`: 机翻特征检测

## 红牌信号

- 直译痕迹（"为了" → 위해서 用法不自然）
- 量词使用错误（韩文有特殊量词）
- 名词中文化（"交易所" 写成 "交易所" 而不是 "거래소"）
- 敬语等级混用（습니다/해요/한다 混用）
- 缺韩国本地化引用（无 KRW / 韩国法规 / 韩国生态）

## 必备信号

- 韩国本地货币 KRW 提及
- 韩国监管 / 法规相关说明（如必要）
- 韩国用户语境（"한국 사용자")

## 输出 JSON

```json
{
  "rule_id": "naver.crank.korean-content-authenticity",
  "severity": "blocker",
  "confidence": 0.85,
  "evidence": {
    "red_flags": ["机翻痕迹明显", "缺 KRW", "敬语混用"],
    "missing_signals": ["KRW", "Korean regulatory context"],
    "sample_problematic_sentences": ["...", "..."]
  },
  "recommendation": "请韩国本地编辑团队重写，不要依赖机翻",
  "reasoning": "Naver 完全无法容忍机翻韩文 → 不参与排名"
}
```
