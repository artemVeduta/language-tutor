from __future__ import annotations

import json
from datetime import UTC, datetime

from language_tutor.dal.paths import resolve_paths
from language_tutor.dal.sqlite_store import connect
from tests.conftest import invoke_json


def test_cli_error_envelope(runner) -> None:  # type: ignore[no-untyped-def]
    result = runner.invoke(
        __import__("language_tutor.cli").cli.main, ["setup", "write", "--json", "{bad"]
    )
    assert result.exit_code == 1
    assert '"error"' in result.output


def test_doctor_json(runner) -> None:  # type: ignore[no-untyped-def]
    data = invoke_json(runner, ["doctor", "--json"])
    assert "checks" in data


def test_boot_context_reports_safe_weak_tag_summary(runner) -> None:  # type: ignore[no-untyped-def]
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
                ) VALUES (?, ?, 'writing', 'low', 'case', 'private prose', 'high', ?)
                """,
                (f"mistake_{session_id}", session_id, datetime(2026, 5, day, tzinfo=UTC).isoformat()),
            )
        conn.commit()
    finally:
        conn.close()

    context = invoke_json(runner, ["boot-context", "--json"])
    weak_section = next(section for section in context["sections"] if section["title"] == "Weak Patterns")  # type: ignore[index]
    assert len(weak_section["lines"]) == 1  # type: ignore[index]
    assert "case" in weak_section["lines"][0]  # type: ignore[index]
    assert "private prose" not in json.dumps(context)


def test_vocab_start_json_selection_reason_invariants(runner) -> None:  # type: ignore[no-untyped-def]
    invoke_json(
        runner,
        [
            "setup",
            "write",
            "--json",
            '{"profile":{"native_language":"en","target_language":"uk"},"preferences":{"session_length":2}}',
        ],
    )
    plan = invoke_json(runner, ["vocab", "start", "--json"])
    item_ids = {item["id"] for item in plan["items"]}  # type: ignore[index]
    reason_ids = {reason["item_id"] for reason in plan["selection_reasons"]}  # type: ignore[index]
    assert reason_ids == item_ids
    assert len(plan["active_weak_tags"]) <= 5  # type: ignore[arg-type]
    assert "learner_answer" not in json.dumps(plan)
