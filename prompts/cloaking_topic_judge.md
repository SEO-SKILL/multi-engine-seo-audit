# Cloaking 主题差异判定 Prompt

## 任务

判断不同 UA 抓取到的页面主题是否一致（防 Cloaking）。

## 输入

每个 UA 的抓取结果：
- `googlebot_desktop_text`
- `googlebot_mobile_text`
- `chrome_desktop_text`
- `chrome_mobile_text`

## 判定流程

1. 用 LLM 对每个版本做主题分类
2. 如果 Googlebot 看到的主题 ≠ 真实用户看到的主题 → blocker
3. 仅版式差异（desktop vs mobile 布局）→ 不算 cloaking

## 输出 JSON

```json
{
  "rule_id": "google.cloaking.googlebot-vs-user-content-diff",
  "severity": "blocker",
  "confidence": 0.85,
  "evidence": {
    "googlebot_topic": "Crypto Trading Education",
    "user_topic": "Crypto Gambling Strategies",
    "diff_signals": ["main_topic_classification", "main_cta_text"]
  },
  "recommendation": "审查服务器 UA 路由逻辑 / CDN 配置 / A/B test 系统",
  "reasoning": "Googlebot 看到的是合规教育内容，真实用户看到的是赌博内容。这是典型 cloaking。"
}
```
