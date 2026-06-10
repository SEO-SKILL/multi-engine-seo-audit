---
name: seo-audit
description: BYDFi 专属的 SEO 风控 + 增长决策中台。防 Google 人工处置 + 跑通合约工具页 SEO MVP。覆盖 34 项业务能力 / 11 个框架模块 / 8 个搜索引擎平台规则库。Triggers on '/seo-audit', 'SEO检测', 'SEO审核', 'pre-publish 卡审', '竞品 SEO 对比', '工具页 SEO 验收'.
---

# BYDFi SEO Audit Skill

## 一句话

为 BYDFi 量身打造的 SEO 风控 + 增长中台 — 防 Google 处置 + 工具页 MVP 增长闭环 + 跨平台（Google/Bing/Naver/Yandex/LLM）规则库 + 组织级知识沉淀。

## 4 个核心命令

| 命令 | 用途 |
|---|---|
| `audit <url>` | 单页 16 维度审核 + Final Verdict（上线/暂不上线/改后再审）|
| `gate <md_file>` | 发布前卡审（Git pre-commit hook）|
| `compare <self_url> <competitors...>` | 竞品对比 + HTML 仪表盘 |
| `watch <site>` | 全站快照 + 周报 + Slack 推送 |

## 关键文档

- `PRD.md` — V1+V2 完整产品需求文档
- `tasks/todo.md` — 可勾选执行清单
- `tasks/lessons.md` — 经验沉淀（每次纠错后更新）

## 状态

- **当前阶段**：Phase 0（启动）
- **V1 目标**：4 周内上线 16 项业务能力 + 9 框架模块 + 5 平台规则库
- **V2 目标**：再 4-6 周补全到 34 项 + 11 模块 + 8 平台

## 项目范围

- **租户**：BYDFi（单租户，架构留多租户 hook）
- **域名**：bydfi.com
- **语言**：en, zh-CN, ja, ko, vi, tr, pt, es, ru
- **竞品**：MEXC / WEEX / Binance / Bybit / OKX / CoinGlass
- **合规区域**：US-SEC / EU-MiCA / SG-MAS / JP-JFSA / HK-SFC

## 协作方式

按 CLAUDE.md「Claude + Codex 分工」流程：

1. Codex 调研出方案
2. Claude 审批
3. Codex 写代码（codex exec --full-auto）
4. Codex 自审
5. Claude 终审 + 合并

Claude 不下场写 ≥ 30 行的代码。
