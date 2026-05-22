"""T035 (US3): all four host profiles declare the shared no-hook lifecycle.

Asserts FR-009 — every host capability profile carries the canonical lifecycle
fields plus the two new fields (``persistence_mode`` and ``session_id_source``).
"""

from __future__ import annotations

import pytest

from language_tutor.adapters.registry import default_capability_profiles
from language_tutor.schemas import (
    BootTrigger,
    HostId,
    LifecycleEnd,
    LifecycleStart,
    PersistenceMode,
    SessionIdSource,
)

HOSTS = (HostId.CLAUDE, HostId.CODEX, HostId.HERMES, HostId.OPENCLAW)


@pytest.mark.parametrize("host", HOSTS)
def test_lifecycle_start_is_first_message(host: HostId) -> None:
    profile = default_capability_profiles()[host]
    assert profile.lifecycle_start == LifecycleStart.FIRST_MESSAGE.value


@pytest.mark.parametrize("host", HOSTS)
def test_lifecycle_end_is_not_available(host: HostId) -> None:
    """FR-007: no automatic session end — every host declares ``not_available``."""
    profile = default_capability_profiles()[host]
    assert profile.lifecycle_end == LifecycleEnd.NOT_AVAILABLE.value


@pytest.mark.parametrize("host", HOSTS)
def test_boot_context_trigger_is_first_tutor_message(host: HostId) -> None:
    profile = default_capability_profiles()[host]
    assert profile.boot_context_trigger == BootTrigger.FIRST_TUTOR_MESSAGE.value


@pytest.mark.parametrize("host", HOSTS)
def test_persistence_mode_is_incremental_checkpoint(host: HostId) -> None:
    profile = default_capability_profiles()[host]
    assert profile.persistence_mode == PersistenceMode.INCREMENTAL_CHECKPOINT.value


@pytest.mark.parametrize("host", HOSTS)
def test_session_id_source_is_valid(host: HostId) -> None:
    profile = default_capability_profiles()[host]
    assert profile.session_id_source in (
        SessionIdSource.HOST_CONVERSATION.value,
        SessionIdSource.TUTOR_GENERATED.value,
    )
