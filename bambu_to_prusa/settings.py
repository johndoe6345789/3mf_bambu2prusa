"""Settings helpers for Bambu2Prusa.

This module stores lightweight user preferences in platform-appropriate
configuration directories (XDG on Unix-like systems, AppData on Windows).
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict


APP_NAME = "bambu2prusa"
DEFAULTS = {"last_input_dir": "", "last_output_dir": ""}


def _default_config_path() -> Path:
    """Return the default settings file path for the current platform."""

    if os.name == "nt":
        base_dir = os.environ.get("APPDATA")
        if base_dir:
            return Path(base_dir) / APP_NAME / "settings.json"
        return Path.home() / "AppData" / "Roaming" / APP_NAME / "settings.json"

    base_dir = os.environ.get("XDG_CONFIG_HOME")
    if base_dir:
        return Path(base_dir) / APP_NAME / "settings.json"

    return Path.home() / ".config" / APP_NAME / "settings.json"


class SettingsManager:
    """Load and persist small bits of user configuration."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = Path(config_path) if config_path else _default_config_path()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.settings: Dict[str, Any] = DEFAULTS.copy()
        self.load()

    def load(self) -> None:
        """Load settings from disk, keeping defaults on errors."""

        if not self.config_path.exists():
            return

        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                self.settings.update({key: str(data.get(key, "")) for key in DEFAULTS})
        except Exception as exc:  # pragma: no cover - defensive logging
            logging.warning("Failed to load settings from %s: %s", self.config_path, exc)
            self.save()

    def save(self) -> None:
        """Persist settings to disk."""

        with self.config_path.open("w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=2)

    @property
    def last_input_dir(self) -> str:
        return str(self.settings.get("last_input_dir", ""))

    @property
    def last_output_dir(self) -> str:
        return str(self.settings.get("last_output_dir", ""))

    def update_last_input_dir(self, path: str) -> None:
        self.settings["last_input_dir"] = path
        self.save()

    def update_last_output_dir(self, path: str) -> None:
        self.settings["last_output_dir"] = path
        self.save()
