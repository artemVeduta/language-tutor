"""T028 (US2): ``recent_sessions`` ordering + ``SessionView`` label derivation.

Covers FR-018 — ``stale``/``abandoned`` are read-time labels only, derived
deterministically from the session set and the boot-time ``now``. Never stored.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.lifecycle import (
    ABANDONED_AFTER,
    derive_session_label,
    session_views,
)
from language_tutor.schemas import HostId, SessionLabel, SessionStatus


def _t(days_ago: int) -> datetime:
    return datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC) - timedelta(days=days_ago)


NOW = datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC)


@pytest.fixture()
def repo(tmp_path: Path):  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        yield TutorRepository(conn), conn
    finally:
        conn.close()


def test_recent_sessions_orders_by_last_seen_at_desc(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    older = r.open_session(HostId.CLAUDE, None, _t(days_ago=10))
    newer = r.open_session(HostId.CODEX, None, _t(days_ago=2))
    middle = r.open_session(HostId.HERMES, None, _t(days_ago=5))
    rows = r.recent_sessions(limit=10)
    assert [s.id for s in rows] == [newer.id, middle.id, older.id]


def test_recent_sessions_respects_limit(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    for i in range(5):
        r.open_session(HostId.CLAUDE, None, _t(days_ago=i))
    rows = r.recent_sessions(limit=3)
    assert len(rows) == 3


def test_derive_label_newest_open_is_open(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    newest = r.open_session(HostId.CLAUDE, None, _t(days_ago=0))
    label = derive_session_label(newest, is_newest=True, now=NOW)
    assert label == SessionLabel.OPEN


def test_derive_label_older_open_is_stale_within_14_days(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    older = r.open_session(HostId.CLAUDE, None, _t(days_ago=10))
    label = derive_session_label(older, is_newest=False, now=NOW)
    assert label == SessionLabel.STALE


def test_derive_label_older_open_past_14_days_is_abandoned(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    s = r.open_session(HostId.CLAUDE, None, _t(days_ago=30))
    label = derive_session_label(s, is_newest=False, now=NOW)
    assert label == SessionLabel.ABANDONED


def test_derive_label_closed_is_closed(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    s = r.open_session(HostId.CLAUDE, None, _t(days_ago=2))
    closed = r.close_session(s.id, now=_t(days_ago=2))
    assert closed.status == SessionStatus.CLOSED.value
    # Closed sessions get the closed label whether they're newest or not.
    assert derive_session_label(closed, is_newest=False, now=NOW) == SessionLabel.CLOSED
    assert derive_session_label(closed, is_newest=True, now=NOW) == SessionLabel.CLOSED


def test_session_views_marks_first_as_newest(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    older = r.open_session(HostId.CLAUDE, None, _t(days_ago=10))
    newer = r.open_session(HostId.CODEX, None, _t(days_ago=2))
    rows = r.recent_sessions(limit=10)
    views = session_views(rows, now=NOW)
    assert views[0].session.id == newer.id
    assert views[0].label == SessionLabel.OPEN
    # Older still within 14 days → stale.
    assert views[1].session.id == older.id
    assert views[1].label == SessionLabel.STALE


def test_session_views_empty() -> None:
    assert session_views([], now=NOW) == []


def test_abandoned_threshold_is_14_days() -> None:
    """Boundary: exactly 14 days old (older, not newest) → still stale."""
    assert timedelta(days=14) == ABANDONED_AFTER
