"""Daily worker outputs and rerun behavior."""

import csv
import json
from datetime import date

from src.analytics import METRICS
from src.worker import run_daily


def test_daily_outputs_and_same_day_rerun(tmp_path) -> None:
    day = date(2026, 10, 2)
    report = run_daily(day, tmp_path)
    json_path = tmp_path / "data" / "json" / "2026-10-02.json"
    csv_path = tmp_path / "data" / "csv" / "2026-10-02.csv"
    assert 50 <= report.total_jobs <= 100
    assert len({result.job_id for result in report.results}) == report.total_jobs
    assert {result.status for result in report.results} <= {"success", "failed"}
    assert {result.metric for result in report.results} == set(METRICS)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["total_jobs"] == len(payload["results"])
    assert payload["successful_jobs"] + payload["failed_jobs"] == payload["total_jobs"]
    assert all(set(result) == {"job_id", "metric", "value", "status", "duration_ms"} for result in payload["results"])
    with csv_path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == ["job_id", "metric", "value", "status", "duration_ms"]
        rows = list(reader)
    assert len(rows) == report.total_jobs
    assert [int(row["job_id"]) for row in rows] == list(range(1, report.total_jobs + 1))

    first_contents = [path.read_bytes() for path in (json_path, csv_path, tmp_path / "DASHBOARD.md")]
    assert run_daily(day, tmp_path) == report
    assert [path.read_bytes() for path in (json_path, csv_path, tmp_path / "DASHBOARD.md")] == first_contents


def test_previous_daily_files_are_preserved(tmp_path) -> None:
    first = tmp_path / "data" / "json" / "2026-10-01.json"
    first.parent.mkdir(parents=True)
    first.write_text("older daily report", encoding="utf-8")
    run_daily(date(2026, 10, 2), tmp_path)
    assert first.read_text(encoding="utf-8") == "older daily report"


def test_failed_job_does_not_stop_later_jobs(tmp_path) -> None:
    class OccasionallyFailingSource:
        def observations(self, day: date, metric: str, job_id: int) -> list[int]:
            if job_id == 2:
                raise RuntimeError("source unavailable")
            return [job_id]

    report = run_daily(date(2026, 10, 2), tmp_path, OccasionallyFailingSource())
    assert report.failed_jobs == 1
    assert report.results[1].status == "failed"
    assert report.results[1].value is None
    assert report.results[-1].status == "success"
    with (tmp_path / "data" / "csv" / "2026-10-02.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[1]["value"] == ""
    assert "Completed with job failures" in (tmp_path / "DASHBOARD.md").read_text(encoding="utf-8")
