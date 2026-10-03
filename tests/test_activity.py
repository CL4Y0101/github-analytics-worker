"""Daily activity commit count and rerun behavior."""

import subprocess
from datetime import date

from src.activity import commit_activity, target_commit_count


def test_target_commit_count_is_repeatable_and_bounded() -> None:
    days = [date(2026, 10, day) for day in range(1, 8)]
    counts = [target_commit_count(day) for day in days]
    assert all(10 <= count <= 40 for count in counts)
    assert counts == [target_commit_count(day) for day in days]


def test_activity_commits_resume_without_duplicates(tmp_path, monkeypatch) -> None:
    day = date(2026, 10, 3)
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path,
                   check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"],
                   cwd=tmp_path, check=True)
    report = tmp_path / "data" / "json" / f"{day}.json"
    report.parent.mkdir(parents=True)
    report.write_text("{}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "daily report"], cwd=tmp_path,
                   check=True, capture_output=True)
    monkeypatch.setattr("src.activity.target_commit_count", lambda _: 10)

    assert commit_activity(day, tmp_path) == 9
    assert commit_activity(day, tmp_path) == 0
    count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"],
                                    cwd=tmp_path)
    assert int(count) == 10
    assert len(list((tmp_path / "data" / "activity" / str(day)).glob("*.txt"))) == 9
