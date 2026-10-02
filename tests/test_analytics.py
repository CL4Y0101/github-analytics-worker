"""Analytics calculations and source behavior."""

from datetime import date

import pytest

from src.analytics import METRICS, SimulatedSource, aggregate_metrics, calculate_statistics, job_count, run_job
from src.models import JobResult


def test_statistics_and_metric_aggregation() -> None:
    results = [
        JobResult(1, "commits", 4, "success", 100),
        JobResult(2, "commits", None, "failed", 200),
        JobResult(3, "issues", 6, "success", 300),
    ]
    assert calculate_statistics(results) == {
        "total_jobs": 3,
        "successful_jobs": 2,
        "failed_jobs": 1,
        "success_rate": 66.67,
        "average_duration_ms": 200.0,
    }
    totals = aggregate_metrics(results)
    assert totals["commits"] == 4
    assert totals["issues"] == 6
    assert all(metric in totals for metric in METRICS)


def test_empty_statistics() -> None:
    assert calculate_statistics([])["success_rate"] == 0.0
    assert calculate_statistics([])["average_duration_ms"] == 0.0


def test_simulated_job_is_repeatable() -> None:
    day = date(2026, 10, 2)
    source = SimulatedSource()
    assert 50 <= job_count(day) <= 100
    assert run_job(day, 1, "commits", source) == run_job(day, 1, "commits", source)


def test_job_failure_is_isolated() -> None:
    class FailingSource:
        def observations(self, day: date, metric: str, job_id: int) -> list[int]:
            raise RuntimeError("temporary source error")

    result = run_job(date(2026, 10, 2), 1, "commits", FailingSource())
    assert result.status == "failed"
    assert result.value is None


def test_corrupted_source_data_is_fatal() -> None:
    class InvalidSource:
        def observations(self, day: date, metric: str, job_id: int) -> list[int]:
            return [-1]

    with pytest.raises(ValueError, match="invalid source observations"):
        run_job(date(2026, 10, 2), 1, "commits", InvalidSource())
