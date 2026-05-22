"""T043 (US4): contract test for ``session-close`` CLI JSON shape.

Covers session-close.cli.md:
- Input requires session_id; reuses existing analysis/costs payloads.
- Output: ``{session_id, status, summary_id?, next_focus?}``.
- Idempotent-already-closed: closing an already-closed session is an error.
"""

from __future__ import annotations

import json

from language_tutor.cli import main
from tests.conftest import invoke_json


def _start(runner) -> str:  # type: ignore[no-untyped-def]
    result = invoke_json(runner, ["session-start", "--json", '{"host":"claude"}'])
    return str(result["session_id"])


def test_session_close_flushes_summary_and_marks_closed(runner) -> None:  # type: ignore[no-untyped-def]
    sid = _start(runner)
    payload = {
        "session_id": sid,
        "analysis": {
            "summary_for_next_boot": "wrapped up past-tense drill",
            "next_focus": "verbs_of_motion",
        },
        "costs": [],
    }
    result = invoke_json(runner, ["session-close", "--json", json.dumps(payload)])
    assert result["session_id"] == sid
    assert result["status"] == "complete"
    assert result["summary_id"]
    assert result["next_focus"] == "verbs_of_motion"


def test_session_close_requires_session_id(runner) -> None:  # type: ignore[no-untyped-def]
    result = runner.invoke(main, ["session-close", "--json", json.dumps({"analysis": {}, "costs": []})])
    assert result.exit_code != 0
    assert "error" in result.output.lower()


def test_session_close_rejects_unknown_session(runner) -> None:  # type: ignore[no-untyped-def]
    payload = {"session_id": "sess_does_not_exist", "analysis": {}, "costs": []}
    result = runner.invoke(main, ["session-close", "--json", json.dumps(payload)])
    assert result.exit_code != 0
    assert "error" in result.output.lower()


def test_session_close_already_closed_is_error(runner) -> None:  # type: ignore[no-untyped-def]
    sid = _start(runner)
    payload = {"session_id": sid, "analysis": {}, "costs": []}
    first = invoke_json(runner, ["session-close", "--json", json.dumps(payload)])
    assert first["session_id"] == sid
    second = runner.invoke(main, ["session-close", "--json", json.dumps(payload)])
    assert second.exit_code != 0, "closing twice must error (idempotent-already-closed)"
    assert "error" in second.output.lower()


def test_session_close_marks_status_closed_and_sets_closed_at(runner, tutor_home) -> None:  # type: ignore[no-untyped-def]
    sid = _start(runner)
    invoke_json(
        runner,
        [
            "session-close",
            "--json",
            json.dumps({"session_id": sid, "analysis": {}, "costs": []}),
        ],
    )
    import sqlite3
    from pathlib import Path

    candidates = [
        p for p in Path(tutor_home).rglob("*.sqlite*")
        if p.is_file() and not p.name.endswith("-journal")
    ]
    assert candidates
    conn = sqlite3.connect(candidates[0])
    try:
        row = conn.execute(
            "SELECT status, closed_at FROM sessions WHERE id = ?", (sid,)
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "closed"
    assert row[1] is not None
