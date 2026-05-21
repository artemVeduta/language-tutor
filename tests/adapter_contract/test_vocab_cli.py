from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import invoke_json


def setup_learner(runner) -> None:  # type: ignore[no-untyped-def]
    invoke_json(
        runner,
        [
            "setup",
            "write",
            "--json",
            '{"profile":{"native_language":"en","target_language":"uk"},"preferences":{"transliteration_tolerance":true}}',
        ],
    )


def test_vocab_start_answer_idempotent(runner) -> None:  # type: ignore[no-untyped-def]
    setup_learner(runner)
    plan = invoke_json(runner, ["vocab", "start", "--json"])
    item_id = plan["items"][0]["id"]  # type: ignore[index]
    payload = f'{{"item_id":"{item_id}","answer":"privit","idempotency_key":"same"}}'
    first = invoke_json(runner, ["vocab", "answer", "--json", payload])
    second = invoke_json(runner, ["vocab", "answer", "--json", payload])
    assert first["review"]["id"] == second["review"]["id"]
    assert second["duplicate"] is True


def test_vocab_add_import_filter_and_history_contract(runner) -> None:  # type: ignore[no-untyped-def]
    setup_learner(runner)
    add_payload = json.dumps(
        {
            "target": "привіт",
            "prompt": "hello",
            "accepted_answers": ["привіт", "privit"],
            "tags": ["greetings"],
            "source": "manual",
        }
    )
    add = invoke_json(runner, ["vocab", "add", "--json", add_payload])
    duplicate = invoke_json(runner, ["vocab", "add", "--json", add_payload])
    assert add["status"] == "created"
    assert duplicate["status"] == "duplicate"
    seed_path = Path("tests/fixtures/vocabulary/phase2_seed.json").resolve()
    imported = invoke_json(
        runner, ["vocab", "import", "--json", json.dumps({"path": str(seed_path)})]
    )
    assert imported["updated_count"] >= 1
    assert imported["invalid_count"] == 1
    filtered = invoke_json(runner, ["vocab", "start", "--json", '{"tags":["daily"]}'])
    assert filtered["matching_count"] == 1
    assert filtered["items"][0]["id"] == add["item_id"]  # type: ignore[index]
    history = invoke_json(
        runner, ["vocab", "history", "--json", json.dumps({"item_id": add["item_id"]})]
    )
    assert history["item"]["id"] == add["item_id"]
    assert history["attempts"] == []


def test_vocab_cloze_reveals_answer(runner) -> None:  # type: ignore[no-untyped-def]
    setup_learner(runner)
    payload = json.dumps(
        {
            "card_type": "cloze",
            "target": "дякую",
            "prompt": "{{answer}} means thank you.",
            "accepted_answers": ["дякую", "diakuiu"],
            "tags": ["cloze"],
        }
    )
    add = invoke_json(runner, ["vocab", "add", "--json", payload])
    plan = invoke_json(runner, ["vocab", "start", "--json", '{"tags":["cloze"]}'])
    assert "____" in plan["items"][0]["prompt"]  # type: ignore[index]
    answer_payload = json.dumps(
        {"item_id": add["item_id"], "answer": "diakuiu", "idempotency_key": "cloze-k1"}
    )
    answer = invoke_json(runner, ["vocab", "answer", "--json", answer_payload])
    assert answer["feedback"]["cloze_sentence"] == "дякую means thank you."
