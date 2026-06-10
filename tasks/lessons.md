# BYDFi SEO Audit Skill — 经验沉淀

> 按 CLAUDE.md「Self-Evolution Loop」规范：每次用户纠错或踩坑后立即记录。
> 创建：2026-06-10

---

## 起点教训（来自资料）

### L01 — 转载内容必须有原创增量

**触发场景**：MEXC 页面转载 BlockchainReporter 原文，移除作者 bio / FAQ / 目录 / 部分外链，但保留 self-canonical。

**Why**：Google 对金融 / 科技 / 收益类内容更看重 E-E-A-T、来源、责任归属和独特价值。单纯转载且 self-canonical 容易被判低增量内容。

**How to apply**：
- 检测 canonical 是否指向自身但内容来自外站
- 计算正文与原文语义相似度
- 相似度 > 80% 必须给 cross-domain canonical 或 noindex 建议
- 或要求补 BYDFi 自有编辑评审、风险边界、事实核验、独立增量段落

---

### L02 — Ticker 自动识别必须有上下文判断

**触发场景**："Pros and Cons" 中的 PROS 被自动关联成 Pharos PROS 代币，出现 PROS 行情卡 / Buy PROS Now / relatedLink。

**Why**：让 Google 和用户把"Techsslaash 评测"误读成 Pharos 代币内容，内部链接语义污染重。

**How to apply**：
- 维护 ticker 白名单 + 黑名单（`rules/bydfi/sensitive-tickers.yaml`）
- 对新闻正文里的 ticker 自动识别加上下文判断（语义解析整段，不是单词匹配）
- BYDFi 文章页禁用未在白名单的 ticker 行情组件
- schema 里的 relatedLink 必须经过语义校验

---

### L03 — hreflang 与 robots/canonical 必须一致

**触发场景**：主页面输出 `/en-TR/news/1057200` 等 alternate，但 robots.txt 禁止多个本地化 news 路径，部分 alternate 还返回 404，部分语言页内容仍是英文。

**Why**：Google 需要能抓取 hreflang alternate，并看到互相一致的 canonical/语言信号；否则 hreflang 被忽略，严重时造成重复页和错误地区版本。

**How to apply**：
- 只输出真实存在、可抓取、可索引、语言匹配的 alternate
- 被 robots 禁止或 404 的语言版本不要出现在 hreflang
- 自动校验：每个 alternate URL 实际抓取 → 状态码 + 语言识别

---

### L04 — Schema 字段必须反映页面真实内容

**触发场景**：渲染后有 NewsArticle JSON-LD 但 raw HTML 中没有；schema 里塞 MEXC App 的 AggregateRating 但页面没有评分；copyrightNotice 邮箱与页面可见邮箱不一致。

**Why**：Google 要求结构化数据反映用户可见内容。错误 rating 和不一致声明降低富结果资格，严重时有结构化数据人工处置风险。

**How to apply**：
- JSON-LD 每个字段都去页面可见内容里找证据
- AggregateRating 必须对应可见评价区
- author / publisher / date 必须 raw HTML SSR 输出
- JSON-LD 不能只在 CSR 后才出现

---

### L05 — 分类标签必须真实反映正文主题

**触发场景**：页面标签 SEC / Lending，原文标签 AI，正文主题是 Techsslaash / fintech / creator platform / SEO guest posts。

**Why**：标签页和内部推荐把页面放进错误主题簇，削弱站内架构相关性。

**How to apply**：
- 标签自动生成必须基于正文语义聚类，不是 ticker 匹配
- 标签库需要维护白名单
- 编辑工作流加 tag review 卡审

---

### L06 — Google 处置成本远高于 SEO 失败

**触发场景**：MEXC 页面已是 200 + index, follow + self-canonical，但内容质量问题导致 Google 人工处置。

**Why**：技术 SEO 正常 ≠ 内容 SEO 正常。Google 处置一次，恢复成本可能是几个月 + 全站权重下降。

**How to apply**：
- Pre-publish Gate 必须是硬卡口，不是建议
- 任何"暂不上线"的判定必须有 owner 拍板才能 override
- 历史处置案例必须沉淀到 `rules/bydfi/google-action-history.md`

---

## 待积累区（V1 上线后填）

