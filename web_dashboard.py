"""
Multi-Engine SEO Audit — Web Dashboard v3
重设计：黑橙金 / 守门员置顶 / 一句话结论 / 雷达图 / 业务术语
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path


def _load_dotenv() -> None:
    """轻量 .env 加载（避免新增依赖）"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


_load_dotenv()

SKILL_ROOT = Path(__file__).parent
sys.path.insert(0, str(SKILL_ROOT))

from flask import Flask, jsonify, request  # noqa: E402

from orchestrator import Orchestrator  # noqa: E402

app = Flask(__name__)


# composite 维度业务命名映射
DIM_LABELS = {
    "eeat": ("内容权威性", "E-E-A-T 信号（作者/审核/来源/日期）"),
    "schema": ("结构化数据", "JSON-LD 真实性 + SSR 输出"),
    "crawlability": ("可抓取性", "Canonical / hreflang / robots / viewport"),
    "performance": ("加载性能", "TTFB / HTTP2 / 压缩 / 大小"),
    "internal_linking": ("内链结构", "锚文本 / 集群 / 死链"),
    "geo": ("AI 引用友好", "LLM Overview / Perplexity / ChatGPT Search"),
    "multilingual": ("多语言路由", "hreflang / x-default / 本地化"),
    "image": ("图片 SEO", "alt / 格式 / lazy / sitemap"),
    "naver_korean": ("Naver 韩文真实性", "C-Rank / 韩文 / Naver 生态"),
    "yandex_russian": ("Yandex 俄文真实性", "MatrixNet / Metrica / 俄文"),
    "baidu_chinese": ("Baidu 中文合规", "ICP / 简体中文 / 百度生态"),
}


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Multi-Engine SEO Audit · 守门员 + 优化</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --orange:#FF6B00;--orange-dk:#E65A00;--orange-lt:#FFE4D0;
  --bg:#FAFAF8;--ink:#0A0A0A;--ink-2:#333;--mute:#777;--border:#EAEAEA;
  --gate:#D32F2F;--gate-lt:#FFEBEE;
  --opt:#7CB342;--opt-lt:#E8F5E9;
  --warn:#F57C00;--warn-lt:#FFF8E1;
  --shadow:0 1px 3px rgba(0,0,0,0.04),0 8px 24px rgba(0,0,0,0.04);
  --gold:#D4A24A;
}
html,body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","PingFang SC","HarmonyOS Sans","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased;line-height:1.55}
body{padding-bottom:80px}

