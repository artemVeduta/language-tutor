from __future__ import annotations

from datetime import UTC, datetime

from language_tutor.schemas import LearnerPreferences, Verdict, VocabularyItemState
from language_tutor.srs import quality_for_verdict, schedule_review
from language_tutor.vocab import queue_size


def test_sm2_correct_advances_schedule() -> None:
    now = datetime(2026, 5, 20, tzinfo=UTC)
    next_state = schedule_review(VocabularyItemState(due_at=now), Verdict.CORRECT, now)
    assert next_state.repetition_count == 1
    assert next_state.interval_days == 1
    assert quality_for_verdict(Verdict.CORRECT) == 5


def test_sm2_is_invariant_across_review_intensity() -> None:
    now = datetime(2026, 5, 20, tzinfo=UTC)
    previous = VocabularyItemState(
        state="review",
        ease_factor=2.4,
        repetition_count=3,
        interval_days=7,
        due_at=now,
    )
    schedules = []
    for intensity in ("light", "normal", "heavy"):
        assert queue_size(LearnerPreferences(session_length=10, review_intensity=intensity)) >= 1
        schedules.append(schedule_review(previous, Verdict.PARTIAL, now))
    assert schedules[0] == schedules[1] == schedules[2]
