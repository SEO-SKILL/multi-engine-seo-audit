"""pytest fixtures 共享"""
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = SKILL_ROOT / "fixtures"
RULES_DIR = SKILL_ROOT / "rules"


@pytest.fixture
def skill_root() -> Path:
    return SKILL_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def rules_dir() -> Path:
    return RULES_DIR


@pytest.fixture
def mexc_incident_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "mexc-incident.html").read_text()


@pytest.fixture
def good_tools_page_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "good-tools-page.html").read_text()


@pytest.fixture
def bad_hreflang_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "bad-hreflang.html").read_text()


@pytest.fixture
def cloaking_suspect_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "cloaking-suspect.html").read_text()


@pytest.fixture
def thin_content_html(fixtures_dir: Path) -> str:
    return (fixtures_dir / "thin-content.html").read_text()
