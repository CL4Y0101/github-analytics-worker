"""Deterministic analytics jobs and report calculations."""

import random
import logging
from collections.abc import Sequence
from datetime import date
from typing import Protocol

from .models import DailyReport, JobResult


METRICS = (
    "commits",
    "pull_requests",
    "issues",
    "stars",
    "forks",
    "workflow_runs",
)
LOGGER = logging.getLogger(__name__)


class ObservationSource(Protocol):
    """Source of observations to aggregate for an individual job."""

    def observations(self, day: date, metric: str, job_id: int) -> Sequence[int]:
        """Return nonnegative counts for a metric and job."""


class SimulatedSource:
    """Provide repeatable sample observations without API credentials."""

    def observations(self, day: date, metric: str, job_id: int) -> Sequence[int]:
        """Create eight deterministic counts for a job."""
        if metric not in METRICS:
            raise ValueError(f"Unsupported metric: {metric}")
        rng = random.Random(f"{day.isoformat()}:{metric}:{job_id}:observations")
        return [rng.randint(0, 30) for _ in range(8)]


def job_count(day: date) -> int:
    """Choose 50 to 100 jobs using the local reporting date as seed."""
    return random.Random(day.isoformat()).randint(50, 100)


def run_job(day: date, job_id: int, metric: str, source: ObservationSource) -> JobResult:
    """Aggregate one metric's observations, recording a repeatable simulated duration."""
    duration_ms = random.Random(f"{day.isoformat()}:{job_id}:duration").randint(100, 600)
    try:
        observations = source.observations(day, metric, job_id)
    except Exception as exc:
        LOGGER.warning("Job %d (%s) failed: %s", job_id, metric, exc)
        return JobResult(job_id, metric, None, "failed", duration_ms)
    if not observations or any(type(value) is not int or value < 0 for value in observations):
        raise ValueError(f"Job {job_id} has invalid source observations")
    value = sum(observations)
    return JobResult(job_id, metric, value, "success", duration_ms)


def calculate_statistics(results: Sequence[JobResult]) -> dict[str, int | float]:
    """Calculate daily counts, success percentage, and mean duration across all jobs."""
    total = len(results)
    successful = sum(result.status == "success" for result in results)
    return {
        "total_jobs": total,
        "successful_jobs": successful,
        "failed_jobs": total - successful,
        "success_rate": round(successful * 100 / total, 2) if total else 0.0,
        "average_duration_ms": round(sum(result.duration_ms for result in results) / total, 2)
        if total else 0.0,
    }


def aggregate_metrics(results: Sequence[JobResult]) -> dict[str, int]:
    """Sum successful values by metric; failed jobs contribute no value."""
    totals = {metric: 0 for metric in METRICS}
    for result in results:
        if result.status == "success" and result.value is not None:
            totals[result.metric] = totals.get(result.metric, 0) + result.value
    return totals


def create_report(day: date, generated_at: str, source: ObservationSource) -> DailyReport:
    """Run the day's jobs and collect them in one report."""
    results = [
        run_job(day, job_id, METRICS[(job_id - 1) % len(METRICS)], source)
        for job_id in range(1, job_count(day) + 1)
    ]
    return DailyReport(day.isoformat(), generated_at, results=results, **calculate_statistics(results))
