"""Helpers for detecting cloud-backed storage folders for output defaults."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional

# Common cloud storage root folder names. The order reflects typical install precedence.
CLOUD_ROOT_CANDIDATES = (
    "Dropbox",
    "OneDrive",
    "Google Drive",
    "iCloud Drive",
)


def _existing_path(candidates: Iterable[Path]) -> Path | None:
    for candidate in candidates:
        expanded = candidate.expanduser()
        if expanded.exists():
            return expanded
    return None


def detect_cloud_storage_root(home: Optional[Path] = None) -> Path | None:
    """Return a cloud storage directory if common options are found."""

    base_home = home or Path.home()

    env_candidates = [
        Path(os.environ[var])
        for var in ("OneDriveCommercial", "OneDriveConsumer", "OneDrive")
        if os.environ.get(var)
    ]

    fallback_candidates = [base_home / name for name in CLOUD_ROOT_CANDIDATES]
    onedrive_globs = list(base_home.glob("OneDrive*"))

    icloud_candidates = [
        base_home / "Library" / "Mobile Documents" / "com~apple~CloudDocs",
        base_home / "Library" / "CloudStorage" / "iCloud Drive",
        base_home / "iCloudDrive",
    ]

    return _existing_path([*env_candidates, *fallback_candidates, *onedrive_globs, *icloud_candidates])
