from __future__ import annotations

from pathlib import Path

from language_tutor.adapters import claude
from language_tutor.adapters.base import run_conformance
from language_tutor.boot_context import select_boot_trigger
from language_tutor.schemas import (
    BootTrigger,
    CapabilitySupport,
    Decision,
    LifecycleStart,
    TriggerType,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_claude_capability() -> None:
    profile = claude.capability_profile()
    assert profile.host == "claude"
    assert profile.text_support == CapabilitySupport.SUPPORTED.value
    assert profile.audio_support == "unsupported"


def test_claude_lifecycle_is_hook() -> None:
    profile = claude.capability_profile()
    assert profile.lifecycle_start == LifecycleStart.HOOK.value
    assert profile.boot_context_trigger == BootTrigger.SESSION_START_HOOK.value
    trigger = select_boot_trigger(profile.boot_context_trigger)
    assert trigger.trigger_type == TriggerType.HOOK.value
    assert trigger.host_event_name == "SessionStart"


def test_claude_baseline_preserved() -> None:
    for rel in (".claude-plugin/plugin.json", "hooks/hooks.json", "bin/tutor"):
        assert (REPO_ROOT / rel).exists()


def test_claude_conformance_passes() -> None:
    run = run_conformance(claude.capability_profile())
    assert run.decision == Decision.PASS.value
    assert run.skipped_flows == []
