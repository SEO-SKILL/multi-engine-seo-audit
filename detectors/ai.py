"""AI Bot 访问 / GEO detector functions"""
from __future__ import annotations


def robots_txt_check(robots_txt: str, required_allow_for_ua: list[str]) -> dict:
    if not robots_txt:
        return {"present": False, "issues": ["robots.txt 缺失"]}

    issues = []
    blocked = []
    for ua in required_allow_for_ua:
        # 简化：检查每个 UA 是否被 Disallow: /
        ua_block_pattern = f"user-agent: {ua.lower()}"
        lines = [l.lower() for l in robots_txt.splitlines()]
        if ua_block_pattern in lines:
            idx = lines.index(ua_block_pattern)
            for line in lines[idx + 1: idx + 10]:
                if line.startswith("disallow: /") and line == "disallow: /":
                    blocked.append(ua)
                    break
                if line.startswith("user-agent:"):
                    break

    if blocked:
        issues.append(f"以下 AI bot 被阻断: {', '.join(blocked)}")

    return {"present": True, "blocked_bots": blocked, "issues": issues}


def code_snippet_check(html: str) -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    code_blocks = soup.find_all(["code", "pre"])
    return {"code_block_count": len(code_blocks)}


def schema_ai_friendly_check(jsonld_parsed: list | None = None) -> dict:
    encouraged = ["HowTo", "WebApplication", "SoftwareApplication", "QAPage", "Article"]
    present = [b.get("@type") for b in (jsonld_parsed or []) if isinstance(b, dict) and b.get("@type") in encouraged]
    return {"present_types": present, "passed": len(present) > 0}
