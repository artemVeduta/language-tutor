from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HERMES_ROOT = REPO_ROOT / "hermes-profile"


def _skip_if_absent(path: Path) -> None:
    if not path.exists():
        pytest.skip(f"{path.relative_to(REPO_ROOT)} not yet created by the Hermes subagent")


def test_hermes_distribution_yaml_present() -> None:
    _skip_if_absent(HERMES_ROOT / "distribution.yaml")
    assert (HERMES_ROOT / "distribution.yaml").read_text(encoding="utf-8").strip()


def test_hermes_required_profile_files() -> None:
    _skip_if_absent(HERMES_ROOT)
    for rel in ("distribution.yaml", "SOUL.md", "config.yaml"):
        assert (HERMES_ROOT / rel).exists(), rel


def test_hermes_profile_excludes_user_owned_data() -> None:
    _skip_if_absent(HERMES_ROOT)
    offenders: list[str] = []
    forbidden = (".env", ".sqlite", ".sqlite3", ".db", ".log")
    forbidden_dirs = {"memories", "sessions", "local", "logs", "caches"}
    for path in HERMES_ROOT.rglob("*"):
        if path.is_file() and path.suffix in forbidden:
            offenders.append(str(path.relative_to(REPO_ROOT)))
        if path.is_dir() and path.name in forbidden_dirs:
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == [], f"user-owned data in hermes-profile: {offenders}"
