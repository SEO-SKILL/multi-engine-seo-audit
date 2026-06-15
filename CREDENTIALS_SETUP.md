# 凭证申请清单（按优先级）

> 11 个凭证 / 6 个网站 / 估计总时长 30 分钟

---

## 🔥 P0 必须配（解锁 LLM 能力）

### 1. ANTHROPIC_API_KEY
- **注册**：https://console.anthropic.com/
- **路径**：Login → API Keys → Create Key
- **成本**：按 token 付费（约 $0.02/audit）
- **充值**：建议先充 $20 测试
- **导出**：`export ANTHROPIC_API_KEY="sk-ant-api03-..."`

---

## 🟠 P1 强烈推荐（解锁真实业务数据）

### 2. GSC_SERVICE_ACCOUNT_JSON（Google Search Console）
- **注册**：
  1. https://console.cloud.google.com/iam-admin/serviceaccounts （创建 service account）
  2. 给该 service account 下载 JSON key
  3. https://search.google.com/search-console → 设置 → 用户和权限 → 添加 service account email 为 "全部" 权限
- **成本**：免费
- **导出**：`export GSC_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'`

### 3. GA4_SERVICE_ACCOUNT_JSON + GA4_PROPERTY_ID
- **注册**：同上（重用 GSC service account）
  1. GA4 → 管理 → 资源访问权限管理 → 添加 service account email 为 "查看者"
  2. 资源 ID 在 GA4 → 管理 → 资源详情
- **成本**：免费
- **导出**：
  ```bash
  export GA4_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
  export GA4_PROPERTY_ID="123456789"
  ```

### 4. PLATFORM_SLACK_WEBHOOK
- **注册**：
  1. Slack workspace → Apps → Incoming Webhooks
  2. https://api.slack.com/messaging/webhooks
  3. 选择频道（如 `#seo-alerts`）→ 复制 webhook URL
- **成本**：免费
- **导出**：`export PLATFORM_SLACK_WEBHOOK="https://hooks.slack.com/services/T.../B.../..."`

---

## 🟡 P2 按需配置

### 5. CLOUDFLARE_API_TOKEN
- **注册**：https://dash.cloudflare.com/profile/api-tokens → Create Token
- **权限**：`Account:Logs:Read` + `Zone:Logs:Read`
- **成本**：Cloudflare 免费版可读 log（24h 内）
- **导出**：`export CLOUDFLARE_API_TOKEN="..."`

### 6. PERPLEXITY_API_KEY（GEO 真测试）
- **注册**：https://www.perplexity.ai/settings/api
- **成本**：约 $5/月起步
- **导出**：`export PERPLEXITY_API_KEY="pplx-..."`

### 7. DATAFORSEO_API_KEY（真实 SERP 数据）
- **注册**：https://dataforseo.com → Sign Up
- **替代**：https://serper.dev（更便宜，$50/100k 查询）
- **成本**：$50-100/月
- **导出**：`export DATAFORSEO_API_KEY="..."`

---

## 🟢 P3 可选（V2 后期）

### 8. AHREFS_API_TOKEN
- **注册**：https://ahrefs.com → 付费订阅 + 申请 API access
- **成本**：$500+/月（昂贵）
- **替代**：先用 CSV 导出（免费），跑 `compare` 命令时手动导入

### 9. OPENAI_API_KEY（Cross-LLM 验证）
- **注册**：https://platform.openai.com/api-keys
- **成本**：按 token 付费
- **用于**：cross_llm-agent 真接 GPT

### 10. GOOGLE_AI_API_KEY（Gemini）
- **注册**：https://aistudio.google.com/apikey
- **成本**：免费额度大
- **用于**：cross_llm-agent 真接 Gemini

### 11. GSC_OAUTH_TOKEN
- **注册**：作为 service account 替代方案，更适合个人用户
- **跳过**：用 #2 service account 即可

---

## 🎯 最低配（5 分钟）

只配这 2 个就能解锁 80% 能力：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."           # 解锁 LLM judges
export PLATFORM_SLACK_WEBHOOK="https://hooks..."   # 解锁告警

uv run python cli.py doctor    # 验证
```

---

## 🚀 推荐组合（30 分钟全配）

```bash
# 必配
ANTHROPIC_API_KEY      ← 5 min
PLATFORM_SLACK_WEBHOOK    ← 3 min

# 强推
GSC_SERVICE_ACCOUNT_JSON ← 10 min（含给 GSC 加权限）
GA4_SERVICE_ACCOUNT_JSON ← 5 min（复用 GSC）
GA4_PROPERTY_ID          ← 1 min

# 可选
CLOUDFLARE_API_TOKEN     ← 3 min
GOOGLE_AI_API_KEY        ← 3 min（免费）

总计 ≈ 30 分钟 → 解锁 100% 能力
```
