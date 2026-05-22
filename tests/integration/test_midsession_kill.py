"""Integration: SC-002 — mid-session app kill loses no data through the last checkpoint."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from language_tutor.cli import main


def _invoke(runner: CliRunner, args: list[str]) -> dict[str, object]:
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_mid_session_kill_preserves_session_and_checkpoints(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """SC-002: present step → checkpoint, simulate kill (no end event), re-open
    and confirm prior session + all checkpoints are recoverable.
    """
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    runner = CliRunner()

    # 1. First tutor message → boot + session.
    first = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    session_id = str(first["session_id"])

    # 2. Tutor presents three steps → three immediate checkpoints.
    for step in range(3):
        checkpoint_payload = {
            "session_id": session_id,
            "modality": "lesson",
            "step_kind": "prompt_shown",
            "prompt_ref": f"lesson_42_step{step}",
            "state": {"step_index": step, "total_steps": 8},
            "summary": f"Showed step {step}/8",
        }
        result = _invoke(runner, ["checkpoint", "--json", json.dumps(checkpoint_payload)])
        assert result["session_id"] == session_id

    # 3. Mid-session "kill": no session-end event runs. The process just stops.
    #    Anything durably committed must still be present in SQLite.

    # 4. Re-open: a NEW conversation calls session-start; the prior session is
    #    surfaced as history with all checkpoints intact.
    second = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    new_session_id = str(second["session_id"])
    assert new_session_id != session_id, "new conversation must get a fresh id (FR-004)"

    prior = second["context"]["prior_sessions"]
    assert any(entry["session_id"] == session_id for entry in prior), (
        "killed session must appear in prior_sessions (SC-002, FR-008)"
    )

    # 5. Confirm checkpoints are still in storage under the killed session id.
    import sqlite3

    # Locate the SQLite database the CLI used. paths.resolve_paths reads
    # LANGUAGE_TUTOR_HOME; the database lives under tutor_home/data/.
    candidates = list(Path(tmp_path).rglob("*.sqlite*"))
    assert candidates, f"expected a SQLite file under {tmp_path}"
    db_path = next(p for p in candidates if p.is_file() and not p.name.endswith("-journal"))
    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM checkpoints WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
        assert count == 3, "all checkpoints written before kill must survive"
        status = conn.execute(
            "SELECT status FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()[0]
        assert status == "open", "killed session is never auto-closed (FR-007)"
    finally:
        conn.close()
