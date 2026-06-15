# Manon（燕子）SEO 整改工作流

> 给 Will 团队的 SEO 工程师 Manon 用的入门指南
> 完全非技术 · 浏览器操作 · Lark 云文档兼容
> 创建：2026-06-11

---

## 🎯 你要做的事

按 Will 的要求：
1. 用我们的 skill 跑 BYDFi 线上页面
2. 看分析结果
3. 准备 Google 问题的修改方案
4. 导出 Lark 云文档继续协作

---

## 🚀 3 步上手（浏览器操作）

### Step 1: 打开 Dashboard

部署完成后，访问：

```
https://bydfi-seo-audit.fly.dev
```

（在 Kelly 部署前可访问本地：http://localhost:8080）

### Step 2: 一键跑 BYDFi 核心 8 页

点击页面上紫色按钮：**🚀 跑 BYDFi 8 个核心页**

30-60 秒后你会看到一张表格：

| 页面 | Score | Verdict | B / H / M |
|---|---|---|---|
| Homepage (EN) | 78 | 上线 | 0 / 0 / 2 |
| Homepage (KO) | 78 | 上线 | 0 / 0 / 2 |
| Homepage (JA) | 78 | 上线 | 0 / 0 / 2 |
| Homepage (RU) | 78 | 上线 | 0 / 0 / 2 |
| Futures | **58** ⚠️ | 上线 | 0 / 0 / 4 |
| Learn Center | 78 | 上线 | 0 / 0 / 2 |
| Price/BTC | 78 | 上线 | 0 / 0 / 2 |
| Support | **88** ✅ | 上线 | 0 / 0 / 1 |

> **B / H / M** = Blocker / High / Medium 数量

### Step 3: 重点关注分数低的页

把分数最低的页面 URL 复制到上方输入框 → 选 locale → 点 **▶ Run Audit**

详细 audit 会显示：
- 🎯 优先级行动计划（按 ROI 排序）
- 🔍 完整 Findings（每条可展开看完整修复指南）

---

## 📋 导出到 Lark 云文档

跑完单页 audit 后，点击 **📋 导出 Lark Markdown** 按钮：

1. 下载 `.md` 文件到本地
2. 打开 Lark 云文档 → 新建文档
3. **复制整个 Markdown 内容 → 粘贴**
4. Lark 自动渲染（表格 / 代码块 / 列表全部支持）

导出的文档结构：

```
# BYDFi SEO 深度分析与整改方案

## 📊 总体结论
- Brand SEO Score
- Final Verdict
- Findings 数量

## 📊 8 维度 Composite Scores（表格）

## 🎯 优先级行动计划
### Phase 1: 修复 XXX
- Severity / ROI / 工时
- 修复建议
- 对 BYDFi 影响

## 🔍 完整 Findings 详情
### 每个 finding 含：
- 修复步骤（含 before/after 代码）
- 验证方式
- 工时估算
- 预期效果
- 参考文档链接
```

---

## ❓ 看不懂某条 finding？

每条 finding 在 dashboard 中**点击展开**，会显示：

| 字段 | 含义 |
|---|---|
| 问题 | 具体什么问题（一句话）|
| 为什么 | 为什么 Google 看重 |
| 修复步骤 | 1-4 步，含改前/改后代码 |
| 如何验证 | 修完怎么确认成功 |
| 工时 | 估算多少分钟 |
| 预期效果 | 修完 Score 上升多少 |
| 相关问题 | 建议一起修的关联问题 |
| 参考 | Google 官方文档链接 |

---

## 🔥 当前 BYDFi 最大问题（基于真实 audit）

| 维度 | 当前分 | 应到 | 工时 | 价值 |
|---|---|---|---|---|
| **E-E-A-T** | **0.04** 🔴 | 0.80+ | 5 天 | **+33% 流量 / 年化 $146K** |
| **GEO** | **0.34** 🔴 | 0.70+ | 4 天 | +12% 流量 |
| Performance | 0.65 🟡 | 0.85 | 3 天 | +3% 流量 |
| Image | 0.75 🟡 | 0.95 | 2 天 | +2% 流量 |

**🎯 P0 优先修的就是 E-E-A-T（缺作者 / 缺审核 / 缺日期 / 缺来源）**

---

## 📚 完整文档导航

| 想看 | 看哪份 |
|---|---|
| **整改方案（基于真实数据）** | `BYDFI_REMEDIATION_PLAN.md` |
| **增长机会量化（CTO 看）** | `snapshots/growth-opportunity-*.md` |
| **覆盖了哪些 Google 主题** | `GOOGLE_RANKING_COVERAGE.md` |
| **我们 vs Will 知识库** | `COMPARISON_WITH_WILL.md` |
| **Manual Action 防复发 SOP** | `rules/platforms/google/_knowledge/manual-actions-reconsideration.md` |

---

## 🤝 反馈给规则库

你跑的过程中如果发现：

### ✅ 规则准了
```
（无需操作 — 自动累积准确度）
```

### ❌ 规则误报
浏览器打开：http://localhost:8080/api/feedback?rule_id=XXX&verdict=false_positive

或跑命令：
```bash
uv run python cli.py feedback "bydfi.l02.ticker-context-mismatch" false_positive --notes "误报原因"
```

我们的规则库会自动校准 confidence。

---

## 🆘 遇到问题

| 问题 | 怎么办 |
|---|---|
| Dashboard 打不开 | 看 Kelly 是否已 deploy |
| 跑某 URL 报错 | 跟 Kelly 说 trace_id |
| 不知道哪条规则是真问题 | 看 severity (blocker > high > medium > low) |
| Will 想要的"整改方案"长啥样 | 跑 audit → 导出 Markdown → 给 Will |

---

## 💡 给 Will 团队的协同建议

| 你（Manon）做 | 我们 Skill 做 |
|---|---|
| 跑 audit → 看 finding | 自动检测 371 条规则 |
| 验证 finding 是不是真问题 | 提供 evidence + bydfi 影响 |
| 把"整改方案"录入 Lark | 一键导出 Lark 兼容 Markdown |
| 跟工程团队对接修复 | 提供 patch 模板 + 代码示例 |
| 复盘修复效果 | 重新 audit 自动出对比 |

---

*Skill: `~/.claude/skills/seo-audit/` · Owner: Kelly Chen · Updated: 2026-06-11*
