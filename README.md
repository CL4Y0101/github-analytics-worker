# GitHub Analytics Worker

A small daily analytics pipeline that processes 50–100 jobs, writes date-based JSON and CSV reports, and updates a Markdown dashboard. The current source supplies **synthetic sample observations** so the project runs without GitHub credentials. It does not report live GitHub repository activity.

## Features

- A date-seeded job count from 50 through 100, with unique sequential job IDs.
- Six supported metrics: commits, pull requests, issues, stars, forks, and workflow runs.
- Per-job failure recording, daily statistics, and successful-value totals by metric.
- Repeatable job results and simulated processing durations. A rerun retains the first report timestamp, producing identical artifacts for the same date.
- One JSON and one CSV file per reporting date, plus a GitHub-readable dashboard.

## Architecture

`src.worker` determines today's date in WIB (UTC+07:00), runs jobs through `src.analytics`, and writes the outputs. `SimulatedSource` supplies eight sample observations for each job; the job sums them into its metric value. The `ObservationSource` protocol is the replacement point for a future GitHub API client. `src.models` holds the report types, and `src.dashboard` renders Markdown.

Source exceptions mark only the affected job as failed. Invalid observation data and output errors stop the run. Successful metric values are summed in the dashboard; failed jobs have a null JSON value and an empty CSV value. Average duration includes all jobs. Durations are deterministic simulated values, not performance measurements.

```text
Data → Worker → Analytics → JSON/CSV → Dashboard
```

## Project structure

```text
.github/workflows/daily.yml  Daily and manual automation
data/json/                  Date-based JSON reports
data/csv/                   Date-based CSV reports
src/models.py               Job and report data types
src/analytics.py            Sources, jobs, and calculations
src/worker.py               Command-line entry point and persistence
src/dashboard.py            Markdown renderer
tests/                      Worker, analytics, and dashboard tests
DASHBOARD.md                Latest generated report
```

## Installation

Use Python 3.12 or newer. From the repository root:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the virtual environment if you want `python` to point to it. Runtime code uses only the Python standard library; `pytest` is the test dependency.

## Local usage

```bash
python -m src.worker
```

The worker writes `data/json/YYYY-MM-DD.json`, `data/csv/YYYY-MM-DD.csv`, and `DASHBOARD.md`. The date is the current WIB calendar date. Previous date files are left in place. Running it again on the same date refreshes the same files with identical content when the source is unchanged.

## Testing

```bash
python -m pytest
```

Tests cover job boundaries and IDs, file formats, calculations, dashboard content, failure handling, and same-day reruns.

## GitHub Actions

The [daily workflow](.github/workflows/daily.yml) runs at `20:00 UTC` (about `03:00 WIB` the next day) and supports manual dispatch. It checks out the repository, sets up Python 3.12, installs test dependencies, runs tests, then runs the worker. It stages only the generated JSON, CSV, and dashboard. A commit named `chore: daily analytics YYYY-MM-DD` is pushed to the branch only when those files change. The workflow uses `contents: write`; repository settings must allow GitHub Actions to write to the branch.

## Output examples

JSON reports contain the date, UTC generation timestamp, daily statistics, and an array of job results. One result looks like this:

```json
{
  "job_id": 1,
  "metric": "commits",
  "value": 130,
  "status": "success",
  "duration_ms": 320
}
```

See the generated daily file for the complete report. CSV columns are `job_id,metric,value,status,duration_ms`.

## Dashboard preview

The generated [dashboard](DASHBOARD.md) shows the latest date and run status, daily job statistics, per-metric totals, the last five jobs, and the pipeline diagram. Its sample-data notice keeps the simulated figures distinct from live repository measurements.

## Future improvements

Implement an `ObservationSource` backed by the GitHub API, with credentials supplied through GitHub Actions secrets. That integration should define repository and time-window semantics for each metric before replacing the simulated source. Historical trend views and measured processing times can then be added without changing the report pipeline.
