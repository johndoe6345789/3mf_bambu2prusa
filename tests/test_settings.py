import json
from pathlib import Path

from bambu_to_prusa.settings import SettingsManager


def test_settings_persist(tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "settings.json"
    settings = SettingsManager(config_path)

    settings.update_last_input_dir("/tmp/input")
    settings.update_last_output_dir("/tmp/output")

    reloaded = SettingsManager(config_path)
    assert reloaded.last_input_dir == "/tmp/input"
    assert reloaded.last_output_dir == "/tmp/output"


def test_settings_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "settings.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("not-json", encoding="utf-8")

    settings = SettingsManager(config_path)
    assert settings.last_input_dir == ""
    assert settings.last_output_dir == ""
    assert json.loads(config_path.read_text(encoding="utf-8")) == {
        "last_input_dir": "",
        "last_output_dir": "",
    }
