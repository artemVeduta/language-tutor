from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_MANIFEST = REPO_ROOT / ".codex-plugin/plugin.json"
MARKETPLACE = REPO_ROOT / ".agents/plugins/marketplace.json"


def _skip_if_absent(path: Path) -> None:
    if not path.exists():
        pytest.skip(f"{path.relative_to(REPO_ROOT)} not yet created by the Codex subagent")


def test_codex_manifest_points_to_skills() -> None:
    _skip_if_absent(CODEX_MANIFEST)
    manifest = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))
    raw = json.dumps(manifest)
    assert "skills" in raw.lower()


def test_codex_marketplace_entry_references_plugin() -> None:
    _skip_if_absent(MARKETPLACE)
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    raw = json.dumps(data).lower()
    assert "language-tutor" in raw or "codex-plugin" in raw


def test_codex_hooks_disabled_by_default() -> None:
    _skip_if_absent(CODEX_MANIFEST)
    text = CODEX_MANIFEST.read_text(encoding="utf-8")
    # Hooks must remain opt-in; do not auto-enable plugin_hooks.
    assert "plugin_hooks = true" not in text
    assert '"plugin_hooks": true' not in text


def test_codex_manifest_is_cache_safe() -> None:
    _skip_if_absent(CODEX_MANIFEST)
    raw = CODEX_MANIFEST.read_text(encoding="utf-8").lower()
    for forbidden in (".env", ".sqlite", "memories", "sessions"):
        assert forbidden not in raw


def test_root_skills_available_for_codex() -> None:
    # Codex consumes the same root-level skills/ surface as Claude.
    assert (REPO_ROOT / "skills/tutor-setup/SKILL.md").exists()
