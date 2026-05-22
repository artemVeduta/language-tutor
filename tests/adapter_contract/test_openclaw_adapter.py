from __future__ import annotations

from language_tutor.adapters import openclaw
from language_tutor.adapters.base import run_conformance
from language_tutor.boot_context import select_boot_trigger
from language_tutor.schemas import (
    BootTrigger,
    CapabilitySupport,
    Decision,
    LifecycleStart,
    TriggerType,
)


def test_openclaw_capability() -> None:
    profile = openclaw.capability_profile()
    assert profile.host == "openclaw"
    assert profile.text_support == CapabilitySupport.SUPPORTED.value


def test_openclaw_uses_first_message_trigger() -> None:
    profile = openclaw.capability_profile()
    assert profile.lifecycle_start == LifecycleStart.FIRST_MESSAGE.value
    assert profile.boot_context_trigger == BootTrigger.FIRST_TUTOR_MESSAGE.value
    trigger = select_boot_trigger(profile.boot_context_trigger)
    assert trigger.trigger_type == TriggerType.FIRST_MESSAGE.value


def test_openclaw_optional_side_effectful_tool_declared() -> None:
    profile = openclaw.capability_profile()
    assert profile.side_effectful_capabilities, "OpenClaw declares opt-in side-effectful tools"


def test_openclaw_conformance_passes() -> None:
    run = run_conformance(openclaw.capability_profile())
    assert run.decision == Decision.PASS.value
