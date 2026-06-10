"""测试 rule YAML 文件全部能被合法加载 + 元 schema 校验"""
from pathlib import Path

import pytest
import yaml


def list_rule_files(rules_dir: Path) -> list[Path]:
    return [p for p in rules_dir.rglob("*.yaml") if "_system" not in str(p)]


def test_all_rule_files_valid_yaml(rules_dir: Path):
    for path in list_rule_files(rules_dir):
        try:
            yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            pytest.fail(f"{path} is not valid YAML: {e}")


def test_all_rules_have_required_fields(rules_dir: Path):
    required = ["id", "source", "severity", "applies_to", "detector"]
    valid_severities = {"blocker", "high", "medium", "low", "info"}

    for path in list_rule_files(rules_dir):
        data = yaml.safe_load(path.read_text())
        rules = data.get("rules", []) if isinstance(data, dict) else []
        for rule in rules:
            for field in required:
                assert field in rule, f"{path}::{rule.get('id')} missing required field: {field}"
            assert rule["severity"] in valid_severities, f"{path}::{rule['id']} invalid severity"


def test_rule_ids_globally_unique(rules_dir: Path):
    seen = {}
    for path in list_rule_files(rules_dir):
        data = yaml.safe_load(path.read_text())
        rules = data.get("rules", []) if isinstance(data, dict) else []
        for rule in rules:
            rid = rule.get("id")
            if rid in seen:
                pytest.fail(f"Duplicate rule id '{rid}' in {path} and {seen[rid]}")
            seen[rid] = path


def test_confidence_default_in_range(rules_dir: Path):
    for path in list_rule_files(rules_dir):
        data = yaml.safe_load(path.read_text())
        rules = data.get("rules", []) if isinstance(data, dict) else []
        for rule in rules:
            cd = rule.get("confidence_default")
            if cd is not None:
                assert 0.0 <= cd <= 1.0, f"{path}::{rule['id']} confidence_default out of range"
