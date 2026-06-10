"""
Rule Loader — 加载所有 YAML 规则文件
按 rules/_system/rule-schema.yaml 元规则校验
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SKILL_ROOT = Path(__file__).parent
RULES_DIR = SKILL_ROOT / "rules"

VALID_SEVERITIES = {"blocker", "high", "medium", "low", "info"}
REQUIRED_RULE_FIELDS = ["id", "source", "severity", "applies_to", "detector"]


class RuleLoadError(Exception):
    pass


def list_rule_files() -> list[Path]:
    return [p for p in RULES_DIR.rglob("*.yaml") if "_system" not in str(p)]


def load_one_file(path: Path) -> list[dict[str, Any]]:
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise RuleLoadError(f"{path}: invalid YAML: {e}") from e
    if not isinstance(data, dict) or "rules" not in data:
        return []
    rules = data["rules"]
    if not isinstance(rules, list):
        return []
    return rules


def validate_rule(rule: dict[str, Any], path: Path) -> None:
    for field in REQUIRED_RULE_FIELDS:
        if field not in rule:
            raise RuleLoadError(f"{path}::{rule.get('id')} missing field: {field}")
    if rule["severity"] not in VALID_SEVERITIES:
        raise RuleLoadError(f"{path}::{rule['id']} invalid severity: {rule['severity']}")
    cd = rule.get("confidence_default")
    if cd is not None and not (0.0 <= cd <= 1.0):
        raise RuleLoadError(f"{path}::{rule['id']} confidence_default out of range")


def load_all_rules() -> dict[str, dict[str, Any]]:
    """返回 id -> rule 的全局字典，启动时检查 id 唯一性"""
    all_rules: dict[str, dict[str, Any]] = {}
    for path in list_rule_files():
        rules = load_one_file(path)
        for rule in rules:
            validate_rule(rule, path)
            rid = rule["id"]
            if rid in all_rules:
                raise RuleLoadError(f"Duplicate rule id '{rid}'")
            rule["_source_file"] = str(path.relative_to(SKILL_ROOT))
            all_rules[rid] = rule
    return all_rules


def filter_rules_for_context(
    rules: dict[str, dict[str, Any]],
    *,
    platforms: list[str] | None = None,
    page_type: str | None = None,
    locale: str | None = None,
    command: str | None = None,
) -> list[dict[str, Any]]:
    matched: list[dict[str, Any]] = []
    for rule in rules.values():
        applies = rule.get("applies_to", {})
        if platforms:
            rule_platforms = applies.get("platforms", [])
            if rule_platforms and not any(p in rule_platforms for p in platforms):
                continue
        if page_type:
            rule_pts = applies.get("page_types", [])
            if rule_pts and "all" not in rule_pts and page_type not in rule_pts:
                continue
        if locale:
            rule_locales = applies.get("locales", [])
            if rule_locales and "all" not in rule_locales and locale not in rule_locales:
                continue
        if command:
            rule_commands = applies.get("commands", [])
            if rule_commands and "all" not in rule_commands and command not in rule_commands:
                continue
        matched.append(rule)
    return matched


if __name__ == "__main__":
    rules = load_all_rules()
    print(f"Loaded {len(rules)} rules from {len(list_rule_files())} files")
