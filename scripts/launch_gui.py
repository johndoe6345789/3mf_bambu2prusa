#!/usr/bin/env python3
"""Launch the GUI entrypoint with an optional virtual environment."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parent.parent
GUI_ENTRYPOINT = REPO_ROOT / "bambu_to_prusa_gui.py"
VENV_PATH = REPO_ROOT / ".venv"


def _candidate_pythons() -> list[str]:
    candidates: list[str] = []

    if sys.platform == "darwin":
        for path in ("/opt/homebrew/bin/python3", "/usr/local/bin/python3"):
            if Path(path).exists():
                candidates.append(path)

    for name in ("python3", "python"):
        discovered = shutil.which(name)
        if discovered:
            candidates.append(discovered)

    unique: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def _venv_python() -> Path | None:
    if not VENV_PATH.exists():
        return None
    python_name = "python.exe" if os.name == "nt" else "python"
    candidate = VENV_PATH / ("Scripts" if os.name == "nt" else "bin") / python_name
    return candidate if candidate.exists() else None


def _choose_python() -> Path:
    venv_python = _venv_python()
    if venv_python:
        return venv_python

    candidates = _candidate_pythons()
    if not candidates:
        raise RuntimeError("No Python interpreter found. Please install Python 3.8+.")
    return Path(candidates[0])


def _run(command: Iterable[str]) -> None:
    subprocess.run(list(command), check=True)


def main() -> None:
    python_exe = _choose_python()
    print(f"Launching GUI with interpreter: {python_exe}")

    command = [str(python_exe), str(GUI_ENTRYPOINT), *sys.argv[1:]]
    _run(command)


if __name__ == "__main__":
    main()
