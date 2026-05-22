from __future__ import annotations

import json
from pathlib import Path

import pytest

from language_tutor.adapters import codex
from language_tutor.adapters.base import run_conformance
from language_tutor.boot_context import select_boot_trigger
from language_tutor.schemas import (
    BootTrigger,
    CapabilitySupport,
    Decision,
    LifecycleEnd,
    LifecycleStart,
    TriggerType,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_MANIFEST = REPO_ROOT / ".codex-plugin/plugin.json"


def test_codex_capability() -> None:
    profile = codex.capability_profile()
    assert profile.host == "codex"
    assert profile.text_support == CapabilitySupport.SUPPORTED.value
    assert profile.lifecycle_end == LifecycleEnd.NOT_AVAILABLE.value


def test_codex_lifecycle_is_plugin_hook() -> None:
    profile = codex.capability_profile()
    assert profile.lifecycle_start == LifecycleStart.HOOK.value
    assert profile.boot_context_trigger == BootTrigger.CODEX_PLUGIN_HOOK.value
    trigger = select_boot_trigger(profile.boot_context_trigger)
    assert trigger.trigger_type == TriggerType.HOOK.value


def test_codex_hooks_disabled_by_default() -> None:
    if not CODEX_MANIFEST.exists():
        pytest.skip("codex manifest not present")
    text = CODEX_MANIFEST.read_text(encoding="utf-8")
    assert "plugin_hooks = true" not in text
    assert '"plugin_hooks": true' not in text
    data = json.loads(text)
    assert json.dumps(data)


def test_codex_conformance_passes() -> None:
    run = run_conformance(codex.capability_profile())
    assert run.decision == Decision.PASS.value
