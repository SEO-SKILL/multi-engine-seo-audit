"""
Auto-patch — 将 audit 报告中的修复建议生成可应用的 patch 文件
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

SKILL_ROOT = Path(__file__).parent.parent
PATCH_DIR = SKILL_ROOT / "templates" / "patches"


def list_available_patches() -> list[str]:
    return [p.stem for p in PATCH_DIR.glob("*.diff.j2")]


def render_patch(template_name: str, context: dict[str, Any]) -> str:
    """渲染单个 patch 模板"""
    env = Environment(loader=FileSystemLoader(PATCH_DIR), autoescape=False)
    try:
        template = env.get_template(f"{template_name}.diff.j2")
        return template.render(**context)
    except Exception as e:
        return f"# Patch render error: {e}"


def auto_generate_patches(findings: list[dict], output_dir: Path | None = None) -> dict:
    """根据 findings 自动生成所有 patch 文件"""
    out_dir = output_dir or SKILL_ROOT / "snapshots" / "patches"
    out_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    skipped = []
    for finding in findings:
        patch_hint = finding.get("patch_hint")
        if not patch_hint:
            skipped.append({"id": finding.get("id"), "reason": "no_patch_hint"})
            continue

        template_name = patch_hint.get("template", "").replace("patches/", "").replace(".diff.j2", "")
        if not template_name:
            skipped.append({"id": finding.get("id"), "reason": "empty_template_name"})
            continue

        context = {
            "file_path": finding.get("evidence", {}).get("url", "UNKNOWN"),
            "finding_id": finding.get("id"),
            "recommendation": finding.get("recommendation"),
        }

        rendered = render_patch(template_name, context)
        patch_file = out_dir / f"{finding.get('id', 'unknown')}.diff"
        patch_file.write_text(rendered)
        generated.append({"id": finding.get("id"), "file": str(patch_file), "priority": patch_hint.get("priority", "P2")})

    return {
        "generated_count": len(generated),
        "skipped_count": len(skipped),
        "output_dir": str(out_dir),
        "generated": generated,
        "skipped": skipped,
    }


def apply_patch_to_file(patch_content: str, target_file: str, dry_run: bool = True) -> dict:
    """应用 patch 到实际文件（V2 — 当前 dry_run 默认 True）"""
    # 真实应用需要 unified diff parser + 目标文件读写
    # V1 阶段只生成 patch 文件，让 Will/编辑人工应用
    return {
        "dry_run": dry_run,
        "would_modify": target_file,
        "patch_preview_lines": len(patch_content.splitlines()),
        "applied": False,  # V1 不自动应用
        "reason": "auto-apply pending V2 — manual review recommended",
    }
