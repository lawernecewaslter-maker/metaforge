from __future__ import annotations

import argparse

from desktop.build_engine import BuildEngine
from desktop.config import load_config
from desktop.history import BuildHistoryStore
from desktop.logger import configure_logging


def main() -> int:
    parser = argparse.ArgumentParser(description="Build MetaForge desktop executable")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    configure_logging()
    cfg = load_config()
    if args.output_dir:
        cfg.build.output_dir = args.output_dir

    engine = BuildEngine(cfg.build, history_store=BuildHistoryStore())
    result = engine.build(on_log=print)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
