"""Web3/Crypto specific detector functions"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

ETHEREUM_ADDRESS_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
SOLANA_ADDRESS_PATTERN = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")


def detect_contract_addresses(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text()
    eth = ETHEREUM_ADDRESS_PATTERN.findall(text)
    return list(set(eth))


def contract_address_link_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text()
    addresses = ETHEREUM_ADDRESS_PATTERN.findall(text)

    linked = []
    for a in soup.find_all("a", href=True):
        if any(domain in a["href"] for domain in ["etherscan.io", "bscscan.com", "solscan.io", "polygonscan.com"]):
            linked.append(a["href"])

    return {
        "addresses_found": len(set(addresses)),
        "explorer_links": len(linked),
        "unlinked_addresses": len(set(addresses)) - len(linked) if len(set(addresses)) > len(linked) else 0,
    }


def defi_data_citation_check(visible_text: str, citations: list | None = None) -> dict:
    text = (visible_text or "").lower()
    sources = [s for s in ["coingecko", "coinmarketcap", "defillama", "etherscan", "dune"] if s in text]
    return {"defi_sources": sources, "passed": len(sources) >= 1}


def ticker_link_check(html: str, known_tickers: list[str]) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    issues = []
    for ticker in known_tickers:
        # 找到 ticker 出现的位置
        text = soup.get_text()
        if ticker in text:
            # 检查是否被 link 化
            ticker_links = soup.find_all("a", string=re.compile(rf"\b{ticker}\b"))
            if not ticker_links:
                issues.append({"ticker": ticker, "linked": False})
    return issues
