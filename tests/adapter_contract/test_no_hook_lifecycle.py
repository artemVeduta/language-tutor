"""T036 (US3): hook boot triggers and hook lifecycle starts are rejected
for ALL hosts.

Covers FR-010 / FR-011: the no-hook lifecycle is a hard contract — no host
may declare ``lifecycle_start=hook`` or any hook boot trigger
(``session_start_hook`` / ``codex_plugin_hook``).
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from language_tutor.adapters.registry import default_capability_profiles
from language_tutor.boot_context import select_boot_trigger
from language_tutor.schemas import (
    AdapterCapabilityProfile,
    BootTrigger,
    CapabilitySupport,
    HostId,
    LifecycleEnd,
    LifecycleStart,
    TriggerType,
)

HOSTS = (HostId.CLAUDE, HostId.CODEX, HostId.HERMES, HostId.OPENCLAW)


def _base(host: HostId, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "host": host,
        "display_name": host.value.title(),
        "text_support": CapabilitySupport.SUPPORTED,
        "lifecycle_start": LifecycleStart.FIRST_MESSAGE,
        "lifecycle_end": LifecycleEnd.NOT_AVAILABLE,
        "boot_context_trigger": BootTrigger.FIRST_TUTOR_MESSAGE,
        "setup_entry_point": "n/a",
        "update_behavior": "n/a",
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize("host", HOSTS)
def test_hook_lifecycle_start_rejected_per_host(host: HostId) -> None:
    with pytest.raises(ValidationError):
        AdapterCapabilityProfile(**_base(host, lifecycle_start=LifecycleStart.HOOK))


@pytest.mark.parametrize("host", HOSTS)
def test_session_start_hook_trigger_rejected_per_host(host: HostId) -> None:
    with pytest.raises(ValidationError):
        AdapterCapabilityProfile(
            **_base(host, boot_context_trigger=BootTrigger.SESSION_START_HOOK)
        )


@pytest.mark.parametrize("host", HOSTS)
def test_codex_plugin_hook_trigger_rejected_per_host(host: HostId) -> None:
    with pytest.raises(ValidationError):
        AdapterCapabilityProfile(
            **_base(host, boot_context_trigger=BootTrigger.CODEX_PLUGIN_HOOK)
        )


def test_no_default_profile_declares_hook_lifecycle() -> None:
    for profile in default_capability_profiles().values():
        assert profile.lifecycle_start != LifecycleStart.HOOK.value
        assert profile.boot_context_trigger != BootTrigger.SESSION_START_HOOK.value
        assert profile.boot_context_trigger != BootTrigger.CODEX_PLUGIN_HOOK.value


def test_hook_triggers_do_not_map_to_hook_trigger_type() -> None:
    """select_boot_trigger never returns a TriggerType.HOOK branch (R7)."""
    for trigger in (
        BootTrigger.SESSION_START_HOOK,
        BootTrigger.CODEX_PLUGIN_HOOK,
    ):
        mapped = select_boot_trigger(trigger.value)
        assert mapped.trigger_type != TriggerType.HOOK.value
