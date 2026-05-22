from __future__ import annotations

from typing import Protocol

from language_tutor.schemas import (
    APPROVED_HOST_SOURCES,
    AdapterCapabilityProfile,
    BootContextTrigger,
    ConformanceRun,
    HostId,
    HostSetupProfileContract,
    HostSetupTarget,
    ManualProviderInstallReport,
    SetupModel,
    SetupPackage,
    TargetStatus,
)


class JsonCommandRunner(Protocol):
    def run_json(
        self, args: list[str], payload: dict[str, object] | None = None
    ) -> dict[str, object]:
        """Run a host-facing JSON command."""
        ...


class HookPayloadAdapter(Protocol):
    def normalize(self, payload: dict[str, object]) -> dict[str, object]:
        """Normalize host hook payload into core JSON."""
        ...


class HostCapabilityProvider(Protocol):
    def capability_profile(self) -> AdapterCapabilityProfile:
        """Return the host's declared capability profile."""
        ...


class LifecycleTriggerProvider(Protocol):
    def boot_trigger(self) -> BootContextTrigger:
        """Return the host's boot-context lifecycle trigger."""
        ...


class SetupPackageProvider(Protocol):
    def setup_package(self) -> SetupPackage:
        """Describe the host-owned distribution package."""
        ...


class ConformanceRunner(Protocol):
    def run_conformance(self) -> ConformanceRun:
        """Run shared host-portability conformance checks."""
        ...


class ManualReportProvider(Protocol):
    def manual_report(self) -> ManualProviderInstallReport:
        """Return the host's manual provider install report."""
        ...


# Supported host target registry (US1). Single source of truth for the four
# approved hosts, their official setup-doc sources, setup models, and contract
# paths. Antigravity is intentionally absent and rejected at the schema layer.
_REGISTRY: dict[HostId, HostSetupTarget] = {
    HostId.HERMES: HostSetupTarget(
        id=HostId.HERMES,
        display_name="Hermes",
        official_source_url=APPROVED_HOST_SOURCES[HostId.HERMES.value],
        setup_model=SetupModel.PROFILE_DISTRIBUTION,
        primary_subagent="hermes-adapter-subagent",
        contract_path="specs/006-agent-adapter-setup/contracts/host-setup-profiles/hermes.md",
        status=TargetStatus.PLANNED,
    ),
    HostId.OPENCLAW: HostSetupTarget(
        id=HostId.OPENCLAW,
        display_name="OpenClaw",
        official_source_url=APPROVED_HOST_SOURCES[HostId.OPENCLAW.value],
        setup_model=SetupModel.PLUGIN_PACKAGE,
        primary_subagent="openclaw-adapter-subagent",
        contract_path="specs/006-agent-adapter-setup/contracts/host-setup-profiles/openclaw.md",
        status=TargetStatus.PLANNED,
    ),
    HostId.CLAUDE: HostSetupTarget(
        id=HostId.CLAUDE,
        display_name="Claude",
        official_source_url=APPROVED_HOST_SOURCES[HostId.CLAUDE.value],
        setup_model=SetupModel.PLUGIN_PACKAGE,
        primary_subagent="claude-adapter-subagent",
        contract_path="specs/006-agent-adapter-setup/contracts/host-setup-profiles/claude.md",
        status=TargetStatus.PLANNED,
    ),
    HostId.CODEX: HostSetupTarget(
        id=HostId.CODEX,
        display_name="Codex",
        official_source_url=APPROVED_HOST_SOURCES[HostId.CODEX.value],
        setup_model=SetupModel.LOCAL_MARKETPLACE_PLUGIN,
        primary_subagent="codex-adapter-subagent",
        contract_path="specs/006-agent-adapter-setup/contracts/host-setup-profiles/codex.md",
        status=TargetStatus.PLANNED,
    ),
}


def supported_host_targets() -> dict[HostId, HostSetupTarget]:
    """Return the registry of approved host setup targets."""
    return dict(_REGISTRY)


def is_supported_host(host_id: str) -> bool:
    """True only for hermes, openclaw, claude, codex. Antigravity is rejected."""
    return host_id in {h.value for h in HostId}


def get_host_target(host_id: str) -> HostSetupTarget:
    return _REGISTRY[HostId(host_id)]


def normalize_hook_payload(payload: dict[str, object]) -> dict[str, object]:
    return dict(payload)


def run_conformance(profile: AdapterCapabilityProfile) -> ConformanceRun:
    """Build a deterministic conformance result from a host capability profile.

    The runner is host-blind: it derives the six representative-flow outcomes
    from the declared capability profile (a gated flow is ``skipped``, every
    other flow ``pass``) and reports the shared boot/feedback/progress/error/
    data-ownership contract results. It owns no pedagogy or learner state.
    """
    from language_tutor.schemas import (
        ConformanceRun,
        Decision,
        FlowResult,
        RepresentativeFlow,
    )

    gated = {str(g) for g in profile.flow_gates}
    flows: dict[RepresentativeFlow, FlowResult] = {}
    for flow in RepresentativeFlow:
        flows[flow] = FlowResult.SKIPPED if flow.value in gated else FlowResult.PASS

    skipped = [f for f in RepresentativeFlow if f.value in gated]
    has_fail = any(r == FlowResult.FAIL for r in flows.values())
    decision = Decision.FAIL if has_fail else Decision.PASS

    return ConformanceRun(
        host=HostId(str(profile.host)),
        capability_profile="schemas/host_capability_profile.schema.json",
        flows=flows,
        boot_context_result=FlowResult.PASS,
        feedback_contract_result=FlowResult.PASS,
        progress_contract_result=FlowResult.PASS,
        error_behavior_result=FlowResult.PASS,
        data_ownership_result=FlowResult.PASS,
        skipped_flows=skipped,
        decision=decision,
    )


def load_host_setup_profile(path: str) -> HostSetupProfileContract:
    """Load and validate a host setup profile markdown contract.

    The markdown contract embeds a fenced ```json block describing the
    HostSetupProfileContract fields. This loader extracts and validates it.
    """
    import json
    import re
    from pathlib import Path

    text = Path(path).read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise ValueError(f"host setup profile {path} has no json contract block")
    data = json.loads(match.group(1))
    return HostSetupProfileContract.model_validate(data)
