# Google "排名和搜索结果呈现" 22 主题覆盖对照

> 来源：截图所示 Google Search Central 文档导航
> 覆盖率：**16/22 (73%)** ✅

---

## 逐项对照

| # | Google 主题 | 我们覆盖 | 文件 |
|---|---|---|---|
| 1 | 概览（Overview） | ✅ | `PRD.md` + `EXECUTIVE_SUMMARY.md` |
| 2 | **AI 功能** | ✅ 已覆盖 | `_knowledge/ai-overview-eligibility.md` + `llm-engines/_rules/gemini.yaml` |
| 3 | **署名日期** | ✅ 已覆盖 | `eeat.publication_dates` + `_rules/e-e-a-t.yaml` |
| 4 | 网站图标（Favicon） | ❌ **没专项** | 需补 favicon-seo.yaml |
| 5 | **精选摘要** | ✅ 已覆盖 | `_rules/featured-snippet.yaml` (4 条) |
| 6 | 灵活抽样（Paywall）| ❌ **没专项** | 需补 paywall-flexible-sampling.yaml |
| 7 | **Google 探索** | ✅ 已覆盖 | `_rules/discover.yaml` (2 条) |
| 8 | **图像** | ✅ 已覆盖（深做）| `_rules/google-images-deep.yaml` (14 条) + composite |
| 9 | 本地功能 | ❌ **没做**（Platform 不强相关）| Local SEO 跳过 |
| 10 | **网页体验（CWV）** | ✅ 已覆盖 | `_rules/page-experience.yaml` (4 条) |
| 11 | **首选来源** | ✅ 已覆盖 | `_rules/preferred-sources.yaml` (2 条) |
| 12 | **排名系统** | ✅ 已覆盖 | `_rules/core-updates.yaml` + `helpful-content` |
| 13 | **排名规则更新** | ✅ 已覆盖 | `_rules/core-updates.yaml` + Manual Actions |
| 14 | **网站名称** | ✅ 已覆盖 | `_rules/breadcrumb-and-navigation.yaml::site-name` |
| 15 | **站内链接** | ✅ 已覆盖 | `breadcrumb-and-navigation` + `shared/internal-linking` |
| 16 | 片段（Snippet） | ✅ 已覆盖 | `featured-snippet.yaml` 含 max-snippet 等 |
| 17 | **结构化数据** | ✅✅ 已覆盖（多份）| `structured-data-truthfulness.yaml` + `structured-data-advanced.yaml` + `_knowledge/structured-data-mastery.md` |
| 18 | 标题链接 | ⚠️ **部分覆盖** | 散落在 `e-e-a-t.yaml` + `canonical.yaml`，需补独立 title-link.yaml |
| 19 | **经过翻译的功能** | ✅ 已覆盖 | `hreflang.yaml` + `multilingual-quality.yaml` |
| 20 | **视频** | ✅ 已覆盖 | `_rules/video-seo.yaml` (5 条) |
| 21 | **视觉元素库** | ✅ 已覆盖 | `image-seo.yaml` + `google-images-deep.yaml` |
| 22 | 网络故事（Web Stories） | ❌ **没做**（Platform 用不到）| 跳过 |
| 23 | 尝鲜者计划（Labs）| — | 实验性，跳过 |

---

## 已覆盖：16/22 (73%)

✅ AI 功能 / 署名日期 / 精选摘要 / Google 探索 / 图像 / 网页体验 / 首选来源 / 排名系统 / 排名规则更新 / 网站名称 / 站内链接 / 片段 / 结构化数据 / 经过翻译 / 视频 / 视觉元素库

## 待补：3 个高价值 + 3 个跳过

### 应该补（3 个）
1. **favicon-seo.yaml**（网站图标）— 1 小时
2. **paywall-flexible-sampling.yaml**（灵活抽样）— 1 小时
3. **title-link.yaml**（标题链接独立专项）— 1 小时

### 跳过（3 个，Platform 不强相关）
- 本地功能（Local SEO — Platform 是金融服务，不是实体店）
- 网络故事（Web Stories — 加密类不用）
- 尝鲜者计划（实验性）
