from __future__ import annotations

import json
from pathlib import Path

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
