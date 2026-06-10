"""BYDFi SEO Audit CLI 入口"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from orchestrator import Orchestrator

app = typer.Typer(name="seo-audit", help="BYDFi SEO 风控+增长决策中台")
console = Console()


@app.command()
def audit(
    url: str = typer.Argument(..., help="待审核 URL"),
    locale: str = typer.Option(None, "--locale", "-l"),
    no_cache: bool = typer.Option(False, "--no-cache"),
    output: str = typer.Option("terminal", "--output", "-o"),
) -> None:
    """单页审核 + Final Verdict"""
    orch = Orchestrator()
    report = asyncio.run(orch.audit(url=url, locale=locale, no_cache=no_cache))

    if output == "json":
        console.print_json(report.model_dump_json(indent=2))
        return

    table = Table(title=f"SEO Audit: {url}")
    table.add_column("Severity")
    table.add_column("Count")
    table.add_column("Top Findings")

    for sev, findings in report.findings_by_severity.items():
        if not findings:
            continue
        top_ids = ", ".join(f.id for f in findings[:3])
        table.add_row(sev.value, str(len(findings)), top_ids)

    console.print(table)
    console.print(f"\n[bold]Final Verdict:[/bold] {report.final_verdict.value}")
    console.print(f"[bold]Brand SEO Score:[/bold] {report.brand_seo_score:.1f}/100")


@app.command()
def gate(md_file: str = typer.Argument(...)) -> None:
    """发布前卡审"""
    typer.echo(f"Gate command: {md_file} (stub — Codex W2)")


@app.command()
def compare(
    self_url: str = typer.Argument(...),
    competitor_urls: list[str] = typer.Argument(...),
) -> None:
    """竞品对比"""
    typer.echo(f"Compare command (stub — Codex W3)")


@app.command()
def watch(site: str = typer.Argument(...)) -> None:
    """全站快照"""
    typer.echo(f"Watch command (stub — Codex W4)")


@app.command()
def doctor() -> None:
    """检查 skill 健康状态"""
    skill_root = Path(__file__).parent
    checks = {
        "config.yaml": (skill_root / "config.yaml").exists(),
        "rules/_system/": (skill_root / "rules" / "_system").exists(),
        "rules/bydfi/": (skill_root / "rules" / "bydfi").exists(),
        "fixtures/": (skill_root / "fixtures").exists(),
        "tasks/todo.md": (skill_root / "tasks" / "todo.md").exists(),
        "agents/_schema.py": (skill_root / "agents" / "_schema.py").exists(),
        "orchestrator.py": (skill_root / "orchestrator.py").exists(),
    }
    table = Table(title="Skill Health Check")
    table.add_column("Component")
    table.add_column("Status")
    for component, ok in checks.items():
        table.add_row(component, "[green]✅[/green]" if ok else "[red]❌[/red]")
    console.print(table)

    # Rule count
    try:
        from rule_loader import load_all_rules
        rules = load_all_rules()
        console.print(f"\n[bold]Rules loaded:[/bold] [cyan]{len(rules)}[/cyan]")
    except Exception as e:
        console.print(f"[red]Rule loader error: {e}[/red]")


if __name__ == "__main__":
    app()
