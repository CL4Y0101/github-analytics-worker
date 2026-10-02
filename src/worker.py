"""CLI entry point and daily report persistence."""

import csv
import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .analytics import ObservationSource, SimulatedSource, create_report
from .dashboard import write_dashboard
from .models import DailyReport


LOGGER = logging.getLogger(__name__)
WIB = timezone(timedelta(hours=7))
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FIELDS = ("job_id", "metric", "value", "status", "duration_ms")


def write_report(report: DailyReport, root: Path) -> tuple[Path, Path]:
    """Write the date's JSON and CSV files without touching older dates."""
    json_path = root / "data" / "json" / f"{report.date}.json"
    csv_path = root / "data" / "csv" / f"{report.date}.csv"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(result.to_dict() for result in report.results)
    return json_path, csv_path


def run_daily(day: date, root: Path, source: ObservationSource | None = None) -> DailyReport:
    """Process one WIB date and save its JSON, CSV, and dashboard."""
    json_path = root / "data" / "json" / f"{day.isoformat()}.json"
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    if json_path.exists():
        try:
            previous = json.loads(json_path.read_text(encoding="utf-8"))
            if previous["date"] != day.isoformat() or not isinstance(previous["generated_at"], str):
                raise ValueError("Existing report has invalid date or timestamp")
            generated_at = previous["generated_at"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError(f"Cannot read existing daily report: {json_path}") from exc
    report = create_report(day, generated_at, source if source is not None else SimulatedSource())
    json_output, csv_output = write_report(report, root)
    write_dashboard(report, root / "DASHBOARD.md")
    LOGGER.info("Processed %d analytics jobs (%d failed)", report.total_jobs, report.failed_jobs)
    LOGGER.info("Generated %s, %s, and DASHBOARD.md", json_output, csv_output)
    return report


def main() -> int:
    """Run today's analytics and return a process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run_daily(datetime.now(WIB).date(), PROJECT_ROOT)
    except (OSError, ValueError) as exc:
        LOGGER.error("Daily analytics failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
