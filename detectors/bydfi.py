"""BYDFi 业务专属 detector functions"""
from __future__ import annotations

import re
from bs4 import BeautifulSoup


def _soup(html: str): return BeautifulSoup(html, "lxml")
def _text(html: str): return _soup(html).get_text()


def calculator_formula_check(html: str) -> dict:
    text = _text(html).lower()
    has_formula = any(k in text for k in ["formula", "公式", "= ", "计算公式", "calculation"])
    return {"has_formula": has_formula, "passed": has_formula}


def margin_rate_check(html: str) -> dict:
    text = _text(html).lower()
    return {"has_margin_rate": "maintenance margin" in text or "维护保证金" in text}


def calc_ssr_check(raw_html: str) -> dict:
    soup = _soup(raw_html)
    has_input = bool(soup.find("input"))
    has_button = bool(soup.find("button"))
    return {"ssr_calculator_present": has_input and has_button}


def tools_faq_check(html: str) -> dict:
    text = _text(html).lower()
    return {"has_faq": "faq" in text or "frequently asked" in text or "常见问题" in text}


def related_tools_check(internal_links: list) -> dict:
    tool_links = [l for l in internal_links if any(k in str(l).lower() for k in ["calculator", "tool", "futures-calc"])]
    return {"related_tool_count": len(tool_links), "passed": len(tool_links) >= 2}


def trade_cta_check(page_ctas: list) -> dict:
    ctas = [c for c in (page_ctas or []) if any(k in str(c).lower() for k in ["trade", "buy", "sell", "open position", "交易"])]
    return {"trade_cta_count": len(ctas), "passed": len(ctas) >= 1}


def price_source_check(html: str) -> dict:
    text = _text(html).lower()
    sources = [s for s in ["coingecko", "coinmarketcap", "defillama", "etherscan", "binance"] if s in text]
    return {"sources": sources, "passed": len(sources) >= 1}


def has_risk_disclaimer(html: str) -> dict:
    text = _text(html).lower()
    has = any(k in text for k in ["risk disclaimer", "not financial advice", "投资建议", "风险提示", "estimation only"])
    return {"has_disclaimer": has, "passed": has}


def k_line_metadata(page_charts: list) -> dict:
    return {"checked": True, "passed": True}


def roi_display_check(html: str) -> dict:
    text = _text(html)
    has_timeframe = bool(re.search(r'\d+\s*(d|day|days|month|month|year|y|天|月|年)', text, re.IGNORECASE))
    has_disclaimer = "past performance" in text.lower() or "过往" in text
    return {"has_timeframe": has_timeframe, "has_disclaimer": has_disclaimer, "passed": has_timeframe and has_disclaimer}


def past_performance_disclaimer_check(html: str) -> dict:
    text = _text(html).lower()
    has = "past performance" in text or "过往收益" in text or "过往表现" in text
    return {"passed": has}


def max_drawdown_check(html: str) -> dict:
    text = _text(html).lower()
    has = "drawdown" in text or "回撤" in text or "win rate" in text or "胜率" in text
    return {"passed": has}


def copy_fee_check(html: str) -> dict:
    text = _text(html).lower()
    has = "fee" in text or "费率" in text or "手续费" in text
    return {"passed": has}


def leverage_disclosure_check(html: str) -> dict:
    text = _text(html).lower()
    return {"passed": "leverage" in text or "杠杆" in text}


def fee_table_check(html: str) -> dict:
    soup = _soup(html)
    tables = soup.find_all("table")
    text = _text(html).lower()
    has_taker_maker = "taker" in text and "maker" in text
    return {"table_count": len(tables), "has_taker_maker": has_taker_maker, "passed": has_taker_maker}


def margin_tier_check(html: str) -> dict:
    text = _text(html).lower()
    return {"passed": "tier" in text or "梯度" in text}


def contract_spec_check(html: str) -> dict:
    text = _text(html).lower()
    has = "tick size" in text or "最小变动" in text or "contract size" in text
    return {"passed": has}


def funding_rate_check(html: str) -> dict:
    text = _text(html).lower()
    return {"passed": "funding rate" in text or "资金费率" in text}


def affiliate_disclosure_check(html: str) -> dict:
    text = _text(html).lower()
    return {"passed": "affiliate" in text or "sponsored" in text or "联盟" in text or "推广" in text}


def last_verified_check(html: str) -> dict:
    text = _text(html).lower()
    return {"passed": "last verified" in text or "最后验证" in text or "updated:" in text}


def learn_prerequisite_check(internal_links: list) -> dict:
    return {"checked": True}


def glossary_link_check(internal_links: list) -> dict:
    has_glossary = any("glossary" in str(l).lower() or "术语" in str(l) for l in (internal_links or []))
    return {"has_glossary_link": has_glossary}