/* HEADER */
header.top{background:var(--ink);color:white;padding:18px 32px;display:flex;justify-content:space-between;align-items:center}
header.top h1{font-size:18px;font-weight:600;letter-spacing:-0.2px}
header.top h1 span.brand{color:var(--orange)}
header.top .meta{font-size:12px;color:#999}

/* MAIN GRID */
.wrap{max-width:1800px;margin:24px auto;padding:0 max(24px,3vw);width:100%;box-sizing:border-box}
.hero-stats{max-width:1400px}
.hero .lead{max-width:900px}
.control{max-width:1400px}
.control form input[type=url]{flex:1;min-width:280px;max-width:560px}
header.top{padding-left:max(32px,calc((100vw - 1800px)/2 + 24px));padding-right:max(32px,calc((100vw - 1800px)/2 + 24px))}
@media(max-width:1900px){header.top{padding-left:32px;padding-right:32px}}

/* CONTROL BAR */
.control{background:white;border-radius:14px;padding:24px 28px;box-shadow:var(--shadow);margin-bottom:24px;max-width:1600px}
.control h2{font-size:14px;color:var(--mute);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;font-weight:500}
.control form{display:flex;gap:10px;flex-wrap:wrap;align-items:stretch}
.control input[type=url]{flex:1;min-width:280px;font-size:15px;padding:14px 18px;border:1.5px solid var(--border);border-radius:10px;font-family:inherit}
.control input[type=url]:focus{outline:0;border-color:var(--orange);box-shadow:0 0 0 3px rgba(255,107,0,.12)}
.control select{padding:14px 16px;border:1.5px solid var(--border);border-radius:10px;font-size:15px;font-family:inherit;background:white}
.btn{font-size:15px;padding:14px 22px;border-radius:10px;border:0;font-weight:600;cursor:pointer;transition:.2s;font-family:inherit;letter-spacing:.2px}
.btn-primary{background:var(--orange);color:white}
.btn-primary:hover{background:var(--orange-dk)}
.btn-secondary{background:white;color:var(--ink);border:1.5px solid var(--ink)}
.btn-secondary:hover{background:var(--ink);color:white}
.btn:disabled{opacity:.45;cursor:not-allowed;background:white;color:var(--mute);border-color:var(--mute)}
.btn:disabled:hover{background:white;color:var(--mute)}

/* VERDICT (一句话结论 hero) */
.verdict-hero{padding:36px 32px;border-radius:16px;margin-bottom:24px;display:flex;align-items:center;gap:24px;box-shadow:var(--shadow)}
.verdict-hero.pass{background:linear-gradient(135deg,#E8F5E9,#C8E6C9)}
.verdict-hero.fail{background:linear-gradient(135deg,#FFEBEE,#FFCDD2)}
.verdict-hero.warn{background:linear-gradient(135deg,#FFF8E1,#FFE082)}
.verdict-hero .icon{font-size:64px;line-height:1}
.verdict-hero .text h2{font-size:32px;font-weight:700;letter-spacing:-0.5px;margin-bottom:6px}
.verdict-hero .text p{font-size:15px;color:var(--ink-2);margin-bottom:2px}
.verdict-hero .text .url{font-family:"SF Mono",Menlo,monospace;font-size:12px;color:var(--mute);margin-top:6px}

/* SCORE + RADAR side by side */
.metrics-row{display:grid;grid-template-columns:300px 1fr;gap:24px;margin-bottom:24px}
@media(max-width:900px){.metrics-row{grid-template-columns:1fr}}
.score-card{background:white;border-radius:16px;padding:28px;box-shadow:var(--shadow);text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center}
.score-ring{width:180px;height:180px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:10px solid var(--orange);background:white;margin-bottom:16px;position:relative}
.score-ring.good{border-color:var(--opt)}
.score-ring.warn{border-color:var(--warn)}
.score-ring.bad{border-color:var(--gate)}
.score-ring .num{font-size:54px;font-weight:700;letter-spacing:-2px;line-height:1}
.score-ring .unit{font-size:12px;color:var(--mute);margin-top:4px;letter-spacing:1.5px}
.score-card .label{font-size:13px;color:var(--mute);text-transform:uppercase;letter-spacing:1px}
.score-card .delta{margin-top:8px;font-size:14px;color:var(--mute)}

.radar-card{background:white;border-radius:16px;padding:28px;box-shadow:var(--shadow)}
.radar-card h3{font-size:14px;color:var(--mute);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;font-weight:500}
.radar-wrap{position:relative;width:100%;max-width:420px;margin:0 auto}
.radar-wrap svg{width:100%;height:auto;display:block}

/* GATEKEEPER 主区 */
.gate-section{background:white;border-radius:16px;overflow:hidden;box-shadow:var(--shadow);margin-bottom:24px;border-left:6px solid var(--gate)}
.gate-section.passed{border-left-color:var(--opt)}
.gate-header{padding:24px 28px;background:var(--gate-lt);display:flex;align-items:center;gap:14px;justify-content:space-between}
.gate-section.passed .gate-header{background:var(--opt-lt)}
.gate-header .left{display:flex;align-items:center;gap:14px}
.gate-header .icon{font-size:36px}
.gate-header h2{font-size:20px;font-weight:700;color:var(--gate)}
.eng-note{font-size:12px;font-weight:500;color:#888;margin-left:8px}
.skip-section{background:#fafafa;border:1px solid #e5e5e5;border-radius:10px;padding:16px 20px;margin:16px 0}
.skip-header{display:flex;gap:12px;align-items:flex-start}
.skip-header .icon{font-size:22px;line-height:1}
.skip-header h3{font-size:15px;font-weight:600;color:#555;margin:0}
.skip-header .sub{font-size:12.5px;color:#888;margin-top:2px}
.skip-body{margin-top:12px;display:flex;flex-direction:column;gap:6px}
.skip-row{font-size:12.5px;color:#666}
.skip-row code{background:#f1f1f1;padding:1px 6px;border-radius:4px;font-size:12px}
.skip-row .scope{color:#999;margin-left:4px}
.skip-row .sev-high{color:#d83f31;font-weight:600}
.skip-row .sev-medium{color:#f5a623;font-weight:600}
.skip-row .sev-blocker{color:#c62828;font-weight:700}
.skip-more{font-size:12px;color:#aaa;margin-top:4px}
.gate-section.passed .gate-header h2{color:var(--opt)}
.gate-header .sub{font-size:13px;color:var(--ink-2);margin-top:2px}
.gate-header .badge-count{background:white;padding:8px 16px;border-radius:24px;font-weight:700;font-size:16px;color:var(--gate);border:2px solid var(--gate)}
.gate-section.passed .gate-header .badge-count{color:var(--opt);border-color:var(--opt)}
.gate-body{padding:24px 28px}

/* 优化区 */
.opt-section{background:white;border-radius:16px;overflow:hidden;box-shadow:var(--shadow);margin-bottom:24px;border-left:6px solid var(--orange)}
.opt-header{padding:20px 28px;background:#FFFBF5;display:flex;align-items:center;gap:14px;justify-content:space-between}
.opt-header .left{display:flex;align-items:center;gap:14px}
.opt-header .icon{font-size:32px}
.opt-header h2{font-size:18px;font-weight:700;color:var(--orange-dk)}
.opt-section.local{border-color:#3b82f6;background:#f0f7ff}
.opt-section.local .opt-header h2{color:#1d4ed8}
.comp-section{background:#fff;border:1px solid #eee;border-radius:12px;padding:18px 22px;margin:16px 0}
.comp-section h3{font-size:15px;font-weight:600;color:#333;margin:0 0 14px 0}
.comp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}
.comp-card{border:1px solid #ececec;border-radius:8px;background:#fafafa;overflow:hidden}
.comp-card{border:1px solid #ececec;border-radius:8px;background:#fafafa;overflow:hidden;transition:border-color .15s,box-shadow .15s}
.comp-card:hover{border-color:#FFB370;box-shadow:0 2px 8px rgba(255,107,0,.08)}
.comp-card details summary{padding:12px 14px;cursor:pointer;list-style:none;display:flex;align-items:center;gap:10px;transition:background .15s}
.comp-card details summary:hover{background:#fff5e6}
.comp-card details summary::-webkit-details-marker{display:none}
.comp-card details summary::before{content:'▼';color:#FF6B00;transition:transform .2s;font-size:14px;display:inline-block;font-weight:700;transform:rotate(-90deg);margin-right:4px}
.comp-card details[open]{background:#fff;border-radius:8px;box-shadow:0 4px 12px rgba(27,46,111,.08)}
.comp-card details[open] summary{background:linear-gradient(90deg,#fff5e6 0%,#fff 100%);border-bottom:1px solid #f0f0f0}
.comp-card details[open] summary::before{transform:rotate(90deg);color:#FF6B00}
.comp-head strong{flex:1;color:#222;font-size:13.5px}
.comp-score{font-size:18px;font-weight:700;margin-left:8px}
.comp-score.muted{font-size:12px;font-weight:500;color:#aaa}
.comp-verdict{font-size:11px;padding:2px 8px;border-radius:10px;font-weight:600}
.comp-body{padding:14px;background:#fff;animation:slideDown .2s ease-out}
@keyframes slideDown{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}
.comp-bar{height:6px;background:#eee;border-radius:3px;overflow:hidden;margin:10px 0}
.comp-bar-fill{height:100%;transition:width .3s}
.weakest-row{font-size:12.5px;color:#d83f31;background:#fff4f1;padding:8px 12px;border-radius:6px;margin:8px 0}
.comp-tag{font-size:11.5px;color:#888;margin:6px 0 10px}
.comp-breakdown{width:100%;font-size:12px;border-collapse:collapse;margin-top:8px}
.comp-breakdown th{text-align:left;padding:4px 6px;background:#f0f0f0;color:#666;font-weight:500;border-bottom:1px solid #ddd}
.comp-breakdown td{padding:4px 6px;border-bottom:1px solid #f0f0f0;color:#444}
.comp-card.skipped{opacity:.55}
.comp-empty{font-size:12.5px;color:#aaa;padding:14px;text-align:center;background:#f8f8f8;border-radius:6px;margin-top:8px}
.opt-header .sub{font-size:13px;color:var(--ink-2);margin-top:2px}
.opt-header .badge-count{background:white;padding:6px 14px;border-radius:20px;font-weight:600;color:var(--orange);border:2px solid var(--orange)}
.opt-body{padding:24px 28px}

/* finding card */
.finding{padding:16px 20px;border:1px solid var(--border);border-radius:10px;margin-bottom:10px;background:white;transition:.15s}
.finding:hover{border-color:var(--orange);box-shadow:0 4px 16px rgba(255,107,0,.08)}
.finding details summary{cursor:pointer;display:flex;flex-wrap:wrap;align-items:center;gap:10px;list-style:none}
.finding details summary::-webkit-details-marker{display:none}
.finding details summary::after{content:'▼';margin-left:auto;color:var(--mute);font-size:11px;transition:.2s}
.finding details[open] summary::after{transform:rotate(180deg)}
.sev{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.sev-blocker{background:var(--gate);color:white}
.sev-high{background:var(--warn);color:white}
.sev-medium{background:#FFD54F;color:var(--ink)}
.sev-low{background:#AED581;color:var(--ink)}
.sev-info{background:#90CAF9;color:var(--ink)}
.rule-code{background:var(--orange-lt);padding:3px 8px;border-radius:4px;font-family:"SF Mono",Menlo,monospace;font-size:12px;color:var(--orange-dk);cursor:help}
.rule-zh{display:inline-block;color:var(--ink);font-size:13px;font-weight:600;margin-left:2px;line-height:1.4}
.rule-zh .cat{color:var(--orange-dk);font-weight:700}
.rule-zh .sep{color:var(--mute);margin:0 4px;font-weight:400}
.must-fix{background:var(--gate);color:white;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;letter-spacing:.3px;cursor:help}
.suggest{background:var(--orange-lt);color:var(--orange-dk);padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;letter-spacing:.3px;cursor:help}
.sev{cursor:help}
.finding-body{margin-top:14px;padding-top:14px;border-top:1px solid var(--border);font-size:14px;line-height:1.7}
.finding-body .row{margin-bottom:12px}
.impact-box{padding:12px 14px;background:var(--orange-lt);border-left:3px solid var(--orange);border-radius:0 6px 6px 0;margin:10px 0}
.fix-guide{padding:18px;background:#FFFBF5;border:1px solid var(--orange-lt);border-radius:10px;margin-top:14px}
.fix-guide h4{color:var(--orange-dk);font-size:14px;margin-bottom:10px;letter-spacing:.5px;text-transform:uppercase}
.step{margin:12px 0;padding:12px 14px;background:white;border-left:3px solid var(--orange);border-radius:0 6px 6px 0}
.step .step-title{font-weight:600;margin-bottom:6px;font-size:13px}
.step pre{background:#FAFAF5;padding:10px;border-radius:6px;font-size:12px;overflow-x:auto;margin:4px 0;border-left:2px solid var(--mute)}
.step pre.before{border-left-color:var(--gate);background:#FFF5F5}
.step pre.after{border-left-color:var(--opt);background:#F5FFF5}
.step pre.cmd{background:#0A0A0A;color:#0F0;border-left-color:var(--gold)}
.meta-row{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--ink-2);margin-top:10px;padding-top:10px;border-top:1px dashed var(--border)}

/* batch table */
.batch-table{width:100%;border-collapse:collapse;margin-top:16px;background:white;border-radius:10px;overflow:hidden;box-shadow:var(--shadow)}
.batch-table th{background:var(--ink);color:white;padding:14px 18px;text-align:left;font-size:12px;text-transform:uppercase;letter-spacing:1px}
.batch-table td{padding:14px 18px;border-bottom:1px solid var(--border);font-size:14px}
.batch-table tr:last-child td{border-bottom:0}
.batch-table tr:hover{background:#FAFAF5}

/* loading */
#loading{display:none;text-align:center;padding:48px;background:white;border-radius:16px;box-shadow:var(--shadow);margin-bottom:24px}
.spinner{display:inline-block;width:40px;height:40px;border:4px solid var(--orange-lt);border-top-color:var(--orange);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#loading p{margin-top:14px;color:var(--mute)}

/* hidden helper */
.hidden{display:none}
.text-mute{color:var(--mute)}
.small{font-size:13px}

/* Hero（uhaoseo 借鉴）*/
.hero{background:linear-gradient(135deg,#1b2e6f 0%,#2d4ba0 100%);color:white;border-radius:18px;padding:36px 40px;margin-bottom:20px;box-shadow:0 8px 24px rgba(27,46,111,.15)}
.hero h1{font-size:30px;font-weight:700;letter-spacing:-.5px;margin:0 0 8px 0;color:white}
.hero .lead{font-size:15px;color:rgba(255,255,255,.85);max-width:680px;line-height:1.6;margin-bottom:22px}
.hero .lead b{color:#FF6B00;font-weight:600}
.hero-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px}
.hero-stat{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:14px 16px;backdrop-filter:blur(8px)}
.hero-stat .num{font-size:26px;font-weight:700;color:#FFB370;line-height:1}
.hero-stat .label{font-size:11.5px;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.6px;margin-top:6px}

/* CTA 改造 */
.cta-primary{font-size:16px;padding:14px 28px;font-weight:700;box-shadow:0 4px 12px rgba(255,107,0,.3)}
.cta-primary:hover{transform:translateY(-1px);box-shadow:0 6px 16px rgba(255,107,0,.4)}

/* 历史快捷栏 */
.recent-section{background:white;border-radius:14px;padding:14px 18px;margin-bottom:18px;box-shadow:var(--shadow)}
.recent-section .head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.recent-section h3{font-size:13px;font-weight:600;color:var(--ink-2);text-transform:uppercase;letter-spacing:.6px;margin:0}
.recent-section .clear-btn{font-size:11px;color:#888;background:none;border:none;cursor:pointer;text-decoration:underline}
.recent-list{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px}
.recent-item{flex:0 0 auto;border:1px solid var(--border);border-radius:8px;padding:8px 12px;cursor:pointer;background:#fafafa;font-size:12px;display:flex;align-items:center;gap:8px;transition:.15s;white-space:nowrap}
.recent-item:hover{border-color:var(--orange);background:white;transform:translateY(-1px)}
.recent-item .ri-score{font-weight:700;font-size:14px}
.recent-item .ri-score.good{color:#7CB342}
.recent-item .ri-score.warn{color:#F57C00}
.recent-item .ri-score.bad{color:#D32F2F}
.recent-item .ri-url{color:#666;max-width:180px;overflow:hidden;text-overflow:ellipsis}
.recent-item .ri-locale{background:#eee;padding:1px 6px;border-radius:3px;font-size:10px;color:#666;font-weight:600}
.recent-empty{font-size:12px;color:#aaa;padding:8px 4px}
.no-cache-toggle{font-size:12px;color:#666;display:inline-flex;align-items:center;gap:4px;margin-left:12px;cursor:pointer}
.no-cache-toggle input{margin:0}
</style>
</head>
<body>

<header class="top">
  <h1>🛡️ <span class="brand">Platform SEO</span> Audit · <span class="text-mute" style="font-size:13px;color:#999;font-weight:400">守门员 + 优化双模式</span></h1>
  <div class="meta"><span id="rules-count">382 rules · 8 dimensions · 100% detector</span></div>
</header>

<div class="wrap">

  <!-- HERO（uhaoseo 借鉴 + 真实数据 stat 卡）-->
  <div class="hero">
    <h1>深度审计您的 SEO，防 Manual Action / 提升多市场流量</h1>
    <div class="lead">
      Platform 专属审计 · <b>440+ 条规则</b> · 覆盖 <b>Google / Naver / Yandex / Yahoo!JAPAN</b> 4 大本地搜索引擎 · 9 个 locale 真本地化路由 · 守门员 vs 优化双模式 · 一键导出 Markdown 整改方案
    </div>
    <div class="hero-stats" id="hero-stats">
      <div class="hero-stat"><div class="num" id="stat-rules">—</div><div class="label">SEO 规则</div></div>
      <div class="hero-stat"><div class="num" id="stat-engines">4</div><div class="label">本地搜索引擎</div></div>
      <div class="hero-stat"><div class="num" id="stat-audited">—</div><div class="label">已审核页面</div></div>
      <div class="hero-stat"><div class="num" id="stat-avg">—</div><div class="label">平均 SEO 分</div></div>
      <div class="hero-stat"><div class="num" id="stat-blockers">—</div><div class="label">已识别守门员问题</div></div>
    </div>
  </div>

  <!-- 历史快捷栏 -->
  <div class="recent-section" id="recent-section">
    <div class="head">
      <h3>📂 最近审核（点击重看）</h3>
      <button class="clear-btn" id="refresh-history-btn">🔄 刷新</button>
    </div>
    <div class="recent-list" id="recent-list">
      <div class="recent-empty">还没有历史记录，下方跑一次 audit 即可。</div>
    </div>
  </div>

  <div class="control">
    <h2>🎯 审核目标</h2>
    <form id="audit-form">
      <input type="url" id="url" placeholder="https://example.com" value="https://example.com" required>
      <select id="locale">
        <option value="">Auto</option>
        <option value="en">English</option>
        <option value="zh-CN">中文</option>
        <option value="ja">日本語</option>
        <option value="ko">한국어</option>
        <option value="ru">Русский</option>
      </select>
      <button type="submit" class="btn btn-primary cta-primary">🔍 一键深度诊断</button>
      <button type="button" id="batch-btn" class="btn btn-secondary">🚀 跑 Platform 8 个核心页</button>
      <button type="button" id="export-btn" class="btn btn-secondary" disabled title="跑完单页 audit 后可导出 Markdown 报告，可粘贴到飞书 / Notion / GitHub 等">📋 导出 Markdown 报告</button>
      <label class="no-cache-toggle" title="绕过 30 分钟 LLM cache，强制让所有 LLM judge 真跑（更慢但更新）"><input type="checkbox" id="no-cache" /> 🔄 强制重跑（绕过 cache）</label>
    </form>
  </div>

  <div id="loading"><div class="spinner"></div><p>多 UA 抓取 + 22 agents + 8 维度评分中...</p></div>

  <div id="result"></div>

</div>

<script>
const form = document.getElementById('audit-form');
const loading = document.getElementById('loading');
const resultEl = document.getElementById('result');
let lastAuditData = null;
let lastBatchData = null;  // batch 结果（用于批量导出）

// === uhaoseo 借鉴 #1 & #4: Hero 指标 + 历史快捷栏 ===
async function refreshHeroStats() {
  try {
    const r = await fetch('/api/stats');
    const s = await r.json();
    document.getElementById('stat-rules').textContent = s.total_rules || '—';
    document.getElementById('stat-engines').textContent = s.supported_engines || 5;
    document.getElementById('stat-audited').textContent = s.audited_pages || 0;
    document.getElementById('stat-avg').textContent = s.audited_pages > 0 ? s.avg_score.toFixed(0) : '—';
    document.getElementById('stat-blockers').textContent = s.gatekeeper_blockers || 0;
  } catch(e) { console.warn('stats failed', e); }
}

async function refreshHistory() {
  try {
    const r = await fetch('/api/history');
    const d = await r.json();
    const listEl = document.getElementById('recent-list');
    if (!d.runs || d.runs.length === 0) {
      listEl.innerHTML = '<div class="recent-empty">还没有历史记录，下方跑一次 audit 即可。</div>';
      return;
    }
    listEl.innerHTML = '';
    for (const r of d.runs.slice(0, 20)) {
      const score = r.score != null ? Math.round(r.score) : '?';
      const scoreCls = score>=80?'good':score>=60?'warn':'bad';
      const shortUrl = (r.url||'').replace(/^https?:\/\/(www\.)?/,'').slice(0,40);
      const item = document.createElement('div');
      item.className = 'recent-item';
      item.title = `${r.url} · ${r.verdict} · 守门员 ${r.blocker} blocker / ${r.high} high`;
      item.innerHTML = `<span class="ri-score ${scoreCls}">${score}</span><span class="ri-locale">${r.locale||'?'}</span><span class="ri-url">${shortUrl}</span>`;
      item.addEventListener('click', () => loadRun(r.run_id));
      listEl.appendChild(item);
    }
  } catch(e) { console.warn('history failed', e); }
}

async function loadRun(runId) {
  loading.style.display = 'block';
  resultEl.innerHTML = '';
  try {
    const r = await fetch('/api/run/' + encodeURIComponent(runId));
    if (!r.ok) throw new Error('run not found');
    const d = await r.json();
    loading.style.display = 'none';
    lastAuditData = d;
    document.getElementById('export-btn').disabled = false;
    renderAudit(d);
    window.scrollTo({top: document.querySelector('.control').offsetTop, behavior: 'smooth'});
  } catch(e) {
    loading.style.display = 'none';
    resultEl.innerHTML = '<div class="control" style="color:var(--gate)">无法加载历史记录: '+e+'</div>';
  }
}

document.getElementById('refresh-history-btn').addEventListener('click', () => {
  refreshHistory();
  refreshHeroStats();
});

refreshHeroStats();
refreshHistory();

// 业务术语映射
const DIM_LABELS = {
  eeat: ['内容权威性', 'E-E-A-T'],
  schema: ['结构化数据', 'JSON-LD 真实性'],
  crawlability: ['可抓取性', 'Canonical / hreflang'],
  performance: ['加载性能', 'TTFB / 压缩'],
  internal_linking: ['内链结构', '锚文本 / 集群'],
  geo: ['AI 引用友好', 'LLM 时代新流量'],
  multilingual: ['多语言路由', 'hreflang 配置'],
  image: ['图片 SEO', 'alt / format / lazy'],
  naver_korean: ['Naver 韩文', 'C-Rank / 真实性'],
  yandex_russian: ['Yandex 俄文', 'MatrixNet / Metrica'],
  baidu_chinese: ['Baidu 中文', 'ICP / 简体'],
};

document.getElementById('batch-btn').addEventListener('click', async () => {
  loading.style.display = 'block';
  resultEl.innerHTML = '';
  lastAuditData = null;  // batch 模式下清除单页缓存
  document.getElementById('export-btn').disabled = true;
  try {
    const r = await fetch('/api/batch');
    const d = await r.json();
    loading.style.display = 'none';
    lastBatchData = d;
    renderBatch(d);
    // batch 完成 → 启用导出（智能路由到 batch endpoint）
    document.getElementById('export-btn').disabled = false;
    document.getElementById('export-btn').title = '导出 ' + (d.results || []).length + ' 页批量审计 Markdown 汇总报告';
    refreshHeroStats();
    refreshHistory();
  } catch (e) {
    loading.style.display = 'none';
    resultEl.innerHTML = '<div class="control" style="color:var(--gate)">Error: '+e+'</div>';
  }
});

document.getElementById('export-btn').addEventListener('click', async () => {
  // 智能路由：单页用 export-markdown，batch 用 export-batch-markdown
  let endpoint, payload;
  if (lastAuditData) {
    endpoint = '/api/export-markdown';
    payload = {run_id: lastAuditData.run_id, audit_data: lastAuditData};
  } else if (lastBatchData) {
    endpoint = '/api/export-batch-markdown';
    const runIds = (lastBatchData.results || []).map(r => r.run_id).filter(Boolean);
    payload = {run_ids: runIds, results: lastBatchData.results};
  } else {
    return;  // 无数据
  }
  const r = await fetch(endpoint, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  const d = await r.json();
  if (d.error) { alert('导出失败: '+d.error); return; }
  const blob = new Blob([d.markdown], {type:'text/markdown'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = d.filename;
  a.click();
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  loading.style.display = 'block';
  resultEl.innerHTML = '';
  lastBatchData = null;  // 单页 audit 模式下清除 batch 缓存
  document.getElementById('export-btn').disabled = true;
  document.getElementById('export-btn').title = '跑完单页 audit 后可导出 Markdown 报告，可粘贴到飞书 / Notion / GitHub 等';
  try {
    const r = await fetch('/api/audit', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        url: document.getElementById('url').value,
        locale: document.getElementById('locale').value,
        no_cache: document.getElementById('no-cache').checked,
      })
    });
    const d = await r.json();
    loading.style.display = 'none';
    lastAuditData = d;
    document.getElementById('export-btn').disabled = false;
    renderAudit(d);
    refreshHeroStats();
    refreshHistory();
  } catch (e) {
    loading.style.display = 'none';
    resultEl.innerHTML = '<div class="control" style="color:var(--gate)">Error: '+e+'</div>';
  }
});

function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

// === rule_id → 中文友好名 ===
const PLATFORM_ZH = {google:'Google',naver:'Naver',yandex:'Yandex','yahoo-jp':'Yahoo!JAPAN',platform:'Platform',shared:'通用'};
const CAT_ZH = {
  'spam-2024':'垃圾内容政策2024','manual-action':'人工处置风险','spam-update':'垃圾内容更新','helpful-content':'有用内容(HCU)','hcu':'有用内容(HCU)','core-update':'核心算法更新','eeat':'EEAT 经验权威可信','ymyl':'YMYL 高风险主题',
  'duplicate-content':'重复内容','duplicate':'重复内容','plagiarism':'抄袭检测','thin-content':'薄内容','content':'内容质量','freshness':'内容时效',
  'cloaking':'隐蔽伪装','hidden-text':'隐藏文本','hidden-links':'隐藏链接','doorway':'桥页','keyword':'关键词','exact-match':'精确匹配',
  'schema':'结构化数据','breadcrumb':'面包屑','title':'标题','meta-description':'Meta 描述','snippet':'摘要片段','featured-snippet':'Featured Snippet',
  'ai':'AI 内容','ai-overviews':'AI Overviews','ai-overview':'AI Overview','brand-mention-in-llm':'LLM 品牌提及','citation-rate-measurement':'引用率度量',
  'compliance':'金融合规','disclosure':'信息披露','privacy':'隐私','trust':'信任信号','author':'作者署名',
  'web3':'Web3/链上','price':'价格页','futures':'永续合约','tools':'工具页','copy':'跟单页','compare':'对比页','learn':'学院教学','news':'新闻','product':'产品','merchant':'商家','review':'评论','reviews-system':'评论系统','y1':'Yandex Y1','dia':'D.I.A 算法','crank':'C-Rank 算法','minusinsk':'Minusinsk 反作弊','madrid':'Madrid 反作弊','ags':'AGS 反作弊','metrica':'Yandex Metrica','webmaster':'站长平台','chiebukuro':'Yahoo 知恵袋','airsearch':'AirSearch','smart-block':'Smart Block','image-pack':'图片包',
  'mobile':'移动端','security':'安全','cwv':'Core Web Vitals','web-vitals':'Core Web Vitals','perf':'性能','js':'JS 渲染','image':'图片','video':'视频','favicon':'Favicon','a11y':'无障碍','behavior':'用户行为','user-behavior':'用户行为','view':'阅读体验','social':'社交信号','social-signals':'社交信号','kg':'知识图谱','knowledge-in':'知识图谱',
  'url':'URL 结构','canonical':'Canonical 规范','hreflang':'hreflang','multilingual':'多语言','preferred':'首选语言','sitemap':'站点地图','robots':'robots/抓取','redirect':'重定向','migration':'迁移','index':'索引','indexability':'可索引性','crawlability':'可抓取性','crawl-budget':'抓取预算','soft-404':'Soft 404','pagination':'分页','lazy-loading':'懒加载','indexnow':'IndexNow','site-name':'站点名','sitelinks':'站点链接','flexible-sampling':'弹性抽样','paywall':'付费墙','log':'日志','pruning':'内容修剪',
  'geo':'地域','regional':'地域','referral':'推广链路','internal-link':'内链','internal-search':'站内搜索','media-content':'媒体内容','experiment':'A/B 实验','technical':'技术','ecosystem':'生态','discover':'Discover','ugc':'UGC 用户内容','ugc-spam':'UGC 垃圾','thin':'薄内容',
  'l01':'L01 低增量','l02':'L02 内链','l05':'L05 标签页',
};
const TAIL_ZH = {
  'site-reputation-abuse':'站点声誉滥用（寄生 SEO）','scaled-content-risk-awareness':'AI 规模化低价值内容风险','scaled-content-abuse':'AI 规模化内容滥用','expired-domain-abuse':'过期域名滥用',
  'hacked-content':'被黑入侵内容','user-generated-spam':'UGC 垃圾内容','spam-pattern-check':'垃圾内容模式','paid-outbound-check':'付费外链','paid-link-buying':'购买链接',
  'plagiarism-no-value-add':'无增量抄袭','low-value-page':'低价值页面','thin-promo':'薄推广页','keyword-stuffing':'关键词堆砌','sneaky-redirect':'隐蔽重定向',
  'ymyl-eeat-required':'YMYL 必备 EEAT 信号','ymyl-awareness':'YMYL 信号检查','ymyl-eeat-signals':'EEAT 信号缺失','authority-sources':'权威信息源',
  'banned-keywords-present':'违禁词出现','risk-disclaimer-required':'风险披露缺失','no-risk-disclaimer':'风险免责缺失','region-restricted-content':'区域受限内容',
  'korean-content-authenticity':'韩文内容真实性','content-authenticity':'内容真实性','machine-translation-suspect':'疑似机翻',
  'past-performance-disclaimer':'过往业绩免责声明','trader-roi-display':'带单员 ROI 展示规范',
  'data-source-not-cited':'数据来源未引用','deviation-from-source':'数据偏离源','prediction-language':'预测性表述','k-line-source-missing':'K线数据来源缺失',
  'contract-address-not-linked':'合约地址未链接','chain-name-disambiguation':'链名歧义','token-symbol-with-chain':'代币符号缺链标识','defi-data-source-citation':'DeFi 数据源引用',
  'faqpage-deprecated':'FAQPage 富结果已弃用','howto-deprecated':'HowTo 富结果限制','breadcrumb-position-non-sequential':'面包屑序号非连续','json-ld-syntax-error':'JSON-LD 语法错误','multiple-products-on-same-page':'同页多 Product 需 ItemList',
  'featured-snippet-strategy':'Featured Snippet 策略','faq-richresult-deprecated-notice':'FAQ 富结果弃用提醒','monitoring-readiness':'核心更新监控就绪',
  'ua-content-diff':'UA 内容差异（伪装）','hidden-text-check':'隐藏文本检测',
  'calculator-formula-missing':'计算器公式缺失','maintenance-margin-rate-missing':'维持保证金率缺失','csr-only-calculator-shell':'仅 CSR 的计算器空壳','faq-missing':'FAQ 缺失','related-tools-missing':'相关工具缺失','trading-cta-missing':'交易 CTA 缺失',
  'republished-content-low-increment':'转载内容低增量','tagging-topic-mismatch':'标签主题不匹配','tag-page-quality':'标签页质量',
  'missing-or-short':'缺失或过短','bad-length':'长度不合规','duplicate':'重复','too-long-or-too-short':'长度不合规（过长/过短）','too-long-or-stuffed':'过长或关键词堆砌','too-long-truncated':'过长被截断','brand-name-position':'品牌名位置不当',
  'off-screen-positioning':'屏幕外定位（隐藏文本）','zero-font-size':'零号字体（隐藏）','same-color-as-background':'同色文本（隐藏）',
  'low-value-single-page':'单页低价值','homepage-author-or-org-missing':'主页缺作者/组织声明','author-attribution-missing':'作者署名缺失','signals-weak':'EEAT 信号薄弱',
  'inp-interactivity':'INP 交互延迟','lazy-loaded-content-blocks-render':'懒加载阻塞首屏渲染','async-script-blocking':'异步脚本阻塞渲染','history-api-misuse':'History API 滥用',
  'x-default-handling':'x-default 多语言兜底','llms-txt-missing':'llms.txt 缺失（AI 抓取协议）','field-not-grounded-in-visible-content':'字段未在可见内容佐证','no-direct-answer':'缺直接答案（Snippet 不友好）',
  'anchor-text-spam':'锚文本垃圾（过度优化）','keyword-stuffed-landing':'落地页关键词堆砌','sneaky-redirect':'隐蔽重定向',
  'site-reputation-abuse-awareness':'站点声誉滥用风险提示','core-update-monitoring':'核心更新监控就绪',
  'missing':'缺失',
};
const SEV_ZH = {blocker:'阻塞（违反即合规风险）',high:'高（强烈建议修复）',medium:'中（影响 SEO 分）',low:'低（建议优化）',info:'提示（认知层）'};
function ruleIdToZh(id) {
  const parts = (id||'').split('.');
  if (parts.length < 2) return '';
  const plat = PLATFORM_ZH[parts[0]] || parts[0];
  const cat = CAT_ZH[parts[1]] || parts[1].replace(/-/g,' ');
  const restRaw = parts.slice(2).join('.');
  const rest = TAIL_ZH[restRaw] || TAIL_ZH[parts.slice(-1)[0]] || restRaw.replace(/[-.]/g,' ');
  return {plat, cat, rest};
}
function ruleZhHtml(id) {
  const z = ruleIdToZh(id);
  if (!z) return '';
  return '<span class="rule-zh"><span class="cat">'+esc(z.plat)+' · '+esc(z.cat)+'</span><span class="sep">/</span>'+esc(z.rest)+'</span>';
}

const ENGINE_LABELS = {
  google: 'Google',
  naver: 'Naver',
  yandex: 'Yandex',
  'baidu+google': 'Baidu + Google',
  baidu: 'Baidu',
  'yahoo-japan': 'Yahoo!JAPAN',
  'google+yahoo-jp': 'Google + Yahoo!JAPAN',
};

function engineName(d) {
  const e = d.composite && d.composite._primary_engine;
  return ENGINE_LABELS[e] || 'Google';
}

function renderAudit(d) {
  const gate = d.findings.filter(f => f.mode === 'gatekeeper');
  const opt = d.findings.filter(f => f.mode === 'optimizer');
  const gatePassed = gate.length === 0;
  const verdict = d.verdict;
  const eng = engineName(d);

  let html = '';

  // === HERO: 一句话结论 ===
  let heroClass, heroIcon, heroTitle, heroSub;
  if (!gatePassed) {
    heroClass = 'fail';
    heroIcon = '🛑';
    heroTitle = '不可上线';
    heroSub = '守门员发现 ' + gate.length + ' 个合规底线违反（Google Manual Action 风险），必须先修';
  } else if (d.score >= 80) {
    heroClass = 'pass';
    heroIcon = '✅';
    heroTitle = '可以上线';
    heroSub = '守门员全部通过 · SEO 分 ' + d.score.toFixed(0) + ' · 还有 ' + opt.length + ' 个优化建议';
  } else {
    heroClass = 'warn';
    heroIcon = '🟡';
    heroTitle = '可上线但建议优化';
    heroSub = '守门员通过 · 但 ' + opt.length + ' 个优化项影响 SEO 分（当前 ' + d.score.toFixed(0) + '）';
  }
  html += '<div class="verdict-hero ' + heroClass + '">';
  html += '<div class="icon">' + heroIcon + '</div>';
  html += '<div class="text"><h2>' + heroTitle + '</h2><p>' + esc(heroSub) + '</p>';
  html += '<div class="url">' + esc(d.url) + ' · run_id=' + esc(d.run_id) + '</div></div></div>';

  // === SCORE RING + RADAR ===
  html += '<div class="metrics-row">';
  // Score
  const scoreClass = d.score >= 80 ? 'good' : d.score >= 60 ? 'warn' : 'bad';
  html += '<div class="score-card"><div class="score-ring ' + scoreClass + '">';
  html += '<div class="num">' + d.score.toFixed(0) + '</div><div class="unit">/ 100</div></div>';
  html += '<div class="label">Brand SEO Score</div>';
  if (d.action_plan && d.action_plan.length > 0) {
    let topUplift = 0;
    for (const a of d.action_plan.slice(0,3)) topUplift += (a.impact_score || 0) / 10;
    if (topUplift > 0) html += '<div class="delta">修完 Top 3 → 预计 +' + topUplift.toFixed(0) + ' 分</div>';
  }
  html += '</div>';

  // Radar
  html += '<div class="radar-card"><h3>📊 8 维度评分</h3>';
  html += renderRadar(d.composite);
  html += '</div></div>';

  // === 维度诊断详情（雷达图下方解读）===
  html += renderCompositeDetails(d.composite);

  // === GATEKEEPER 区 ===
  html += '<div class="gate-section ' + (gatePassed ? 'passed' : '') + '">';
  html += '<div class="gate-header"><div class="left">';
  html += '<div class="icon">' + (gatePassed ? '✅' : '🛑') + '</div><div>';
  const engNote = eng === 'Google' ? '' : '（当前主搜索引擎: ' + eng + '；守门规则按 Google 全球合规执行）';
  html += '<h2>守门员审核 · Google + 合规底线 <span class="eng-note">' + engNote + '</span></h2>';
  html += '<div class="sub">' + (gatePassed ? '全部通过 · 无 Manual Action 风险' : '违反 Google 全球合规规则 · 必须立即修复 · 不修=Manual Action / SEC / MiCA 风险') + '</div>';
  html += '</div></div><div class="badge-count">' + gate.length + '</div></div>';
  if (gate.length > 0) {
    html += '<div class="gate-body">' + renderFindings(gate, 'gatekeeper') + '</div>';
  }
  html += '</div>';

  // === 待 batch / 跨页规则提示 ===
  const skipped = d.skipped_rules || [];
  if (skipped.length > 0) {
    html += '<div class="skip-section"><div class="skip-header">';
    html += '<div class="icon">⏸️</div><div><h3>待全站 batch 才能验证（单页 audit 跳过）</h3>';
    html += '<div class="sub">以下 ' + skipped.length + ' 条规则需要全站语料 / 多 locale 抓取 / 外部数据源 · 跑 Platform 8 页或更大 batch 时会触发</div>';
    html += '</div></div><div class="skip-body">';
    for (const s of skipped.slice(0, 8)) {
      html += '<div class="skip-row"><span class="sev-' + s.severity + '" title="'+esc(SEV_ZH[s.severity]||s.severity)+'">' + s.severity + '</span> <code class="rule-code" title="规则 ID: '+esc(s.id)+'">' + esc(s.id) + '</code>' + ruleZhHtml(s.id) + ' <span class="scope">· ' + esc(s.scope_label) + '</span></div>';
    }
    if (skipped.length > 8) html += '<div class="skip-more">… 还有 ' + (skipped.length - 8) + ' 条</div>';
    html += '</div></div>';
  }

  // === 优化区（local-engine 优先 + global 二级） ===
  if (opt.length > 0) {
    const LOCAL_ENGINES = {naver:'Naver', yandex:'Yandex', 'yahoo-jp':'Yahoo!JAPAN'};
    const optLocal = opt.filter(f => LOCAL_ENGINES[(f.id||'').split('.')[0]]);
    const optGlobal = opt.filter(f => !LOCAL_ENGINES[(f.id||'').split('.')[0]]);

    if (optLocal.length > 0) {
      html += '<div class="opt-section local"><div class="opt-header"><div class="left">';
      html += '<div class="icon">🎯</div><div>';
      html += '<h2>本地优化（' + eng + ' 主战场）</h2>';
      html += '<div class="sub">针对当前 locale 的主搜索引擎 ' + eng + ' 的本地化建议 · 修完直接影响 ' + (d.locale||'') + ' 市场排名</div>';
      html += '</div></div><div class="badge-count">' + optLocal.length + '</div></div>';
      html += '<div class="opt-body">' + renderFindings(optLocal, 'optimizer') + '</div></div>';
    }

    if (optGlobal.length > 0) {
      html += '<div class="opt-section"><div class="opt-header"><div class="left">';
      html += '<div class="icon">🚀</div><div>';
      html += '<h2>全球优化（Google / 通用 SEO）</h2>';
      html += '<div class="sub">不影响索引 · 按 ROI 决策 · 修完预计 +' + optGlobal.length * 3 + '-' + optGlobal.length * 6 + ' 分</div>';
      html += '</div></div><div class="badge-count">' + optGlobal.length + '</div></div>';
      html += '<div class="opt-body">' + renderFindings(optGlobal, 'optimizer') + '</div></div>';
    }
  }

  resultEl.innerHTML = html;
}

function renderRadar(composite) {
  if (!composite || Object.keys(composite).length === 0) return '<p class="text-mute">No data</p>';
  const dims = Object.entries(composite)
    .filter(([k,v]) => !k.startsWith('_') && v && typeof v.composite_score === 'number')
    .map(([k,v]) => ({key:k, label:(DIM_LABELS[k]||[k])[0], score:v.composite_score, weakest:v.weakest_link}));

  if (dims.length === 0) return '<p class="text-mute">No data</p>';

  const cx=270, cy=220, R=160;
  const n=dims.length;
  const points = dims.map((d,i)=>{
    const angle = (Math.PI*2*i/n) - Math.PI/2;
    const r = R * d.score;
    return {
      x: cx + r*Math.cos(angle),
      y: cy + r*Math.sin(angle),
      labelX: cx + (R+32)*Math.cos(angle),
      labelY: cy + (R+32)*Math.sin(angle),
      score: d.score, label: d.label, key: d.key, weakest: d.weakest
    };
  });

  let svg = '<svg viewBox="0 0 540 440" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">';
  // grid rings
  for (let g=0.25; g<=1; g+=0.25) {
    svg += '<circle cx="'+cx+'" cy="'+cy+'" r="'+(R*g)+'" fill="none" stroke="#EEE" stroke-width="1"/>';
  }
  // axis lines
  for (let i=0;i<n;i++){
    const a=(Math.PI*2*i/n)-Math.PI/2;
    svg += '<line x1="'+cx+'" y1="'+cy+'" x2="'+(cx+R*Math.cos(a))+'" y2="'+(cy+R*Math.sin(a))+'" stroke="#EEE"/>';
  }
  // shape
  const pathD = points.map((p,i)=>(i===0?'M':'L')+p.x+','+p.y).join(' ')+'Z';
  svg += '<path d="'+pathD+'" fill="rgba(255,107,0,0.18)" stroke="#FF6B00" stroke-width="2.5"/>';
  // dots + labels
  for (const p of points){
    const col = p.score>=0.8?'#7CB342':p.score>=0.6?'#F57C00':p.score>=0.4?'#FF6B00':'#D32F2F';
    svg += '<circle cx="'+p.x+'" cy="'+p.y+'" r="5" fill="'+col+'"/>';
    // label position adjustment
    const ta = p.labelX < cx-10 ? 'end' : p.labelX > cx+10 ? 'start' : 'middle';
    svg += '<text x="'+p.labelX+'" y="'+p.labelY+'" text-anchor="'+ta+'" dy=".35em" font-size="11" fill="#333" font-weight="600">'+esc(p.label)+'</text>';
    svg += '<text x="'+p.labelX+'" y="'+(p.labelY+13)+'" text-anchor="'+ta+'" font-size="10" fill="'+col+'" font-weight="700">'+p.score.toFixed(2)+'</text>';
  }
  svg += '</svg>';
  return '<div class="radar-wrap">'+svg+'</div>';
}

// 子信号 → 中文解读
const SIGNAL_LABELS = {
  // EEAT
  'author_signal': '作者署名信号', 'has_author': '作者署名', 'jsonld_author': 'JSON-LD 作者',
  'citation_signal': '引用权威来源', 'ymyl_compliance': 'YMYL 合规',
  'first_hand_experience': '一手经验信号', 'reviewer_signal': '审核人信号',
  // Schema
  'jsonld_present': 'JSON-LD 存在', 'jsonld_ssr': 'JSON-LD 服务端渲染',
  'jsonld_truthful': 'JSON-LD 真实性', 'schema_completeness': 'Schema 完整度',
  // Crawlability
  'canonical_present_and_ssr': 'canonical SSR 输出', 'hreflang_with_x_default': 'hreflang 含 x-default',
  'robots_meta_not_noindex': 'robots meta 未 noindex',
  // Performance
  'html_size_reasonable': 'HTML 体积合理', 'cls_under_0.1': 'CLS < 0.1',
  'http2_or_higher': 'HTTP/2 或更高', 'image_lazy_load': '图片懒加载',
  'critical_css_inlined': '关键 CSS 内联',
  // Image SEO
  'alt_text_coverage': 'alt 文本覆盖率', 'image_filename_seo': '文件名 SEO 友好',
  'next_gen_format': '现代图片格式（webp/avif）',
  // Multilingual
  'hreflang_self_referencing': 'hreflang 自引', 'lang_attr_correct': 'html lang 属性正确',
  'translated_content_ratio': '本地化内容比例',
  // Internal Linking
  'avg_internal_links': '内链数量', 'anchor_text_diversity': '锚文本多样性',
  // GEO (AI)
  'ai_bots_allowed': 'AI 蜘蛛 robots 放行', 'answerable_chunks_ratio': '可问答片段比例',
  'fact_citations': '事实引用来源',
  // Naver
  'creator_authority': '创作者权威信号', 'korean_authenticity': '韩文真实性',
  'korean_local_context': '韩国本地化上下文', 'naver_ecosystem': 'Naver 生态整合',
  // Yandex
  'metrica_installed': 'Yandex Metrica 装载', 'cyrillic_authenticity': '西里尔字符真实',
  'russian_region_signals': '俄罗斯地域信号',
  // Baidu
  'icp_license': 'ICP 备案', 'simplified_chinese': '简体中文内容',
};

function sigLabel(key) { return SIGNAL_LABELS[key] || key; }

function scoreColor(s) {
  if (s >= 0.8) return '#7CB342';
  if (s >= 0.6) return '#F57C00';
  if (s >= 0.4) return '#FF6B00';
  return '#D32F2F';
}

function renderCompositeDetails(composite) {
  if (!composite) return '';
  const entries = Object.entries(composite).filter(([k,v]) => !k.startsWith('_') && v);
  if (entries.length === 0) return '';
  let html = '<div class="comp-section"><h3>📐 8 维度诊断详情（点击展开看具体子信号）</h3>';
  html += '<div class="comp-grid">';
  for (const [key, info] of entries) {
    const label = (DIM_LABELS[key]||[key])[0];
    const tag = (DIM_LABELS[key]||[key,''])[1];
    const score = info.composite_score;
    if (score === null || typeof score !== 'number') {
      html += '<div class="comp-card skipped"><div class="comp-head"><strong>'+esc(label)+'</strong><span class="comp-score muted">— '+esc(info.skipped||'无数据')+'</span></div></div>';
      continue;
    }
    const col = scoreColor(score);
    const pct = (score*100).toFixed(0);
    const weakest = info.weakest_link ? sigLabel(info.weakest_link) : null;
    const weakestVal = info.weakest_pass_value;
    const verdict = score>=0.8?'优秀':score>=0.6?'达标':score>=0.4?'待优化':'严重不足';
    html += '<div class="comp-card"><details>';
    html += '<summary class="comp-head"><strong>'+esc(label)+'</strong>';
    html += '<span class="comp-score" style="color:'+col+'">'+score.toFixed(2)+'</span>';
    html += '<span class="comp-verdict" style="background:'+col+'22;color:'+col+'">'+verdict+'</span>';
    html += '</summary>';
    html += '<div class="comp-body">';
    html += '<div class="comp-bar"><div class="comp-bar-fill" style="width:'+pct+'%;background:'+col+'"></div></div>';
    if (weakest) {
      html += '<div class="weakest-row">⚠️ <strong>最弱信号：</strong>'+esc(weakest);
      if (typeof weakestVal === 'number') html += ' <span style="color:#999">(pass='+weakestVal.toFixed(2)+')</span>';
      html += '</div>';
    }
    if (tag) html += '<div class="comp-tag">'+esc(tag)+'</div>';
    const bd = info.breakdown || {};
    const keys = Object.keys(bd);
    if (keys.length > 0) {
      html += '<table class="comp-breakdown"><thead><tr><th>子信号</th><th>得分</th><th>权重</th><th>加权</th></tr></thead><tbody>';
      const rows = keys.map(k=>({key:k, pass:bd[k].pass, weight:bd[k].weight, weighted:(bd[k].pass||0)*(bd[k].weight||0)}));
      rows.sort((a,b)=>a.pass-b.pass);
      for (const r of rows) {
        const rc = scoreColor(r.pass);
        html += '<tr><td>'+esc(sigLabel(r.key))+'</td><td style="color:'+rc+'">'+(r.pass||0).toFixed(2)+'</td><td>'+(r.weight||0).toFixed(2)+'</td><td>'+(r.weighted||0).toFixed(2)+'</td></tr>';
      }
      html += '</tbody></table>';
    } else {
      html += '<div class="comp-empty">该维度暂无子信号 breakdown 数据（detector 只返回总分）</div>';
    }
    html += '</div></details></div>';
  }
  html += '</div></div>';
  return html;
}

function renderFindings(arr, mode) {
  let html = '';
  for (const f of arr) {
    html += '<div class="finding"><details><summary>';
    html += '<span class="sev sev-'+f.severity+'" title="'+esc(SEV_ZH[f.severity]||f.severity)+'">'+f.severity+'</span>';
    html += '<code class="rule-code" title="规则 ID: '+esc(f.id)+'">'+esc(f.id)+'</code>';
    html += ruleZhHtml(f.id);
    html += mode==='gatekeeper'?'<span class="must-fix" title="守门员规则 · 违反即触发 Manual Action / 合规风险 · 必须修复才能上线">必修</span>':'<span class="suggest" title="优化建议 · 影响 SEO 分但不阻塞上线 · 按 ROI 决策">建议</span>';
    if (f.human_review_required) html += '<span class="must-fix" style="background:var(--ink)" title="需人工复核：检测结果可能误报，建议人工二次确认后修复">人工复核</span>';
    html += '</summary><div class="finding-body">';
    html += '<div class="row"><strong>📝 修复建议:</strong> '+esc(f.recommendation||'—')+'</div>';
    if (f.platform_impact) html += '<div class="impact-box"><strong>💼 对 Platform:</strong> '+esc(f.platform_impact)+'</div>';

    if (f.fix_guide) {
      const fg = f.fix_guide;
      html += '<div class="fix-guide"><h4>🛠️ 修复指南</h4>';
      if (fg.issue) html += '<div class="row"><strong>问题:</strong> '+esc(fg.issue)+'</div>';
      if (fg.why) html += '<div class="row"><strong>为什么:</strong> '+esc(fg.why)+'</div>';
      if (fg.steps) for (const s of fg.steps) {
        html += '<div class="step"><div class="step-title">'+esc(s.title)+'</div>';
        if (s.code_before) html += '<div class="small text-mute">改前:</div><pre class="before"><code>'+esc(s.code_before)+'</code></pre>';
        if (s.code_after) html += '<div class="small text-mute">改后:</div><pre class="after"><code>'+esc(s.code_after)+'</code></pre>';
        if (s.command) html += '<pre class="cmd"><code>'+esc(s.command)+'</code></pre>';
        if (s.note) html += '<div class="small text-mute" style="white-space:pre-wrap">'+esc(s.note)+'</div>';
        html += '</div>';
      }
      if (fg.verify) html += '<div class="row" style="margin-top:10px;padding:10px;background:var(--opt-lt);border-radius:6px"><strong>✅ 验证:</strong> '+esc(fg.verify)+'</div>';
      const mp=[];
      if (fg.effort_minutes) mp.push('⏱️ '+fg.effort_minutes+' min');
      if (fg.expected_impact) mp.push('📈 '+esc(fg.expected_impact));
      if (mp.length) html += '<div class="meta-row">'+mp.join(' · ')+'</div>';
      if (fg.references && fg.references.length) {
        html += '<div class="meta-row"><strong>📚 参考:</strong> ';
        html += fg.references.map(r => '<a href="'+esc(r.url)+'" target="_blank" style="color:var(--orange)">'+esc(r.label)+' →</a>').join(' · ');
        html += '</div>';
      }
      html += '</div>';
    }
    html += '</div></details></div>';
  }
  return html;
}

function renderBatch(d) {
  let html = '<div class="control"><h2>📊 Platform 8 核心页批量审计</h2>';
  html += '<p class="text-mute small">平均 SEO Score: <strong style="color:var(--orange);font-size:18px">'+d.avg_score.toFixed(1)+' / 100</strong> · 点击页面行查详细 audit</p>';
  html += '<table class="batch-table"><thead><tr><th>页面</th><th>URL</th><th>Score</th><th>结论</th><th>B/H/M</th></tr></thead><tbody>';
  for (const r of d.results) {
    if (r.error) {
      html += '<tr><td>'+esc(r.label)+'</td><td colspan="4">Error: '+esc(String(r.error).substring(0,80))+'</td></tr>';
    } else {
      const col = r.score>=80?'var(--opt)':r.score>=60?'var(--warn)':'var(--gate)';
      html += '<tr style="cursor:pointer" onclick="document.getElementById(\\'url\\').value=\\''+esc(r.url)+'\\';document.getElementById(\\'locale\\').value=\\''+esc(r.locale||'')+'\\';window.scrollTo({top:0,behavior:\\'smooth\\'})">';
      html += '<td><strong>'+esc(r.label)+'</strong></td>';
      html += '<td><code class="rule-code">'+esc(r.url)+'</code></td>';
      html += '<td style="font-weight:700;font-size:18px;color:'+col+'">'+r.score.toFixed(0)+'</td>';
      html += '<td>'+esc(r.verdict)+'</td>';
      html += '<td style="font-family:monospace">'+r.blockers+'/'+r.highs+'/'+r.mediums+'</td>';
      html += '</tr>';
    }
  }
  html += '</tbody></table></div>';
  resultEl.innerHTML = html;
}
</script>

</body>
</html>"""


@app.route("/")
def index():
    return DASHBOARD_HTML


@app.route("/api/health")
def health():
    from _secrets import report_health
    from rule_loader import load_all_rules
    return jsonify({"rules_loaded": len(load_all_rules()), "secrets": report_health(), "status": "ok"})


@app.route("/api/run/<run_id>")
def run_by_id(run_id):
    payload = _load_run(run_id)
    if not payload:
        return jsonify({"error": "not found"}), 404
    return jsonify(payload)


@app.route("/api/history")
def history():
    """列出 /tmp/seo-audit-runs/ 的全部 run，最近 50 个"""
    out = []
    if RUN_STORE.exists():
        files = sorted(RUN_STORE.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for p in files[:50]:
            try:
                d = json.loads(p.read_text())
                out.append({
                    "run_id": d.get("run_id"),
                    "url": d.get("url"),
                    "locale": d.get("locale"),
                    "page_type": d.get("page_type"),
                    "score": d.get("score"),
                    "verdict": d.get("verdict"),
                    "blocker": d.get("summary", {}).get("by_severity", {}).get("blocker", 0),
                    "high": d.get("summary", {}).get("by_severity", {}).get("high", 0),
                    "ts": int(p.stat().st_mtime),
                })
            except Exception:
                continue
    return jsonify({"runs": out, "total": len(out)})


@app.route("/api/stats")
def stats():
    """聚合首页指标——总 audit 数 / 平均分 / 守门员问题数 / 覆盖规则数"""
    from rule_loader import load_all_rules
    total_runs = 0
    scores = []
    blockers = 0
    highs = 0
    locales = set()
    if RUN_STORE.exists():
        for p in RUN_STORE.glob("*.json"):
            try:
                d = json.loads(p.read_text())
                total_runs += 1
                s = d.get("score")
                if isinstance(s, (int, float)):
                    scores.append(s)
                bs = d.get("summary", {}).get("by_severity", {})
                blockers += bs.get("blocker", 0)
                highs += bs.get("high", 0)
                if d.get("locale"):
                    locales.add(d["locale"])
            except Exception:
                continue
    return jsonify({
        "audited_pages": total_runs,
        "avg_score": round(sum(scores) / max(1, len(scores)), 1),
        "gatekeeper_blockers": blockers,
        "gatekeeper_highs": highs,
        "locales_covered": sorted(locales),
        "total_rules": len(load_all_rules()),
        "supported_engines": 4,
    })


BATCH_CONCURRENCY = 3  # LLM judge 真启用后并发 3 防 Platform 限流 + 防 LLM rate limit
BATCH_PER_TASK_TIMEOUT = 90  # LLM judge × 多个规则可能慢，单页 90s 上限


PLATFORM_DEFAULT_BATCH = [
    {"label": "Homepage (EN)", "url": "https://example.com/en", "locale": "en"},
    {"label": "Homepage (KO)", "url": "https://example.com/ko", "locale": "ko"},
    {"label": "Homepage (JA)", "url": "https://example.com/ja", "locale": "ja"},
    {"label": "Homepage (RU)", "url": "https://example.com/ru", "locale": "ru"},
    {"label": "Futures", "url": "https://example.com/en/futures", "locale": "en"},
    {"label": "News", "url": "https://www.example.com/en/news", "locale": "en"},
    {"label": "Price BTC", "url": "https://example.com/en/price/btc", "locale": "en"},
    {"label": "Support", "url": "https://example.com/en/support", "locale": "en"},
]


@app.route("/api/batch", methods=["GET", "POST"])
def batch():
    # GET → 默认 Platform 8；POST {urls:[{url,locale,label?}]} → 自定义
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        raw = body.get("urls") or []
        items = []
        for i, it in enumerate(raw):
            if not isinstance(it, dict) or not it.get("url"):
                continue
            items.append({
                "url": it["url"],
                "locale": it.get("locale") or "en",
                "label": it.get("label") or it["url"],
            })
            if len(items) >= 20:  # 防滥用：单次 batch 上限 20
                break
        if not items:
            return jsonify({"error": "POST body needs {urls:[{url,locale}]}"}), 400
        PLATFORM_LIST = items
    else:
        PLATFORM_LIST = PLATFORM_DEFAULT_BATCH

    async def _run_all():
        sem = asyncio.Semaphore(BATCH_CONCURRENCY)

        # 批量任务复用 rules_map 避免每页重复加载（性能优化）
        try:
            from _router import get_router
            shared_rules_map = get_router().load_all_rules()
        except Exception:
            shared_rules_map = {}

        async def _one(label, url, locale):
            async with sem:
                try:
                    orch = Orchestrator()
                    r = await asyncio.wait_for(orch.audit(url=url, locale=locale),
                                                timeout=BATCH_PER_TASK_TIMEOUT)
                    # 提取 composite + 完整 enriched findings（与单页 audit 一致）
                    composite_b = {}
                    for o_inner in r.agent_outputs:
                        if o_inner.agent == "crawler" and o_inner.artifacts.get("composite_scores"):
                            composite_b = o_inner.artifacts["composite_scores"]
                            break
                    page_type_b = r.target.page_type if hasattr(r, "target") and r.target else None
                    all_findings_b = []
                    for sev_findings in r.findings_by_severity.values():
                        for fb in sev_findings:
                            all_findings_b.append(_enrich(fb, shared_rules_map, page_type=page_type_b))
                    # batch 也 persist 到 run store，让 hero stats / history / 批量导出共用同一份数据
                    try:
                        _persist_run(r.run_id, {
                            "run_id": r.run_id, "url": url, "locale": locale, "label": label,
                            "page_type": page_type_b,
                            "score": r.brand_seo_score, "verdict": r.final_verdict.value,
                            "composite": composite_b,
                            "findings": all_findings_b,
                            "skipped_rules": list(r.skipped_rules or []),
                            "summary": {
                                "total_findings": len(all_findings_b),
                                "by_severity": {
                                    "blocker": sum(1 for f in all_findings_b if f["severity"] == "blocker"),
                                    "high": sum(1 for f in all_findings_b if f["severity"] == "high"),
                                    "medium": sum(1 for f in all_findings_b if f["severity"] == "medium"),
                                    "low": sum(1 for f in all_findings_b if f["severity"] == "low"),
                                },
                            },
                            "batch": True,
                        })
                    except Exception as pe:
                        app.logger.warning(f"batch_persist_failed {pe}")
                    return {"label": label, "url": url, "locale": locale,
                            "run_id": r.run_id,
                            "score": r.brand_seo_score, "verdict": r.final_verdict.value,
                            "page_type": page_type_b,
                            "blockers": sum(1 for f in all_findings_b if f["severity"] == "blocker"),
                            "highs": sum(1 for f in all_findings_b if f["severity"] == "high"),
                            "mediums": sum(1 for f in all_findings_b if f["severity"] == "medium")}
                except asyncio.TimeoutError:
                    return {"label": label, "url": url, "error": f"timeout >{BATCH_PER_TASK_TIMEOUT}s"}
                except Exception as e:
                    return {"label": label, "url": url, "error": str(e)}

        return await asyncio.gather(*[_one(it["label"], it["url"], it["locale"]) for it in PLATFORM_LIST])

    import time
    t0 = time.time()
    results = asyncio.run(_run_all())
    elapsed = round(time.time() - t0, 1)
    scored = [r for r in results if "score" in r]
    avg = sum(r["score"] for r in scored) / max(1, len(scored))
    return jsonify({"results": results, "avg_score": avg,
                    "elapsed_seconds": elapsed,
                    "concurrency": BATCH_CONCURRENCY,
                    "succeeded": len(scored), "failed": len(results) - len(scored)})


@app.route("/api/rules")
def rules():
    from _router import get_router
    return jsonify(get_router().stats(locale=request.args.get("locale"), page_type=request.args.get("page_type"), command=request.args.get("command", "audit")))


def _enrich(f, rules_map, page_type=None):
    from fix_guide import generate_fix_guide
    from _modes import classify_rule
    rule = rules_map.get(f.id, {})
    tags = rule.get("tags", [])
    sev = f.severity.value
    base = {
        "id": f.id, "severity": sev, "confidence": f.confidence, "recommendation": f.recommendation,
        "evidence_snippet": (f.evidence.text_snippet[:200] if f.evidence and f.evidence.text_snippet else None),
        "source": rule.get("source"), "source_doc_url": rule.get("source_url"),
        "platform_impact": rule.get("platform_business_impact", "").strip(), "tags": tags,
        "patch_template": f.patch_hint.template if f.patch_hint else None,
        "human_review_required": rule.get("human_review_required", False),
        "platform": f.platform.value if hasattr(f.platform, 'value') else str(f.platform),
        "mode": classify_rule(f.id, sev, tags, page_type=page_type, rule_applies_to=rule.get("applies_to")),
    }
    fg = generate_fix_guide(base)
    if fg:
        base["fix_guide"] = fg
    return base


def _action_plan(findings, composite):
    sw = {"blocker": 100, "high": 60, "medium": 30, "low": 10, "info": 0}
    em = {"P0": 1, "P1": 2, "P2": 3, "P3": 5}
    actions = []
    for f in findings:
        actions.append({
            "rule_id": f["id"], "severity": f["severity"], "mode": f["mode"],
            "recommendation": f["recommendation"],
            "estimated_effort_days": em.get(f.get("patch_priority", "P2"), 3),
            "impact_score": sw.get(f["severity"], 0),
            "roi": round(sw.get(f["severity"], 0) / max(1, em.get(f.get("patch_priority", "P2"), 3)), 1),
            "platform_impact": f.get("platform_impact"),
        })
    return sorted(actions, key=lambda x: (x["mode"] != "gatekeeper", -x["roi"]))[:10]


@app.route("/api/audit", methods=["POST"])
def audit():
    data = request.get_json()
    url = data.get("url")
    locale = data.get("locale") or None
    no_cache = bool(data.get("no_cache", False))
    if not url:
        return jsonify({"error": "missing url"}), 400

    orch = Orchestrator()
    report = asyncio.run(orch.audit(url=url, locale=locale, no_cache=no_cache))

    gsc_data: dict = {}
    try:
        from integrations import gsc as _gsc
        if _gsc.is_configured():
            gsc_data = asyncio.run(_gsc.url_inspection(url))
    except Exception as e:
        app.logger.warning(f"gsc_inspection_failed url={url} err={e}")
        gsc_data = {"skipped": True, "reason": "gsc_exception", "detail": str(e)[:200]}

    composite = {}
    for o in report.agent_outputs:
        if o.agent == "crawler" and o.artifacts.get("composite_scores"):
            composite = o.artifacts["composite_scores"]
            break

    try:
        from _router import get_router
        rules_map = get_router().load_all_rules()
    except Exception:
        rules_map = {}

    page_type = report.target.page_type if hasattr(report, "target") and report.target else None
    all_findings = []
    for sev_findings in report.findings_by_severity.values():
        for f in sev_findings:
            all_findings.append(_enrich(f, rules_map, page_type=page_type))

    from _modes import mode_summary
    payload = {
        "url": url, "locale": locale, "page_type": page_type,
        "score": report.brand_seo_score, "verdict": report.final_verdict.value,
        "composite": composite, "findings": all_findings,
        "action_plan": _action_plan(all_findings, composite),
        "skipped_rules": list(report.skipped_rules or []),
        "summary": {
            "total_findings": len(all_findings),
            "by_severity": {s: sum(1 for f in all_findings if f["severity"] == s) for s in ["blocker", "high", "medium", "low", "info"]},
            "by_mode": mode_summary(all_findings),
            "skipped_count": len(report.skipped_rules or []),
        },
        "run_id": report.run_id, "trace_id": report.trace_id,
        "gsc": gsc_data,
    }
    _persist_run(report.run_id, payload)
    return jsonify(payload)


RUN_STORE = Path("/tmp/seo-audit-runs")
RUN_STORE.mkdir(parents=True, exist_ok=True)


def _persist_run(run_id: str, payload: dict) -> None:
    try:
        (RUN_STORE / f"{run_id}.json").write_text(json.dumps(payload, ensure_ascii=False, default=str))
    except Exception as e:
        app.logger.warning(f"persist_run_failed run_id={run_id} err={e}")


def _load_run(run_id: str) -> dict | None:
    p = RUN_STORE / f"{run_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


@app.route("/api/export-markdown", methods=["POST"])
def export_markdown():
    from datetime import datetime
    data = request.get_json() or {}
    ad = None
    run_id = data.get("run_id")
    if run_id:
        ad = _load_run(run_id)
    if ad is None:
        ad = data.get("audit_data") or {}
    if not ad:
        return jsonify({"error": "run_id not found and no audit_data fallback"}), 404
    gate = [f for f in ad.get("findings", []) if f.get("mode") == "gatekeeper"]
    opt = [f for f in ad.get("findings", []) if f.get("mode") == "optimizer"]
    _engine_labels = {"google":"Google","naver":"Naver","yandex":"Yandex","yahoo-japan":"Yahoo!JAPAN","google+yahoo-jp":"Google + Yahoo!JAPAN"}
    eng = _engine_labels.get((ad.get("composite") or {}).get("_primary_engine"), "Google")
    md = [
        f"# Platform SEO 深度分析与整改方案",
        f"",
        f"> URL: {ad.get('url')}",
        f"> 时间: {datetime.utcnow().isoformat()}",
        f"",
        f"## 一句话结论",
        f"",
        f"**{('🛑 不可上线 — 守门员有 ' + str(len(gate)) + ' 个问题') if gate else ('✅ 可以上线' if ad.get('score', 0) >= 80 else '🟡 可上线但建议优化')}**",
        f"",
        f"- Brand SEO Score: **{ad.get('score', 0):.0f} / 100**",
        f"- 守门员问题: **{len(gate)}**（必修）",
        f"- 优化机会: **{len(opt)}**（建议）",
        f"",
        f"---",
        f"",
        f"## 🛑 守门员审核（Google + 合规底线 · 全平台必修）" + (f"\n> 当前主搜索引擎: {eng}（守门规则按 Google 全球合规执行）" if eng != "Google" else ""),
        f"",
    ]
    if not gate:
        md.append("✅ 全部通过 · 无 Manual Action 风险")
    else:
        for f in gate:
            md.extend([f"### `{f['id']}` <span>[{f['severity']}]</span>", "",
                       f"- **修复建议**: {f.get('recommendation', '—')}", ""])
            if f.get("platform_impact"):
                md.append(f"- **对 Platform**: {f['platform_impact']}")
                md.append("")
            fg = f.get("fix_guide", {})
            if fg:
                if fg.get("steps"):
                    md.append("**修复步骤**:")
                    for j, s in enumerate(fg["steps"], 1):
                        md.append(f"{j}. {s['title']}")
                        if s.get("code_after"):
                            md.extend([f"   ```{s.get('language', '')}", f"   {s['code_after']}", "   ```"])
                    md.append("")
                if fg.get("effort_minutes"):
                    md.append(f"⏱️ 工时: {fg['effort_minutes']} 分钟")
                if fg.get("expected_impact"):
                    md.append(f"📈 预期: {fg['expected_impact']}")
                md.append("")
            md.append("---")
            md.append("")

    md.extend([f"## 🚀 优化机会（按 ROI · 建议）", ""])
    if not opt:
        md.append("✅ 已是最佳实践")
    else:
        for f in opt:
            md.extend([f"### `{f['id']}` [{f['severity']}]",
                       f"- {f.get('recommendation', '—')}", ""])
            if f.get("platform_impact"):
                md.append(f"- **对 Platform**: {f['platform_impact'][:200]}")
            md.append("")
    md.append("\n*本报告由 Multi-Engine SEO Audit Skill 生成，可粘贴到飞书 / Notion / GitHub 等支持 Markdown 的工具。*")

    return jsonify({"markdown": "\n".join(md), "filename": f"platform-seo-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.md"})


@app.route("/api/export-batch-markdown", methods=["POST"])
def export_batch_markdown():
    """批量导出：8 页（或自定义 batch）汇总 Markdown 报告
    支持 {run_ids:[...]} 或 {results:[{run_id|url|label|score|blockers|highs|mediums}]}
    """
    from datetime import datetime
    from collections import defaultdict
    body = request.get_json() or {}
    run_ids = body.get("run_ids") or []
    fallback = body.get("results") or []

    # 优先按 run_ids 加载完整数据；否则用 fallback 的 summary
    pages = []
    if run_ids:
        for rid in run_ids:
            ad = _load_run(rid)
            if ad:
                pages.append(ad)
    if not pages and fallback:
        # fallback：只用 results summary（没 findings 详细数据）
        for r in fallback:
            if r.get("run_id"):
                ad = _load_run(r["run_id"])
                if ad:
                    pages.append(ad); continue
            # 完全 fallback：当 placeholder（无 findings）
            pages.append({
                "url": r.get("url"), "label": r.get("label"),
                "locale": r.get("locale"), "score": r.get("score", 0),
                "verdict": r.get("verdict", "未知"),
                "findings": [],
                "summary": {"by_severity": {
                    "blocker": r.get("blockers", 0), "high": r.get("highs", 0),
                    "medium": r.get("mediums", 0), "low": r.get("lows", 0),
                }},
            })

    if not pages:
        return jsonify({"error": "no batch data: pass run_ids or results"}), 404

    def _label(p):
        return p.get("label") or (p.get("url", "")[:50])

    # 全局汇总
    total_b = total_h = total_m = total_l = 0
    avg_score = sum(p.get("score", 0) for p in pages) / max(1, len(pages))
    for p in pages:
        sev = (p.get("summary") or {}).get("by_severity") or {}
        total_b += sev.get("blocker", 0)
        total_h += sev.get("high", 0)
        total_m += sev.get("medium", 0)
        total_l += sev.get("low", 0)

    md = [
        "# Platform 多页 SEO 批量审计报告",
        "",
        f"> 生成时间: {datetime.utcnow().isoformat()}Z",
        f"> 页数: {len(pages)} · 平均分: **{avg_score:.1f} / 100**",
        f"> 总计: blockers={total_b} · highs={total_h} · mediums={total_m} · lows={total_l}",
        "",
        "## 📊 总览（按 score 排序）",
        "",
        "| Page | URL | Score | B/H/M/L | Verdict |",
        "|------|-----|------:|---------|---------|",
    ]
    for p in sorted(pages, key=lambda x: -x.get("score", 0)):
        sev = (p.get("summary") or {}).get("by_severity") or {}
        b, h, m, lo = sev.get("blocker", 0), sev.get("high", 0), sev.get("medium", 0), sev.get("low", 0)
        bhm = f"{b}/{h}/{m}/{lo}"
        url = p.get("url", "")
        score = p.get("score", 0)
        md.append(f"| {_label(p)} | {url} | {score:.0f} | {bhm} | {p.get('verdict', '')} |")
    md.append("")

    # 跨页问题聚合（高 ROI 抓手）
    agg = defaultdict(lambda: {"pages": [], "sev": None, "reco": None, "platform_impact": None})
    for p in pages:
        for f in p.get("findings", []) or []:
            if f.get("severity") not in ("blocker", "high"):
                continue
            rid = f.get("id", "")
            agg[rid]["pages"].append(_label(p))
            agg[rid]["sev"] = f.get("severity")
            agg[rid]["reco"] = f.get("recommendation", "")
            agg[rid]["platform_impact"] = (f.get("platform_impact") or "")[:200]

    if agg:
        md.extend([
            "## 🎯 跨页问题聚合（高 ROI 修复抓手）",
            "",
            "**按「修一处影响 N 页」排序——优先修命中 ≥ 3 页的规则**",
            "",
            "| 命中页数 | 严重度 | 规则 ID | 命中页 | 推荐修复 |",
            "|---------:|--------|---------|--------|----------|",
        ])
        for rid, info in sorted(agg.items(), key=lambda x: (-len(x[1]["pages"]), x[1]["sev"])):
            flag = "🛑" if info["sev"] == "blocker" else "🔴"
            md.append(f"| {flag} {len(info['pages'])} | {info['sev']} | `{rid}` | {', '.join(info['pages'])} | {info['reco'][:120]} |")
        md.append("")

    # 每页详细 findings
    md.extend(["## 🔍 每页详细 findings（blocker + high）", ""])
    for p in sorted(pages, key=lambda x: x.get("score", 0)):  # 低分页排前，优先治理
        gate = [f for f in (p.get("findings", []) or []) if f.get("mode") == "gatekeeper"]
        opt_high = [f for f in (p.get("findings", []) or []) if f.get("mode") == "optimizer" and f.get("severity") == "high"]
        md.extend([
            f"### {_label(p)} · score={p.get('score', 0):.0f}",
            f"> URL: {p.get('url', '')} · locale: `{p.get('locale', '')}` · verdict: **{p.get('verdict', '')}**",
            "",
        ])
        if not gate and not opt_high:
            md.append("✓ 守门员全部通过，且无 high 优化建议"); md.append("")
            continue
        if gate:
            md.append("**🛑 守门员（必修）**:")
            md.append("")
            for f in gate:
                md.append(f"- `[{f['severity']}]` `{f['id']}` — {f.get('recommendation', '')[:200]}")
            md.append("")
        if opt_high:
            md.append("**🔴 高优先级优化（建议）**:")
            md.append("")
            for f in opt_high:
                md.append(f"- `[{f['severity']}]` `{f['id']}` — {f.get('recommendation', '')[:200]}")
            md.append("")
        md.append("---"); md.append("")

    md.append("")
    md.append("## 📦 配套交付")
    md.append("")
    md.append("- 详细 patch 包: `/Users/coco/.claude/skills/seo-audit/deliverables/`（5 个可直接 apply 的 fix 文件）")
    md.append("- 单页 audit 详情: 任意 Platform 工程师在本机起 dashboard 后查任意 run_id")
    md.append("")
    md.append("*本报告由 Multi-Engine SEO Audit Skill 生成 · 可粘贴到飞书 / Notion / GitHub*")

    return jsonify({
        "markdown": "\n".join(md),
        "filename": f"platform-seo-batch-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.md",
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    # 安全默认：仅本机回环（127.0.0.1）— 避免局域网暴露
    # 如需公网/局域网访问：HOST=0.0.0.0 + 加 basic auth + tunnel 鉴权
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=False)
