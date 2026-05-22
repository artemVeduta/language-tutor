from __future__ import annotations

from datetime import datetime, timedelta

from language_tutor.boot_context import build_boot_context
from language_tutor.dal.repositories import TutorRepository
from language_tutor.schemas import (
    BootResult,
    HostId,
    LearnerPreferences,
    LearnerProfile,
    PriorSessionEntry,
    Session,
    SessionEndInput,
    SessionEndResult,
    SessionLabel,
    SessionStatus,
    SessionView,
)

ABANDONED_AFTER = timedelta(days=14)
DEFAULT_PRIOR_SESSION_LIMIT = 3


def end_session(repo: TutorRepository, payload: SessionEndInput) -> SessionEndResult:
    summary_id, next_focus = repo.record_session_end(
        payload.session_id, payload.analysis, payload.costs
    )
    if summary_id is None:
        return SessionEndResult(session_id=payload.session_id, status="pending")
    return SessionEndResult(
        session_id=payload.session_id,
        status="complete",
        summary_id=summary_id,
        next_focus=next_focus,
    )


def derive_session_label(session: Session, *, is_newest: bool, now: datetime) -> SessionLabel:
    """Read-time label per FR-018. Never stored."""
    if session.status == SessionStatus.CLOSED.value:
        return SessionLabel.CLOSED
    if is_newest:
        return SessionLabel.OPEN
    if now - session.last_seen_at > ABANDONED_AFTER:
        return SessionLabel.ABANDONED
    return SessionLabel.STALE


def session_views(sessions: list[Session], now: datetime) -> list[SessionView]:
    """Annotate ``sessions`` (ordered newest-first by last_seen_at) with labels."""
    if not sessions:
        return []
    newest_id = sessions[0].id
    return [
        SessionView(
            session=session,
            label=derive_session_label(session, is_newest=session.id == newest_id, now=now),
        )
        for session in sessions
    ]


def start_session(
    repo: TutorRepository,
    *,
    profile: LearnerProfile,
    preferences: LearnerPreferences,
    host: HostId,
    host_conversation_id: str | None,
    now: datetime,
    prior_session_limit: int = DEFAULT_PRIOR_SESSION_LIMIT,
) -> BootResult:
    """Mint a session, durably commit it, build boot context with prior history."""
    # Read prior sessions BEFORE creating the new one so the new id is excluded.
    prior_raw = repo.recent_sessions(prior_session_limit)
    views = session_views(prior_raw, now=now)
    prior_sessions = [
        PriorSessionEntry(
            session_id=view.session.id,
            label=view.label,
            last_seen_at=view.session.last_seen_at,
        )
        for view in views
    ]

    session = repo.open_session(host, host_conversation_id, now)
    context = build_boot_context(
        repo, profile, preferences, prior_sessions=prior_sessions
    )
    return BootResult(session_id=session.id, context=context)
