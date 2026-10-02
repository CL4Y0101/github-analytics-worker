"""GitHub-readable Markdown dashboard generation."""

from pathlib import Path

from .analytics import aggregate_metrics
from .models import DailyReport


def generate_dashboard(report: DailyReport) -> str:
    """Render the latest report as a Markdown dashboard."""
    status = "Success" if report.failed_jobs == 0 else "Completed with job failures"
    lines = [
        "# GitHub Analytics Worker",
        "",
        "> Synthetic sample data. Values and processing durations are simulated; this report does not measure a live repository.",
        "",
        f"**Current date (WIB):** {report.date}  ",
        f"**Latest run status:** {status}  ",
        f"**Generated at (UTC):** {report.generated_at}",
        "",
        "## Daily statistics",
        "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Total jobs | {report.total_jobs} |",
        f"| Successful jobs | {report.successful_jobs} |",
        f"| Failed jobs | {report.failed_jobs} |",
        f"| Success rate | {report.success_rate:.2f}% |",
        f"| Average processing duration (simulated) | {report.average_duration_ms:.2f} ms |",
        "",
        "## Metric summary",
        "",
        "Successful job values, summed by metric.",
        "",
        "| Metric | Total |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {metric.replace('_', ' ').title()} | {total:,} |" for metric, total in aggregate_metrics(report.results).items())
    lines.extend([
        "",
        "## Recent activity",
        "",
        "The last five jobs from this run.",
        "",
        "| Job | Metric | Value | Status | Duration |",
        "| ---: | --- | ---: | --- | ---: |",
    ])
    lines.extend(
        f"| {result.job_id} | {result.metric.replace('_', ' ').title()} | "
        f"{result.value if result.value is not None else '—'} | {result.status} | {result.duration_ms} ms |"
        for result in report.results[-5:]
    )
    lines.extend([
        "",
        "## Pipeline",
        "",
        "```text",
        "Data → Worker → Analytics → JSON/CSV → Dashboard",
        "```",
        "",
    ])
    return "\n".join(lines)


def write_dashboard(report: DailyReport, path: Path) -> None:
    """Write the dashboard file for a daily report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_dashboard(report), encoding="utf-8")
