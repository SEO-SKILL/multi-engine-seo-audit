![Multi-Engine SEO Audit cover: 442 rules across Google / Naver / Yandex / Yahoo!JAPAN, 22 agents, 9 locale routing, deep audit terminal](assets/cover.svg)

# Multi-Engine SEO Audit

**Multi-Engine SEO Audit is an enterprise-grade deep audit platform built for crypto exchanges and financial YMYL sites.** It runs 22 agents in parallel across 442 rules covering Google Spam Policy 2024, Naver C-Rank, Yandex MatrixNet, and Yahoo!JAPAN — produces a prioritized action plan with falsifiable, primary-source-grounded recommendations. Ships as both a Web Dashboard and a one-click Electron desktop app for non-technical teammates.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Electron 32](https://img.shields.io/badge/Electron-32.x-47848F?logo=electron&logoColor=white)](https://www.electronjs.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-FF6B00.svg)](LICENSE)
[![Rules](https://img.shields.io/badge/SEO_rules-442-success)](rules/)
[![Engines](https://img.shields.io/badge/search_engines-4-blue)](#platform-coverage)
[![Agents](https://img.shields.io/badge/agents-22-purple)](agents/)

> **Two modes ship in one binary.**
> - 🌐 **Web Dashboard** — `uv run python web_dashboard.py` → browser at `localhost:8080`. Best for dev iteration + custom batch.
> - 🖥️ **Electron Desktop App** — `npm run build:mac` → drag `.dmg` into `Applications`. Best for non-technical teammates who want one-click audit.

### Why Multi-Engine SEO Audit

- **Defends against Google Manual Action.** Spam Policy 2024 (site reputation abuse, scaled AI content, expired domain abuse), EEAT signal gap detection, HCU helpfulness signals — all hard-rule gated **before** the page goes live, so you never have to file reconsideration requests.
- **Beyond Google.** Naver controls 60%+ of Korean search, Yandex 65%+ of Russian, Yahoo!JAPAN 30%+ of Japan — and they ignore Google's playbook entirely. We ship platform-native rules for C-Rank, MatrixNet, JFSA disclosure, plus locale routing so you don't waste audit cycles on irrelevant rules.
- **Falsifiable, not promotional.** Every finding carries the detector function name, the exact evidence snippet, a recommended fix, and a verification command. No "improve EEAT" hand-waving — concrete diffs and grep patterns the engineer can apply today.
- **Built for crypto / YMYL.** Pre-baked compliance rules for SEC / MiCA / JFSA / FSC banned keywords, risk disclosure requirements, regional restriction detection, schema-spam Review-as-price-description, and parasite-SEO sub-path classification.

### Real signal

After running on a real 8-page audit:

```
Stage                      avg_score   blockers   broadcast误报
─────────────────────────  ─────────  ─────────  ──────────────
Pre-applies_to filter         14.3      8/8       naver rules on en/ja/ru pages
Post P0 fix                   37.2      2/8       legit only
Post P1 fix                   38.9      1/8       single KO Korean signal issue
```

**precision improvement: +184%**. 6 of 8 pages cleared gatekeeper. The 1 remaining blocker is a true positive (KO homepage lacks real Korean content).

## Who this is for

- **In-house SEO leads at crypto / fintech / publisher companies.** Catches what GSC and Lighthouse miss: schema deprecation (FAQ 富结果 2026-05), parasite-SEO exposure on UGC sub-paths, expired-domain heritage risk, AI-citability gaps.
- **DevOps + compliance teams.** Pre-merge gate that blocks Manual Action risks before they ship. Banned-keyword detector with anti-scam context guard (won't fire on educational "Risk-free returns is a red flag" content).
- **Multi-market growth teams.** Single tool covers en / ko / ja / ru / vi / tr / pt / es / zh-CN — auto-routes each locale to its dominant search engine instead of forcing Google patterns on Naver-first markets.

## Quick Start

### Prerequisites
```bash
brew install python@3.12 uv node
```

### Way A · Web Dashboard (dev iteration)
```bash
git clone https://github.com/twitter-bot-tech/multi-engine-seo-audit.git
cd multi-engine-seo-audit
uv sync
cp .env.example .env                # fill ANTHROPIC_API_KEY / GOOGLE_AI_API_KEY
uv run python web_dashboard.py      # → http://localhost:8080
```

### Way B · Electron Desktop App (one-click for teammates)
```bash
cd electron-app
npm install
npm run dev                         # spawn Flask + open BrowserWindow
npm run build:mac                   # → dist/*.dmg (arm64 + x64)
```

### Way C · Single-page CLI
```bash
curl -X POST http://localhost:8080/api/audit \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/en", "locale":"en", "no_cache":true}'
```

## Platform Coverage

| Engine | Market Share | Core Algorithm | Locale Routes |
|--------|:------------:|----------------|:---------------:|
| 🔵 Google | Global | EEAT · HCU · Spam Policy 2024 · Core Update | `en` `zh-CN` `vi` `tr` `pt` `es` |
| 🟢 Naver | 🇰🇷 60%+ | C-Rank · D.I.A · Korean authenticity | `ko` |
| 🔴 Yandex | 🇷🇺 65%+ | MatrixNet · Minusinsk · Madrid · AGS · Metrica | `ru` |
| 🟡 Yahoo!JAPAN | 🇯🇵 30%+ | Chiebukuro · JFSA disclosure | `ja` |

## Features

### 442 SEO Rules across 8 dimensions
- **EEAT signals** (13 rules) — author attribution, organization schema, YMYL signal completeness
- **Schema** (15 rules) — JSON-LD syntax, deprecated types (FAQ/HowTo), grounding in visible content
- **Manual Action** (17 rules) — cloaking, hidden text, hacked content patterns, paid outbound links
- **Spam Policy 2024** (4 rules) — site reputation abuse, scaled AI content, expired domain abuse
- **Multi-engine native** — Naver C-Rank (6), Yandex (8), Yahoo!JAPAN (3)
- **Compliance** (9 rules) — banned keywords with anti-scam guard, risk disclosure, region restriction, YMYL EEAT
- See full list in [`rules/`](rules/)

### Parallel agent fan-out
```
crawler-agent (多 UA + WAF retry + 限流)
    │
    ├──> technical-agent (canonical / hreflang / schema / EEAT / hidden / quality / web-vitals)
    ├──> safety-agent (banned keywords / pros-ticker)
    ├──> geo-agent (AI Overviews / Discover / LLM citation)
    ├──> lifecycle-agent (freshness / pruning / dia)
    ├──> localization-agent (Naver / Yandex / Yahoo!JP / Bing per-locale)
    │
    ▼
semantic-agent (LLM judge: plagiarism / authenticity / EEAT depth)
    │
    ▼
report-agent (composite score · action plan · markdown export)
```

### UI / UX polish
- **Hero verdict** — one-glance "可上线 / 暂不上线 / 改后再审" + 8-dim radar
- **守门员 vs 优化双区** — Blocker rules block deploy, Medium-Low surface as ROI-ranked optimization
- **Chinese rule labels** — `google.spam-2024.site-reputation-abuse` auto-renders as `Google · 垃圾内容政策2024 / 站点声誉滥用（寄生 SEO）`
- **Markdown export** — single-page or batch aggregate, paste into Lark / Notion / GitHub Issues

### Security defaults
- Backend binds `127.0.0.1` only — never exposed on LAN or internet
- `applies_to.platforms` + `applies_to.locales` strict filtering — no rule broadcasts across engines
- API keys stored in `.env` only (gitignored, never uploaded)
- Anti-scam context guard prevents banned-keyword false positives on educational content
- First-party path whitelist prevents UGC misclassification as parasite SEO

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│           Electron Desktop App (Mac · Win)                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Main process: spawn Flask + IPC + lifecycle + menu     │  │
│  └────────────┬───────────────────────────────────────────┘  │
│               ▼                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ BrowserWindow → http://127.0.0.1:8080                  │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                  │ child_process.spawn
                  ▼
┌──────────────────────────────────────────────────────────────┐
│        Flask Backend · 127.0.0.1 only (sealed)               │
│                                                              │
│   Orchestrator (locale → active_platforms routing)           │
│        │                                                     │
│        ├─► 22 parallel agents (asyncio.gather)               │
│        │                                                     │
│        ├─► Generic detector runner                           │
│        │     - applies_to filter                             │
│        │     - 442 yaml rules → detector fn dispatch         │
│        │                                                     │
│        └─► LLM judge (Anthropic + Gemini fallback)           │
│                                                              │
│   Composite score · action plan · markdown export            │
└──────────────────────────────────────────────────────────────┘
```

## Documentation

| Doc | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Full capability matrix (commands · agents · rules) |
| [PRD.md](PRD.md) | Product requirements |
| [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) | High-level summary |
| [V2_MILESTONE_REPORT.md](V2_MILESTONE_REPORT.md) | v2 milestone deliverables |
| [GOOGLE_RANKING_COVERAGE.md](GOOGLE_RANKING_COVERAGE.md) | Google ranking factor coverage matrix |
| [PLATFORM_REMEDIATION_PLAN.md](PLATFORM_REMEDIATION_PLAN.md) | Internal remediation playbook |
| [WILL_ONBOARDING.md](WILL_ONBOARDING.md) | New engineer onboarding |
| [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) | API key setup walkthrough |
| [electron-app/README.md](electron-app/README.md) | Desktop app build + distribution |

## Roadmap

- [x] **v1.0** · 442 rules · 8-dim composite score · Web Dashboard
- [x] **v1.1** · Locale-aware routing · Naver / Yandex / Yahoo!JP native rules
- [x] **v2.0** · Gatekeeper vs Optimizer dual-mode · Electron desktop app · BYDFi 2026-05 incident prevention
- [ ] **v2.1** · Bundled Python runtime (teammates don't need `uv` install)
- [ ] **v2.2** · macOS code signing + notarization (drop Gatekeeper warning)
- [ ] **v2.3** · Auto-update via electron-updater
- [ ] **v3.0** · GSC + GA4 historical trend integration · multi-tenant org mode

## Contributing

Internal team only — submit issues / PRs via GitHub.

- New rules go to `rules/{platform}/_rules/*.yaml` (must include `applies_to` + `bydfi_business_impact` + `tags`)
- New detectors go to `detectors/*.py` with fixture + test under `tests/`
- Run `uv run pytest tests/` to verify all green before merge
- LLM judge prompts go to `prompts/*.md` — use existing fixtures for snapshot tests

## License

[MIT](LICENSE) — see `LICENSE` for full terms.

## Author

Maintained by the internal SEO team. For questions, open an issue.

---

<div align="center">
<sub>Built with ☕ + Python 3.12 + Flask + Electron 32 + Anthropic Claude · 2026</sub>
</div>
