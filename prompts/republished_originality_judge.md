# 转载内容原创增量评估 Prompt

## 任务

判断页面是否为转载内容 + 原创增量百分比。

## 输入

- `visible_text`: 我方页面可见文字
- `canonical_url`: 我方页面 canonical
- `external_source_url`: 外部来源 URL（如有）
- `source_article_text`: 原文文本（如能抓到）

## 判定流程

1. **是否为转载**：
   - 检测 source link / "Source:" / "Originally published" 等信号
   - 主体内容与原文相似度（80%+ = 转载）

2. **原创增量评估**（如转载）：
   - 我方新增段落比例
   - 我方编辑评审 / 风险边界 / 事实核验段落
   - 是否补充原作者 bio 和来源透明度
   - FAQ / 目录 / 衍生内容

3. **判定阈值**：
   - 增量 < 20% + self-canonical = blocker
   - 增量 20-50% = high
   - 增量 ≥ 50% = pass

## 输出 JSON 示例

```json
{
  "rule_id": "platform.l01.republished-content-low-increment",
  "severity": "blocker",
  "confidence": 0.88,
  "evidence": {
    "is_republished": true,
    "source_url": "https://blockchainreporter.net/...",
    "main_content_similarity": 0.92,
    "originality_increment_pct": 12,
    "missing_signals": ["原作者 bio", "我方编辑评审", "FAQ", "风险提示"]
  },
  "recommendation": "三选一：(1) noindex (2) cross-domain canonical 到原文 (3) 补足原创增量 ≥ 50%",
  "reasoning": "页面 92% 内容与原文相同，且 self-canonical。仅 12% 是 Platform 新增。"
}
```
