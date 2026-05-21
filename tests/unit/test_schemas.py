from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from language_tutor.schemas import (
    FeedbackEnvelope,
    LearnerPreferences,
    LearnerProfile,
    SelectionPolicy,
    SelectionReason,
    VocabularyCardDefinition,
    VocabularyDrillRequest,
    VocabularyItem,
    VocabularySessionPlan,
    WeakTagSignal,
    WeakTagSourceCounts,
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
    assert (tmp_path / "weak_tag_signal.schema.json").exists()
    assert (tmp_path / "selection_reason.schema.json").exists()
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


def test_smarter_engine_schema_contracts() -> None:
    signal = WeakTagSignal(
        tag="case",
        session_count=2,
        latest_seen_at="2026-05-21T12:00:00Z",
        priority_rank=1,
        source_counts=WeakTagSourceCounts(mistake_events=2, low_quality_reviews=1),
    )
    reason = SelectionReason(
        item_id="vocab_1",
        rank=1,
        bucket="due_today",
        reasons=["due", "weak_tag_match"],
        matched_weak_tags=["case"],
        due_at="2026-05-21T12:00:00Z",
    )
    plan = VocabularySessionPlan(
        items=[
            VocabularyItem(
                id="vocab_1",
                target_language="uk",
                prompt="book",
                accepted_answers=["книга"],
            )
        ],
        requested_count=90,
        effective_count=60,
        active_weak_tags=[signal],
        selection_reasons=[reason],
        selection_policy=SelectionPolicy(intensity="heavy", reserved_non_weak_due_slot=True),
    )
    assert plan.active_weak_tags[0].source_counts.low_quality_reviews == 1
    assert plan.selection_reasons[0].item_id == "vocab_1"
    assert plan.selection_policy.intensity == "heavy"


def test_review_intensity_validation() -> None:
    assert LearnerPreferences().review_intensity == "normal"
    with pytest.raises(ValidationError):
        LearnerPreferences.model_validate({"review_intensity": "extreme"})
