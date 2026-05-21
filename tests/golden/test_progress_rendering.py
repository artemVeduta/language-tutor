from __future__ import annotations

from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.progress import progress_report
from language_tutor.progress_rendering import render_progress_markdown
from language_tutor.schemas import LearnerPreferences, ProgressReportRequest
from tests.fixtures.progress.phase4_scenarios import BASE_TIME, seed_mixed_history


def test_progress_markdown_no_data(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        report = progress_report(
            TutorRepository(conn),
            LearnerPreferences(),
            ProgressReportRequest(generated_at=BASE_TIME),
        )
        markdown = render_progress_markdown(report).markdown
        assert "# Progress Report" in markdown
        assert "No mastery evidence yet." in markdown
        assert "Start vocabulary or writing practice." in markdown
    finally:
        conn.close()


def test_progress_markdown_non_empty_is_stable_and_ascii(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        seed_mixed_history(repo, 10)
        request = ProgressReportRequest(window_size=10, generated_at=BASE_TIME)
        report = progress_report(repo, LearnerPreferences(), request)
        markdown_a = render_progress_markdown(report).markdown
        markdown_b = render_progress_markdown(report).markdown
        assert markdown_a == markdown_b
        assert "## Tag Mastery" in markdown_a
        first_section = [line for line in markdown_a.splitlines() if line.strip()][:30]
        assert any("case" in line or "aspect" in line for line in first_section)
        assert all(len(line) <= 120 for line in markdown_a.splitlines())
        assert "Mermaid" not in markdown_a
        assert "SVG" not in markdown_a
    finally:
        conn.close()
