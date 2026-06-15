"""
F9 — Platform Router
按 locale + page_type + command 动态过滤规则集
"""
from __future__ import annotations

from pathlib import Path

import yaml

SKILL_ROOT = Path(__file__).parent


class PlatformRouter:
    """根据 locale / page_type / command 决定应用哪些规则"""

    def __init__(self, config_path: Path | None = None) -> None:
        cfg_path = config_path or SKILL_ROOT / "config.yaml"
        self.config = yaml.safe_load(cfg_path.read_text())
        self._rules_cache: dict | None = None

    def get_platforms_for_locale(self, locale: str, project: str = "platform") -> list[str]:
        routing = self.config["projects"][project].get("platform_routing", {})
        return routing.get(locale or "en", routing.get("en", ["google"]))

    def load_all_rules(self) -> dict[str, dict]:
        if self._rules_cache is not None:
            return self._rules_cache
        rules: dict = {}
        for f in (SKILL_ROOT / "rules").rglob("*.yaml"):
            if "_system" in str(f):
                continue
            try:
                data = yaml.safe_load(f.read_text())
                if isinstance(data, dict):
                    for rule in data.get("rules", []):
                        rid = rule.get("id")
                        if rid:
                            rules[rid] = rule
            except Exception:
                continue
        self._rules_cache = rules
        return rules

    def filter_rules(
        self,
        locale: str | None = None,
        page_type: str | None = None,
        command: str | None = None,
        platforms_override: list[str] | None = None,
    ) -> list[dict]:
        """按上下文过滤适用规则"""
        all_rules = self.load_all_rules()
        platforms = platforms_override or self.get_platforms_for_locale(locale or "en")
        platforms_set = set(platforms) | {"shared", "platform"}  # always include shared+platform

        matched: list[dict] = []
        for rule in all_rules.values():
            applies = rule.get("applies_to", {})

            # Platform 匹配
            rule_platforms = applies.get("platforms", [])
            if rule_platforms and not (set(rule_platforms) & platforms_set):
                continue

            # Page type 匹配
            if page_type:
                rule_pts = applies.get("page_types", [])
                if rule_pts and "all" not in rule_pts and page_type not in rule_pts:
                    continue

            # Locale 匹配
            if locale:
                rule_locales = applies.get("locales", [])
                if rule_locales and "all" not in rule_locales and locale not in rule_locales:
                    continue

            # Command 匹配
            if command:
                rule_commands = applies.get("commands", [])
                if rule_commands and "all" not in rule_commands and command not in rule_commands:
                    continue

            matched.append(rule)

        # Platform 风控规则优先
        matched.sort(key=lambda r: (
            0 if "platform" in str(r.get("source", "")) else 1,
            {"blocker": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(r.get("severity", "low"), 4),
        ))
        return matched

    def stats(self, locale: str | None = None, page_type: str | None = None, command: str | None = None) -> dict:
        all_rules = self.load_all_rules()
        matched = self.filter_rules(locale, page_type, command)
        return {
            "total_rules": len(all_rules),
            "matched_for_context": len(matched),
            "filtered_ratio": len(matched) / max(1, len(all_rules)),
            "by_severity": {
                sev: sum(1 for r in matched if r.get("severity") == sev)
                for sev in ["blocker", "high", "medium", "low", "info"]
            },
        }


_default_router: PlatformRouter | None = None


def get_router() -> PlatformRouter:
    global _default_router
    if _default_router is None:
        _default_router = PlatformRouter()
    return _default_router
