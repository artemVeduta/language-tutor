from __future__ import annotations

from datetime import UTC, datetime

from language_tutor.boot_context import build_boot_context, render_boot_context
from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.schemas import LearnerPreferences, LearnerProfile


def test_boot_context_bounded(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        context = build_boot_context(
            repo, LearnerProfile(native_language="en", target_language="uk"), LearnerPreferences()
        )
        rendered = render_boot_context(context)
        assert "First session guidance" in rendered
        assert len(rendered) <= 6000
        assert len(context.sections) <= 8
    finally:
        conn.close()


def test_boot_context_weak_summary_is_bounded_and_safe(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        for index in range(10):
            session_id = f"s{index}"
            conn.execute(
                """
                INSERT INTO session_summaries(
                  id, session_id, summary_for_user, summary_for_next_boot,
                  weak_tags_json, next_focus, cost_snapshot_json, created_at
                ) VALUES (?, ?, 'u', 'b', '[]', 'focus', '{}', ?)
                """,
                (
                    f"summary_{index}",
                    session_id,
                    datetime(2026, 5, 10 + index, tzinfo=UTC).isoformat(),
                ),
            )
            for tag in ("case", "aspect", "agreement"):
                conn.execute(
                    """
                    INSERT INTO mistake_events(
                      id, session_id, skill, severity, tag, explanation, confidence, created_at
                    ) VALUES (?, ?, 'writing', 'low', ?, 'full feedback prose', 'high', ?)
                    """,
                    (
                        f"mistake_{index}_{tag}",
                        session_id,
                        tag,
                        datetime(2026, 5, 10 + index, tzinfo=UTC).isoformat(),
                    ),
                )
        conn.commit()
        rendered = render_boot_context(
            build_boot_context(
                repo,
                LearnerProfile(native_language="en", target_language="uk"),
                LearnerPreferences(),
            )
        )
        assert "case" in rendered
        assert "full feedback prose" not in rendered
        assert len(rendered) <= 6000
    finally:
        conn.close()
