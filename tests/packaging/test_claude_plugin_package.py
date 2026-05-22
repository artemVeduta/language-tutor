from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Existing Claude baseline components that must remain present (regression guard).
REQUIRED = (
    ".claude-plugin/plugin.json",
    "skills/tutor-setup/SKILL.md",
    "skills/tutor-vocab/SKILL.md",
    "skills/tutor-writing/SKILL.md",
    "skills/tutor-progress/SKILL.md",
    "skills/tutor-reading/SKILL.md",
    "skills/tutor-lesson/SKILL.md",
    "hooks/hooks.json",
    "agents/tutor-judge.md",
    "bin/tutor",
)


def test_claude_baseline_components_present() -> None:
    for rel in REQUIRED:
        assert (REPO_ROOT / rel).exists(), rel


def test_claude_manifest_is_valid_json_with_name() -> None:
    manifest = json.loads((REPO_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "language-tutor"
    assert "version" in manifest


def test_claude_hooks_declare_session_start() -> None:
    hooks = json.loads((REPO_ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
    assert "SessionStart" in hooks["hooks"]


def test_claude_manifest_excludes_user_state() -> None:
    raw = (REPO_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8").lower()
    for forbidden in (".env", ".sqlite", "memories", "sessions"):
        assert forbidden not in raw
