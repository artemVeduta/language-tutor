from __future__ import annotations

import pytest
from pydantic import ValidationError

from language_tutor.boot_context import select_boot_trigger
from language_tutor.schemas import BootContextTrigger, BootTrigger, TriggerType


def test_hook_trigger_requires_event_name() -> None:
    with pytest.raises(ValidationError):
        BootContextTrigger(
            trigger_type=TriggerType.HOOK,
            input_contract="payload",
            output_contract="BootContext",
        )


def test_explicit_command_trigger_requires_command() -> None:
    with pytest.raises(ValidationError):
        BootContextTrigger(
            trigger_type=TriggerType.EXPLICIT_COMMAND,
            input_contract="payload",
            output_contract="BootContext",
        )


def test_session_start_hook_maps_to_hook_trigger() -> None:
    trigger = select_boot_trigger(BootTrigger.SESSION_START_HOOK.value)
    assert trigger.trigger_type == TriggerType.HOOK.value
    assert trigger.host_event_name == "SessionStart"


def test_codex_plugin_hook_maps_to_hook_trigger() -> None:
    trigger = select_boot_trigger(BootTrigger.CODEX_PLUGIN_HOOK.value)
    assert trigger.trigger_type == TriggerType.HOOK.value
    assert trigger.host_event_name == "CodexPluginStart"


def test_explicit_tutor_command_maps_to_explicit_trigger() -> None:
    trigger = select_boot_trigger(BootTrigger.EXPLICIT_TUTOR_COMMAND.value)
    assert trigger.trigger_type == TriggerType.EXPLICIT_COMMAND.value
    assert trigger.command


def test_first_message_maps_to_first_message_trigger() -> None:
    trigger = select_boot_trigger(BootTrigger.FIRST_TUTOR_MESSAGE.value)
    assert trigger.trigger_type == TriggerType.FIRST_MESSAGE.value


def test_host_specific_maps_to_manual_trigger() -> None:
    trigger = select_boot_trigger(BootTrigger.HOST_SPECIFIC.value)
    assert trigger.trigger_type == TriggerType.MANUAL.value
    assert trigger.fallback is None
