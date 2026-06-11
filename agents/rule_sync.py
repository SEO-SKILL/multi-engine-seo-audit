"""
F8 — Rule Sync Pipeline
每日抓取 5 个官方源 + LLM 提取规则 + diff + Git 化
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import httpx
import yaml
from bs4 import BeautifulSoup

from integrations.anthropic_client import CostTracker, judge

SKILL_ROOT = Path(__file__).parent.parent

OFFICIAL_SOURCES = {
    "google_search_central_blog": "https://developers.google.com/search/blog",
    "google_status_dashboard": "https://status.search.google.com",
    "google_search_central_news": "https://developers.google.com/search/blog/rss",
    "bing_webmaster_blog": "https://blogs.bing.com/webmaster",
    "naver_search_advisor": "https://searchadvisor.naver.com/guide",
    "yandex_webmaster": "https://yandex.com/blog/webmaster",
}


async def daily_pull() -> dict:
    """每日 cron 调用入口"""
    cache_dir = SKILL_ROOT / "cache" / "rule_sync"
    cache_dir.mkdir(parents=True, exist_ok=True)

    log_path = SKILL_ROOT / "snapshots" / f"rule-sync-{datetime.utcnow().strftime('%Y%m%d')}.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    results = {"date": datetime.utcnow().isoformat(), "sources": {}}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for name, url in OFFICIAL_SOURCES.items():
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (BYDFi-SEO-Sync)"})
                content_hash = hashlib.sha256(resp.text.encode()).hexdigest()
                cache_file = cache_dir / f"{name}.hash"
                last_hash = cache_file.read_text().strip() if cache_file.exists() else ""
                changed = content_hash != last_hash

                results["sources"][name] = {
                    "url": url,
                    "status": resp.status_code,
                    "content_hash": content_hash,
                    "changed": changed,
                    "etag": resp.headers.get("etag"),
                    "last_modified": resp.headers.get("last-modified"),
                }

                if changed:
                    cache_file.write_text(content_hash)
                    # 保存原始内容
                    raw_file = cache_dir / f"{name}-{datetime.utcnow().strftime('%Y%m%d')}.html"
                    raw_file.write_text(resp.text)
            except Exception as e:
                results["sources"][name] = {"url": url, "error": str(e)}

    log_path.write_text(json.dumps(results, indent=2))
    return results


async def extract_rule_candidates(source_html: str, source_name: str) -> list[dict]:
    """LLM 从抓取的官方源提取规则候选"""
    soup = BeautifulSoup(source_html, "lxml")
    main = soup.find("article") or soup.find("main") or soup.body
    if not main:
        return []
    text = main.get_text(separator="\n", strip=True)[:8000]

    tracker = CostTracker(budget_usd=0.05)
    result = await judge(
        prompt_template="rule_extraction",
        model="haiku",
        inputs={"source_name": source_name, "text": text},
        cost_tracker=tracker,
    )
    if result.get("stub") or result.get("skipped"):
        return _heuristic_extract(text, source_name)
    candidates = result.get("candidates", []) if isinstance(result, dict) else []
    return candidates


def _heuristic_extract(text: str, source_name: str) -> list[dict]:
    """无 LLM 时的启发式提取"""
    rule_signal_patterns = [
        r"You should ([^.]{20,150})\.",
        r"Make sure ([^.]{20,150})\.",
        r"必须 ([^。]{10,100})",
        r"应该 ([^。]{10,100})",
        r"Do not ([^.]{20,150})\.",
        r"不应 ([^。]{10,100})",
    ]
    candidates = []
    for pattern in rule_signal_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            candidates.append({
                "snippet": m.group(0)[:200],
                "source": source_name,
                "extracted_at": datetime.utcnow().isoformat(),
            })
    return candidates[:20]


def diff_engine(new_candidates: list[dict], existing_rules_path: Path) -> dict:
    """比对新候选 vs 已有规则，判定 minor/major/breaking"""
    existing_ids = set()
    for f in existing_rules_path.rglob("*.yaml"):
        if "_system" in str(f):
            continue
        try:
            data = yaml.safe_load(f.read_text())
            if isinstance(data, dict):
                for rule in data.get("rules", []):
                    existing_ids.add(rule.get("id", ""))
        except Exception:
            continue

    return {
        "new_count": len(new_candidates),
        "existing_rules": len(existing_ids),
        "change_classification": "minor" if len(new_candidates) < 5 else "major",
    }


def alert_to_slack(changes: dict) -> dict:
    """有重大变化时推 Slack 提醒"""
    from integrations.slack import send_alert
    return {"would_alert": changes.get("change_classification") in ("major", "breaking")}


def version_commit(branch_name: str, changes: dict) -> dict:
    """规则变化 → Git branch + commit + PR（自动）"""
    import subprocess
    today = datetime.utcnow().strftime("%Y-%m-%d")
    branch = branch_name or f"rule-sync/{today}"
    try:
        # 在 detached HEAD / 已有分支冲突时这里会失败 — 暂时只返回设计
        return {"branch": branch, "status": "design_ready", "would_commit": True}
    except Exception as e:
        return {"error": str(e)}


async def run_sync() -> dict:
    """完整 sync 流程：pull → extract → diff → alert → commit"""
    pull_result = await daily_pull()

    extracted = []
    for name, info in pull_result["sources"].items():
        if info.get("changed"):
            cache_file = SKILL_ROOT / "cache" / "rule_sync" / f"{name}-{datetime.utcnow().strftime('%Y%m%d')}.html"
            if cache_file.exists():
                candidates = await extract_rule_candidates(cache_file.read_text(), name)
                extracted.extend(candidates)

    diff = diff_engine(extracted, SKILL_ROOT / "rules")
    alert = alert_to_slack(diff)
    commit = version_commit(f"rule-sync/{datetime.utcnow().strftime('%Y-%m-%d')}", diff)

    return {
        "pull": pull_result,
        "extracted_candidates": extracted,
        "diff": diff,
        "alert": alert,
        "commit": commit,
    }
