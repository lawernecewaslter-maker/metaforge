from __future__ import annotations

import json
import threading
import tkinter as tk
from dataclasses import asdict
from tkinter import ttk

from app.analysis import evaluate_trade
from app.metaforge_client import MetaForgeClient
from app.models import ItemSide


class MetaForgeDesktopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MetaForge Trade AI")
        self.geometry("980x680")
        self.minsize(900, 620)
        self.configure(bg="#0f172a")
        self.client = MetaForgeClient(timeout=20)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#f8fafc")
        style.configure("Card.TLabelframe", background="#1f2937", foreground="#dbeafe")
        style.configure("Card.TLabelframe.Label", background="#1f2937", foreground="#dbeafe", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", background="#2563eb", foreground="white", padding=6)

        self._build_layout()

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)

        header = ttk.Label(root, text="MetaForge Trade AI (Desktop)", style="Title.TLabel")
        header.pack(anchor="w", pady=(0, 8))

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.market_tab = ttk.Frame(notebook)
        self.trade_tab = ttk.Frame(notebook)
        self.log_tab = ttk.Frame(notebook)

        notebook.add(self.market_tab, text="Research Center")
        notebook.add(self.trade_tab, text="Trade Evaluator")
        notebook.add(self.log_tab, text="Live Log")

        self._build_market_tab()
        self._build_trade_tab()
        self._build_log_tab()

    def _build_market_tab(self) -> None:
        wrapper = ttk.Frame(self.market_tab, padding=12)
        wrapper.pack(fill="both", expand=True)

        actions = ttk.Frame(wrapper)
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(actions, text="Refresh Live Snapshot", command=self.refresh_snapshot).pack(side="left")

        self.snapshot_text = tk.Text(wrapper, wrap="word", bg="#0b1220", fg="#e2e8f0", insertbackground="#e2e8f0", relief="flat")
        self.snapshot_text.pack(fill="both", expand=True)

    def _build_trade_tab(self) -> None:
        wrapper = ttk.Frame(self.trade_tab, padding=12)
        wrapper.pack(fill="both", expand=True)

        top = ttk.LabelFrame(wrapper, text="Input JSON (giving / receiving)", style="Card.TLabelframe")
        top.pack(fill="both", expand=True)

        sample = {
            "giving": [
                {"name": "Item A", "current_lowest_listing": 100, "avg_7d": 95, "recent_trend_pct": 2, "liquidity_score": 8}
            ],
            "receiving": [
                {"name": "Item B", "current_lowest_listing": 120, "avg_7d": 110, "recent_trend_pct": 4, "liquidity_score": 7}
            ],
        }

        self.trade_input = tk.Text(top, height=14, wrap="word", bg="#0b1220", fg="#e2e8f0", insertbackground="#e2e8f0", relief="flat")
        self.trade_input.pack(fill="both", expand=True, padx=8, pady=8)
        self.trade_input.insert("1.0", json.dumps(sample, indent=2))

        actions = ttk.Frame(wrapper)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Evaluate Trade", command=self.evaluate_trade_from_input).pack(side="left")

        bottom = ttk.LabelFrame(wrapper, text="Decision", style="Card.TLabelframe")
        bottom.pack(fill="both", expand=True)

        self.trade_output = tk.Text(bottom, height=12, wrap="word", bg="#0b1220", fg="#d1fae5", insertbackground="#d1fae5", relief="flat")
        self.trade_output.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_log_tab(self) -> None:
        wrapper = ttk.Frame(self.log_tab, padding=12)
        wrapper.pack(fill="both", expand=True)

        self.log_text = tk.Text(wrapper, wrap="word", bg="#0b1220", fg="#cbd5e1", insertbackground="#cbd5e1", relief="flat")
        self.log_text.pack(fill="both", expand=True)
        self._log("Desktop app ready.")

    def _log(self, message: str) -> None:
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def refresh_snapshot(self) -> None:
        def run() -> None:
            self._log("Pulling live research snapshot...")
            try:
                snapshot = self.client.research_center_snapshot()
                content = json.dumps(snapshot, indent=2)
                self.snapshot_text.delete("1.0", "end")
                self.snapshot_text.insert("1.0", content)
                self._log("Snapshot updated.")
            except Exception as exc:  # noqa: BLE001
                self.snapshot_text.delete("1.0", "end")
                self.snapshot_text.insert("1.0", f"Error: {exc}")
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
            self._log("Trade evaluated successfully.")
        except Exception as exc:  # noqa: BLE001
            self.trade_output.delete("1.0", "end")
            self.trade_output.insert("1.0", f"Input error: {exc}")
            self._log(f"Trade evaluation failed: {exc}")


def main() -> None:
    app = MetaForgeDesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
