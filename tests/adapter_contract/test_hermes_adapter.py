from __future__ import annotations

from language_tutor.adapters import hermes
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


def test_hermes_capability() -> None:
    profile = hermes.capability_profile()
    assert profile.host == "hermes"
    assert profile.text_support == CapabilitySupport.SUPPORTED.value
    assert profile.lifecycle_end == LifecycleEnd.NOT_AVAILABLE.value


def test_hermes_uses_explicit_boot_trigger() -> None:
    profile = hermes.capability_profile()
    assert profile.lifecycle_start == LifecycleStart.EXPLICIT_COMMAND.value
    assert profile.boot_context_trigger == BootTrigger.EXPLICIT_TUTOR_COMMAND.value
    trigger = select_boot_trigger(profile.boot_context_trigger)
    assert trigger.trigger_type == TriggerType.EXPLICIT_COMMAND.value
    assert trigger.command


def test_hermes_setup_entry_point() -> None:
    assert hermes.capability_profile().setup_entry_point == "hermes profile install"


def test_hermes_conformance_passes() -> None:
    run = run_conformance(hermes.capability_profile())
    assert run.decision == Decision.PASS.value
