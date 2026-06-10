# E-E-A-T 作者信号判定

## 任务

判断作者信号是否满足 YMYL 标准。

## 输入

- `jsonld`: 解析后 JSON-LD（含 author）
- `visible_text`
- `dom_metadata`: byline / author profile link 等

## 必备信号（任一缺失即 finding）

YMYL 必备（≥ 1 套）：
- 套 1: jsonld.author.name + jsonld.author.url
- 套 2: visible_byline + clickable_author_profile_page
- 套 3: meta[name=author] + 作者历史内容

YMYL 加强（建议）：
- 作者 bio 段落
- 作者资质（如 "CFA / SEC 注册 / 法律顾问"）
- 利益冲突声明
- LinkedIn / Twitter 真实身份

## 输出 JSON

```json
{
  "rule_id": "google.eeat.author-attribution-missing",
  "severity": "high",
  "confidence": 0.92,
  "evidence": {
    "ymyl_signals_found": [],
    "ymyl_signals_missing": ["author.name", "author.url", "author_bio"]
  },
  "recommendation": "添加作者元数据 + 作者 profile 页 + bio 段落",
  "reasoning": "金融 YMYL 内容缺作者署名 = E-E-A-T 信号弱"
}
```
