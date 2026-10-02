"""Dashboard rendering checks."""

from datetime import date

from src.analytics import SimulatedSource, aggregate_metrics, create_report
from src.dashboard import generate_dashboard, write_dashboard


def test_dashboard_contains_report_values_and_sections(tmp_path) -> None:
    report = create_report(date(2026, 10, 2), "2026-10-01T20:00:00Z", SimulatedSource())
    path = tmp_path / "DASHBOARD.md"
    write_dashboard(report, path)
    content = path.read_text(encoding="utf-8")
    assert content == generate_dashboard(report)
    for section in ("# GitHub Analytics Worker", "## Daily statistics", "## Metric summary", "## Recent activity", "## Pipeline"):
        assert section in content
    for expected in (
        report.date,
        report.generated_at,
        f"| Total jobs | {report.total_jobs} |",
        f"| Successful jobs | {report.successful_jobs} |",
        f"| Failed jobs | {report.failed_jobs} |",
        f"| Success rate | {report.success_rate:.2f}% |",
        f"| Average processing duration (simulated) | {report.average_duration_ms:.2f} ms |",
        f"| Commits | {aggregate_metrics(report.results)['commits']:,} |",
        "Data → Worker → Analytics → JSON/CSV → Dashboard",
    ):
        assert expected in content
