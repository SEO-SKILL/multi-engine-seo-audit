"""
Multi-tenant 隔离 (V2)
保留 V1 单租户兼容性，同时支持未来多项目
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SKILL_ROOT = Path(__file__).parent
CONFIG_PATH = SKILL_ROOT / "config.yaml"


class TenantContext:
    def __init__(self, project: str | None = None) -> None:
        self._config = yaml.safe_load(CONFIG_PATH.read_text())
        self.project = project or self._config.get("default_project", "bydfi")
        if self.project not in self._config.get("projects", {}):
            raise ValueError(f"Unknown project: {self.project}")
        self.project_config = self._config["projects"][self.project]

    def get_rules_path(self) -> Path:
        return SKILL_ROOT / "rules"

    def get_project_rules_path(self) -> Path:
        return SKILL_ROOT / "rules" / self.project

    def get_snapshots_path(self, date: str | None = None) -> Path:
        base = SKILL_ROOT / "snapshots" / self.project
        if date:
            base = base / date
        return base

    def get_cache_path(self) -> Path:
        return SKILL_ROOT / "cache" / self.project

    def get_secret_env_name(self, key: str) -> str:
        return f"{self.project.upper()}_{key.upper()}"

    @property
    def domain(self) -> str:
        return self.project_config.get("primary_domain", "")

    @property
    def locales(self) -> list[str]:
        return self.project_config.get("locales", ["en"])

    @property
    def competitors(self) -> list[str]:
        return self.project_config.get("competitors", [])


def get_default_tenant() -> TenantContext:
    return TenantContext()


def list_all_tenants() -> list[str]:
    config = yaml.safe_load(CONFIG_PATH.read_text())
    return list(config.get("projects", {}).keys())
