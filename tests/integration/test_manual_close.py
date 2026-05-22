"""T044 (US4): manual close is the ONLY path that closes a session.

Asserts FR-007, FR-015, SC-003: boot/checkpoint/record paths never close a
session. Only an explicit ``session-close`` transitions ``status=closed`` and
sets ``closed_at``.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from click.testing import CliRunner

from language_tutor.cli import main


def _invoke(runner: CliRunner, args: list[str]) -> dict[str, object]:
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def _db_path(tmp_path: Path) -> Path:
    candidates = [
        p for p in Path(tmp_path).rglob("*.sqlite*")
        if p.is_file() and not p.name.endswith("-journal")
    ]
    assert candidates
    return candidates[0]


def _row(db: Path, sid: str) -> sqlite3.Row | None:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            "SELECT status, closed_at FROM sessions WHERE id = ?", (sid,)
        ).fetchone()
    finally:
        conn.close()


def test_boot_path_never_closes_session(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    runner = CliRunner()

    first = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    sid = str(first["session_id"])
    # Start a *new* conversation — this re-boots but must NOT close the prior session.
    _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])

    row = _row(_db_path(tmp_path), sid)
    assert row is not None
    assert row["status"] == "open", "boot must never auto-close a prior session (FR-007)"
    assert row["closed_at"] is None


def test_checkpoint_path_never_closes_session(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    runner = CliRunner()

    boot = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    sid = str(boot["session_id"])
    for step in range(3):
        _invoke(
            runner,
            [
                "checkpoint",
                "--json",
                json.dumps(
                    {
                        "session_id": sid,
                        "modality": "lesson",
                        "step_kind": "prompt_shown",
                        "prompt_ref": f"lesson_step_{step}",
                        "state": {"step_index": step, "total_steps": 3},
                        "summary": f"step {step}",
                    }
                ),
            ],
        )
    row = _row(_db_path(tmp_path), sid)
    assert row is not None
    assert row["status"] == "open", "checkpoint must never close a session (FR-007)"
    assert row["closed_at"] is None


def test_session_close_transitions_to_closed_with_summary(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    runner = CliRunner()

    boot = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    sid = str(boot["session_id"])
    payload = {
        "session_id": sid,
        "analysis": {
            "summary_for_next_boot": "wrapped up drill",
            "next_focus": "case",
        },
        "costs": [],
    }
    out = _invoke(runner, ["session-close", "--json", json.dumps(payload)])
    assert out["session_id"] == sid
    assert out["status"] == "complete"

    row = _row(_db_path(tmp_path), sid)
    assert row is not None
    assert row["status"] == "closed"
    assert row["closed_at"] is not None
