"""Data structures shared by the worker and report renderers."""

from dataclasses import asdict, dataclass
from typing import Literal


Status = Literal["success", "failed"]


@dataclass(frozen=True)
class JobResult:
    """Result of one analytics job; failed jobs have no metric value."""

    job_id: int
    metric: str
    value: int | None
    status: Status
    duration_ms: int

    def to_dict(self) -> dict[str, int | str | None]:
        """Return the public JSON and CSV fields in their documented order."""
        return asdict(self)


@dataclass(frozen=True)
class DailyReport:
    """One date's results and aggregate statistics."""

    date: str
    generated_at: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    success_rate: float
    average_duration_ms: float
    results: list[JobResult]

    def to_dict(self) -> dict[str, object]:
        """Return the documented JSON report structure."""
        return asdict(self)
