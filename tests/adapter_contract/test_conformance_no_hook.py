"""T037 (US3): per-host conformance with ZERO hooks installed (SC-001).

For each of the four hosts:
1. The five lifecycle fields hold the required values (FR-009).
2. First-message boot succeeds: ``session-start`` mints a session id and
   returns boot context — no hook process runs.
3. Checkpoint persistence succeeds anchored to the active session id.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from language_tutor.adapters.registry import default_capability_profiles
from language_tutor.cli import main
from language_tutor.schemas import (
    BootTrigger,
    HostId,
    LifecycleEnd,
    LifecycleStart,
    PersistenceMode,
    SessionIdSource,
)

HOSTS = ("claude", "codex", "hermes", "openclaw")


@pytest.fixture()
def tutor_runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    return CliRunner()


def _invoke(runner: CliRunner, args: list[str]) -> dict[str, object]:
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


@pytest.mark.parametrize("host", HOSTS)
def test_lifecycle_fields_hold_required_values(host: str) -> None:
    profile = default_capability_profiles()[HostId(host)]
    assert profile.lifecycle_start == LifecycleStart.FIRST_MESSAGE.value
    assert profile.lifecycle_end == LifecycleEnd.NOT_AVAILABLE.value
    assert profile.boot_context_trigger == BootTrigger.FIRST_TUTOR_MESSAGE.value
    assert profile.persistence_mode == PersistenceMode.INCREMENTAL_CHECKPOINT.value
    assert profile.session_id_source in (
        SessionIdSource.HOST_CONVERSATION.value,
        SessionIdSource.TUTOR_GENERATED.value,
    )


@pytest.mark.parametrize("host", HOSTS)
def test_first_message_boot_succeeds_without_hooks(host: str, tutor_runner: CliRunner) -> None:
    """SC-001: session-start mints a session and boot context with no hook installed."""
    result = _invoke(tutor_runner, ["session-start", "--json", json.dumps({"host": host})])
    sid = str(result["session_id"])
    assert sid.startswith("sess_")
    assert "context" in result
    assert "sections" in result["context"]
    assert "prior_sessions" in result["context"]


@pytest.mark.parametrize("host", HOSTS)
def test_checkpoint_persistence_succeeds_without_hooks(host: str, tutor_runner: CliRunner) -> None:
    boot = _invoke(tutor_runner, ["session-start", "--json", json.dumps({"host": host})])
    sid = str(boot["session_id"])
    payload = {
        "session_id": sid,
        "modality": "lesson",
        "step_kind": "prompt_shown",
        "prompt_ref": "lesson_1_step0",
        "state": {"step_index": 0, "total_steps": 4},
        "summary": f"hook-free checkpoint for {host}",
    }
    ckpt = _invoke(tutor_runner, ["checkpoint", "--json", json.dumps(payload)])
    assert ckpt["session_id"] == sid
    assert ckpt["modality"] == "lesson"
