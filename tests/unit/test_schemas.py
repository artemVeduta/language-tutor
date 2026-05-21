from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from language_tutor.schemas import (
    FeedbackEnvelope,
    LearnerProfile,
    VocabularyCardDefinition,
    VocabularyDrillRequest,
    VocabularyItem,
    export_json_schemas,
)


def test_profile_requires_languages() -> None:
    profile = LearnerProfile(native_language="en", target_language="uk")
    assert profile.level_target == "A1"


def test_json_schema_export(tmp_path: Path) -> None:
    export_json_schemas(tmp_path)
    schema = json.loads((tmp_path / "feedback_envelope.schema.json").read_text())
    assert schema["title"] == FeedbackEnvelope.__name__
    assert (tmp_path / "vocabulary_card_definition.schema.json").exists()
    assert (tmp_path / "vocabulary_import_summary.schema.json").exists()
    assert (tmp_path / "vocabulary_session_plan.schema.json").exists()
    assert (tmp_path / "vocabulary_review_history.schema.json").exists()


def test_vocabulary_item_phase2_defaults() -> None:
    item = VocabularyItem(
        id="vocab_1",
        target_language="uk",
        prompt="hello",
        accepted_answers=["привіт"],
    )
    assert item.card_type == "standard"
    assert item.notes == []
    assert item.sources == []


def test_card_definition_rejects_empty_metadata() -> None:
    with pytest.raises(ValidationError):
        VocabularyCardDefinition.model_validate(
            {
                "target": "привіт",
                "prompt": "hello",
                "accepted_answers": ["привіт"],
                "tags": [""],
            }
        )


def test_card_definition_validates_cloze_marker_count() -> None:
    card = VocabularyCardDefinition.model_validate(
        {
            "card_type": "cloze",
            "target": "привіт",
            "prompt": "{{answer}} is a greeting.",
            "accepted_answers": ["привіт"],
        }
    )
    assert card.card_type == "cloze"
    with pytest.raises(ValidationError):
        VocabularyCardDefinition.model_validate(
            {
                "card_type": "cloze",
                "target": "привіт",
                "prompt": "{{answer}} and {{answer}}",
                "accepted_answers": ["привіт"],
            }
        )


def test_drill_request_rejects_empty_tags() -> None:
    with pytest.raises(ValidationError):
        VocabularyDrillRequest.model_validate({"tags": []})
