from __future__ import annotations

import time

from language_tutor.dal.repositories import TutorRepository
from language_tutor.dal.sqlite_store import connect
from language_tutor.progress import progress_report
from language_tutor.progress_rendering import render_progress_markdown
from language_tutor.schemas import LearnerPreferences, ProgressReportRequest
from tests.fixtures.progress.phase4_scenarios import BASE_TIME, seed_one_year


def test_one_year_progress_json_and_markdown_under_five_seconds(tmp_path) -> None:  # type: ignore[no-untyped-def]
    conn = connect(tmp_path / "db.sqlite3")
    try:
        repo = TutorRepository(conn)
        seed_one_year(repo)
        start = time.perf_counter()
        report = progress_report(
            repo,
            LearnerPreferences(),
            ProgressReportRequest(window_size=30, generated_at=BASE_TIME),
        )
        export = render_progress_markdown(report)
        elapsed = time.perf_counter() - start
        assert report.report_window.actual_session_count == 30
        assert export.content_type == "text/markdown"
        assert elapsed < 5
    finally:
        conn.close()