### 来自 BYDFi 真实页面审核
（W4 后开始填）

### 来自 Codex 协作踩坑

#### LE01 — Codex usage quota 是硬约束，不要假设无限可用

**触发场景**：W1 Day 1 让 Codex 跑工程骨架，第一次任务跑到 195 秒就报 "usage limit, try again Jul 10"。

**Why**：Codex 使用的是付费 quota，与 Claude 不同的预算池。CLAUDE.md 「Claude+Codex 分工」流程默认 Codex 可用，但实际有 quota 上限。

**How to apply**：
- 重大 Codex 任务前先确认 quota
- Codex 跑不动时不要硬等，Claude 直接接手骨架级工作
- 关键设计文档 / 元规则 / 知识层文档 → Claude 写
- 实际业务代码 / 重复性 / 大量样板 → Codex 写（quota 允许时）
- 长任务拆小：单次任务 ≤ 30 分钟 quota 消耗

### 来自用户反馈
（V1 上线后填）

### 来自 Will 知识库对比研究

#### LE02 — 静态文档 ≠ 可执行规则

**触发场景**：研究 Will 团队 Google SEO 知识库（76 份 MD / 324KB），发现质量高但全是给人读的文字描述。

**Why**：人工 SOP 文档 vs 机器可执行规则之间有"工程鸿沟"。Will 写"页面应有 SSR 内容"是给人提示，我们需要 detector function + threshold + fixture 才能跑。

**How to apply**：
- 任何规则都必须能 detector function 化
- 文字描述（_knowledge/*.md）作为 prompt context 喂 LLM
- 结构化规则（_rules/*.yaml）作为硬规则跑
- 两者通过 rule.id 关联

#### LE03 — Will 团队是 benchmark to beat，不是 dependency

**触发场景**：本想 fork Will 知识库到 skill 内，被 Kelly 否决——Will 后续要用我们的 skill，我们必须比他做的好才能让他切换。

**Why**：差异化产品价值在于"比现有方案好"。如果只是消费 Will 的输出，Will 没有理由切换。

**How to apply**：
- 不消费 Will 知识库
- 参考他的结构 + 主题覆盖 + BYDFi 业务对齐方式
- 必须在他没覆盖的维度做（Naver / GEO / Cloaking / Web3 / 跨 LLM / 时间序列）
- 必须在他覆盖的维度做得更深（每条规则带 detector + fixture + patch hint）

---

## 沉淀规则

1. **每次踩坑必须记录**：哪怕只是一行字，胜过下次重犯
2. **必含三段式**：触发场景 / Why / How to apply
3. **关联到代码**：明确指向哪个 sub-agent / rule 文件
4. **季度回顾**：每季度 review，把高频 lesson 升级为硬规则

---

## W1 复盘（2026-06-10）

### W1 完成

- ✅ Phase 0 启动（PRD / config / SKILL / todo / lessons）
- ✅ Codex 调研报告（37KB / 713 行）
- ✅ 5 项决策固化（PRD v1.1）
- ✅ Will 知识库对照战略（PRD v1.2 + COMPARISON_WITH_WILL.md）
- ✅ 4 个元规则文件落地（rule-schema / severity / confidence / conflict-resolution）
- ✅ 12 条结构化业务规则落地（含 MEXC 事故 7 类全覆盖）
- ✅ 1 篇 self-knowledge 文档（helpful-content-eat.md，超越 Will 版本）

### W1 数据

- 规则文件数：10 份 YAML + 2 份 MD = 12 份
- 规则条目数：~50 条结构化规则（V1 目标 300+ 的 ~17%）
- 平台覆盖：Google + Naver + LLM engines（5 个 V1 平台中的 3 个）
- 代码量：0（W1 全部是规则 + 文档，符合规划）

### W1 经验

- LE01：Codex quota 是硬约束
- LE02：静态文档 ≠ 可执行规则
- LE03：Will 是 benchmark，不是 dependency

### W2 计划

- Bing / Yandex 平台规则库初始化
- shared/ 通用规则（technical-baseline / url-health / sitemap-quality）
- 写更多 _knowledge/ 自研知识 MD
- Codex quota 恢复 → 启动工程骨架
- 准备 5 个 golden fixture 的 HTML 文件
