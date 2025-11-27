"""Safety check to ensure no merge conflict markers remain in tracked files."""

from pathlib import Path
import subprocess


def test_repository_has_no_merge_conflicts():
    repo_root = Path(__file__).resolve().parents[1]
    tracked_files = subprocess.check_output(["git", "ls-files"], cwd=repo_root, text=True).splitlines()

    conflict_markers = tuple(marker.encode() for marker in ("<" * 7, "=" * 7, ">" * 7))
    offenders = []

    for relative_path in tracked_files:
        file_path = repo_root / relative_path
        if file_path.is_dir():
            continue

        data = file_path.read_bytes()
        if any(marker in data for marker in conflict_markers):
            offenders.append(relative_path)

    assert not offenders, f"Files with merge conflict markers: {offenders}"
