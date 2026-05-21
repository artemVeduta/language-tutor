from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from language_tutor.dal.paths import resolve_paths
from language_tutor.dal.sqlite_store import connect
from tests.conftest import invoke_json


def test_vocabulary_flow(runner) -> None:  # type: ignore[no-untyped-def]
    invoke_json(
        runner,
        [
            "setup",
            "write",
            "--json",
            '{"profile":{"native_language":"en","target_language":"uk"},"preferences":{"session_length":2,"review_intensity":"normal","transliteration_tolerance":true}}',
        ],
    )
    plan = invoke_json(runner, ["vocab", "start", "--json"])
    assert plan["requested_count"] == 2
    item_id = plan["items"][0]["id"]  # type: ignore[index]
    answer = invoke_json(
        runner,
        [
            "vocab",
            "answer",
            "--json",
            f'{{"item_id":"{item_id}","answer":"privit","idempotency_key":"k"}}',
        ],
    )
    assert answer["feedback"]["verdict"] == "correct"


def test_phase2_vocabulary_flow(runner) -> None:  # type: ignore[no-untyped-def]
    invoke_json(
        runner,
        [
            "setup",
            "write",
            "--json",
            '{"profile":{"native_language":"en","target_language":"uk"},"preferences":{"session_length":3,"review_intensity":"normal","transliteration_tolerance":true}}',
        ],
    )
    manual = invoke_json(
        runner,
        [
            "vocab",
            "add",
            "--json",
            json.dumps(
                {
                    "target": "так",
                    "prompt": "yes",
                    "accepted_answers": ["так"],
                    "tags": ["confirm"],
                }
            ),
        ],
    )
    seed_path = Path("tests/fixtures/vocabulary/phase2_seed.json").resolve()
    first_import = invoke_json(
        runner, ["vocab", "import", "--json", json.dumps({"path": str(seed_path)})]
    )
    second_import = invoke_json(
        runner, ["vocab", "import", "--json", json.dumps({"path": str(seed_path)})]
    )
    assert first_import["created_count"] == 2
    assert first_import["updated_count"] == 1
    assert first_import["invalid_count"] == 1
    assert second_import["created_count"] == 0
    filtered = invoke_json(runner, ["vocab", "start", "--json", '{"tags":["confirm","cloze"]}'])
    assert {item["id"] for item in filtered["items"]} >= {manual["item_id"]}  # type: ignore[index]
    item_id = filtered["items"][0]["id"]  # type: ignore[index]
    invoke_json(
        runner,
        [
            "vocab",
            "answer",
            "--json",
            json.dumps({"item_id": item_id, "answer": "так", "idempotency_key": "phase2-k1"}),
        ],
    )
    history = invoke_json(
        runner, ["vocab", "history", "--json", json.dumps({"item_id": item_id})]
    )
    assert len(history["attempts"]) == 1


def test_cross_session_weak_targeting_filter_precedence_and_determinism(runner) -> None:  # type: ignore[no-untyped-def]
    invoke_json(
        runner,
        [
            "setup",
            "write",
            "--json",
            '{"profile":{"native_language":"en","target_language":"uk"},"preferences":{"session_length":2}}',
        ],
    )
    weak = invoke_json(
        runner,
        [
            "vocab",
            "add",
            "--json",
            json.dumps(
                {
                    "target": "книга",
                    "prompt": "book",
                    "accepted_answers": ["книга"],
                    "tags": ["case"],
                }
            ),
        ],
    )
    plain = invoke_json(
        runner,
        [
            "vocab",
            "add",
            "--json",
            json.dumps(
                {
                    "target": "читати",
                    "prompt": "read",
                    "accepted_answers": ["читати"],
                    "tags": ["aspect"],
                }
            ),
        ],
    )
    conn = connect(resolve_paths().database_path)
    try:
        now = datetime.now(UTC).replace(microsecond=0)
        conn.execute(
            "UPDATE vocabulary_items SET state = 'review', repetition_count = 1, due_at = ? WHERE id = ?",
            ((now - timedelta(minutes=1)).isoformat(), plain["item_id"]),
        )
        conn.execute(
            "UPDATE vocabulary_items SET state = 'review', repetition_count = 1, due_at = ? WHERE id = ?",
            (now.isoformat(), weak["item_id"]),
        )
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
                ) VALUES (?, ?, 'writing', 'low', 'case', '', 'high', ?)
                """,
                (f"mistake_{session_id}", session_id, datetime(2026, 5, day, tzinfo=UTC).isoformat()),
            )
        conn.commit()
    finally:
        conn.close()

    selected_runs = [
        invoke_json(runner, ["vocab", "start", "--json"])["items"] for _ in range(5)
    ]
    selected_ids = [[item["id"] for item in items] for items in selected_runs]  # type: ignore[index]
    assert all(ids == selected_ids[0] for ids in selected_ids)
    assert weak["item_id"] in selected_ids[0]

    filtered = invoke_json(runner, ["vocab", "start", "--json", '{"tags":["aspect"]}'])
    assert {item["id"] for item in filtered["items"]} == {plain["item_id"]}  # type: ignore[index]
