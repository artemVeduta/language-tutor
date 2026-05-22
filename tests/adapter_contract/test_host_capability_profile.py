from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from language_tutor.adapters.registry import (
    capability_profile_for,
    default_capability_profiles,
)
from language_tutor.schemas import (
    REPRESENTATIVE_FLOWS,
    AdapterCapabilityProfile,
    BootTrigger,
    CapabilitySupport,
    HostId,
    LifecycleEnd,
    LifecycleStart,
)


def _base(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "host": HostId.HERMES,
        "display_name": "Hermes",
        "text_support": CapabilitySupport.SUPPORTED,
        "lifecycle_start": LifecycleStart.EXPLICIT_COMMAND,
        "lifecycle_end": LifecycleEnd.NOT_AVAILABLE,
        "boot_context_trigger": BootTrigger.EXPLICIT_TUTOR_COMMAND,
        "setup_entry_point": "hermes profile install",
        "update_behavior": "hermes profile update",
    }
    data.update(overrides)
    return data


def test_text_unsupported_rejected() -> None:
    with pytest.raises(ValidationError):
        AdapterCapabilityProfile(**_base(text_support=CapabilitySupport.UNSUPPORTED))


def test_audio_and_image_locked_unsupported() -> None:
    profile = AdapterCapabilityProfile(**_base())
    assert profile.audio_support == "unsupported"
    assert profile.image_support == "unsupported"


def test_hook_lifecycle_requires_hook_boot_trigger() -> None:
    with pytest.raises(ValidationError):
        AdapterCapabilityProfile(
            **_base(
                lifecycle_start=LifecycleStart.HOOK,
                boot_context_trigger=BootTrigger.EXPLICIT_TUTOR_COMMAND,
            )
        )


def test_non_hook_lifecycle_requires_non_hook_trigger() -> None:
    with pytest.raises(ValidationError):
        AdapterCapabilityProfile(
            **_base(
                lifecycle_start=LifecycleStart.EXPLICIT_COMMAND,
                boot_context_trigger=BootTrigger.SESSION_START_HOOK,
            )
        )


def test_all_four_hosts_have_defaults() -> None:
    defaults = default_capability_profiles()
    assert set(defaults) == {HostId.HERMES, HostId.OPENCLAW, HostId.CLAUDE, HostId.CODEX}
    for profile in defaults.values():
        assert profile.text_support == CapabilitySupport.SUPPORTED.value


def test_antigravity_not_a_host() -> None:
    with pytest.raises((KeyError, ValueError)):
        capability_profile_for("antigravity")


def test_representative_flows_are_six() -> None:
    assert len(REPRESENTATIVE_FLOWS) == 6
    assert set(REPRESENTATIVE_FLOWS) == {
        "reading",
        "lesson",
        "transcript",
        "vocab",
        "writing",
        "progress",
    }
