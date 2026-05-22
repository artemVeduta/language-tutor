from __future__ import annotations

import json

from language_tutor.cli import main
from tests.conftest import invoke_json


def _open_session(runner) -> str:  # type: ignore[no-untyped-def]
    result = invoke_json(runner, ["session-start", "--json", '{"host":"claude"}'])
    return str(result["session_id"])


def test_missing_idempotency_key_names_the_field(runner) -> None:  # type: ignore[no-untyped-def]
    session_id = _open_session(runner)
    started = invoke_json(runner, ["vocab", "start", "--json"])
    item_id = str(started["items"][0]["id"])
    result = runner.invoke(
        main,
        [
            "vocab",
            "answer",
            "--json",
            json.dumps(
                {
                    "session_id": session_id,
                    "item_id": item_id,
                    "answer": "привет",
                }
            ),
        ],
    )
    assert result.exit_code != 0
    payload = json.loads(result.output)
    # The repair hint must point at the actual failing field, not at item_id,
    # which is valid here.
    assert "idempotency_key" in result.output
    assert "valid item_id" not in payload["error"]["repair_hint"]
