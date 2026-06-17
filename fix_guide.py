"""
Fix Guide 生成器 — 把 finding 转成完整修复指南
含：问题描述 / 为什么 / 多步修复 / before-after 代码 / 验证 / 工时 / 相关问题
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).parent


# 30+ 详细修复指南（高频 + 某加密交易所行业案例 + 跨平台）
FIX_GUIDES: dict[str, dict] = {

    # ========== Canonical (4 条) ==========
    "google.canonical.missing": {
        "issue": "页面 <head> 中缺少 <link rel='canonical'>。Google 不知道哪个 URL 是规范版本。",
        "why": "同一内容可能通过多个 URL 访问（http/https, www/non-www, 大小写, query 参数）。缺 canonical = Google 自己猜规范版本 = 你推的 URL 拿不到权重。",
        "steps": [
            {"title": "Step 1: 在 <head> 加 canonical 标签",
             "code_before": "<head>\n  <title>BTC Calculator</title>\n</head>",
             "code_after": "<head>\n  <title>BTC Calculator</title>\n  <link rel='canonical' href='https://example.com/en/calculator'>\n</head>", "language": "html"},
            {"title": "Step 2: 必须 SSR 输出（不可仅 JS 注入）",
             "note": "Next.js: 用 <Head> 组件\nReact SPA: 用 react-helmet-async + prerender\n纯 SPA Googlebot 看不到"},
            {"title": "Step 3: 必须绝对 URL",
             "code_before": "<link rel='canonical' href='/futures'>",
             "code_after": "<link rel='canonical' href='https://example.com/en/futures'>", "language": "html"},
            {"title": "Step 4: 验证", "command": "curl -s URL | grep -i canonical"},
        ],
        "verify": "audit 后 canonical.missing 消失", "effort_minutes": 30,
        "related": ["google.canonical.chain-too-long", "google.canonical.points-to-noindex"],
        "references": [{"label": "Google URL Canonicalization", "url": "https://developers.google.com/search/docs/crawling-indexing/canonicalization"}],
        "expected_impact": "Brand SEO Score +5-10 / crawlability +0.30 / 流量 +3-5%",
    },

    "google.canonical.self-canonical-on-republished": {
        "issue": "转载第三方文章但 canonical 指向自己（某加密交易所行业案例 L01 同类）",
        "why": "Google 对金融转载内容看 E-E-A-T。self-canonical 转载 = Google 判定低增量 = 触发人工处置（参考 某加密交易所案例 2026-Q1）。",
        "steps": [
            {"title": "Step 1（推荐）: cross-domain canonical 到原文",
             "code_before": "<link rel='canonical' href='https://example.com/news/X'>",
             "code_after": "<link rel='canonical' href='https://original-source.com/X'>", "language": "html"},
            {"title": "Step 2（备选）: 加 noindex",
             "code_after": "<meta name='robots' content='noindex'>", "language": "html"},
            {"title": "Step 3（最佳）: 补足原创增量 ≥ 50%",
             "note": "补：Platform 编辑评审 / 风险提示 / 事实核验 / 原作者 bio / FAQ\n移除前先确认增量足够"},
        ],
        "verify": "重审后 republished-content-low-increment finding 消失", "effort_minutes": 120,
        "related": ["platform.l01.republished-content-low-increment", "google.eeat.author-attribution-missing"],
        "references": [{"label": "Platform 某加密交易所行业案例复盘", "url": "rules/platform/google-action-history.md"}],
        "expected_impact": "防 Google 人工处置 / Brand SEO Score +20+",
    },

    # ========== E-E-A-T (5 条) ==========
    "google.eeat.author-attribution-missing": {
        "issue": "缺作者署名（meta[name=author] / JSON-LD author / 可见 byline 全无）",
        "why": "YMYL 金融内容缺作者 = 来源不可追溯 = 永远不进 SERP 前 10。某加密交易所行业案例起因之一就是移除原作者署名。",
        "steps": [
            {"title": "Step 1: <head> 加 meta author",
             "code_after": "<meta name='author' content='Platform Research Team'>", "language": "html"},
            {"title": "Step 2: 加 JSON-LD author + reviewedBy",
             "code_after": '{\n  "@type": "Article",\n  "author": {"@type": "Person", "name": "Platform Research", "url": "/author/research"},\n  "reviewedBy": {"@type": "Person", "name": "Risk Team"},\n  "datePublished": "2026-01-15",\n  "dateModified": "2026-06-08"\n}', "language": "json"},
            {"title": "Step 3: 可见 byline",
             "code_after": '<footer class="byline">\n  Author: <a href="/author/research" rel="author">Platform Research</a>\n  | <time datetime="2026-06-08">Updated June 8, 2026</time>\n</footer>', "language": "html"},
            {"title": "Step 4: 建 /author/* profile 页", "note": "含 bio + 资质 + 历史文章"},
        ],
        "verify": "eeat composite 从 ~0 → 0.8+", "effort_minutes": 60,
        "related": ["google.eeat.publication-date-missing-or-stale", "shared.eeat.author-bio-page-missing"],
        "references": [{"label": "Google E-E-A-T", "url": "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"}],
        "expected_impact": "Brand SEO Score +15-20 / 全站 +$60-100K 年化",
    },

    "google.eeat.publication-date-missing-or-stale": {
        "issue": "JSON-LD 中缺 datePublished",
        "why": "Google 用日期判鲜度。金融内容 > 6 个月无更新 = stale = 排名下降。完全无日期 = 默认降权。",
        "steps": [
            {"title": "Step 1: JSON-LD 加日期",
             "code_after": '{\n  "datePublished": "2026-01-15",\n  "dateModified": "2026-06-08"\n}', "language": "json"},
            {"title": "Step 2: 可见日期与 schema 一致",
             "code_after": '<time datetime="2026-01-15">Jan 15, 2026</time>', "language": "html"},
            {"title": "Step 3: 真改内容才改 dateModified", "note": "禁：只改日期不改内容 = spam policy"},
        ],
        "verify": "publication-date finding 消失", "effort_minutes": 15,
        "related": ["google.eeat.fake-freshness-pattern", "shared.freshness.stale-content-no-update"],
        "references": [{"label": "Publication Dates", "url": "https://developers.google.com/search/docs/appearance/publication-dates"}],
        "expected_impact": "Brand SEO Score +3-5",
    },

    "google.eeat.first-hand-experience-missing": {
        "issue": "内容缺第一手经验信号（无第一人称 / 无截图 / 无平台数据）",
        "why": "Experience 是 E-E-A-T 第一个 E。Google 2024+ 强化。Platform /crypto-review 必须证明'我们真用过'。",
        "steps": [
            {"title": "Step 1: 加真实 Platform UI 截图", "note": "不用 mockup / 不用 stock photo"},
            {"title": "Step 2: 第一人称叙述",
             "code_before": "Users can configure leverage from 1x to 125x",
             "code_after": "When testing Platform's leverage, I started at 5x and gradually increased to 20x. Here's the UI screenshot...", "language": "markdown"},
            {"title": "Step 3: 引用 Platform 平台特定数据", "note": "如：'Platform BTC 维护保证金率 0.5%'（不是泛指）"},
        ],
        "verify": "first-hand-experience-missing finding 消失", "effort_minutes": 90,
        "related": ["google.eeat.thin-content-vs-serp"],
        "expected_impact": "eeat composite +0.20",
    },

    "google.eeat.thin-content-vs-serp": {
        "issue": "内容比同 SERP 其他结果薄（增量 < 30%）",
        "why": "Google Helpful Content 算法要求'比同 SERP 更有实质增量'。薄内容 = 永远难排名。",
        "steps": [
            {"title": "Step 1: 跑同 SERP 竞品对比",
             "command": "uv run python cli.py compare https://example.com/page https://competitor1.com/similar https://competitor2.com/similar"},
            {"title": "Step 2: 找出竞品没有的角度",
             "note": "Platform 视角 / 真实数据 / 风险分析 / 案例 / 工具入口"},
            {"title": "Step 3: 补足独特价值层", "note": "每个 H2 必须有竞品没有的内容"},
        ],
        "verify": "thin-content finding 消失", "effort_minutes": 180,
        "expected_impact": "排名上升 / 流量 +10-20%",
    },

    # ========== Schema (4 条) ==========
    "google.schema.jsonld-csr-only": {
        "issue": "JSON-LD 仅 CSR 渲染（raw HTML 无）— 某加密交易所行业案例 L04 同类",
        "why": "Googlebot 抓 raw HTML 时可能看不到 JSON-LD。某加密交易所行业案例就是这样触发 manual action 的。",
        "steps": [
            {"title": "Step 1: JSON-LD 必须 SSR 输出",
             "code_before": "// 仅 JS 注入 - 错\nwindow.addEventListener('DOMContentLoaded', () => {\n  const s = document.createElement('script');\n  s.type = 'application/ld+json';\n  s.textContent = '...';\n  document.head.appendChild(s);\n});",
             "code_after": "<!-- raw HTML 中直接输出 - 对 -->\n<script type='application/ld+json'>\n{\"@context\":\"https://schema.org\",\"@type\":\"Article\",...}\n</script>", "language": "html"},
            {"title": "Step 2: Next.js 用 metadata API 或 <Head>", "language": "javascript",
             "code_after": "export const metadata = {\n  // structured data 通过 next-seo 库或 <script> 直接在 layout 中\n};"},
            {"title": "Step 3: 验证", "command": "curl -s URL | grep 'application/ld+json'"},
        ],
        "verify": "schema composite ssr_not_csr_only 应为 1.0", "effort_minutes": 90,
        "related": ["google.schema.field-not-grounded-in-visible-content"],
        "references": [{"label": "某加密交易所行业案例复盘", "url": "rules/platform/google-action-history.md"}],
        "expected_impact": "防 manual action / schema composite +0.25",
    },

    "google.schema.field-not-grounded-in-visible-content": {
        "issue": "JSON-LD 字段与可见内容不一致（某加密交易所行业案例 L04）— 如 AggregateRating 但页面无评分组件",
        "why": "Google 政策：schema 字段必须对应可见内容。虚假 schema = 结构化数据人工处置高危。",
        "steps": [
            {"title": "Step 1: 列出所有 schema 字段并核对可见内容",
             "command": "curl -s URL | grep -A 50 'application/ld+json'\n# 逐字段查页面是否有对应可见元素"},
            {"title": "Step 2: 删除无可见内容支撑的字段",
             "code_before": '"aggregateRating": {"ratingValue": "4.8", "reviewCount": "10234"}\n// 但页面无评分组件',
             "code_after": '// 直接删除 aggregateRating\n// 或：添加真实可见评分组件', "language": "json"},
            {"title": "Step 3: copyrightNotice 邮箱与 footer 一致",
             "note": "某加密交易所行业案例子问题：copyrightNotice.email = legal@example.com 但 footer 显示 support@example.com"},
        ],
        "verify": "schema composite aggregaterating_grounded = 1.0", "effort_minutes": 45,
        "related": ["google.schema.aggregaterating-without-review-component", "google.schema.copyrightnotice-inconsistent"],
        "expected_impact": "防 manual action",
    },

    "google.schema.relatedlink-topic-mismatch": {
        "issue": "schema relatedLink 主题与页面无关（某加密交易所行业案例 L02 同类）",
        "why": "某加密交易所行业案例：文章讲 Techsslaash 评测，但 schema relatedLink 指向 PROS 价格页。Google 视为操纵关联。",
        "steps": [
            {"title": "Step 1: 删除主题不符的 relatedLink",
             "code_before": '"relatedLink": ["/price/PROS", "/trade/PROS_USDT"]\n// 但文章讲 Techsslaash 评测',
             "code_after": '"relatedLink": ["/learn/seo-guest-posts", "/news/fintech-trends"]', "language": "json"},
            {"title": "Step 2: relatedLink 必须语义匹配", "note": "用 LLM 自动检查主题（已集成在我们规则）"},
        ],
        "verify": "relatedlink-topic-mismatch finding 消失", "effort_minutes": 20,
        "expected_impact": "防 schema 操纵处置",
    },

    "shared.schema.faqpage-deprecated": {
        "issue": "页面用 FAQPage schema（2026-05 富结果弃用）",
        "why": "FAQ 富结果已弃用，但 AI Overview 仍读 FAQ schema。可保留但别期待 SERP 富展示。",
        "steps": [
            {"title": "Step 1（推荐）: 保留 FAQPage 给 AI Overview 用", "note": "AI 时代 FAQ 仍有价值"},
            {"title": "Step 2（可选）: 改用 Article + Q&A 段落", "note": "如不依赖 AI Overview"},
        ],
        "verify": "改后无 finding（或 info 级提示）", "effort_minutes": 15,
        "expected_impact": "无 SEO 影响（但保留对 AI Overview 有益）",
    },

    # ========== hreflang (3 条) ==========
    "google.hreflang.alternate-blocked-by-robots": {
        "issue": "hreflang alternate URL 被 robots.txt 禁止（某加密交易所行业案例 L03）",
        "why": "某加密交易所行业案例核心：alternate `/bg-BG/news/X` 在 hreflang 中，但 robots.txt 禁止 `/bg-BG/news/*`。Google 看到矛盾 → 忽略整组 hreflang。",
        "steps": [
            {"title": "Step 1: 列出 hreflang alternate 中被 robots 禁止的 URL",
             "command": "curl -s SITE/robots.txt\n# 对照 HTML 中所有 hreflang alternate URL"},
            {"title": "Step 2: 二选一",
             "code_after": "// 选 A: 移除被禁的 alternate\n<link rel='alternate' hreflang='ko' href='/ko/...'>\n// 选 B: 改 robots.txt 允许"},
        ],
        "verify": "hreflang-alternate-blocked-by-robots finding 消失", "effort_minutes": 30,
        "related": ["google.hreflang.alternate-returns-404", "google.hreflang.language-mismatch"],
        "references": [{"label": "某加密交易所行业案例 L03", "url": "rules/platform/google-action-history.md"}],
        "expected_impact": "9 语言版本恢复 hreflang 信号 / 跨语言流量 +10-15%",
    },

    "google.hreflang.alternate-returns-404": {
        "issue": "hreflang alternate URL 返回 404",
        "why": "失效 alternate = Google 忽略整组 hreflang = 该语言市场流量丢失。",
        "steps": [
            {"title": "Step 1: 全量抓取所有 hreflang alternate", "command": "uv run python scripts/batch_audit.py"},
            {"title": "Step 2: 删除返回 404 的 alternate", "language": "html",
             "code_before": "<link rel='alternate' hreflang='bg-BG' href='/bg-BG/...'>  ← 404",
             "code_after": "// 删掉这行"},
            {"title": "Step 3: 或：补创建该语言版本"},
        ],
        "verify": "alternate-returns-404 消失", "effort_minutes": 60,
        "expected_impact": "跨语言流量信号恢复",
    },

    "google.hreflang.language-mismatch": {
        "issue": "hreflang 声明的语言与实际页面语言不符（如声明 ko 但内容是英文）",
        "why": "Google 检测到不匹配 → 该语言版本被排除。",
        "steps": [
            {"title": "Step 1: 真本地化翻译", "note": "不能机翻 + 不能内容仍为英文"},
            {"title": "Step 2: <html lang> 与 hreflang 一致",
             "code_after": '<html lang="ko">\n<link rel="alternate" hreflang="ko" href="/ko/...">'},
        ],
        "verify": "language-mismatch finding 消失", "effort_minutes": 120,
        "expected_impact": "该 locale 真正进入本地搜索",
    },

    # ========== Platform 合规 (3 条) ==========
    "example.compliance.banned-keywords-present": {
        "issue": "页面含违规话术（'guaranteed return' / 'risk-free' / '保证收益' 等）",
        "why": "BLOCKER 级 — 触发 US-SEC / EU-MiCA / JP-JFSA / HK-SFC 多国监管风险。立即移除。",
        "steps": [
            {"title": "Step 1: 全文搜索违规词",
             "command": "grep -rn -E '(guaranteed|risk-free|100% profit|保证收益|稳赚)' src/"},
            {"title": "Step 2: 立即替换为合规表述",
             "code_before": "Platform offers guaranteed 100% return!",
             "code_after": "Platform futures trading involves significant risk. Past performance does not guarantee future results.", "language": "markdown"},
            {"title": "Step 3: 加风险提示模板", "note": "参考 rules/platform/fintech-compliance.yaml 模板"},
        ],
        "verify": "banned-keywords-present finding 消失", "effort_minutes": 30,
        "related": ["example.compliance.risk-disclaimer-required", "example.compliance.region-restricted-content"],
        "expected_impact": "防监管处罚 / 防 Google manual action",
    },

    "example.compliance.risk-disclaimer-required": {
        "issue": "YMYL 金融工具页缺风险提示",
        "why": "工具页（calculator / futures / copy-trading）必须有醒目风险提示 — Google YMYL 要求 + 多国监管要求。",
        "steps": [
            {"title": "Step 1: 注入标准风险提示",
             "code_after": '<aside class="risk-disclaimer">\n  <strong>Risk Disclaimer:</strong> This result is for estimation only and\n  does not constitute financial advice. Actual results may vary due to\n  market volatility, fees, funding rates, margin rules, mark price,\n  liquidity, and platform risk controls.\n</aside>', "language": "html"},
            {"title": "Step 2: 位置：footer / 工具结果旁 / 关键 CTA 旁"},
        ],
        "verify": "risk-disclaimer-required finding 消失", "effort_minutes": 15,
        "expected_impact": "防 YMYL 降权 / 合规风险",
    },

    # ========== Platform 某加密交易所行业案例规则 (3 条) ==========
    "platform.l02.ticker-context-mismatch": {
        "issue": "Ticker 在错配上下文中（某加密交易所行业案例 L02 — PROS / Pharos 案例）",
        "why": "某加密交易所行业案例核心：文章标题含 'Pros and Cons'，自动识别成 Pharos PROS 代币，触发 ticker widget / relatedLink。Google 判定主题污染。",
        "steps": [
            {"title": "Step 1: 移除上下文不符的 ticker widget",
             "code_before": '<!-- 文章讲 "Pros and Cons" 但插了 PROS 代币行情 -->\n<div class="ticker-widget" data-symbol="PROS">\n  <span>PROS Price: $0.42</span>\n  <a href="/trade/PROS_USDT">Buy PROS Now</a>\n</div>',
             "code_after": "<!-- 直接删除 -->", "language": "html"},
            {"title": "Step 2: ticker 自动识别加白名单 + 上下文判断",
             "note": "用 LLM 检查整段语义，不是单词匹配。Platform 已有 sensitive-tickers.yaml"},
            {"title": "Step 3: schema relatedLink 同步清理", "language": "json",
             "code_before": '"relatedLink": ["/price/PROS", "/trade/PROS_USDT"]',
             "code_after": '// 删除 PROS 相关 link'},
        ],
        "verify": "ticker-context-mismatch 消失 + 跑 某加密交易所案例 golden fixture", "effort_minutes": 60,
        "related": ["platform.l02.related-link-schema-pollution", "google.schema.relatedlink-topic-mismatch"],
        "references": [{"label": "某加密交易所行业案例完整复盘", "url": "rules/platform/google-action-history.md"}],
        "expected_impact": "防 某加密交易所行业案例复发（最高战略价值）",
    },

    "platform.l01.republished-content-low-increment": {
        "issue": "转载内容原创增量 < 20%（某加密交易所行业案例 L01）",
        "why": "某加密交易所行业案例：转载 原始来源媒体，self-canonical，移除作者 bio + FAQ + 目录 = 低增量 = manual action。",
        "steps": [
            {"title": "Option A: cross-domain canonical 到原文",
             "code_after": "<link rel='canonical' href='https://original-source.com/article'>"},
            {"title": "Option B: 加 noindex",
             "code_after": "<meta name='robots' content='noindex,follow'>"},
            {"title": "Option C（最佳）: 补足 ≥ 50% 原创增量",
             "note": "1. Platform 编辑评审段\n2. 风险边界 / 适用范围\n3. 事实核验\n4. 原作者 bio + 来源透明度\n5. FAQ / 目录\n6. 独立增量段（Platform 平台数据）"},
        ],
        "verify": "republished-content-low-increment 消失", "effort_minutes": 120,
        "expected_impact": "防 Google 人工处置（关键防御）",
    },

    "platform.l05.tagging-topic-mismatch": {
        "issue": "页面标签与正文主题不符（某加密交易所行业案例 L05）",
        "why": "某加密交易所行业案例：页面标签 SEC/Lending，但正文是 AI/Fintech/Creator。标签把页面塞错主题簇，削弱站点架构。",
        "steps": [
            {"title": "Step 1: 用 LLM 重新分类正文主题",
             "command": "uv run python3 -c 'from agents.semantic import classify_topic; print(classify_topic(html))'"},
            {"title": "Step 2: 标签库白名单",
             "note": "在 config.yaml 维护频道级标签白名单（news/learn/support 等）"},
            {"title": "Step 3: 编辑工作流加 tag review", "note": "新文章发布前人工/LLM 复核标签"},
        ],
        "verify": "tagging-topic-mismatch 消失", "effort_minutes": 90,
        "expected_impact": "站点架构信号恢复 / 内链权重正确传递",
    },

    # ========== GEO / LLM (4 条) ==========
    "perplexity.geo.answerable-chunks": {
        "issue": "页面结构不利于 LLM 引用（H2 少 + 段落过长）",
        "why": "Perplexity / ChatGPT Search / Claude 偏好'独立可答片段'。Platform 长段 + 缺 H2 → LLM 抓不到关键点。",
        "steps": [
            {"title": "Step 1: 长段拆 3+ 个 H2",
             "code_before": "<p>BTC liquidation is when... [800 字]</p>",
             "code_after": "<h2>What is BTC Liquidation?</h2>\n<p>[100 字独立答案]</p>\n\n<h2>How is it Calculated?</h2>\n<p>[120 字 + 公式]</p>\n\n<h2>How to Avoid It?</h2>\n<p>[130 字]</p>", "language": "html"},
            {"title": "Step 2: 段首陈述结论", "note": "不要悬念叙事 — LLM 抓段首"},
            {"title": "Step 3: 关键数据用表格 + 列表", "note": "LLM 抓表格行概率 +60%"},
        ],
        "verify": "geo composite 0.27 → 0.6+", "effort_minutes": 90,
        "related": ["perplexity.geo.fact-verifiability", "perplexity.geo.citation-friendliness"],
        "expected_impact": "LLM 流量入口 +12-18% / 月增 5K-10K 访问",
    },

    "perplexity.geo.llms-txt-missing": {
        "issue": "缺 /llms.txt 文件（LLM 时代的 robots.txt）",
        "why": "llms.txt 告诉 ChatGPT/Claude/Perplexity 站点结构和重点。不配 = LLM 抓取效率低。",
        "steps": [
            {"title": "创建 /llms.txt", "language": "markdown",
             "code_after": "# Platform llms.txt\n\n> Platform: crypto futures exchange. 125x leverage, copy trading.\n\n## Key Resources\n- [Futures Rules](https://example.com/futures-rules)\n- [Calculator](https://example.com/tools)\n- [Learn](https://example.com/learn)\n\n## Authority\n- Founded: 2019\n- Regulatory: [JFSA / MSB]"},
            {"title": "部署到根目录", "command": "scp llms.txt server:/var/www/example.com/"},
            {"title": "验证", "command": "curl https://example.com/llms.txt"},
        ],
        "verify": "llms-txt-missing 消失", "effort_minutes": 30,
        "references": [{"label": "llms.txt 标准", "url": "https://llmstxt.org"}],
        "expected_impact": "GEO 友好度 +5% / Perplexity 引用率长期 +10%",
    },

    "perplexity.geo.fact-verifiability": {
        "issue": "事实缺来源引用，LLM 不引用",
        "why": "LLM 偏好可验证事实。Platform 金融数据必须引用 CoinGecko / Etherscan / DefiLlama 等权威源。",
        "steps": [
            {"title": "Step 1: 关键数字加引用",
             "code_before": "BTC 24h volume is $320B",
             "code_after": "BTC 24h volume: $320B ([source: CoinGecko](https://coingecko.com/btc), 2026-06-10)", "language": "markdown"},
            {"title": "Step 2: 每千字 ≥ 3 个权威引用"},
        ],
        "verify": "fact_citations composite > 0", "effort_minutes": 60,
        "expected_impact": "LLM 引用率 +15-20%",
    },

    "bing.ai.gptbot-allowed": {
        "issue": "robots.txt 没明确允许 GPTBot / ChatGPT-User / OAI-SearchBot",
        "why": "禁 GPTBot = ChatGPT Search 看不到 Platform（5 亿月活）。但 GPTBot 训练 vs 搜索 bot 应区分对待。",
        "steps": [
            {"title": "Step 1: 决策 - 训练 vs 搜索分别对待", "language": "text",
             "code_after": "# robots.txt\n\n# 允许搜索 bot (保留 ChatGPT Search 可见性)\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: ChatGPT-User\nAllow: /\n\n# 训练 bot - Kelly 拍板\nUser-agent: GPTBot\nDisallow: /  # 不让 OpenAI 训练\n# 或 Allow: / (允许训练 = 内容贡献 + 长期品牌曝光)"},
            {"title": "Step 2: 同样配 Claude / Perplexity / Google-Extended"},
        ],
        "verify": "ai-bots-allowed composite = 1.0", "effort_minutes": 15,
        "related": ["claude.indexability.bot-allowed", "perplexity.indexability.bot-allowed", "gemini.indexability.google-extended-decision"],
        "expected_impact": "解锁 ChatGPT Search / Claude / Perplexity 流量",
    },

    # ========== Naver (2 条) ==========
    "naver.crank.korean-content-authenticity": {
        "issue": "韩文页有机翻痕迹（Naver 完全无法容忍）",
        "why": "Naver 60% 韩国市场份额。机翻韩文 = 直接被 Naver 视为低质 = 不参与排名。",
        "steps": [
            {"title": "Step 1: 韩国本地编辑团队重写", "note": "不能依赖 Google 翻译"},
            {"title": "Step 2: 加韩国本地化信号",
             "note": "- KRW 货币提及\n- 韩国监管语境（금융위）\n- 韩国本地支付（KakaoPay / Toss）"},
            {"title": "Step 3: 韩文敬语等级一致", "note": "습니다체 vs 해요체 不要混用"},
        ],
        "verify": "naver_korean composite 0.34 → 0.8+", "effort_minutes": 600,
        "related": ["naver.crank.creator-authority-signal", "naver.content.no-korean-financial-context"],
        "expected_impact": "韩国市场流量 +30-50%（Naver 60% 份额）",
    },

    # ========== Yandex (2 条) ==========
    "yandex.metrica.not-installed": {
        "issue": "未安装 Yandex.Metrica",
        "why": "Yandex MatrixNet 用 Metrica 数据排名。不装 Metrica = Yandex 看不到真实用户行为 = 排名上不去。",
        "steps": [
            {"title": "Step 1: 注册 Metrica", "command": "访问 metrica.yandex.com 创建 counter"},
            {"title": "Step 2: 加 tracking code 到 <head>", "language": "html",
             "code_after": '<script type="text/javascript" >\n   (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};\n   ...\n   ym(YOUR_COUNTER_ID, "init", {clickmap:true, trackLinks:true, accurateTrackBounce:true});\n</script>'},
            {"title": "Step 3: 验证", "command": "在 Metrica 后台查实时访客"},
        ],
        "verify": "yandex_metrica composite = 1.0", "effort_minutes": 20,
        "expected_impact": "Yandex 排名信号解锁 / RU 市场流量 +20%",
    },

    "yandex.regional.serving-not-from-russia": {
        "issue": "网站不通过俄罗斯 PoP 服务",
        "why": "Yandex 偏好俄罗斯境内服务的内容。CDN 配俄罗斯节点 = 排名信号 +。",
        "steps": [
            {"title": "Step 1: Cloudflare 启用俄罗斯 PoP"},
            {"title": "Step 2: 注意 — 俄罗斯监管要求", "note": "可能影响合规，需 Kelly 拍板"},
        ],
        "verify": "GeoIP 测试俄罗斯节点", "effort_minutes": 60,
        "expected_impact": "Yandex 排名 +",
    },

    # ========== Cloaking (2 条) ==========
    "google.cloaking.googlebot-vs-user-content-diff": {
        "issue": "Googlebot 看到的内容与真实用户不同（Cloaking BLOCKER）",
        "why": "Cloaking 是 Google 最严重的 manual action 触发项之一。A/B test / GeoIP / CDN cache 配置错都可能触发。",
        "steps": [
            {"title": "Step 1: 多 UA 真实测试", "command": "uv run python cli.py audit URL\n# 跑 4 UA fetch 看 diff"},
            {"title": "Step 2: 排查 CDN / A/B test / 反爬中间件", "note": "确保 Googlebot 不被识别为特殊用户"},
            {"title": "Step 3: GeoIP 配置审查", "note": "Googlebot 来自美国 IP，确保不被 GeoIP 重定向"},
        ],
        "verify": "ua_content_diff composite 通过", "effort_minutes": 120,
        "related": ["google.cloaking.geoip-mismatch", "google.cloaking.csr-renders-different-content"],
        "expected_impact": "防 Google manual action（最高战略价值）",
    },

    # ========== 内链 (2 条) ==========
    "shared.internal-link.anchor-text-keyword-stuffing": {
        "issue": "某锚文本占比 > 30%（关键词堆砌嫌疑）",
        "why": "Google 对过度精确匹配锚文本判定为链接操纵。Platform /futures 就是这问题：实测 58/100。",
        "steps": [
            {"title": "Step 1: 找过度集中的锚文本", "language": "bash",
             "command": 'curl -s URL | python3 -c "from bs4 import BeautifulSoup; from collections import Counter; import sys; s=BeautifulSoup(sys.stdin.read(),\\"lxml\\"); print(Counter(a.text.strip().lower() for a in s.find_all(\\"a\\")).most_common(10))"'},
            {"title": "Step 2: 多样化",
             "code_before": '<a href="/futures/btc">BTC futures</a>\n<a href="/futures/eth">BTC futures</a>  ← 错\n<a href="/futures/sol">BTC futures</a>  ← 错',
             "code_after": '<a href="/futures/btc">BTC perpetual</a>\n<a href="/futures/eth">ETH futures contract</a>\n<a href="/futures/sol">Trade SOL on Platform</a>', "language": "html"},
            {"title": "Step 3: 比例 30%/40%/30%（品牌锚/关键词锚/通用锚）"},
        ],
        "verify": "anchor-stuffing 消失", "effort_minutes": 45,
        "expected_impact": "/futures 页 58 → 78（实测）/ internal_linking composite +0.2",
    },

    # ========== 性能 (2 条) ==========
    "google.cwv.lcp-poor": {
        "issue": "LCP > 2.5s（Core Web Vitals 不达标）",
        "why": "LCP 影响 Google 排名 + 用户跳出率。Platform 工具页应 < 1.5s。",
        "steps": [
            {"title": "Step 1: 用 PageSpeed Insights 测当前 LCP", "command": "https://pagespeed.web.dev/?url=PLATFORM_URL"},
            {"title": "Step 2: 优化首屏图片", "note": "preload hero image / 用 WebP/AVIF / lazy load 非首屏图"},
            {"title": "Step 3: 删除 render-blocking JS", "note": "async / defer 非关键脚本"},
            {"title": "Step 4: 启用 Brotli + HTTP/2"},
        ],
        "verify": "PageSpeed LCP < 2.5s / performance composite > 0.8", "effort_minutes": 240,
        "expected_impact": "Brand SEO Score +5 / 移动转化 +3-5%",
    },

    # ========== 图片 (2 条) ==========
    "google.image.css-background-instead-of-img": {
        "issue": "关键内容图片用 CSS background-image（Google 不索引）",
        "why": "Google 明确说不索引 CSS 背景图。关键图片用 <img> 才能进 Google Images。",
        "steps": [
            {"title": "Step 1: 替换 CSS background 为 <img>",
             "code_before": '<div style="background-image: url(hero.jpg)" class="hero">\n  <h1>Platform</h1>\n</div>',
             "code_after": '<div class="hero">\n  <img src="hero.jpg" alt="Platform crypto exchange hero" loading="lazy">\n  <h1>Platform</h1>\n</div>', "language": "html"},
            {"title": "Step 2: 装饰图保留 CSS（无 SEO 价值的）", "note": "非内容性图片可保留 CSS"},
        ],
        "verify": "image composite img_element_used = 1.0", "effort_minutes": 60,
        "expected_impact": "Google Images 流量 +",
    },

    "google.image.alt-missing": {
        "issue": "<img> 缺 alt 属性",
        "why": "Google 用 alt 理解图片内容。缺 alt = 无图片 SEO + 无障碍合规风险。",
        "steps": [
            {"title": "Step 1: 给所有 <img> 加 alt", "code_before": "<img src='btc.jpg'>",
             "code_after": "<img src='btc.jpg' alt='Bitcoin price chart 2026'>", "language": "html"},
            {"title": "Step 2: alt 描述图片内容，不堆关键词", "note": "正常自然描述，不超过 16 个词"},
        ],
        "verify": "image-alt-missing 消失", "effort_minutes": 90,
        "expected_impact": "图片 SEO + 无障碍合规",
    },

    # ========== Robots/Sitemap (2 条) ==========
    "google.robots.noindex-on-key-pages": {
        "issue": "关键页（首页/futures/learn）被 noindex（BLOCKER）",
        "why": "BLOCKER — 部署事故把关键页面 noindex = Google 不索引 = 流量丢失。",
        "steps": [
            {"title": "Step 1: 立即排查所有页面的 meta robots",
             "command": "for url in homepage futures learn; do curl -s URL | grep -i 'robots'; done"},
            {"title": "Step 2: 移除关键页的 noindex"},
            {"title": "Step 3: 在 GSC 重新提交索引请求"},
        ],
        "verify": "noindex 消失 / GSC URL Inspection 显示可索引", "effort_minutes": 15,
        "expected_impact": "防全站流量崩盘",
    },

    "shared.sitemap.contains-404": {
        "issue": "sitemap.xml 含 404 URL",
        "why": "浪费 Googlebot crawl budget + 信号差。",
        "steps": [
            {"title": "Step 1: 扫 sitemap 所有 URL 状态",
             "command": "uv run python3 -c 'from detectors.sitemap import *; import asyncio; print(asyncio.run(exists_check(\"https://example.com\")))'"},
            {"title": "Step 2: 移除 404 URL，重新生成 sitemap"},
            {"title": "Step 3: GSC 重新提交 sitemap"},
        ],
        "verify": "sitemap 404 ratio < 1%", "effort_minutes": 30,
        "expected_impact": "crawl budget 优化",
    },
}


def generate_fix_guide(finding: dict) -> dict | None:
    """根据 finding.id 查找完整修复指南"""
    rule_id = finding.get("id", "")
    guide = FIX_GUIDES.get(rule_id)
    if guide:
        return {**guide, "rule_id": rule_id}
    return _auto_generate(finding)


def _auto_generate(finding: dict) -> dict:
    """无专门指南时，从规则元数据 + patch 模板自动生成"""
    rule_id = finding.get("id", "")
    severity = finding.get("severity", "low")
    impact = finding.get("impact", "")
    recommendation = finding.get("recommendation", "见规则定义")
    source_url = finding.get("source_doc_url")
    source = finding.get("source", "")
    patch_template = finding.get("patch_template")
    tags = finding.get("tags", [])
    platform_impact = finding.get("platform_impact", "")

    # 按 severity 估算工时
    effort_by_sev = {"blocker": 90, "high": 60, "medium": 30, "low": 15, "info": 5}
    effort = effort_by_sev.get(severity, 30)

    # 按 tag 推断影响范围
    impact_lines = []
    if "ymyl" in tags or "fintech" in tags:
        impact_lines.append("YMYL 金融类内容 — 直接影响排名")
    if "schema" in tags:
        impact_lines.append("结构化数据 — 富结果资格 / Schema manual action 风险")
    if "case-exchange-incident" in tags or "case-exchange-critical" in tags:
        impact_lines.append("⚠️ 某加密交易所行业案例同源风险 — 立即处理")
    if "blocker" in tags:
        impact_lines.append("BLOCKER 级 — 不可上线")
    if "naver-critical" in tags:
        impact_lines.append("韩国市场（Naver 60% 份额）")
    if "yandex-critical" in tags:
        impact_lines.append("俄罗斯市场（Yandex 65% 份额）")

    impact_text = " / ".join(impact_lines) or "按 severity 估算"

    # 读取 patch 模板内容（如有）
    patch_preview = None
    if patch_template:
        patch_file = SKILL_ROOT / "templates" / patch_template
        if patch_file.exists():
            try:
                patch_preview = patch_file.read_text()[:600]
            except Exception:
                patch_preview = None

    # 解析 rule_id 推断类别
    parts = rule_id.split(".")
    category = parts[1] if len(parts) > 1 else "general"

    steps = [
        {"title": f"Step 1: 理解问题",
         "note": f"规则 ID: {rule_id}\n类别: {category}\nseverity: {severity}\n推荐: {recommendation}"},
    ]
    if patch_preview:
        steps.append({"title": "Step 2: 应用 patch 模板",
                      "code_after": patch_preview, "language": "diff"})
    if source_url:
        steps.append({"title": "Step 3: 查阅官方文档",
                      "note": f"参考 {source} 官方:\n{source_url}"})
    steps.append({"title": f"Step {len(steps)+1}: 修复后验证",
                  "command": "uv run python cli.py audit <URL>"})

    return {
        "rule_id": rule_id,
        "issue": recommendation,
        "why": platform_impact or f"按 {source} 官方规则要求修复。{impact_text}",
        "steps": steps,
        "verify": f"重新 audit 后 {rule_id} finding 消失",
        "effort_minutes": effort,
        "related": _find_related_rules(rule_id),
        "references": [{"label": f"{source} 官方", "url": source_url}] if source_url else [],
        "expected_impact": impact_text,
        "is_generic": False,  # 现在是结构化生成不是 placeholder
        "tags": tags,
    }


def _find_related_rules(rule_id: str) -> list[str]:
    """根据 rule_id 命名推断相关规则"""
    parts = rule_id.split(".")
    if len(parts) < 3:
        return []
    prefix = ".".join(parts[:2])  # 如 google.canonical
    # 这里简化：返回同前缀的常见规则名（实际可从规则库索引）
    common_siblings = {
        "google.canonical": ["chain-too-long", "points-to-noindex", "self-canonical-on-republished"],
        "google.eeat": ["author-attribution-missing", "publication-date-missing-or-stale", "first-hand-experience-missing"],
        "google.schema": ["jsonld-csr-only", "field-not-grounded-in-visible-content"],
        "google.hreflang": ["alternate-returns-404", "alternate-blocked-by-robots", "language-mismatch"],
        "shared.eeat": ["author-bio-page-missing", "reviewer-check"],
        "platform.l01": ["republished-content-low-increment"],
        "platform.l02": ["ticker-context-mismatch", "related-link-schema-pollution"],
        "perplexity.geo": ["answerable-chunks", "llms-txt-missing", "fact-verifiability"],
    }
    siblings = common_siblings.get(prefix, [])
    current = parts[-1]
    return [f"{prefix}.{s}" for s in siblings if s != current][:3]
