# Platform Google 人工处置案例库

> 创建：2026-06-10
> 维护：kelly@example.com
> 用途：积累每次 Platform 被 Google 处置或近处置的案例，反向沉淀为规则
> 引用方式：每条案例对应 `rules/platform/` 下的具体规则

---

## 案例索引

| 案例 ID | 时间 | 严重程度 | 触发原因 | 对应规则 |
|---|---|---|---|---|
| PLATFORM-2026Q1-001 | 2026-Q1 | 已被处置 | 转载 + ticker 误识别 + schema 错配 | platform.l02.* / platform.l03.* / platform.l04.* |

---

## PLATFORM-2026Q1-001：案例页面被 Google 人工处置

### 一句话描述

Platform 转载 原始来源媒体 文章发到 `/news/{id}`，因「转载缺原创增量 + ticker 误关联 + schema 内容错配 + hreflang 冲突」综合触发 Google 人工处置。

### 时间线

- T-0：原始来源媒体 发布原文
- T+N：Platform 转载到 `/en/news/1057200`，移除作者 bio / FAQ / 部分外链
- T+N+M：Google 抓取后判定低增量
- T+N+M+P：Google 人工处置
- 复盘日期：2026-Q1 内部

### 7 类问题（事故口径 byd-google-seo-final-review）

#### 高 1：转载内容缺少足够原创增量

**Issue**：某加密交易所案例 页主体几乎是 原始来源媒体 原文转载，只保留来源链接，但移除了原文的人类作者、作者 bio、FAQ、目录和部分外链来源。

**Why**：Google 对金融/科技/收益相关内容更看重 E-E-A-T、来源、责任归属和独特价值。单纯转载且 self-canonical，容易被判为低增量内容。

**Fix**：二选一：
- 要么 `noindex` 或 cross-domain canonical 到原文
- 要么补 某加密交易所案例 自有编辑评审、摘要、风险边界、事实核验、原作者信息和独立增量段落

**对应规则**：`platform.l01.republished-content-low-increment`（待写）

#### 高 2：自动识别 "PROS" 导致主题错配

**Issue**：页面标题里的 "Pros and Cons" 被关联成 Pharos PROS，出现 PROS 行情卡、Buy PROS Now、relatedLink 到 PROS 价格页。

**Why**：让 Google 和用户把"Techsslaash 评测"误读成 Pharos 代币内容，内部链接语义污染重。

**Fix**：
- 对新闻正文的 ticker 自动识别加白名单/上下文判断
- 本页移除 PROS 行情组件、PROS 交易入口和 schema 里的 PROS relatedLink

**对应规则**：`platform.l02.ticker-context-mismatch` ✅（已写 in `pros-ticker-blacklist.yaml`）

#### 高 3：hreflang 与 robots/canonical 信号冲突

**Issue**：主页面输出大量 alternate，例如 `/en-TR/news/1057200`、`/bg-BG/news/1057200`，但 robots.txt 又禁止多个本地化 news 路径；抽样还发现部分 alternate 返回 404，部分语言页内容仍是英文。

**Why**：Google 需要能抓取 hreflang alternate，并看到互相一致的 canonical/语言信号；否则 hreflang 会被忽略，严重时造成重复页和错误地区版本。

**Fix**：只输出真实存在、可抓取、可索引、语言匹配的 alternate；被 robots 禁止或 404 的语言版本不要出现在 hreflang 中。

**对应规则**：`google.hreflang.consistency` ✅（已写 in `_rules/hreflang.yaml`）

#### 中 1：结构化数据不反映页面真实内容

**Issue**：渲染后有 NewsArticle JSON-LD，但 raw HTML 中没有；schema 里还塞了 某加密交易所案例 App 的 AggregateRating，页面可见内容并不是 某加密交易所案例 App 评价。copyrightNotice 邮箱也和页面可见邮箱不一致。

**Why**：Google 要求结构化数据反映用户可见内容。错误 rating 和不一致声明会降低富结果资格，严重时有结构化数据人工处置风险。

**Fix**：
- 删除与本页无关的 AggregateRating
- 补 image、真实来源 URL、正确 author/source
- 让 JSON-LD SSR 输出，并与页面可见文案一致

**对应规则**：`google.schema.truthfulness` ✅（已写 in `_rules/structured-data-truthfulness.yaml`）

#### 中 2：分类标签明显不准

**Issue**：页面标签是 SEC、Lending，而原文标签是 AI，正文主题是 Techsslaash/fintech/creator platform/SEO guest posts。

**Why**：标签页和内部推荐会把页面放进错误主题簇，削弱站内架构相关性。

**Fix**：改成 AI、Fintech、Tech Review、Guest Posting 这类真实主题标签。

**对应规则**：`platform.tagging.topic-mismatch`（待写）

### 必须修

- noindex/canonical 策略
- PROS 误识别
- hreflang/robots 冲突
- 结构化数据误导字段

### 建议修

- 补原作者与来源透明度
- 恢复 FAQ/目录或加入 某加密交易所案例 自有编辑增量
- 修正标签

### 可忽略

- Title/H1/description 本身可用，不是当前主要问题

### Final Verdict

**暂不上线**。

---

## 行业案例（其他公司被处置案例，用于学习避坑）

> 持续收集 某加密交易所案例 / Bybit / KuCoin / Crypto.com 等同行公开的 Google 处置案例

### 模板

```
案例 ID：INDUSTRY-{年}-{编号}
公司：
时间：
触发原因：
公开来源：
对 Platform 的启示：
对应规则：
```

---

## 沉淀规则

每次新增案例必须：

1. 写完整时间线
2. 拆解触发原因
3. 找到（或新建）对应规则
4. 在 `rules/platform/` 里写 YAML 规则
5. 在 `lessons.md` 里写 lesson
6. 在 `fixtures/` 里加 golden test fixture
