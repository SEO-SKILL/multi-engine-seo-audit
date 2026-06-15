"""
批量 audit Platform 关键页面（校准期工具）
用法：uv run python scripts/batch_audit.py
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

PLATFORM_KEY_URLS = [
    ("https://example.com", "homepage", None),
    ("https://example.com/en/futures", "futures", "en"),
    ("https://example.com/en/copy-trading", "copy-trading", "en"),
    ("https://example.com/en/learn", "learn", "en"),
    ("https://example.com/en/price/btc", "price", "en"),
    ("https://example.com/en/support", "support", "en"),
    ("https://example.com/ko", "homepage-ko", "ko"),
    ("https://example.com/ja", "homepage-ja", "ja"),
    ("https://example.com/ru", "homepage-ru", "ru"),
    ("https://example.com/zh-CN", "homepage-zh", "zh-CN"),
]


async def run_batch() -> dict:
    orch = Orchestrator()
    results = []
    summary = {"total": 0, "blocker_count": 0, "high_count": 0, "score_avg": 0.0}

    for url, label, locale in PLATFORM_KEY_URLS:
        print(f"\n[{label}] auditing {url}...")
        try:
            report = await orch.audit(url=url, locale=locale)
            blocker = len(report.findings_by_severity.get("blocker", []))
            high = len(report.findings_by_severity.get("high", []))
            medium = len(report.findings_by_severity.get("medium", []))
            low = len(report.findings_by_severity.get("low", []))

            results.append({
                "label": label,
                "url": url,
                "locale": locale,
                "final_verdict": report.final_verdict.value,
                "brand_seo_score": report.brand_seo_score,
                "blocker": blocker,
                "high": high,
                "medium": medium,
                "low": low,
                "top_findings": [f.id for sev_findings in report.findings_by_severity.values() for f in sev_findings[:3]][:5],
            })
            summary["total"] += 1
            summary["blocker_count"] += blocker
            summary["high_count"] += high
            summary["score_avg"] += report.brand_seo_score
            print(f"  → Score: {report.brand_seo_score:.1f}, Verdict: {report.final_verdict.value}, Findings: B={blocker} H={high} M={medium} L={low}")
        except Exception as e:
            print(f"  → FAILED: {e}")
            results.append({"label": label, "url": url, "error": str(e)})

    if summary["total"]:
        summary["score_avg"] /= summary["total"]

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "summary": summary,
        "results": results,
    }

    out_path = SKILL_ROOT / "snapshots" / f"batch-audit-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n📊 Snapshot saved: {out_path.relative_to(SKILL_ROOT)}")
    print(f"\n=== Summary ===")
    print(f"Total audited: {summary['total']}")
    print(f"Total blockers: {summary['blocker_count']}")
    print(f"Total high: {summary['high_count']}")
    print(f"Average Brand SEO Score: {summary['score_avg']:.1f}/100")

    return output


if __name__ == "__main__":
    asyncio.run(run_batch())
