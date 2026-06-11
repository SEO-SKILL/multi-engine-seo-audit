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

    # 显示 composite scores
    composite_scores = {}
    for o in report.agent_outputs:
        if o.agent == "crawler" and o.artifacts.get("composite_scores"):
            composite_scores = o.artifacts["composite_scores"]
            break
    if composite_scores:
        comp_table = Table(title="📊 Composite Scores (页面级最佳组合)")
        comp_table.add_column("维度")
        comp_table.add_column("分数")
        comp_table.add_column("最弱环节")
        for name, data in composite_scores.items():
            if isinstance(data, dict) and "composite_score" in data and data["composite_score"] is not None:
                score = data["composite_score"]
                weakest = data.get("weakest_link", "—")
                emoji = "✅" if score >= 0.8 else "🟡" if score >= 0.6 else "🟠" if score >= 0.4 else "🔴"
                comp_table.add_row(name, f"{emoji} {score:.2f}", weakest)
        console.print(comp_table)


@app.command()
def gate(
    md_file: str = typer.Argument(..., help="待卡审 MD 文件路径"),
    locale: str = typer.Option(None, "--locale", "-l"),
    block_threshold: str = typer.Option("high", "--block-threshold"),
) -> None:
    """发布前卡审（Git pre-commit hook 可用）"""
    from agents.gate import gate_md_file
    result = asyncio.run(gate_md_file(md_file, locale=locale, block_threshold=block_threshold))

    if "error" in result:
        console.print(f"[red]Gate error: {result['error']}[/red]")
        raise typer.Exit(code=2)

    t = Table(title=f"Gate Check: {md_file}")
    t.add_column("项")
    t.add_column("结果")
    t.add_row("Pass?", "[green]✅ YES[/green]" if result["pass"] else "[red]❌ NO[/red]")
    t.add_row("Verdict", result["verdict"])
    t.add_row("Score", f"{result['score']:.1f}/100")
    t.add_row("Blockers", str(len(result["blockers"])))
    t.add_row("Highs", str(len(result["highs"])))
    t.add_row("Mediums", str(len(result["mediums"])))
    console.print(t)

    if result["blockers"]:
        console.print("\n[red bold]🔴 BLOCKERS:[/red bold]")
        for f in result["blockers"]:
            console.print(f"  - {f['id']}: {f['rec'][:80]}")
    if result["highs"]:
        console.print("\n[yellow bold]🟠 HIGH:[/yellow bold]")
        for f in result["highs"]:
            console.print(f"  - {f['id']}: {f['rec'][:80]}")

    if not result["pass"]:
        console.print(f"\n[red bold]Gate FAILED. Fix above before commit.[/red bold]")
        raise typer.Exit(code=1)
    console.print(f"\n[green bold]✅ Gate PASSED. Safe to publish.[/green bold]")


@app.command()
def compare(
    self_url: str = typer.Argument(..., help="自家 URL"),
    competitor_urls: list[str] = typer.Argument(..., help="竞品 URLs（可多个）"),
) -> None:
    """竞品对比（输出 HTML 仪表盘）"""
    from agents.compare import compare_pages
    result = asyncio.run(compare_pages(self_url, competitor_urls))
    console.print(f"\n📊 Dashboard: [cyan]{result['output_path']}[/cyan]\n")
    t = Table(title="Compare Summary")
    t.add_column("Label"); t.add_column("Score"); t.add_column("Verdict")
    for r in result["results"]:
        if "error" in r:
            t.add_row(r["label"], "—", f"[red]Error[/red]")
        else:
            t.add_row(r["label"], f"{r['score']:.0f}", r["verdict"])
    console.print(t)


@app.command()
def watch(site: str = typer.Argument(..., help="待监控站点（base URL）")) -> None:
    """全站快照 — 跑 batch_audit + diff 上次"""
    import subprocess
    skill_root = Path(__file__).parent
    console.print(f"[bold]Running batch audit for {site}...[/bold]\n")
    result = subprocess.run(
        ["uv", "run", "python", "scripts/batch_audit.py"],
        cwd=skill_root, capture_output=True, text=True,
    )
    console.print(result.stdout[-2000:])
    if result.returncode != 0:
        console.print(f"[red]Watch failed: {result.stderr[-500:]}[/red]")
        raise typer.Exit(code=1)
    console.print("\n[green]✅ Watch snapshot completed.[/green]")


@app.command()
def init(
    target_repo: str = typer.Argument(".", help="BYDFi 内容仓库路径"),
) -> None:
    """一键初始化 git pre-commit hook + .env 模板"""
    import subprocess
    repo = Path(target_repo).resolve()
    if not (repo / ".git").exists():
        console.print(f"[red]{repo} 不是 git 仓库[/red]")
        raise typer.Exit(code=1)

    skill_root = Path(__file__).parent
    hook_script = skill_root / "scripts" / "install-pre-commit-hook.sh"
    result = subprocess.run(["bash", str(hook_script)], cwd=repo, capture_output=True, text=True)
    console.print(result.stdout)
    if result.returncode != 0:
        console.print(f"[red]{result.stderr}[/red]")
        raise typer.Exit(code=1)

    env_template = repo / ".env.seo-audit.template"
    env_template.write_text("""# BYDFi SEO Audit Skill - 配置模板
ANTHROPIC_API_KEY=
GSC_SERVICE_ACCOUNT_JSON=
CLOUDFLARE_API_TOKEN=
BYDFI_SLACK_WEBHOOK=
PERPLEXITY_API_KEY=
""")
    console.print(f"\n[green]✅ Pre-commit hook + .env template installed[/green]")


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

    # Detector coverage
    try:
        import re, pathlib, yaml
        referenced = set()
        for f in pathlib.Path("rules").rglob("*.yaml"):
            if "_system" in str(f): continue
            try:
                d = yaml.safe_load(f.read_text())
                if isinstance(d, dict):
                    for r in d.get("rules", []):
                        fn = r.get("detector", {}).get("fn")
                        if fn and fn.startswith("detectors."):
                            referenced.add(fn)
            except Exception: pass
        implemented = set()
        for f in pathlib.Path("detectors").glob("*.py"):
            if f.name == "__init__.py": continue
            for m in re.finditer(r"^(?:async\s+)?def (\w+)\(", f.read_text(), re.MULTILINE):
                implemented.add(f"detectors.{f.stem}.{m.group(1)}")
        coverage = len(referenced & implemented) / max(1, len(referenced))
        console.print(f"[bold]Detector coverage:[/bold] [cyan]{int(coverage*100)}%[/cyan] ({len(referenced & implemented)}/{len(referenced)})")
    except Exception:
        pass

    # F4 Secrets health
    try:
        from _secrets import report_health
        sec = report_health(verbose=False)
        s_table = Table(title="🔑 Secrets Health Check")
        s_table.add_column("Total"); s_table.add_column("Configured"); s_table.add_column("Missing")
        s_table.add_row(str(sec["total_secrets"]), str(sec["configured"]),
                        f"[yellow]{len(sec['missing'])}[/yellow]")
        console.print(s_table)
        if sec["configured"] == 0:
            console.print("[dim]提示：所有 secret 未配置，skill 跑 stub 模式。配置任一可解锁对应能力。[/dim]")
    except Exception:
        pass

    # F11 Plugins
    try:
        from _plugins import load_all_plugins
        reg = load_all_plugins()
        if reg.custom_detectors or reg.custom_judges:
            console.print(f"\n[bold]Plugins:[/bold] [green]{len(reg.custom_detectors)} detector + {len(reg.custom_judges)} judge[/green]")
    except Exception:
        pass


if __name__ == "__main__":
    app()
