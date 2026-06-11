"""
BYDFi SEO Audit — Web Dashboard
让非技术人员（Will / Marketing / CTO）通过浏览器跑 audit
部署：fly.io（参考 memory：用户已登录 fly.io）
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent
sys.path.insert(0, str(SKILL_ROOT))

from flask import Flask, jsonify, render_template_string, request  # noqa: E402

from orchestrator import Orchestrator  # noqa: E402

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html><head>
<title>BYDFi SEO Audit Dashboard</title>
<style>
:root {{ --orange: #FF6B00; --orange-light: #FFE4D0; }}
* {{ font-family: -apple-system, sans-serif; box-sizing: border-box; }}
body {{ margin: 0; background: #f5f5f5; }}
header {{ background: var(--orange); color: white; padding: 24px 48px; }}
header h1 {{ margin: 0; font-size: 28px; }}
main {{ max-width: 1100px; margin: 32px auto; padding: 0 24px; }}
.card {{ background: white; border-radius: 12px; padding: 32px; margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
input, select, button {{ font-size: 16px; padding: 12px 16px; border-radius: 8px;
                          border: 1px solid #ddd; }}
input[type=url] {{ width: 60%; }}
button {{ background: var(--orange); color: white; border: 0; cursor: pointer;
         padding: 12px 24px; font-weight: bold; }}
button:hover {{ opacity: 0.9; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
th {{ background: var(--orange-light); padding: 12px; text-align: left; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
.score {{ font-size: 32px; font-weight: bold; color: var(--orange); }}
.score-bad {{ color: #D32F2F; }}
.score-warn {{ color: #F57C00; }}
.score-good {{ color: #7CB342; }}
.composite-bar {{ background: #eee; height: 20px; border-radius: 4px; overflow: hidden; }}
.composite-fill {{ background: var(--orange); height: 100%; }}
.severity-blocker {{ color: #D32F2F; font-weight: bold; }}
.severity-high {{ color: #F57C00; }}
.severity-medium {{ color: #FBC02D; }}
.severity-low {{ color: #7CB342; }}
#loading {{ display: none; padding: 20px; text-align: center; color: var(--orange); }}
.spinner {{ display: inline-block; width: 20px; height: 20px; border: 3px solid var(--orange-light);
            border-top-color: var(--orange); border-radius: 50%; animation: spin 0.8s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>
</head><body>
<header>
  <h1>🚀 BYDFi SEO Audit Dashboard</h1>
  <p>跑 audit → 看 Brand SEO Score + 8 composite + Final Verdict</p>
</header>
<main>
  <div class="card">
    <h2>Audit a URL</h2>
    <form id="audit-form">
      <input type="url" id="url" placeholder="https://bydfi.com" value="https://bydfi.com" required>
      <select id="locale">
        <option value="">Auto-detect</option>
        <option value="en">en</option><option value="zh-CN">zh-CN</option>
        <option value="ja">ja</option><option value="ko">ko</option>
        <option value="ru">ru</option>
      </select>
      <button type="submit">Run Audit</button>
    </form>
    <div id="loading"><div class="spinner"></div> Running 4-UA fetch + 22 agents + 8 composite...</div>
    <div id="result"></div>
  </div>

  <div class="card">
    <h2>📊 Help / Documentation</h2>
    <ul>
      <li><a href="/api/health">Health check (JSON)</a></li>
      <li><a href="/api/rules">Rules library (JSON)</a></li>
      <li>每周 batch: <code>uv run python scripts/batch_audit.py</code></li>
      <li>CLI: <code>uv run python cli.py --help</code></li>
    </ul>
  </div>
</main>
<script>
document.getElementById('audit-form').addEventListener('submit', async (e) => {{
  e.preventDefault();
  document.getElementById('loading').style.display = 'block';
  document.getElementById('result').innerHTML = '';

  const url = document.getElementById('url').value;
  const locale = document.getElementById('locale').value;

  try {{
    const r = await fetch('/api/audit', {{
      method: 'POST', headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{url, locale}})
    }});
    const data = await r.json();
    document.getElementById('loading').style.display = 'none';
    renderResult(data);
  }} catch (e) {{
    document.getElementById('loading').style.display = 'none';
    document.getElementById('result').innerHTML = '<p style="color:red;">Error: ' + e + '</p>';
  }}
}});

function renderResult(data) {{
  const scoreClass = data.score >= 80 ? 'score-good' : data.score >= 60 ? 'score-warn' : 'score-bad';
  let html = '<h3>Result for ' + data.url + '</h3>';
  html += '<div class="score ' + scoreClass + '">' + data.score.toFixed(1) + ' / 100</div>';
  html += '<p><strong>Verdict:</strong> ' + data.verdict + '</p>';

  if (data.composite) {{
    html += '<h4>📊 Composite Scores</h4><table>';
    html += '<tr><th>维度</th><th>分数</th><th>最弱环节</th><th></th></tr>';
    for (const [name, info] of Object.entries(data.composite)) {{
      if (info && info.composite_score !== null) {{
        const score = info.composite_score;
        html += '<tr><td>' + name + '</td><td><strong>' + score.toFixed(2) + '</strong></td>';
        html += '<td><code>' + (info.weakest_link || '—') + '</code></td>';
        html += '<td><div class="composite-bar"><div class="composite-fill" style="width:' + (score * 100) + '%"></div></div></td></tr>';
      }}
    }}
    html += '</table>';
  }}

  if (data.findings && data.findings.length > 0) {{
    html += '<h4>🔍 Findings (' + data.findings.length + ')</h4><table>';
    html += '<tr><th>Severity</th><th>Rule</th><th>Recommendation</th></tr>';
    for (const f of data.findings) {{
      html += '<tr><td class="severity-' + f.severity + '">' + f.severity + '</td>';
      html += '<td><code>' + f.id + '</code></td><td>' + f.recommendation + '</td></tr>';
    }}
    html += '</table>';
  }}

  document.getElementById('result').innerHTML = html;
}}
</script>
</body></html>
"""


@app.route("/")
def index():
    return DASHBOARD_HTML


@app.route("/api/health")
def health():
    from _secrets import report_health
    from rule_loader import load_all_rules
    return jsonify({
        "rules_loaded": len(load_all_rules()),
        "secrets": report_health(),
        "status": "ok",
    })


@app.route("/api/rules")
def rules():
    from _router import get_router
    router = get_router()
    return jsonify(router.stats(
        locale=request.args.get("locale"),
        page_type=request.args.get("page_type"),
        command=request.args.get("command", "audit"),
    ))


@app.route("/api/audit", methods=["POST"])
def audit():
    data = request.get_json()
    url = data.get("url")
    locale = data.get("locale") or None
    if not url:
        return jsonify({"error": "missing url"}), 400

    orch = Orchestrator()
    report = asyncio.run(orch.audit(url=url, locale=locale))

    composite = {}
    for o in report.agent_outputs:
        if o.agent == "crawler" and o.artifacts.get("composite_scores"):
            composite = o.artifacts["composite_scores"]
            break

    all_findings = []
    for sev_findings in report.findings_by_severity.values():
        for f in sev_findings:
            all_findings.append({
                "id": f.id,
                "severity": f.severity.value,
                "confidence": f.confidence,
                "recommendation": f.recommendation,
            })

    return jsonify({
        "url": url,
        "score": report.brand_seo_score,
        "verdict": report.final_verdict.value,
        "composite": composite,
        "findings": all_findings,
        "run_id": report.run_id,
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
