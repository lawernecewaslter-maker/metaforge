from pathlib import Path

from desktop.build_engine import BuildEngine
from desktop.config import BuildConfig, load_config


def test_load_config_defaults_when_missing(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "missing.json")
    assert cfg.build.app_name == "MetaForgeTradeAI"


def test_pyinstaller_command_contains_required_flags() -> None:
    cfg = BuildConfig(app_name="MetaForgeTradeAI", icon_path="missing.ico", output_dir="release")
    engine = BuildEngine(cfg)
    cmd = engine._pyinstaller_cmd()
    assert "--clean" in cmd
    assert "--onefile" in cmd
    assert "--windowed" in cmd
    assert "desktop/ui_app.py" in cmd
