"""Host capability profile defaults (single source of truth).

Each supported host declares its capability profile here. Host-specific adapter
modules (claude.py, codex.py, hermes.py, openclaw.py) may translate runtime
behavior, but capability declarations stay centralized to keep flow names,
lifecycle values, and boot triggers DRY.
"""

from __future__ import annotations

from language_tutor.schemas import (
    AdapterCapabilityProfile,
    BootTrigger,
    CapabilitySupport,
    HostId,
    LifecycleEnd,
    LifecycleStart,
)

_DEFAULTS: dict[HostId, AdapterCapabilityProfile] = {
    HostId.CLAUDE: AdapterCapabilityProfile(
        host=HostId.CLAUDE,
        display_name="Claude",
        text_support=CapabilitySupport.SUPPORTED,
        lifecycle_start=LifecycleStart.HOOK,
        lifecycle_end=LifecycleEnd.HOOK,
        boot_context_trigger=BootTrigger.SESSION_START_HOOK,
        setup_entry_point="claude --plugin-dir <plugin-root>",
        update_behavior="/reload-plugins",
        side_effectful_capabilities=[],
        unsupported_capabilities=["audio", "image"],
        flow_gates=[],
    ),
    HostId.CODEX: AdapterCapabilityProfile(
        host=HostId.CODEX,
        display_name="Codex",
        text_support=CapabilitySupport.SUPPORTED,
        lifecycle_start=LifecycleStart.HOOK,
        lifecycle_end=LifecycleEnd.NOT_AVAILABLE,
        boot_context_trigger=BootTrigger.CODEX_PLUGIN_HOOK,
        setup_entry_point="local marketplace install via .codex-plugin/plugin.json",
        update_behavior="Codex restart/reload after marketplace update",
        side_effectful_capabilities=["plugin_hooks (opt-in via [features].plugin_hooks)"],
        unsupported_capabilities=["audio", "image"],
        flow_gates=[],
    ),
    HostId.HERMES: AdapterCapabilityProfile(
        host=HostId.HERMES,
        display_name="Hermes",
        text_support=CapabilitySupport.SUPPORTED,
        lifecycle_start=LifecycleStart.EXPLICIT_COMMAND,
        lifecycle_end=LifecycleEnd.NOT_AVAILABLE,
        boot_context_trigger=BootTrigger.EXPLICIT_TUTOR_COMMAND,
        setup_entry_point="hermes profile install",
        update_behavior="hermes profile update",
        side_effectful_capabilities=[],
        unsupported_capabilities=["audio", "image"],
        flow_gates=[],
    ),
    HostId.OPENCLAW: AdapterCapabilityProfile(
        host=HostId.OPENCLAW,
        display_name="OpenClaw",
        text_support=CapabilitySupport.SUPPORTED,
        lifecycle_start=LifecycleStart.FIRST_MESSAGE,
        lifecycle_end=LifecycleEnd.NOT_AVAILABLE,
        boot_context_trigger=BootTrigger.FIRST_TUTOR_MESSAGE,
        setup_entry_point="openclaw plugins install <package-name>",
        update_behavior="reinstall/upgrade plugin package",
        side_effectful_capabilities=["binary-dependent tools (opt-in via user allowlist)"],
        unsupported_capabilities=["audio", "image"],
        flow_gates=[],
    ),
}


def default_capability_profiles() -> dict[HostId, AdapterCapabilityProfile]:
    return dict(_DEFAULTS)


def capability_profile_for(host_id: str) -> AdapterCapabilityProfile:
    return _DEFAULTS[HostId(host_id)]
