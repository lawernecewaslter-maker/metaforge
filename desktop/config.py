from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json


DEFAULT_CONFIG_PATH = Path("config/app_config.json")


@dataclass
class BuildConfig:
    app_name: str = "MetaForgeTradeAI"
    version: str = "1.1.0"
    icon_path: str = "assets/app.ico"
    output_dir: str = "release"
    one_file: bool = True
    windowed: bool = True
    optimize: int = 2
    upx: bool = True
    extra_pyinstaller_args: list[str] = field(default_factory=list)
    signing_placeholder: str = "TODO: Sign executable with code signing certificate"


@dataclass
class AppConfig:
    theme: str = "dark"
    auto_check_updates: bool = False
    update_url: str = ""
    build: BuildConfig = field(default_factory=BuildConfig)


def _merge_build(raw: dict) -> BuildConfig:
    cfg = BuildConfig()
    for key, value in raw.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)
    return cfg


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    if not path.exists():
        return AppConfig()

    data = json.loads(path.read_text(encoding="utf-8"))
    build_raw = data.get("build", {}) if isinstance(data, dict) else {}
    build = _merge_build(build_raw if isinstance(build_raw, dict) else {})

    cfg = AppConfig(build=build)
    if isinstance(data, dict):
        cfg.theme = str(data.get("theme", cfg.theme))
        cfg.auto_check_updates = bool(data.get("auto_check_updates", cfg.auto_check_updates))
        cfg.update_url = str(data.get("update_url", cfg.update_url))
    return cfg
