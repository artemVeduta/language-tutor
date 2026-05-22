"""T030 (US2): SC-003 + FR-019.

A new conversation:
- mints a DISTINCT session id (FR-004);
- never mutates a prior session id;
- writes new checkpoints only under the new id;
- threads exactly one session id across every CLI call (FR-019).
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
    assert candidates, f"expected a SQLite file under {tmp_path}"
    return candidates[0]


def test_new_conversation_mints_distinct_id_and_does_not_mutate_prior(
    tmp_path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    runner = CliRunner()

    # First conversation.
    first = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    sid_a = str(first["session_id"])
    _invoke(
        runner,
        [
            "checkpoint",
            "--json",
            json.dumps(
                {
                    "session_id": sid_a,
                    "modality": "lesson",
                    "step_kind": "prompt_shown",
                    "prompt_ref": "lesson_1_step0",
                    "state": {"step_index": 0, "total_steps": 4},
                    "summary": "first conversation step",
                }
            ),
        ],
    )

    # Capture the prior row's started_at / status / last_seen so we can prove
    # the new conversation does not mutate any of them.
    db = _db_path(tmp_path)
    conn = sqlite3.connect(db)
    try:
        before = conn.execute(
            "SELECT id, status, started_at, last_seen_at FROM sessions WHERE id = ?",
            (sid_a,),
        ).fetchone()
    finally:
        conn.close()
    assert before is not None

    # Second conversation.
    second = _invoke(runner, ["session-start", "--json", '{"host":"claude"}'])
    sid_b = str(second["session_id"])
    assert sid_b != sid_a, "new conversation must mint a fresh id (FR-004)"

    prior = second["context"]["prior_sessions"]
    prior_ids = [entry["session_id"] for entry in prior]
    assert sid_a in prior_ids, "prior session must be surfaced as history (FR-008)"
    assert sid_b not in prior_ids, "the freshly-minted id must not appear in its own prior block"

    # Write a checkpoint under the new id, then verify:
    # (a) the prior session row is unchanged (FR-004);
    # (b) new checkpoints are anchored only to sid_b (FR-006, FR-019).
    _invoke(
        runner,
        [
            "checkpoint",
            "--json",
            json.dumps(
                {
                    "session_id": sid_b,
                    "modality": "reading",
                    "step_kind": "prompt_shown",
                    "prompt_ref": "reading_2",
                    "state": {"step_index": 0, "total_steps": 1},
                    "summary": "second conversation step",
                }
            ),
        ],
    )

    conn = sqlite3.connect(db)
    try:
        after = conn.execute(
            "SELECT id, status, started_at, last_seen_at FROM sessions WHERE id = ?",
            (sid_a,),
        ).fetchone()
        # Same row, same started_at, same status. (last_seen could have been
        # touched only via session_start reads — but session_start does not
        # touch prior rows in the spec; assert it stayed exactly the same.)
        assert after is not None
        assert after == before, "prior session row must not be mutated (FR-004)"

        # Every checkpoint belongs to exactly one session id; both sets are disjoint.
        rows_a = conn.execute(
            "SELECT session_id FROM checkpoints WHERE session_id = ?", (sid_a,)
        ).fetchall()
        rows_b = conn.execute(
            "SELECT session_id FROM checkpoints WHERE session_id = ?", (sid_b,)
        ).fetchall()
        assert len(rows_a) == 1
        assert len(rows_b) == 1
        all_ids = {row[0] for row in conn.execute("SELECT session_id FROM checkpoints").fetchall()}
        assert all_ids == {sid_a, sid_b}
    finally:
        conn.close()


def test_single_session_id_threading_within_one_conversation(
    tmp_path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    """FR-019: all writes in one conversation share exactly one session_id."""
    monkeypatch.setenv("LANGUAGE_TUTOR_HOME", str(tmp_path))
    runner = CliRunner()

    boot = _invoke(runner, ["session-start", "--json", '{"host":"codex"}'])
    sid = str(boot["session_id"])

    for step in range(4):
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
                        "state": {"step_index": step, "total_steps": 4},
                        "summary": f"step {step}/4",
                    }
                ),
            ],
        )

    db = _db_path(tmp_path)
    conn = sqlite3.connect(db)
    try:
        ids = {row[0] for row in conn.execute("SELECT DISTINCT session_id FROM checkpoints").fetchall()}
    finally:
        conn.close()
    assert ids == {sid}, "all checkpoints in one conversation must share one session_id (FR-019)"
