# Multi-Engine SEO Audit Skill — Plugins 目录

## F11 — Plugin 扩展机制

把自定义 detector / agent / 规则集 / 输出格式以插件形式接入，**不修改 skill 源码**。

## 插件结构

```
plugins/
└── my_custom_plugin/
    ├── __init__.py          # 必须导出 register(registry) 函数
    ├── detectors.py         # 自定义 detector 函数
    ├── rules/               # 自定义 YAML 规则（启动时自动加载）
    └── README.md
```

## 最小示例

`plugins/example_platform_internal/__init__.py`:

```python
from .detectors import custom_check

def register(registry):
    registry.custom_detectors["platform.internal.custom_check"] = custom_check
    registry.custom_judges["custom_judge"] = "prompts/custom_judge.md"
```

## 加载机制

skill 启动时 `_plugins.load_all_plugins()` 自动扫描 `plugins/` 目录加载所有有 `register()` 的模块。
