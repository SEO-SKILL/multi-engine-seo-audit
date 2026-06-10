"""
competitor-agent — 竞品深度情报快照
对应能力 #8
V1：Ahrefs CSV 导入 + 基本对比
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

from agents._schema import AgentInput, AgentOutput, AgentStatus, Metrics


COMPETITORS = ["binance.com", "bybit.com", "okx.com", "mexc.com", "weex.com", "coinglass.com"]


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)

    # V1: 只检查 Ahrefs CSV 是否存在并读取基础指标
    ahrefs_dir = Path.home() / ".claude/skills/seo-audit/data/ahrefs/"
    artifacts = {"competitors_summary": {}, "ahrefs_csv_loaded": False}

    if ahrefs_dir.exists():
        for csv_file in ahrefs_dir.glob("*.csv"):
            try:
                with csv_file.open() as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                artifacts["competitors_summary"][csv_file.stem] = {
                    "row_count": len(rows),
                    "columns": reader.fieldnames,
                }
                artifacts["ahrefs_csv_loaded"] = True
            except Exception:
                continue

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="competitor",
        status=AgentStatus.OK if artifacts["ahrefs_csv_loaded"] else AgentStatus.SKIPPED,
        artifacts=artifacts,
        next_actions=["Place Ahrefs CSV export in ~/.claude/skills/seo-audit/data/ahrefs/"] if not artifacts["ahrefs_csv_loaded"] else [],
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )
