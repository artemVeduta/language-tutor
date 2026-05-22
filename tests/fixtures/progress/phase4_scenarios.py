from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from freezegun import freeze_time

from language_tutor.dal.repositories import TutorRepository, new_id
from language_tutor.feedback import vocabulary_feedback
from language_tutor.schemas import ErrorSpan, FeedbackEnvelope, VocabularyItem
from language_tutor.srs import quality_for_verdict, schedule_review

BASE_TIME = datetime(2026, 5, 21, 12, tzinfo=UTC)


def seed_completed_session(
    repo: TutorRepository,
    *,
    session_id: str,
    day_offset: int,
    weak_tags: list[str],
    summary: str = "Focused practice saved.",
) -> None:
    observed_at = BASE_TIME - timedelta(days=day_offset)
    repo.conn.execute(
        """
        INSERT INTO session_summaries(
          id, session_id, summary_for_user, summary_for_next_boot,
          weak_tags_json, next_focus, cost_snapshot_json, created_at
        ) VALUES (?, ?, ?, ?, ?, 'review_due_items', '{}', ?)
        """,
        (
            f"summary_{session_id}",
            session_id,
            summary,
            summary,
            json.dumps(weak_tags),
            observed_at.isoformat(),
        ),
    )
    repo.conn.commit()


@freeze_time(BASE_TIME)
def seed_vocab_review(
    repo: TutorRepository,
    *,
    session_id: str,
    tag: str,
    answer: str = "привіт",
) -> None:
    item = VocabularyItem(
        id=new_id("vocab"),
        target_language="uk",
        prompt=f"{tag} prompt {session_id}",
        accepted_answers=["привіт"],
        tags=[tag],
    )
    repo.insert_vocabulary_item(item)
    repo.conn.commit()
    feedback = vocabulary_feedback(answer, ["привіт"])
    next_state = schedule_review(item.state, feedback.verdict)
    repo.record_vocab_answer(
        item=item,
        session_id=session_id,
        answer=answer,
        idempotency_key=f"{session_id}-{tag}-{answer}",
        feedback=feedback,
        previous_state=item.state,
        next_state=next_state,
        quality=quality_for_verdict(feedback.verdict),
    )


@freeze_time(BASE_TIME)
def seed_writing_mistake(
    repo: TutorRepository,
    *,
    session_id: str,
    tag: str,
    severity: str = "medium",
    confidence: str = "high",
) -> None:
    feedback = FeedbackEnvelope(
        verdict="partial",
        severity=severity,  # type: ignore[arg-type]
        confidence=confidence,  # type: ignore[arg-type]
        error_spans=[
            ErrorSpan(
                text="private span",
                tag=tag,  # type: ignore[arg-type]
                severity=severity,  # type: ignore[arg-type]
                explanation="private prose",
            )
        ],
    )
    repo.record_writing_answer(session_id, "writing_prompt", "private answer", feedback)


def seed_one_session(repo: TutorRepository) -> None:
    seed_completed_session(repo, session_id="s1", day_offset=0, weak_tags=["case"])
    seed_vocab_review(repo, session_id="s1", tag="case", answer="wrong")
    seed_writing_mistake(repo, session_id="s1", tag="case")
    repo.conn.commit()


def seed_mixed_history(repo: TutorRepository, count: int = 10) -> None:
    for index in range(count):
        session_id = f"s{index:02d}"
        tag = "case" if index % 2 == 0 else "aspect"
        seed_completed_session(repo, session_id=session_id, day_offset=count - index, weak_tags=[tag])
        seed_vocab_review(
            repo,
            session_id=session_id,
            tag=tag,
            answer="wrong" if index % 3 == 0 else "привіт",
        )
        if index % 2 == 0:
            seed_writing_mistake(repo, session_id=session_id, tag=tag, severity="high")
    repo.conn.commit()


def seed_one_year(repo: TutorRepository, days: int = 365) -> None:
    for index in range(days):
        session_id = f"year_{index:03d}"
        tag = ["case", "aspect", "word_order"][index % 3]
        seed_completed_session(repo, session_id=session_id, day_offset=days - index, weak_tags=[tag])
        seed_vocab_review(repo, session_id=session_id, tag=tag)
        if index % 4 == 0:
            seed_writing_mistake(repo, session_id=session_id, tag=tag, severity="low")
    repo.conn.commit()


def no_data(_: TutorRepository) -> None:
    return None


def stale_tag(repo: TutorRepository) -> None:
    seed_mixed_history(repo, 35)


def tied_tag(repo: TutorRepository) -> None:
    for tag in ("aspect", "case"):
        seed_completed_session(repo, session_id=f"s_{tag}", day_offset=0, weak_tags=[tag])
        seed_vocab_review(repo, session_id=f"s_{tag}", tag=tag, answer="wrong")
    repo.conn.commit()


def skipped_session(repo: TutorRepository) -> None:
    seed_completed_session(repo, session_id="valid", day_offset=0, weak_tags=["case"])
    repo.conn.commit()


def long_text(repo: TutorRepository) -> None:
    tag = "case " + "long" * 20
    seed_completed_session(repo, session_id="long", day_offset=0, weak_tags=[tag], summary="summary " * 30)
    repo.conn.commit()
