"""Create repeatable daily activity commits alongside the analytics report."""

import random
import subprocess
from datetime import date, datetime
from pathlib import Path

from .worker import PROJECT_ROOT, WIB


def target_commit_count(day: date) -> int:
    return random.Random(f"{day.isoformat()}:activity").randint(10, 40)


def commit_activity(day: date, root: Path) -> int:
    """Add the remaining daily commits after the analytics report commit."""
    target = target_commit_count(day)
    created = 0
    for number in range(1, target):
        marker = root / "data" / "activity" / day.isoformat() / f"{number:02d}.txt"
        relative = marker.relative_to(root).as_posix()
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        if tracked:
            continue
        marker.parent.mkdir(parents=True, exist_ok=True)
        if not marker.exists():
            marker.write_text(
                f"Synthetic activity marker {number} for {day.isoformat()}\n",
                encoding="utf-8",
            )
        subprocess.run(["git", "add", "--", relative], cwd=root, check=True)
        subprocess.run(
            ["git", "commit", "--only", "-m",
             f"chore: daily activity {day.isoformat()} ({number}/{target - 1})",
             "--", relative],
            cwd=root, check=True, stdout=subprocess.DEVNULL,
        )
        created += 1
    return created


def main() -> None:
    day = datetime.now(WIB).date()
    created = commit_activity(day, PROJECT_ROOT)
    print(f"Created {created} activity commits for {day}")


if __name__ == "__main__":
    main()
