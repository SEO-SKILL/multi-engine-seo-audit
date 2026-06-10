"""
roi-predictor (V2) — SEO ROI 预测器
对应能力 #32
"""
from __future__ import annotations

import time

from agents._schema import (
    AgentInput,
    AgentOutput,
    AgentStatus,
    Metrics,
)


async def run(input_: AgentInput) -> AgentOutput:
    start_ms = int(time.time() * 1000)

    candidate_keywords = input_.payload.get("candidate_keywords", [])
    site_dr = input_.payload.get("site_domain_rating", 30)

    predictions = []
    for kw in candidate_keywords:
        pred = _predict_one(kw, site_dr)
        predictions.append(pred)

    return AgentOutput(
        trace_id=input_.trace_id,
        agent="roi_predictor",
        status=AgentStatus.OK,
        artifacts={"predictions": predictions, "model_version": "v1-heuristic"},
        metrics=Metrics(duration_ms=int(time.time() * 1000) - start_ms),
    )


def _predict_one(keyword: dict, site_dr: int) -> dict:
    """启发式 ROI 预测（V2 后期可接 ML 模型）"""
    search_volume = keyword.get("search_volume", 0)
    kw_difficulty = keyword.get("difficulty", 50)
    user_intent = keyword.get("intent", "informational")

    rank_probability = max(0.0, min(1.0, (site_dr - kw_difficulty) / 50 + 0.5))
    estimated_position = 1 + (1 - rank_probability) * 19
    ctr_by_position = {1: 0.32, 2: 0.18, 3: 0.12, 4: 0.08, 5: 0.06, 10: 0.025, 20: 0.01}
    pos_bucket = min(ctr_by_position.keys(), key=lambda x: abs(x - estimated_position))
    estimated_ctr = ctr_by_position[pos_bucket]
    estimated_traffic = int(search_volume * estimated_ctr)

    conversion_by_intent = {"transactional": 0.05, "investigational": 0.02, "informational": 0.005, "navigational": 0.10}
    conv_rate = conversion_by_intent.get(user_intent, 0.005)
    estimated_conversions = int(estimated_traffic * conv_rate)

    return {
        "keyword": keyword.get("term"),
        "search_volume": search_volume,
        "predicted_position": round(estimated_position, 1),
        "estimated_monthly_traffic": estimated_traffic,
        "estimated_monthly_conversions": estimated_conversions,
        "confidence": 0.60,
        "build_recommendation": "yes" if estimated_conversions >= 5 else "no",
    }
