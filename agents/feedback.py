"""
F7 — Feedback Loop（自进化）
用户标"准 / 误报 / 补充" → 自动校准规则置信度 + 触发规则修订 PR
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import yaml

SKILL_ROOT = Path(__file__).parent.parent
FEEDBACK_DIR = SKILL_ROOT / "feedback"
FEEDBACK_LOG = FEEDBACK_DIR / "feedback_log.jsonl"


def record_feedback(rule_id: str, finding_trace_id: str, verdict: str, notes: str | None = None) -> dict:
    """记录单条用户反馈

    verdict: 'accurate' | 'false_positive' | 'missed' | 'supplement'
    """
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "rule_id": rule_id,
        "finding_trace_id": finding_trace_id,
        "verdict": verdict,
        "notes": notes,
    }
    with FEEDBACK_LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def calibration_summary(rule_id: str | None = None) -> dict:
    """聚合反馈得到规则置信度校准建议"""
    if not FEEDBACK_LOG.exists():
        return {"total_feedback": 0}

    by_rule: dict = {}
    with FEEDBACK_LOG.open() as f:
        for line in f:
            entry = json.loads(line)
            rid = entry["rule_id"]
            if rule_id and rid != rule_id:
                continue
            by_rule.setdefault(rid, {"accurate": 0, "false_positive": 0, "missed": 0, "supplement": 0})
            by_rule[rid][entry["verdict"]] = by_rule[rid].get(entry["verdict"], 0) + 1

    summary = []
    for rid, counts in by_rule.items():
        total = sum(counts.values())
        if total < 3:
            continue
        precision = counts["accurate"] / max(1, counts["accurate"] + counts["false_positive"])
        recall_signal = counts["missed"]
        adjustment = 0
        if counts["false_positive"] >= 5 and precision < 0.7:
            adjustment = -0.10
        elif counts["accurate"] >= 10 and precision > 0.95:
            adjustment = +0.05
        summary.append({
            "rule_id": rid,
            "total_feedback": total,
            "precision": precision,
            "false_positive_count": counts["false_positive"],
            "missed_count": recall_signal,
            "suggested_confidence_adjustment": adjustment,
        })
    return {"total_feedback": sum(sum(c.values()) for c in by_rule.values()), "by_rule": summary}


def apply_calibration_to_rules(dry_run: bool = True) -> dict:
    """根据 feedback 自动调整规则 confidence_default"""
    calibration = calibration_summary()
    applied = []
    for entry in calibration.get("by_rule", []):
        if entry["suggested_confidence_adjustment"] == 0:
            continue
        rule_files = list((SKILL_ROOT / "rules").rglob("*.yaml"))
        for f in rule_files:
            try:
                data = yaml.safe_load(f.read_text())
                if not isinstance(data, dict):
                    continue
                modified = False
                for rule in data.get("rules", []):
                    if rule.get("id") == entry["rule_id"]:
                        old = rule.get("confidence_default", 0.85)
                        new = max(0.1, min(1.0, old + entry["suggested_confidence_adjustment"]))
                        if not dry_run:
                            rule["confidence_default"] = new
                            modified = True
                        applied.append({"rule_id": entry["rule_id"], "old": old, "new": new})
                if modified:
                    f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
            except Exception:
                continue
    return {"applied_count": len(applied), "dry_run": dry_run, "details": applied[:10]}


def feedback_button_html(rule_id: str, finding_trace_id: str) -> str:
    """生成 HTML 报告中的反馈按钮"""
    return f"""<div class="finding-feedback" data-rule="{rule_id}" data-trace="{finding_trace_id}">
  <button class="fb-accurate" onclick="recordFeedback('{rule_id}','{finding_trace_id}','accurate')">👍 准</button>
  <button class="fb-fp" onclick="recordFeedback('{rule_id}','{finding_trace_id}','false_positive')">👎 误报</button>
  <button class="fb-supp" onclick="recordFeedback('{rule_id}','{finding_trace_id}','supplement')">➕ 补充</button>
</div>"""


def quarterly_review() -> dict:
    """季度回顾：精度趋势 + 高频误报规则"""
    cal = calibration_summary()
    if not cal.get("by_rule"):
        return {"review": "insufficient_data"}

    sorted_by_fp = sorted(cal["by_rule"], key=lambda x: -x["false_positive_count"])[:10]
    sorted_by_precision = sorted(cal["by_rule"], key=lambda x: x["precision"])[:10]

    return {
        "top_false_positive_rules": [{"rule_id": r["rule_id"], "fp_count": r["false_positive_count"]} for r in sorted_by_fp],
        "lowest_precision_rules": [{"rule_id": r["rule_id"], "precision": r["precision"]} for r in sorted_by_precision],
        "total_feedback_collected": cal["total_feedback"],
    }
