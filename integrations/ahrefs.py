"""Ahrefs CSV 导入 + 基本字段抽取"""
from __future__ import annotations

import csv
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def extract_core_metrics(rows: list[dict]) -> dict:
    """从 Ahrefs site explorer CSV 提取核心字段"""
    if not rows:
        return {}
    return {
        "domain_rating": rows[0].get("DR") or rows[0].get("Domain Rating"),
        "backlinks": rows[0].get("Backlinks"),
        "referring_domains": rows[0].get("Ref. domains") or rows[0].get("Referring domains"),
        "organic_keywords": rows[0].get("Organic keyword") or rows[0].get("Organic keywords"),
        "organic_traffic": rows[0].get("Organic traffic"),
    }
