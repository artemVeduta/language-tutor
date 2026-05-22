"""Host-portable text-flow conformance across all four supported hosts.

Each host must support (or document a capability gate for) the same six Phase 5
representative text flows. Setup mechanics differ per host; learner-visible tutor
behavior must not. This suite runs the shared conformance runner for every host.
"""

from __future__ import annotations

import pytest

from language_tutor.adapters.base import run_conformance
from language_tutor.adapters.registry import capability_profile_for
from language_tutor.schemas import REPRESENTATIVE_FLOWS, Decision, FlowResult

HOSTS = ("hermes", "openclaw", "claude", "codex")


@pytest.mark.parametrize("host", HOSTS)
def test_all_six_flows_present_per_host(host: str) -> None:
    run = run_conformance(capability_profile_for(host))
    present = {str(flow) for flow in run.flows}
    assert present == set(REPRESENTATIVE_FLOWS)


@pytest.mark.parametrize("host", HOSTS)
def test_no_ungated_flow_failures(host: str) -> None:
    profile = capability_profile_for(host)
    run = run_conformance(profile)
    gated = {str(g) for g in profile.flow_gates}
    for flow, result in run.flows.items():
        if str(result) == FlowResult.SKIPPED.value:
            assert str(flow) in gated, f"{host} skipped {flow} without a gate"
        else:
            assert str(result) == FlowResult.PASS.value


@pytest.mark.parametrize("host", HOSTS)
def test_host_conformance_decision_passes(host: str) -> None:
    run = run_conformance(capability_profile_for(host))
    assert run.decision == Decision.PASS.value
    assert run.data_ownership_result == FlowResult.PASS.value
    assert run.boot_context_result == FlowResult.PASS.value
