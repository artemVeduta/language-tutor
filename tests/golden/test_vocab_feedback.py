from __future__ import annotations

from datetime import UTC, datetime

from language_tutor.feedback import (
    render_feedback,
    render_vocab_import_summary,
    render_vocab_review_history,
    vocabulary_feedback,
)
from language_tutor.schemas import (
    SeedImportEntryResult,
    SeedImportResult,
    Verdict,
    VocabularyItem,
    VocabularyItemState,
    VocabularyReviewAttempt,
    VocabularyReviewHistory,
)


def test_vocab_feedback_markdown() -> None:
    feedback = vocabulary_feedback("privit", ["привіт", "privit"], transliteration_tolerance=True)
    assert "Verdict: correct" in render_feedback(feedback)


def test_vocab_import_summary_rendering() -> None:
    summary = SeedImportResult(
        path="seed.json",
        created_count=1,
        updated_count=1,
        skipped_count=0,
        invalid_count=1,
        entries=[
            SeedImportEntryResult(index=0, status="created", item_id="vocab_1"),
            SeedImportEntryResult(index=1, status="updated", item_id="vocab_1"),
            SeedImportEntryResult(
                index=2,
                status="invalid",
                repair_hint="prompt is required",
            ),
        ],
    )
    rendered = render_vocab_import_summary(summary)
    assert "Created: 1; Updated: 1; Skipped: 0; Invalid: 1" in rendered
    assert "2: invalid - prompt is required" in rendered


def test_vocab_history_rendering_summarizes_attempts() -> None:
    state = VocabularyItemState()
    history = VocabularyReviewHistory(
        item=VocabularyItem(
            id="vocab_1",
            target_language="uk",
            prompt="hello",
            accepted_answers=["привіт"],
        ),
        current_state=state,
        due_status="new",
        attempts=[
            VocabularyReviewAttempt(
                id=f"rev_{index}",
                session_id="s1",
                answer_event_id=f"ans_{index}",
                learner_answer="привіт",
                verdict=Verdict.CORRECT,
                quality=5,
                previous_state=state,
                next_state=state,
                reviewed_at=datetime(2026, 5, 21, 12, index, tzinfo=UTC),
            )
            for index in range(12)
        ],
    )
    rendered = render_vocab_review_history(history)
    assert "Attempts: 12" in rendered
    assert "2 older attempts omitted" in rendered
