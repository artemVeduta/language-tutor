from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from language_tutor.boot_context import render_boot_context
from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.lifecycle import start_session
from language_tutor.schemas import (
    CheckpointModality,
    CheckpointStepKind,
    HostId,
    LearnerPreferences,
    LearnerProfile,
    SafeStepState,
)


def _profile() -> LearnerProfile:
    return LearnerProfile(native_language="en", target_language="uk")


def _now() -> datetime:
    return datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC)


def test_boot_result_includes_active_session_id_and_empty_prior(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        result = start_session(
            repo,
            profile=_profile(),
            preferences=LearnerPreferences(),
            host=HostId.CLAUDE,
            host_conversation_id=None,
            now=_now(),
        )
        assert result.session_id.startswith("sess_")
        assert result.context.prior_sessions == []
        rendered = render_boot_context(result.context)
        assert "First session guidance" in rendered
    finally:
        conn.close()


def test_boot_result_surfaces_prior_sessions(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        # Three prior sessions at distinct last_seen times.
        s1 = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=5))
        repo.touch_session(s1.id, _now() - timedelta(days=5))
        s2 = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=2))
        repo.touch_session(s2.id, _now() - timedelta(days=2))
        s3 = repo.open_session(HostId.CLAUDE, None, _now() - timedelta(days=1))
        repo.touch_session(s3.id, _now() - timedelta(days=1))
        result = start_session(
            repo,
            profile=_profile(),
            preferences=LearnerPreferences(),
            host=HostId.CLAUDE,
            host_conversation_id=None,
            now=_now(),
        )
        prior_ids = [entry.session_id for entry in result.context.prior_sessions]
        # New session is excluded from prior; the three prior ones are present.
        assert result.session_id not in prior_ids
        assert set(prior_ids) == {s1.id, s2.id, s3.id}
    finally:
        conn.close()


def test_checkpoint_payload_is_deterministic(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Same inputs render the same JSON shape (deterministic golden)."""
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        session = repo.open_session(HostId.CLAUDE, None, _now())
        checkpoint = repo.record_checkpoint(
            session_id=session.id,
            modality=CheckpointModality.LESSON,
            step_kind=CheckpointStepKind.PROMPT_SHOWN,
            prompt_ref="lesson_42_step3",
            state=SafeStepState(prompt_ref="lesson_42_step3", step_index=3, total_steps=8),
            summary="Showed past-tense drill step 3/8",
            now=_now(),
        )
        dumped = checkpoint.model_dump(mode="json")
        # Strip volatile id for stable comparison.
        dumped.pop("id")
        expected = {
            "session_id": session.id,
            "modality": "lesson",
            "step_kind": "prompt_shown",
            "prompt_ref": "lesson_42_step3",
            "state": {
                "prompt_ref": "lesson_42_step3",
                "step_index": 3,
                "total_steps": 8,
                "modality_hint": None,
                "labels": [],
            },
            "summary": "Showed past-tense drill step 3/8",
            "created_at": "2026-05-22T12:00:00Z",
        }
        assert json.dumps(dumped, sort_keys=True) == json.dumps(expected, sort_keys=True)
    finally:
        conn.close()
