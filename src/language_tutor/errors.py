from __future__ import annotations

import json
from typing import TYPE_CHECKING, NoReturn

import click

if TYPE_CHECKING:
    from language_tutor.schemas import HostSetupFailure


class TutorError(Exception):
    def __init__(self, code: str, message: str, repair_hint: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.repair_hint = repair_hint


def error_payload(error: TutorError) -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": error.code,
            "message": error.message,
            "repair_hint": error.repair_hint,
        }
    }


def fail_json(error: TutorError) -> NoReturn:
    click.echo(json.dumps(error_payload(error), ensure_ascii=False, sort_keys=True))
    raise click.exceptions.Exit(1)


def host_setup_failure_payload(failure: HostSetupFailure) -> dict[str, dict[str, str]]:
    """Render a host setup failure as a learner-safe JSON payload.

    The payload names the host, failed phase, category, and data-safety status.
    It never includes secrets, raw learner answers, or local state contents.
    """
    return {
        "host_setup_failure": {
            "host": str(failure.host),
            "phase": str(failure.phase),
            "category": str(failure.category),
            "message": failure.message,
            "remediation": failure.remediation,
            "data_safety": failure.data_safety,
        }
    }


_REMEDIATION_BY_CATEGORY: dict[str, str] = {
    "missing_prerequisite": "Install the named host prerequisite, then retry setup.",
    "invalid_configuration": "Fix the named configuration value, then re-run install.",
    "unsupported_capability": "This flow is gated for the host; use a supported flow.",
    "permission_required": "Grant the named host permission/approval, then retry.",
    "source_changed": "Re-check the official source and update the host setup profile.",
    "unknown": "Re-run setup with verbose output and report the host error.",
}


def default_remediation(category: str) -> str:
    """Return a learner-safe default remediation for a failure category."""
    return _REMEDIATION_BY_CATEGORY.get(category, _REMEDIATION_BY_CATEGORY["unknown"])


def make_host_setup_failure(
    host: str,
    phase: str,
    category: str,
    detail: str,
    *,
    data_safe: bool = True,
    affected_paths: list[str] | None = None,
) -> HostSetupFailure:
    """Build a learner-safe host setup failure naming host, phase, and category.

    The message never includes secrets, raw learner answers, or local state
    contents — only the host, failed phase/category, and the supplied detail.
    """
    from language_tutor.schemas import (
        FailureCategory,
        FailurePhase,
        HostId,
        HostSetupFailure,
    )

    if data_safe:
        data_safety = "No learner data was modified."
    else:
        names = ", ".join(affected_paths or []) or "see host logs"
        data_safety = f"Affected paths: {names}"
    return HostSetupFailure(
        host=HostId(host),
        phase=FailurePhase(phase),
        category=FailureCategory(category),
        message=f"[{host}] {phase} failed: {detail}",
        remediation=default_remediation(category),
        data_safety=data_safety,
    )
