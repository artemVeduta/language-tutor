from __future__ import annotations

import json

from language_tutor.dal.paths import resolve_paths
from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from tests.conftest import invoke_json
from tests.fixtures.progress.phase4_scenarios import seed_mixed_history, seed_one_session


def test_empty_progress(runner) -> None:  # type: ignore[no-untyped-def]
    result = invoke_json(runner, ["progress", "--json"])
    assert result["cost_status"] == "unavailable"
    assert result["snapshot"]["cost_status"] == "unavailable"  # type: ignore[index]
    assert "next_action" in result


def test_progress_flow_mixed_history_and_privacy(runner) -> None:  # type: ignore[no-untyped-def]
    conn = connect(resolve_paths().database_path)
    try:
        seed_mixed_history(TutorRepository(conn), 10)
    finally:
        conn.close()
    result = invoke_json(
        runner,
        ["progress", "--json", '{"window_size":10,"generated_at":"2026-05-21T12:00:00Z"}'],
    )
    assert result["report_window"]["actual_session_count"] == 10  # type: ignore[index]
    assert len(result["tag_mastery"]) >= 2  # type: ignore[arg-type]
    assert result["recent_recap"]["practice_totals"]["answers"] > 0  # type: ignore[index]
    serialized = json.dumps(result)
    assert "private answer" not in serialized
    assert "private span" not in serialized
    assert "feedback_envelope_json" not in serialized


def test_progress_no_history_then_one_session(runner) -> None:  # type: ignore[no-untyped-def]
    empty = invoke_json(
        runner,
        ["progress", "--json", '{"generated_at":"2026-05-21T12:00:00Z"}'],
    )
    assert empty["report_window"]["actual_session_count"] == 0  # type: ignore[index]
    conn = connect(resolve_paths().database_path)
    try:
        seed_one_session(TutorRepository(conn))
    finally:
        conn.close()
    populated = invoke_json(
        runner,
        ["progress", "--json", '{"generated_at":"2026-05-21T12:00:00Z"}'],
    )
    assert populated["report_window"]["actual_session_count"] == 1  # type: ignore[index]
    assert populated["recent_recap"]["trends"][0]["direction"] == "insufficient_data"  # type: ignore[index]
