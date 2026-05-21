from __future__ import annotations

from datetime import UTC, datetime, timedelta

from language_tutor.schemas import (
    LearnerPreferences,
    VocabularyItem,
    VocabularyItemState,
    VocabularySelectionSource,
    WeakTagSourceEvent,
)
from language_tutor.vocab import (
    active_weak_tag_signals,
    queue_size,
    select_vocabulary_queue,
    selection_candidates,
)

NOW = datetime(2026, 5, 21, 12, tzinfo=UTC)


def source(
    item_id: str,
    prompt: str,
    tags: list[str],
    *,
    state: str = "review",
    due_at: datetime | None = None,
    created_at: datetime | None = None,
) -> VocabularySelectionSource:
    return VocabularySelectionSource(
        item=VocabularyItem(
            id=item_id,
            target_language="uk",
            prompt=prompt,
            accepted_answers=[prompt],
            tags=tags,
            state=VocabularyItemState(
                state=state, due_at=due_at or NOW, repetition_count=0 if state == "new" else 1
            ),
        ),
        created_at=created_at or NOW,
    )


def test_active_weak_tags_count_sessions_rank_and_limit() -> None:
    events = [
        WeakTagSourceEvent(
            session_id="s1", tag="case", source="mistake_events", observed_at=NOW
        ),
        WeakTagSourceEvent(
            session_id="s1", tag="case", source="mistake_events", observed_at=NOW
        ),
        WeakTagSourceEvent(
            session_id="s2",
            tag="case",
            source="low_quality_reviews",
            observed_at=NOW - timedelta(hours=1),
        ),
        WeakTagSourceEvent(
            session_id="s1", tag="aspect", source="mistake_events", observed_at=NOW
        ),
        WeakTagSourceEvent(
            session_id="s2", tag="aspect", source="mistake_events", observed_at=NOW
        ),
        WeakTagSourceEvent(
            session_id="s1", tag="punctuation", source="mistake_events", observed_at=NOW
        ),
    ]
    signals = active_weak_tag_signals(events)
    assert [signal.tag for signal in signals] == ["aspect", "case"]
    assert signals[0].session_count == 2
    assert signals[1].source_counts.mistake_events == 2
    assert signals[1].source_counts.low_quality_reviews == 1


def test_due_first_queue_weak_priority_reserved_slot_and_stable_ties() -> None:
    signals = active_weak_tag_signals(
        [
            WeakTagSourceEvent(
                session_id="s1", tag="case", source="mistake_events", observed_at=NOW
            ),
            WeakTagSourceEvent(
                session_id="s2", tag="case", source="mistake_events", observed_at=NOW
            ),
        ]
    )
    candidates = selection_candidates(
        [
            source(
                "overdue",
                "zzz",
                ["misc"],
                due_at=NOW - timedelta(days=1),
                created_at=NOW - timedelta(days=5),
            ),
            source("weak", "bbb", ["case"], due_at=NOW),
            source("nonweak", "aaa", ["misc"], due_at=NOW),
            source("weak2", "ccc", ["case"], due_at=NOW),
        ],
        now=NOW,
        active_weak_tags=signals,
        explicit_filter_active=False,
    )
    items, reasons, reserved = select_vocabulary_queue(
        candidates, effective_count=3, active_weak_tags=signals
    )
    assert [item.id for item in items] == ["overdue", "weak", "weak2"]
    assert reserved is False
    assert reasons[0].bucket == "overdue_due"
    assert "weak_tag_match" in reasons[1].reasons

    without_overdue = selection_candidates(
        [
            source("weak", "bbb", ["case"], due_at=NOW),
            source("nonweak", "aaa", ["misc"], due_at=NOW),
            source("weak2", "ccc", ["case"], due_at=NOW),
        ],
        now=NOW,
        active_weak_tags=signals,
        explicit_filter_active=False,
    )
    items, reasons, reserved = select_vocabulary_queue(
        without_overdue, effective_count=2, active_weak_tags=signals
    )
    assert [item.id for item in items] == ["weak", "nonweak"]
    assert reserved is True
    assert "reserved_non_weak_due" in reasons[1].reasons


def test_new_fill_explicit_filter_and_untagged_fallback() -> None:
    signals = active_weak_tag_signals(
        [
            WeakTagSourceEvent(
                session_id="s1", tag="case", source="mistake_events", observed_at=NOW
            ),
            WeakTagSourceEvent(
                session_id="s2", tag="case", source="mistake_events", observed_at=NOW
            ),
        ]
    )
    candidates = selection_candidates(
        [
            source("weak_new", "b", ["case"], state="new", created_at=NOW - timedelta(days=1)),
            source("plain_new", "a", [], state="new", created_at=NOW - timedelta(days=2)),
        ],
        now=NOW,
        active_weak_tags=signals,
        explicit_filter_active=True,
    )
    items, reasons, _ = select_vocabulary_queue(
        candidates, effective_count=2, active_weak_tags=signals
    )
    assert [item.id for item in items] == ["weak_new", "plain_new"]
    assert reasons[0].reasons == [
        "new_card_fill",
        "explicit_filter_match",
        "weak_tag_match",
    ]
    assert reasons[1].reasons == ["new_card_fill", "explicit_filter_match"]


def test_queue_size_intensity_rounding_minimum_and_cap() -> None:
    assert queue_size(LearnerPreferences(session_length=1, review_intensity="light")) == 1
    assert queue_size(LearnerPreferences(session_length=5, review_intensity="light")) == 2
    assert queue_size(LearnerPreferences(session_length=10, review_intensity="normal")) == 10
    assert queue_size(LearnerPreferences(session_length=41, review_intensity="heavy")) == 60
