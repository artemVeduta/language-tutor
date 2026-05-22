from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.schemas import (
    CheckpointModality,
    CheckpointStepKind,
    HostId,
    SafeStepState,
    SessionStatus,
)


def _now() -> datetime:
    return datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC)


@pytest.fixture()
def repo(tmp_path: Path):  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        yield TutorRepository(conn), conn
    finally:
        conn.close()


def test_open_session_inserts_open_row_with_timestamps(repo) -> None:  # type: ignore[no-untyped-def]
    r, conn = repo
    session = r.open_session(HostId.CLAUDE, host_conversation_id=None, now=_now())
    assert session.status == SessionStatus.OPEN.value
    assert session.started_at == _now()
    assert session.last_seen_at == _now()
    assert session.closed_at is None
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session.id,)).fetchone()
    assert row is not None
    assert row["status"] == "open"
    assert row["host"] == "claude"


def test_open_session_records_host_conversation_id_when_provided(repo) -> None:  # type: ignore[no-untyped-def]
    r, conn = repo
    session = r.open_session(HostId.CODEX, host_conversation_id="conv-123", now=_now())
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session.id,)).fetchone()
    assert row["host_conversation_id"] == "conv-123"


def test_open_session_is_durably_committed(tmp_path: Path) -> None:
    """FR-013: each write commits before returning."""
    db_path = tmp_path / "db.sqlite3"
    conn = connect(db_path)
    try:
        TutorRepository(conn).open_session(HostId.CLAUDE, None, _now())
    finally:
        conn.close()
    fresh = sqlite3.connect(db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) FROM sessions WHERE status = 'open'").fetchone()[0]
        assert count == 1
    finally:
        fresh.close()


def test_touch_session_advances_last_seen(repo) -> None:  # type: ignore[no-untyped-def]
    r, conn = repo
    session = r.open_session(HostId.CLAUDE, None, _now())
    later = _now() + timedelta(minutes=5)
    r.touch_session(session.id, now=later)
    row = conn.execute("SELECT last_seen_at FROM sessions WHERE id = ?", (session.id,)).fetchone()
    assert row["last_seen_at"] == later.isoformat()


def test_record_checkpoint_persists_immediately(tmp_path: Path) -> None:
    """FR-005, FR-013: checkpoint is committed before record_checkpoint returns."""
    db_path = tmp_path / "db.sqlite3"
    conn = connect(db_path)
    try:
        r = TutorRepository(conn)
        session = r.open_session(HostId.CLAUDE, None, _now())
        checkpoint = r.record_checkpoint(
            session_id=session.id,
            modality=CheckpointModality.LESSON,
            step_kind=CheckpointStepKind.PROMPT_SHOWN,
            prompt_ref="lesson_1_step1",
            state=SafeStepState(prompt_ref="lesson_1_step1", step_index=0, total_steps=4),
            summary="Showed step 1/4",
            now=_now(),
        )
        assert checkpoint.session_id == session.id
        assert checkpoint.modality == CheckpointModality.LESSON.value
        assert checkpoint.step_kind == CheckpointStepKind.PROMPT_SHOWN.value
    finally:
        conn.close()
    fresh = sqlite3.connect(db_path)
    try:
        row = fresh.execute(
            "SELECT * FROM checkpoints WHERE session_id = ?", (session.id,)
        ).fetchone()
        assert row is not None
    finally:
        fresh.close()


def test_record_checkpoint_updates_last_seen(repo) -> None:  # type: ignore[no-untyped-def]
    r, conn = repo
    session = r.open_session(HostId.CLAUDE, None, _now())
    later = _now() + timedelta(minutes=3)
    r.record_checkpoint(
        session_id=session.id,
        modality=CheckpointModality.READING,
        step_kind=CheckpointStepKind.PROMPT_SHOWN,
        prompt_ref=None,
        state=SafeStepState(),
        summary="ping",
        now=later,
    )
    row = conn.execute("SELECT last_seen_at FROM sessions WHERE id = ?", (session.id,)).fetchone()
    assert row["last_seen_at"] == later.isoformat()


def test_record_checkpoint_rejects_unknown_session(repo) -> None:  # type: ignore[no-untyped-def]
    r, _ = repo
    with pytest.raises(KeyError):
        r.record_checkpoint(
            session_id="sess_missing",
            modality=CheckpointModality.LESSON,
            step_kind=CheckpointStepKind.PROMPT_SHOWN,
            prompt_ref=None,
            state=SafeStepState(),
            summary="no",
            now=_now(),
        )
