from __future__ import annotations

from datetime import UTC, datetime

from language_tutor.dal.paths import resolve_paths
from language_tutor.dal.sqlite_store import connect
from tests.conftest import invoke_json


def test_progress_json_stable_shape(runner) -> None:  # type: ignore[no-untyped-def]
    result = invoke_json(runner, ["progress", "--json"])
    assert set(result) >= {"streak_days", "due_count", "weak_patterns", "maturity"}


def test_progress_uses_active_weak_tag_signals(runner) -> None:  # type: ignore[no-untyped-def]
    invoke_json(
        runner,
        [
            "setup",
            "write",
            "--json",
            '{"profile":{"native_language":"en","target_language":"uk"},"preferences":{}}',
        ],
    )
    conn = connect(resolve_paths().database_path)
    try:
        for session_id, day in (("s1", 20), ("s2", 21)):
            conn.execute(
                """
                INSERT INTO session_summaries(
                  id, session_id, summary_for_user, summary_for_next_boot,
                  weak_tags_json, next_focus, cost_snapshot_json, created_at
                ) VALUES (?, ?, 'u', 'b', '[]', 'focus', '{}', ?)
                """,
                (f"summary_{session_id}", session_id, datetime(2026, 5, day, tzinfo=UTC).isoformat()),
            )
            conn.execute(
                """
                INSERT INTO mistake_events(
                  id, session_id, skill, severity, tag, explanation, confidence, created_at
                ) VALUES (?, ?, 'writing', 'low', 'case', 'private', 'high', ?)
                """,
                (f"mistake_{session_id}", session_id, datetime(2026, 5, day, tzinfo=UTC).isoformat()),
            )
        conn.commit()
    finally:
        conn.close()
    result = invoke_json(runner, ["progress", "--json"])
    assert result["weak_patterns"] == ["case"]
