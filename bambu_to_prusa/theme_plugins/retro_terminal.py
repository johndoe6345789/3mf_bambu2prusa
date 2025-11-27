"""A neon terminal-inspired plugin theme for the GUI."""

from bambu_to_prusa.theme_engine import Theme


def get_theme() -> Theme:
    return Theme(
        name="Retro Terminal",
        description="High-contrast terminal greens with warm highlights.",
        author="Bambu2Prusa",
        palette={
            "bg": "#0b0f0c",
            "panel": "#111a13",
            "panel_outline": "#1c2b1e",
            "text": "#e2ffe5",
            "muted": "#8ac58f",
            "accent": "#3aff7a",
            "accent_alt": "#f5b971",
            "warning": "#f8d66d",
        },
    )
