#!/usr/bin/env python3
"""Create a virtual environment and install dependencies.

The script prefers the Homebrew Python on macOS to avoid using the
system-provided interpreter. It falls back to other available Python
executables on the PATH.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


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


def _choose_python() -> Path:
    candidates = _candidate_pythons()
    if not candidates:
        raise RuntimeError("No Python interpreter found. Please install Python 3.8+.")
    return Path(candidates[0])


def _venv_bin(venv_path: Path) -> Path:
    return venv_path / ("Scripts" if os.name == "nt" else "bin")


def _run(command: Iterable[str]) -> None:
    subprocess.run(list(command), check=True)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    venv_path = repo_root / ".venv"
    requirements = repo_root / "requirements.txt"

    python_exe = _choose_python()
    print(f"Using Python interpreter: {python_exe}")

    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path} ...")
        _run((str(python_exe), "-m", "venv", str(venv_path)))
    else:
        print(f"Virtual environment already exists at {venv_path}, reusing it.")

    pip_exe = _venv_bin(venv_path) / ("pip.exe" if os.name == "nt" else "pip")

    print("Upgrading pip ...")
    _run((str(pip_exe), "install", "--upgrade", "pip"))

    print("Installing requirements ...")
    _run((str(pip_exe), "install", "-r", str(requirements)))

    activation_hint = (
        f"source {venv_path / 'bin' / 'activate'}"
        if os.name != "nt"
        else f"{venv_path / 'Scripts' / 'activate'}"
    )
    print("\nSetup complete.")
    print(f"Activate the virtual environment with: {activation_hint}")
    print("Launch the GUI with: python scripts/launch_gui.py")


if __name__ == "__main__":
    main()
