"""Lightweight theming engine with plugin discovery for the GUI."""

import importlib.util
import logging
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterable, List, Optional


@dataclass
class Theme:
    """Represents a named theme palette and metadata."""

    name: str
    palette: Dict[str, str]
    description: str = ""
    author: str = ""
    source: Optional[Path] = None

    def resolved_palette(self, fallback: Dict[str, str]) -> Dict[str, str]:
        """Merge this theme with a fallback palette to fill missing keys."""

        merged = fallback.copy()
        merged.update(self.palette)
        return merged


class ThemeEngine:
    """Load themes from built-ins and external plugin files."""

    def __init__(self, base_theme: Theme, plugin_dirs: Optional[Iterable[Path]] = None):
        self.base_theme = base_theme
        self.plugin_dirs = list(plugin_dirs or [])
        self.themes: Dict[str, Theme] = {}
        self.register_theme(base_theme)
        self._load_plugins()

    def register_theme(self, theme: Theme) -> None:
        """Register a theme by name, replacing any existing entry."""

        self.themes[theme.name] = theme

    def _load_plugins(self) -> None:
        for directory in self.plugin_dirs:
            if not directory.exists():
                continue
            for path in directory.glob("*.py"):
                loaded = self._load_theme_from_file(path)
                if loaded:
                    self.register_theme(loaded)

    def _load_theme_from_file(self, path: Path) -> Optional[Theme]:
        spec = importlib.util.spec_from_file_location(f"bambu_theme_{path.stem}", path)
        if spec is None or spec.loader is None:
            logging.debug("Skipping theme plugin with missing spec: %s", path)
            return None

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # pragma: no cover - defensive, plugin provided by users
            logging.error("Failed to load theme plugin %s: %s", path, exc)
            return None

        theme_obj = self._extract_theme_object(module)
        if theme_obj is None:
            logging.debug("No THEME or get_theme() found in %s", path)
            return None

        if isinstance(theme_obj, Theme):
            return theme_obj

        if isinstance(theme_obj, dict):
            palette = theme_obj.get("palette") or {k: v for k, v in theme_obj.items() if isinstance(v, str)}
            name = theme_obj.get("name") or path.stem
            description = theme_obj.get("description", "")
            author = theme_obj.get("author", "")
            return Theme(name=name, palette=palette, description=description, author=author, source=path)

        logging.debug("Unsupported theme object in %s: %s", path, type(theme_obj))
        return None

    @staticmethod
    def _extract_theme_object(module: ModuleType) -> Optional[object]:
        factory = getattr(module, "get_theme", None)
        if callable(factory):
            return factory()
        return getattr(module, "THEME", None)

    def available_themes(self) -> List[str]:
        return list(self.themes.keys())

    def palette_for(self, name: str) -> Dict[str, str]:
        theme = self.themes.get(name, self.base_theme)
        return theme.resolved_palette(self.base_theme.palette)
