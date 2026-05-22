from __future__ import annotations

from language_tutor.adapters.registry import capability_profile_for
from language_tutor.schemas import AdapterCapabilityProfile, HostId


def capability_profile() -> AdapterCapabilityProfile:
    """Claude capability profile. No-hook lifecycle (spec 007)."""
    return capability_profile_for(HostId.CLAUDE.value)


def plugin_root_components() -> dict[str, str]:
    return {
        "manifest": ".claude-plugin/plugin.json",
        "setup_skill": "skills/tutor-setup/SKILL.md",
        "vocab_skill": "skills/tutor-vocab/SKILL.md",
        "writing_skill": "skills/tutor-writing/SKILL.md",
        "progress_skill": "skills/tutor-progress/SKILL.md",
        "judge_agent": "agents/tutor-judge.md",
        "cli": "bin/tutor",
    }
