"""
Platform SEO 增长机会量化报告生成器
基于 batch_audit + composite scores → 算出"修这些能涨多少流量"
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from orchestrator import Orchestrator  # noqa: E402

# 流量基线假设（按 Platform 公开 Ahrefs 数据估算 — 实际换成真实 GSC）
PLATFORM_BASELINE = {
    "monthly_organic_traffic": 250_000,
    "monthly_organic_value_usd": 35_000,
    "avg_conversion_to_signup": 0.02,
    "ltv_per_signup_usd": 180,
}

# Composite 维度 → 流量提升潜力系数（基于行业基准）
COMPOSITE_IMPACT = {
    "eeat": {"max_uplift_pct": 35, "weight": "very_high"},     # YMYL 金融最高
    "schema": {"max_uplift_pct": 15, "weight": "medium"},
    "crawlability": {"max_uplift_pct": 25, "weight": "high"},  # 基础设施
    "performance": {"max_uplift_pct": 8, "weight": "low"},     # CWV 影响小
    "internal_linking": {"max_uplift_pct": 12, "weight": "medium"},
    "geo": {"max_uplift_pct": 18, "weight": "high"},           # LLM 时代新流量
    "multilingual": {"max_uplift_pct": 22, "weight": "high"},  # 9 语言市场
    "image": {"max_uplift_pct": 10, "weight": "medium"},
}


async def gather_audit_data(urls: list[tuple[str, str, str | None]]) -> list[dict]:
    """跑 batch audit 收集每页 composite scores"""
    orch = Orchestrator()
    rows = []
    for label, url, locale in urls:
        try:
            report = await orch.audit(url=url, locale=locale)
            cs = {}
            for o in report.agent_outputs:
                if o.agent == "crawler" and o.artifacts.get("composite_scores"):
                    cs = {k: v.get("composite_score") for k, v in o.artifacts["composite_scores"].items()
                          if isinstance(v, dict) and v.get("composite_score") is not None}
                    break
            rows.append({
                "label": label,
                "url": url,
                "locale": locale,
                "current_score": report.brand_seo_score,
                "verdict": report.final_verdict.value,
                "composite": cs,
            })
        except Exception as e:
            rows.append({"label": label, "url": url, "error": str(e)})
    return rows


def calculate_uplift(composite_score: float | None, max_uplift_pct: float) -> dict:
    """根据 composite 分计算流量提升潜力"""
    if composite_score is None:
        return {"current_score": None, "max_uplift_pct": 0, "estimated_uplift_pct": 0}
    gap = 1.0 - composite_score
    estimated = max_uplift_pct * gap
    return {"current_score": composite_score, "max_uplift_pct": max_uplift_pct, "gap": gap, "estimated_uplift_pct": round(estimated, 1)}


def generate_report(audit_rows: list[dict]) -> dict:
    """聚合所有页面 → 全站维度增长机会"""
    dimensions: dict = {}
    for dim, meta in COMPOSITE_IMPACT.items():
        scores = [r["composite"].get(dim) for r in audit_rows if "composite" in r and r["composite"].get(dim) is not None]
        if not scores:
            continue
        avg = sum(scores) / len(scores)
        uplift = calculate_uplift(avg, meta["max_uplift_pct"])
        dimensions[dim] = {
            "current_avg_score": round(avg, 2),
            "page_count": len(scores),
            "weight": meta["weight"],
            **uplift,
        }

    # 估算总流量增长（保守 — 取各维度独立累加 × 0.6 重叠系数）
    total_uplift_pct = sum(d["estimated_uplift_pct"] for d in dimensions.values()) * 0.6
    monthly_traffic_lift = int(PLATFORM_BASELINE["monthly_organic_traffic"] * total_uplift_pct / 100)
    monthly_value_lift = int(PLATFORM_BASELINE["monthly_organic_value_usd"] * total_uplift_pct / 100)
    annual_value_lift = monthly_value_lift * 12

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "baseline": PLATFORM_BASELINE,
        "audit_summary": {
            "pages_audited": len(audit_rows),
            "avg_score": round(sum(r.get("current_score", 0) for r in audit_rows) / max(1, len(audit_rows)), 1),
        },
        "dimensions": dimensions,
        "projections": {
            "conservative_overlap_factor": 0.6,
            "total_uplift_pct": round(total_uplift_pct, 1),
            "monthly_traffic_lift_estimate": monthly_traffic_lift,
            "monthly_revenue_lift_estimate_usd": monthly_value_lift,
            "annual_revenue_lift_estimate_usd": annual_value_lift,
        },
        "priority_actions": _rank_priorities(dimensions),
        "audit_rows": audit_rows,
    }


def _rank_priorities(dimensions: dict) -> list[dict]:
    """按"提升潜力 × 工程量"排序"""
    effort_estimate = {
        "eeat": "5 days",
        "schema": "2 days",
        "crawlability": "3 days",
        "performance": "5 days",
        "internal_linking": "3 days",
        "geo": "4 days",
        "multilingual": "10 days",
        "image": "2 days",
    }
    priorities = []
    for dim, data in dimensions.items():
        roi_score = data["estimated_uplift_pct"] / max(1, len(effort_estimate.get(dim, "5 days").split()[0]))
        priorities.append({
            "dimension": dim,
            "current_score": data["current_avg_score"],
            "estimated_uplift_pct": data["estimated_uplift_pct"],
            "engineering_effort": effort_estimate.get(dim, "5 days"),
            "roi_score": round(roi_score, 2),
        })
    return sorted(priorities, key=lambda x: -x["roi_score"])


def render_md(report: dict) -> str:
    out = ["# Platform SEO 增长机会量化报告\n",
           f"> 生成时间：{report['generated_at']}",
           f"> 基线流量：{report['baseline']['monthly_organic_traffic']:,} / 月",
           f"> 基线价值：${report['baseline']['monthly_organic_value_usd']:,} / 月\n",
           "---\n## 📊 全站现状",
           f"- 审核页面：**{report['audit_summary']['pages_audited']}** 个",
           f"- 平均 Brand SEO Score：**{report['audit_summary']['avg_score']} / 100**\n",
           "---\n## 🎯 8 个维度的提升机会\n",
           "| 维度 | 当前均分 | 最大潜力 | 估算提升 | 工程量 | ROI |",
           "|---|---|---|---|---|---|"]
    for p in report["priority_actions"]:
        dim = p["dimension"]
        d = report["dimensions"].get(dim, {})
        out.append(f"| **{dim}** | {p['current_score']:.2f} | {d.get('max_uplift_pct')}% | **+{p['estimated_uplift_pct']}%** | {p['engineering_effort']} | {p['roi_score']} |")
    proj = report["projections"]
    out.extend([
        "\n---\n## 💰 收益预测（保守估算）\n",
        f"- 总流量提升潜力：**+{proj['total_uplift_pct']}%**（叠加系数 {proj['conservative_overlap_factor']}）",
        f"- 月度流量增量：**+{proj['monthly_traffic_lift_estimate']:,}** 访问",
        f"- 月度营收增量：**+${proj['monthly_revenue_lift_estimate_usd']:,}**",
        f"- **年度营收增量：${proj['annual_revenue_lift_estimate_usd']:,}**",
        "\n---\n## 🏗️ 建议执行顺序\n",
    ])
    for i, p in enumerate(report["priority_actions"][:5], 1):
        out.append(f"### Phase {i}: 修复 {p['dimension']}（{p['engineering_effort']}）")
        d = report["dimensions"].get(p["dimension"], {})
        out.extend([
            f"- 当前均分：{p['current_score']:.2f}",
            f"- 估算流量提升：**+{p['estimated_uplift_pct']}%**",
            f"- ROI 分：{p['roi_score']}\n",
        ])
    out.extend([
        "\n---\n## 📄 各页面明细\n",
        "| 页面 | URL | Score | Verdict |",
        "|---|---|---|---|"
    ])
    for r in report["audit_rows"]:
        if "error" in r:
            out.append(f"| {r['label']} | {r['url']} | — | Error |")
        else:
            out.append(f"| {r['label']} | {r['url']} | {r.get('current_score', 0):.0f} | {r.get('verdict', '?')} |")
    out.append("\n---\n*本报告由 Multi-Engine SEO Audit Skill 自动生成。具体修复方案见 `PLATFORM_REMEDIATION_PLAN.md`。*")
    return "\n".join(out)


async def main():
    urls = [
        ("homepage", "https://example.com", None),
        ("futures", "https://example.com/en/futures", "en"),
        ("learn", "https://example.com/en/learn", "en"),
        ("price", "https://example.com/en/price/btc", "en"),
        ("support", "https://example.com/en/support", "en"),
        ("homepage-ko", "https://example.com/ko", "ko"),
        ("homepage-ja", "https://example.com/ja", "ja"),
    ]
    print("📊 跑 7 个核心页面 audit...")
    rows = await gather_audit_data(urls)
    report = generate_report(rows)

    out_path = SKILL_ROOT / "snapshots" / f"growth-opportunity-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_md(report))
    json_path = out_path.with_suffix(".json")
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print(f"\n✅ Report saved:")
    print(f"   {out_path.relative_to(SKILL_ROOT)}")
    print(f"   {json_path.relative_to(SKILL_ROOT)}")

    proj = report["projections"]
    print(f"\n🎯 关键数据 (Platform CTO 汇报口径):")
    print(f"   • 总流量提升潜力: +{proj['total_uplift_pct']}%")
    print(f"   • 月度营收增量: +${proj['monthly_revenue_lift_estimate_usd']:,}")
    print(f"   • 年度营收增量: +${proj['annual_revenue_lift_estimate_usd']:,}")
    print(f"\n🏆 ROI 最高的 3 个修复方向:")
    for i, p in enumerate(report["priority_actions"][:3], 1):
        print(f"   {i}. {p['dimension']}: +{p['estimated_uplift_pct']}% / {p['engineering_effort']} (ROI={p['roi_score']})")


if __name__ == "__main__":
    asyncio.run(main())
