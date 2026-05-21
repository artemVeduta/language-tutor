from __future__ import annotations

import json

from language_tutor.dal.paths import resolve_paths
from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from tests.conftest import invoke_json
from tests.fixtures.progress.phase4_scenarios import seed_mixed_history


def test_progress_json_payload_and_privacy(runner) -> None:  # type: ignore[no-untyped-def]
    conn = connect(resolve_paths().database_path)
    try:
        seed_mixed_history(TutorRepository(conn), 3)
    finally:
        conn.close()
    report = invoke_json(
        runner,
        ["progress", "--json", '{"window_size":3,"generated_at":"2026-05-21T12:00:00Z"}'],
    )
    assert report["generated_at"] == "2026-05-21T12:00:00Z"
    assert report["report_window"]["requested_session_count"] == 3  # type: ignore[index]
    assert "tag_mastery" in report
    serialized = json.dumps(report)
    assert "private answer" not in serialized
    assert "private span" not in serialized
    assert "private prose" not in serialized


def test_progress_markdown_direct_export(runner) -> None:  # type: ignore[no-untyped-def]
    report = invoke_json(
        runner,
        ["progress", "--json", '{"format":"markdown","generated_at":"2026-05-21T12:00:00Z"}'],
    )
    assert report["content_type"] == "text/markdown"
    assert "# Progress Report" in report["markdown"]


def test_render_progress_report_command(runner) -> None:  # type: ignore[no-untyped-def]
    report = invoke_json(
        runner,
        ["progress", "--json", '{"generated_at":"2026-05-21T12:00:00Z"}'],
    )
    rendered = invoke_json(runner, ["render", "progress-report", "--json", json.dumps(report)])
    assert rendered["content_type"] == "text/markdown"
    assert rendered["generated_at"] == "2026-05-21T12:00:00Z"


def test_progress_request_validation_errors(runner) -> None:  # type: ignore[no-untyped-def]
    result = runner.invoke(
        __import__("language_tutor.cli").cli.main,
        ["progress", "--json", '{"window_size":0}'],
    )
    assert result.exit_code == 1
    assert "invalid_progress_request" in result.output
    bad = runner.invoke(
        __import__("language_tutor.cli").cli.main,
        ["progress", "--json", '{"format":"svg"}'],
    )
    assert bad.exit_code == 1
    assert "invalid_progress_request" in bad.output
