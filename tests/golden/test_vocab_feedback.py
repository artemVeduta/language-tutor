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
    VocabularySelectionSource,
    WeakTagSourceEvent,
)
from language_tutor.vocab import (
    active_weak_tag_signals,
    select_vocabulary_queue,
    selection_candidates,
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


def test_queue_selection_snapshot() -> None:
    now = datetime(2026, 5, 21, 12, tzinfo=UTC)
    signals = active_weak_tag_signals(
        [
            WeakTagSourceEvent(
                session_id="s1", tag="case", source="mistake_events", observed_at=now
            ),
            WeakTagSourceEvent(
                session_id="s2", tag="case", source="mistake_events", observed_at=now
            ),
        ]
    )
    sources = [
        VocabularySelectionSource(
            item=VocabularyItem(
                id="vocab_case",
                target_language="uk",
                prompt="book",
                accepted_answers=["книга"],
                tags=["case"],
                state=VocabularyItemState(state="review", repetition_count=1, due_at=now),
            ),
            created_at=now,
        ),
        VocabularySelectionSource(
            item=VocabularyItem(
                id="vocab_plain",
                target_language="uk",
                prompt="and",
                accepted_answers=["і"],
                tags=[],
                state=VocabularyItemState(state="new", due_at=now),
            ),
            created_at=now,
        ),
    ]
    items, reasons, reserved = select_vocabulary_queue(
        selection_candidates(
            sources, now=now, active_weak_tags=signals, explicit_filter_active=False
        ),
        effective_count=2,
        active_weak_tags=signals,
    )
    assert [item.id for item in items] == ["vocab_case", "vocab_plain"]
    assert [reason.model_dump(mode="json", exclude_none=True) for reason in reasons] == [
        {
            "item_id": "vocab_case",
            "rank": 1,
            "bucket": "due_today",
            "reasons": ["due", "weak_tag_match"],
            "matched_weak_tags": ["case"],
            "due_at": "2026-05-21T12:00:00Z",
        },
        {
            "item_id": "vocab_plain",
            "rank": 2,
            "bucket": "new_fill",
            "reasons": ["new_card_fill"],
            "matched_weak_tags": [],
        },
    ]
    assert reserved is False
