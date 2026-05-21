from __future__ import annotations

from datetime import UTC, datetime, timedelta

from language_tutor.dal.repositories import TutorRepository, new_id
from language_tutor.dal.sqlite_store import connect
from language_tutor.feedback import vocabulary_feedback
from language_tutor.schemas import VocabularyItem
from language_tutor.srs import quality_for_verdict, schedule_review


def test_vocab_answer_idempotency(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        item = VocabularyItem(
            id=new_id("vocab"),
            target_language="uk",
            prompt="hello",
            lemma="привіт",
            accepted_answers=["привіт"],
        )
        repo.upsert_vocabulary_item(item)
        conn.commit()
        feedback = vocabulary_feedback("привіт", ["привіт"])
        next_state = schedule_review(item.state, feedback.verdict)
        first = repo.record_vocab_answer(
            item=item,
            session_id="s1",
            answer="привіт",
            idempotency_key="k1",
            feedback=feedback,
            previous_state=item.state,
            next_state=next_state,
            quality=quality_for_verdict(feedback.verdict),
        )
        second = repo.record_vocab_answer(
            item=item,
            session_id="s1",
            answer="привіт",
            idempotency_key="k1",
            feedback=feedback,
            previous_state=item.state,
            next_state=next_state,
            quality=quality_for_verdict(feedback.verdict),
        )
        assert first.review.id == second.review.id
        assert second.duplicate is True
    finally:
        conn.close()


def test_import_merges_additive_metadata_without_review_reset(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        item = VocabularyItem(
            id=new_id("vocab"),
            target_language="uk",
            prompt="hello",
            lemma="привіт",
            accepted_answers=["привіт"],
            tags=["greetings"],
            sources=["manual"],
        )
        repo.insert_vocabulary_item(item)
        conn.commit()
        feedback = vocabulary_feedback("привіт", ["привіт"])
        next_state = schedule_review(item.state, feedback.verdict)
        repo.record_vocab_answer(
            item=item,
            session_id="s1",
            answer="привіт",
            idempotency_key="merge-k1",
            feedback=feedback,
            previous_state=item.state,
            next_state=next_state,
            quality=quality_for_verdict(feedback.verdict),
        )
        duplicate = item.model_copy(
            update={
                "id": new_id("vocab"),
                "accepted_answers": ["привіт", "privit"],
                "tags": ["daily"],
                "notes": ["informal"],
                "sources": ["seed"],
            }
        )
        status, item_id = repo.import_vocabulary_item(duplicate)
        stored = repo.get_vocabulary_item(item_id)
        review_count = conn.execute("SELECT COUNT(*) AS count FROM vocabulary_reviews").fetchone()
        assert status == "updated"
        assert stored.accepted_answers == ["привіт", "privit"]
        assert stored.tags == ["greetings", "daily"]
        assert stored.notes == ["informal"]
        assert stored.sources == ["manual", "seed"]
        assert int(review_count["count"]) == 1
        assert stored.state.state == next_state.state
    finally:
        conn.close()


def test_tag_filter_is_inclusive_and_reports_not_due_count(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        due = VocabularyItem(
            id=new_id("vocab"),
            target_language="uk",
            prompt="hello",
            lemma="привіт",
            accepted_answers=["привіт"],
            tags=["Greetings"],
        )
        not_due = VocabularyItem(
            id=new_id("vocab"),
            target_language="uk",
            prompt="thanks",
            lemma="дякую",
            accepted_answers=["дякую"],
            tags=["thanks"],
            state=due.state.model_copy(
                update={"due_at": datetime.now(UTC) + timedelta(days=1)}
            ),
        )
        repo.insert_vocabulary_item(due)
        repo.insert_vocabulary_item(not_due)
        conn.commit()
        items, matching_count, due_matching_count = repo.due_vocabulary_by_tags(
            10, datetime.now(UTC), ["greetings", "thanks"]
        )
        assert [item.id for item in items] == [due.id]
        assert matching_count == 2
        assert due_matching_count == 1
    finally:
        conn.close()


def test_review_history_orders_attempts_and_keeps_new_status(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        item = VocabularyItem(
            id=new_id("vocab"),
            target_language="uk",
            prompt="hello",
            lemma="привіт",
            accepted_answers=["привіт"],
        )
        repo.insert_vocabulary_item(item)
        conn.commit()
        assert repo.vocabulary_review_history(item.id, datetime.now(UTC)).due_status == "new"
        feedback = vocabulary_feedback("wrong", ["привіт"])
        next_state = schedule_review(item.state, feedback.verdict)
        repo.record_vocab_answer(
            item=item,
            session_id="s1",
            answer="wrong",
            idempotency_key="hist-k1",
            feedback=feedback,
            previous_state=item.state,
            next_state=next_state,
            quality=quality_for_verdict(feedback.verdict),
        )
        history = repo.vocabulary_review_history(item.id, datetime.now(UTC))
        assert len(history.attempts) == 1
        assert history.attempts[0].learner_answer == "wrong"
        assert history.attempts[0].answer_detail_available is True
    finally:
        conn.close()
