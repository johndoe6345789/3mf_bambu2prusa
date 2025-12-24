"""Tests for frontend helpers that don't require a display."""

from frontends.common import first_existing_dir


def test_first_existing_dir_returns_first_existing(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()

    choice = first_existing_dir(str(existing), str(tmp_path / "missing"))
    assert choice == str(existing)


def test_first_existing_dir_skips_missing(tmp_path):
    assert first_existing_dir(str(tmp_path / "missing")) is None
