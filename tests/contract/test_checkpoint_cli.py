from __future__ import annotations

import json
import re
from pathlib import Path

from language_tutor.cli import main
from tests.conftest import invoke_json

CHECKPOINT_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[2] / "schemas" / "checkpoint.schema.json").read_text(
        encoding="utf-8"
    )
)


def _open_session(runner) -> str:  # type: ignore[no-untyped-def]
    result = invoke_json(runner, ["session-start", "--json", '{"host":"claude"}'])
    assert re.match(r"^sess_[A-Za-z0-9]+$", result["session_id"])
    return str(result["session_id"])


def test_checkpoint_returns_persisted_checkpoint_object(runner) -> None:  # type: ignore[no-untyped-def]
    session_id = _open_session(runner)
    payload = {
        "session_id": session_id,
        "modality": "lesson",
        "step_kind": "prompt_shown",
        "prompt_ref": "lesson_42_step3",
        "state": {"step_index": 3, "total_steps": 8},
        "summary": "Showed past-tense drill step 3/8",
    }
    result = invoke_json(runner, ["checkpoint", "--json", json.dumps(payload)])
    for field in CHECKPOINT_SCHEMA["required"]:
        assert field in result, f"missing required field {field}"
    assert re.match(r"^ckpt_[A-Za-z0-9]+$", result["id"])
    assert result["session_id"] == session_id
    assert result["modality"] == "lesson"
    assert result["step_kind"] == "prompt_shown"
    assert result["prompt_ref"] == "lesson_42_step3"


def test_checkpoint_requires_explicit_session_id(runner) -> None:  # type: ignore[no-untyped-def]
    result = runner.invoke(
        main,
        [
            "checkpoint",
            "--json",
            json.dumps(
                {
                    "modality": "lesson",
                    "step_kind": "prompt_shown",
                    "state": {},
                    "summary": "no session",
                }
            ),
        ],
    )
    assert result.exit_code != 0 or "error" in result.output.lower()


def test_checkpoint_rejects_unknown_session_id(runner) -> None:  # type: ignore[no-untyped-def]
    result = runner.invoke(
        main,
        [
            "checkpoint",
            "--json",
            json.dumps(
                {
                    "session_id": "sess_does_not_exist",
                    "modality": "lesson",
                    "step_kind": "prompt_shown",
                    "state": {},
                    "summary": "ghost session",
                }
            ),
        ],
    )
    assert result.exit_code != 0
    assert "error" in result.output.lower()


def test_session_start_returns_boot_result(runner) -> None:  # type: ignore[no-untyped-def]
    result = invoke_json(runner, ["session-start", "--json", '{"host":"claude"}'])
    assert "session_id" in result
    assert re.match(r"^sess_[A-Za-z0-9]+$", result["session_id"])
    assert "context" in result
    assert "sections" in result["context"]
    assert "prior_sessions" in result["context"]
