"""T029 (US2): boot context prior-session block (FR-008, FR-016, SC-005).

Asserts:
- N=3 default limit
- most-recent-first ordering by ``last_seen_at``
- deterministic shape for the same inputs
- token-budget on the rendered markdown stays bounded
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from language_tutor.boot_context import render_boot_context
from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.lifecycle import DEFAULT_PRIOR_SESSION_LIMIT, start_session
from language_tutor.schemas import HostId, LearnerPreferences, LearnerProfile, SessionLabel


def _profile() -> LearnerProfile:
    return LearnerProfile(native_language="en", target_language="uk")


def _now() -> datetime:
    return datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC)


def test_default_prior_session_limit_is_three() -> None:
    assert DEFAULT_PRIOR_SESSION_LIMIT == 3


def test_prior_block_caps_to_three_most_recent(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        # Five prior sessions at distinct ages.
        recent_ids: list[str] = []
        for days_ago in (10, 8, 5, 2, 1):
            s = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=days_ago))
            recent_ids.append(s.id)
        # `recent_ids` is oldest→newest; expected top-3 most-recent are the last 3.
        expected_top3 = list(reversed(recent_ids[-3:]))

        result = start_session(
            repo,
            profile=_profile(),
            preferences=LearnerPreferences(),
            host=HostId.CLAUDE,
            host_conversation_id=None,
            now=_now(),
        )
        prior_ids = [entry.session_id for entry in result.context.prior_sessions]
        assert prior_ids == expected_top3
        assert len(prior_ids) == 3
    finally:
        conn.close()


def test_prior_block_most_recent_first(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        oldest = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=20))
        middle = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=10))
        newest = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=2))
        result = start_session(
            repo,
            profile=_profile(),
            preferences=LearnerPreferences(),
            host=HostId.CLAUDE,
            host_conversation_id=None,
            now=_now(),
        )
        ids = [entry.session_id for entry in result.context.prior_sessions]
        assert ids == [newest.id, middle.id, oldest.id]
    finally:
        conn.close()


def test_prior_block_labels_are_derived(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        # Old open session → abandoned (>14 days) since a newer one will exist.
        abandoned = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=30))
        # Recent open session → stale (newer one is the boot's freshly-minted session).
        stale = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=2))
        result = start_session(
            repo,
            profile=_profile(),
            preferences=LearnerPreferences(),
            host=HostId.CLAUDE,
            host_conversation_id=None,
            now=_now(),
        )
        by_id = {e.session_id: e for e in result.context.prior_sessions}
        # First-in-list is newest prior → labelled `open` (newest among the prior set).
        assert by_id[stale.id].label == SessionLabel.OPEN.value
        # Old prior → abandoned.
        assert by_id[abandoned.id].label == SessionLabel.ABANDONED.value
    finally:
        conn.close()


def test_prior_block_is_deterministic(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Two boots from identical DB state at the same ``now`` produce identical
    prior-block shape (labels + last_seen_at), modulo the freshly-minted id."""

    def _boot(db_path):  # type: ignore[no-untyped-def]
        conn = connect(db_path)
        try:
            repo = TutorRepository(conn)
            for days_ago in (10, 5, 2):
                repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=days_ago))
            return start_session(
                repo,
                profile=_profile(),
                preferences=LearnerPreferences(),
                host=HostId.CLAUDE,
                host_conversation_id=None,
                now=_now(),
            )
        finally:
            conn.close()

    def _shape(entries):  # type: ignore[no-untyped-def]
        # Strip session_ids (volatile) — assert ordering by last_seen and labels.
        return json.dumps(
            [{"label": e.label, "last_seen_at": e.last_seen_at.isoformat()} for e in entries],
            sort_keys=True,
        )

    first = _boot(tmp_path / "a.sqlite3")
    second = _boot(tmp_path / "b.sqlite3")
    assert _shape(first.context.prior_sessions) == _shape(second.context.prior_sessions)


def test_render_boot_context_stays_under_token_budget(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        for days_ago in (10, 5, 2):
            repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=days_ago))
        result = start_session(
            repo,
            profile=_profile(),
            preferences=LearnerPreferences(),
            host=HostId.CLAUDE,
            host_conversation_id=None,
            now=_now(),
        )
        rendered = render_boot_context(result.context)
        assert len(rendered) <= result.context.max_rendered_chars
    finally:
        conn.close()
