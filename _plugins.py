"""
Plugin 扩展机制 (V2)
允许用户写自定义规则 / agent / detector / 输出格式
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path.home() / ".claude/skills/seo-audit/plugins"


class PluginRegistry:
    def __init__(self) -> None:
        self.custom_detectors: dict[str, Any] = {}
        self.custom_agents: dict[str, Any] = {}
        self.custom_renderers: dict[str, Any] = {}
        self.custom_judges: dict[str, str] = {}

    def discover(self) -> list[str]:
        if not PLUGIN_DIR.exists():
            return []
        loaded = []
        for plugin_dir in PLUGIN_DIR.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("_"):
                continue
            init = plugin_dir / "__init__.py"
            if init.exists():
                self._load_plugin(plugin_dir, init)
                loaded.append(plugin_dir.name)
        return loaded

    def _load_plugin(self, plugin_dir: Path, init_file: Path) -> None:
        spec = importlib.util.spec_from_file_location(f"plugin_{plugin_dir.name}", init_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "register"):
                module.register(self)


def load_all_plugins() -> PluginRegistry:
    registry = PluginRegistry()
    registry.discover()
    return registry
