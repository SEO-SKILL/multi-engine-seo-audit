"""
compare-agent — 竞品 SEO 对比
对应能力 #8 + PRD §6.3 场景 3
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, select_autoescape

SKILL_ROOT = Path(__file__).parent.parent


async def compare_pages(self_url: str, competitor_urls: list[str], output_path: str | None = None) -> dict:
    """对比 Platform 与 N 个竞品页面，输出 HTML 仪表盘"""
    from orchestrator import Orchestrator
    orch = Orchestrator()

    all_urls = [("self", self_url)] + [(f"competitor-{i+1}", u) for i, u in enumerate(competitor_urls)]

    results = []
    for label, url in all_urls:
        try:
            report = await orch.audit(url=url)
            cs = {}
            for o in report.agent_outputs:
                if o.agent == "crawler" and o.artifacts.get("composite_scores"):
                    cs = {k: v.get("composite_score") for k, v in o.artifacts["composite_scores"].items()
                          if isinstance(v, dict) and v.get("composite_score") is not None}
                    break
            results.append({
                "label": label,
                "url": url,
                "score": report.brand_seo_score,
                "verdict": report.final_verdict.value,
                "blockers": len(report.findings_by_severity.get("blocker", [])),
                "highs": len(report.findings_by_severity.get("high", [])),
                "composite": cs,
            })
        except Exception as e:
            results.append({"label": label, "url": url, "error": str(e)})

    # 渲染对比 HTML
    if not output_path:
        run_id = f"compare-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"
        output_path = SKILL_ROOT / "snapshots" / f"{run_id}.html"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = _render_compare_html(results)
    output_path.write_text(html)

    return {"output_path": str(output_path), "results": results}


def _render_compare_html(results: list[dict]) -> str:
    composite_dims = ["eeat", "schema", "crawlability", "performance", "internal_linking", "geo", "multilingual"]

    rows_html = []
    for r in results:
        if "error" in r:
            rows_html.append(f"<tr><td>{r['label']}</td><td colspan='10'>Error: {r['error']}</td></tr>")
            continue
        cs = r.get("composite", {})
        cells = "".join(
            f'<td style="text-align:center;">{cs.get(d, "N/A") if isinstance(cs.get(d), str) else f"{cs.get(d):.2f}" if cs.get(d) is not None else "N/A"}</td>'
            for d in composite_dims
        )
        rows_html.append(
            f'<tr>'
            f'<td><strong>{r["label"]}</strong><br><code style="font-size:11px;">{r["url"][:60]}</code></td>'
            f'<td style="text-align:center;font-weight:bold;color:var(--brand-orange);font-size:20px;">{r["score"]:.0f}</td>'
            f'<td style="text-align:center;">{r["verdict"]}</td>'
            f'<td style="text-align:center;">{r["blockers"]}</td>'
            f'<td style="text-align:center;">{r["highs"]}</td>'
            f'{cells}'
            f'</tr>'
        )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Platform SEO Compare</title>
<style>
:root {{ --brand-orange: #FF6B00; --brand-orange-light: #FFE4D0; }}
body {{ font-family: -apple-system, sans-serif; padding: 32px; }}
h1 {{ color: var(--brand-orange); }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: var(--brand-orange-light); padding: 12px 8px; text-align: left; }}
td {{ padding: 10px 8px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #fafafa; }}
code {{ background: var(--brand-orange-light); padding: 2px 6px; border-radius: 3px; }}
</style></head><body>
<h1>SEO Compare Dashboard</h1>
<p>Generated: {datetime.utcnow().isoformat()}</p>
<table>
<thead><tr>
  <th>Page</th><th>Score</th><th>Verdict</th><th>B</th><th>H</th>
  <th>EEAT</th><th>Schema</th><th>Crawl</th><th>Perf</th><th>Link</th><th>GEO</th><th>I18N</th>
</tr></thead>
<tbody>{"".join(rows_html)}</tbody>
</table>
</body></html>"""
