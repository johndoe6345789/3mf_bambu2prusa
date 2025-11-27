"""Tests for detecting default cloud storage directories."""

import pytest

from bambu_to_prusa.cloud_storage import CLOUD_ROOT_CANDIDATES, detect_cloud_storage_root


@pytest.fixture(autouse=True)
def clear_onedrive_env(monkeypatch):
    for key in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        monkeypatch.delenv(key, raising=False)


def test_prefers_onedrive_environment_variable(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    onedrive_dir = tmp_path / "cloud"
    onedrive_dir.mkdir()

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("OneDrive", str(onedrive_dir))

    assert detect_cloud_storage_root() == onedrive_dir


def test_falls_back_to_icloud_location(tmp_path, monkeypatch):
    home = tmp_path / "home"
    cloud_root = home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
    cloud_root.mkdir(parents=True)

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    assert detect_cloud_storage_root() == cloud_root


def test_favors_first_known_candidate(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    first = home / CLOUD_ROOT_CANDIDATES[0]
    second = home / CLOUD_ROOT_CANDIDATES[1]
    first.mkdir()
    second.mkdir()

    assert detect_cloud_storage_root(home=home) == first


def test_returns_none_when_no_candidates_exist(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    assert detect_cloud_storage_root() is None
