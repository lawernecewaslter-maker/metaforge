from __future__ import annotations

import json
import logging
from dataclasses import asdict
from queue import Queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.analysis import evaluate_trade
from app.metaforge_client import MetaForgeClient
from app.models import ItemSide
from desktop.build_engine import BuildEngine
from desktop.config import AppConfig, load_config
from desktop.history import BuildHistoryStore
from desktop.logger import configure_logging


class MetaForgeDesktopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.cfg: AppConfig = load_config()
        self.log_path = configure_logging()
        self.logger = logging.getLogger(__name__)

        self.title(f"MetaForge Trade AI v{self.cfg.build.version}")
        self.geometry("1080x760")
        self.minsize(960, 680)
        self.client = MetaForgeClient(timeout=20)
        self.log_queue: Queue[str] = Queue()

        self._configure_style()
        self._build_layout()
        self.after(100, self._pump_logs)

    def _configure_style(self) -> None:
        dark = self.cfg.theme == "dark"
        bg = "#111827" if dark else "#f3f4f6"
        fg = "#e5e7eb" if dark else "#111827"

        self.configure(bg=bg)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=fg)
        style.configure("Card.TLabelframe", background=bg, foreground=fg)
        style.configure("Card.TLabelframe.Label", background=bg, foreground=fg, font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="MetaForge Trade AI Desktop", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text=f"Version {self.cfg.build.version} • Log: {self.log_path}").pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.market_tab = ttk.Frame(notebook)
        self.trade_tab = ttk.Frame(notebook)
        self.build_tab = ttk.Frame(notebook)
        self.log_tab = ttk.Frame(notebook)
        notebook.add(self.market_tab, text="Research Center")
        notebook.add(self.trade_tab, text="Trade Evaluator")
        notebook.add(self.build_tab, text="Download Build")
        notebook.add(self.log_tab, text="Logs")

        self._build_market_tab()
        self._build_trade_tab()
        self._build_builder_tab()
        self._build_log_tab()

    def _build_market_tab(self) -> None:
        wrapper = ttk.Frame(self.market_tab, padding=10)
        wrapper.pack(fill="both", expand=True)
        ttk.Button(wrapper, text="Refresh Live Snapshot", command=self.refresh_snapshot).pack(anchor="w", pady=(0, 8))
        self.snapshot_text = tk.Text(wrapper, wrap="word", relief="flat")
        self.snapshot_text.pack(fill="both", expand=True)

    def _build_trade_tab(self) -> None:
        wrapper = ttk.Frame(self.trade_tab, padding=10)
        wrapper.pack(fill="both", expand=True)

        self.trade_input = tk.Text(wrapper, height=12)
        self.trade_input.pack(fill="both", expand=True)
        self.trade_input.insert(
            "1.0",
            json.dumps(
                {
                    "giving": [{"name": "A", "current_lowest_listing": 100, "avg_7d": 96, "recent_trend_pct": 1, "liquidity_score": 8}],
                    "receiving": [{"name": "B", "current_lowest_listing": 115, "avg_7d": 112, "recent_trend_pct": 2, "liquidity_score": 7}],
                },
                indent=2,
            ),
        )

        ttk.Button(wrapper, text="Evaluate Trade", command=self.evaluate_trade_from_input).pack(anchor="w", pady=8)
        self.trade_output = tk.Text(wrapper, height=12)
        self.trade_output.pack(fill="both", expand=True)

    def _build_builder_tab(self) -> None:
        wrapper = ttk.Frame(self.build_tab, padding=10)
        wrapper.pack(fill="both", expand=True)

        top = ttk.Frame(wrapper)
        top.pack(fill="x")

        ttk.Label(top, text="Output Directory:").pack(side="left")
        self.output_dir_var = tk.StringVar(value=self.cfg.build.output_dir)
        ttk.Entry(top, textvariable=self.output_dir_var, width=48).pack(side="left", padx=6)
        ttk.Button(top, text="Browse", command=self.select_output_dir).pack(side="left")
        ttk.Button(top, text="Download Build", command=self.start_build).pack(side="left", padx=8)

        self.estimate_var = tk.StringVar(value="Estimated build time: 2-5 minutes")
        ttk.Label(wrapper, textvariable=self.estimate_var).pack(anchor="w", pady=(8, 4))

        self.progress = ttk.Progressbar(wrapper, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))

        self.build_status = tk.Text(wrapper, height=18)
        self.build_status.pack(fill="both", expand=True)

    def _build_log_tab(self) -> None:
        wrapper = ttk.Frame(self.log_tab, padding=10)
        wrapper.pack(fill="both", expand=True)
        self.log_text = tk.Text(wrapper)
        self.log_text.pack(fill="both", expand=True)
        self._log("Desktop app ready.")

    def _log(self, message: str) -> None:
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.logger.info(message)

    def _pump_logs(self) -> None:
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.build_status.insert("end", f"{message}\n")
            self.build_status.see("end")
            self._log(message)
        self.after(120, self._pump_logs)

    def refresh_snapshot(self) -> None:
        def run() -> None:
            self._log("Fetching live market snapshot...")
            try:
                snapshot = self.client.research_center_snapshot()
                self.snapshot_text.delete("1.0", "end")
                self.snapshot_text.insert("1.0", json.dumps(snapshot, indent=2))
                self._log("Snapshot updated.")
            except Exception as exc:  # noqa: BLE001
                self.snapshot_text.delete("1.0", "end")
                self.snapshot_text.insert("1.0", f"Error: {exc}")
                messagebox.showerror("Snapshot Error", str(exc))
                self._log(f"Snapshot failed: {exc}")

        threading.Thread(target=run, daemon=True).start()

    def evaluate_trade_from_input(self) -> None:
        try:
            payload = json.loads(self.trade_input.get("1.0", "end").strip())
            giving = [ItemSide(**item) for item in payload.get("giving", [])]
            receiving = [ItemSide(**item) for item in payload.get("receiving", [])]
            result = evaluate_trade(giving, receiving)
            self.trade_output.delete("1.0", "end")
            self.trade_output.insert("1.0", json.dumps(asdict(result), indent=2))
            self._log("Trade evaluated.")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Evaluation Error", str(exc))
            self._log(f"Trade evaluation failed: {exc}")

    def select_output_dir(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.output_dir_var.set(selected)

    def start_build(self) -> None:
        self.cfg.build.output_dir = self.output_dir_var.get().strip() or self.cfg.build.output_dir
        self.progress.start(8)
        self.build_status.delete("1.0", "end")

        def run_build() -> None:
            engine = BuildEngine(self.cfg.build, history_store=BuildHistoryStore())
            result = engine.build(on_log=lambda msg: self.log_queue.put(msg))
            self.after(0, self.progress.stop)
            if result.success:
                self.after(0, lambda: messagebox.showinfo("Build Success", result.message))
            else:
                self.after(0, lambda: messagebox.showerror("Build Failed", result.message))

        threading.Thread(target=run_build, daemon=True).start()


def main() -> None:
    app = MetaForgeDesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
