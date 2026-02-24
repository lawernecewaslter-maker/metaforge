from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable

from desktop.config import BuildConfig
from desktop.history import BuildHistoryEntry, BuildHistoryStore

log = logging.getLogger(__name__)


@dataclass
class BuildResult:
    success: bool
    exe_path: Path | None
    message: str
    duration_seconds: float


class BuildEngine:
    def __init__(self, config: BuildConfig, history_store: BuildHistoryStore | None = None) -> None:
        self.config = config
        self.history_store = history_store or BuildHistoryStore()

    def _pyinstaller_cmd(self) -> list[str]:
        cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean"]
        if self.config.one_file:
            cmd.append("--onefile")
        if self.config.windowed:
            cmd.append("--windowed")
        if self.config.optimize:
            cmd += ["--optimize", str(self.config.optimize)]
        icon = Path(self.config.icon_path)
        if icon.exists():
            cmd += ["--icon", str(icon)]
        cmd += ["--name", self.config.app_name, "desktop/ui_app.py"]
        cmd += self.config.extra_pyinstaller_args
        return cmd

    def _detect_and_install_deps(self, on_log: Callable[[str], None]) -> None:
        try:
            import PyInstaller  # noqa: F401
            on_log("PyInstaller detected.")
        except ModuleNotFoundError:
            on_log("PyInstaller missing. Installing automatically...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    def build(self, on_log: Callable[[str], None]) -> BuildResult:
        started = datetime.now(timezone.utc)
        start_ts = started.timestamp()
        exe_path = Path("dist") / f"{self.config.app_name}.exe"
        output_dir = Path(self.config.output_dir)

        try:
            on_log("Checking dependencies...")
            self._detect_and_install_deps(on_log)

            on_log("Cleaning old build artifacts...")
            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("dist", ignore_errors=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            cmd = self._pyinstaller_cmd()
            on_log(f"Build command: {' '.join(cmd)}")

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            assert process.stdout is not None
            for line in process.stdout:
                on_log(line.rstrip())
            rc = process.wait()
            if rc != 0:
                raise RuntimeError(f"PyInstaller failed with exit code {rc}")

            if not exe_path.exists():
                raise FileNotFoundError(f"Build completed but missing executable: {exe_path}")

            target = output_dir / exe_path.name
            shutil.copy2(exe_path, target)
            duration = datetime.now(timezone.utc).timestamp() - start_ts
            message = f"Build complete. Executable saved to {target}"
            on_log(message)
            self._record_history(started, "success", target, duration)
            return BuildResult(True, target, message, duration)
        except Exception as exc:  # noqa: BLE001
            duration = datetime.now(timezone.utc).timestamp() - start_ts
            error_message = f"Build failed: {exc}"
            log.exception("Build failed")
            on_log(error_message)
            self._record_history(started, "failed", exe_path, duration)
            return BuildResult(False, None, error_message, duration)

    def _record_history(self, started: datetime, status: str, output_exe: Path, duration_seconds: float) -> None:
        entry = BuildHistoryEntry(
            started_at=started.isoformat(),
            finished_at=datetime.now(timezone.utc).isoformat(),
            status=status,
            output_exe=str(output_exe),
            duration_seconds=round(duration_seconds, 2),
            log_file="logs/metaforge_desktop.log",
        )
        self.history_store.append(entry)
