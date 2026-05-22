"""T027 — Assert SKILL.md edits teach the no-hook incremental lifecycle.

Pressure-scenario rules from
``specs/007-hookfree-incremental-lifecycle/skill-pressure-scenarios.md`` reduced
to grep-level invariants so the constitution's RED→GREEN evidence is mechanical.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"

LIFECYCLE_SKILLS = (
    "tutor-lesson",
    "tutor-reading",
    "tutor-vocab",
    "tutor-writing",
    "tutor-progress",
)

PER_SKILL_MODALITY = {
    "tutor-lesson": "lesson",
    "tutor-reading": "reading",
    "tutor-vocab": "vocab",
    "tutor-writing": "writing",
    "tutor-progress": "progress",
}


def _skill_text(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("skill", LIFECYCLE_SKILLS)
def test_skill_mentions_session_start_command(skill: str) -> None:
    """Scenario 1: agent must call ``session-start`` before any stateful step."""
    text = _skill_text(skill)
    assert "session-start" in text, f"{skill} must reference session-start"


@pytest.mark.parametrize("skill", LIFECYCLE_SKILLS)
def test_skill_mentions_session_id_threading(skill: str) -> None:
    """Scenario 2: agent must thread session_id."""
    text = _skill_text(skill)
    assert "session_id" in text, f"{skill} must reference session_id"


@pytest.mark.parametrize("skill", LIFECYCLE_SKILLS)
def test_skill_mentions_checkpoint_on_presentation(skill: str) -> None:
    """Scenario 3: agent must call ``checkpoint`` on presentation."""
    text = _skill_text(skill)
    assert "checkpoint" in text, f"{skill} must reference checkpoint"
    modality = PER_SKILL_MODALITY[skill]
    assert modality in text, f"{skill} must name its checkpoint modality {modality!r}"


@pytest.mark.parametrize("skill", LIFECYCLE_SKILLS)
def test_skill_does_not_recommend_hooks_as_boot(skill: str) -> None:
    """Scenario 5: no hook as normal boot path.

    Explicit anti-hook language ("No SessionStart hooks") is allowed and
    welcomed; only positive references to hook files as the boot path fail.
    """
    text = _skill_text(skill)
    assert "session-start.sh" not in text
    assert "session-end.sh" not in text
    assert "hooks/" not in text
