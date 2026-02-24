# MetaForge Trade AI Desktop + ChatGPT Backend

MetaForge now includes a modular desktop client with a **real integrated EXE build system** and a market-research backend.

## Project structure

- `app/` — market API client, trade-analysis models, backend endpoints.
- `desktop/` — desktop UI, build engine, logging, config loader, CLI build entrypoint.
- `config/app_config.json` — theme/build/version settings.
- `.github/workflows/build-windows-exe.yml` — cloud build + downloadable artifacts.

## Desktop app features

- Research-center snapshot tab (live data from MetaForge APIs).
- Trade evaluator tab (ACCEPT / HOLD / DECLINE logic).
- **Download Build tab** with:
  - real PyInstaller invocation,
  - live build logs,
  - progress indicator,
  - success/failure popups,
  - output directory picker,
  - build-time estimate,
  - build history recording (`build_history.json`).
- Error handling + persistent logging (`logs/metaforge_desktop.log`).
- Version shown in app title.
- Theme toggle support via config (`dark` / `light`).
- Icon integration via config (`build.icon_path`) with graceful fallback when icon file is missing.
- Digital-signature placeholder included in config model.

## Run desktop app (dev)

```bash
python -m desktop.ui_app
```

## Build executable (integrated, no .bat)

Exact packaging command path (used by UI and CI):

```bash
python -m desktop.build_cli --output-dir release
```

What build does:

1. Detect/install missing `pyinstaller`.
2. Clean `build/` and `dist/` artifacts.
3. Compile and bundle all dependencies with PyInstaller.
4. Generate single-file executable.
5. Copy final EXE to `release/MetaForgeTradeAI.exe`.
6. Write full logs + build history.

## Download prebuilt executable

Use GitHub Actions artifacts from `Build Windows EXE` workflow:

- `MetaForgeTradeAI-win64` (zip)
- `MetaForgeTradeAI-exe` (raw exe)

## Backend run

```bash
python app/main.py
```

Endpoints:

- `GET /health`
- `GET /market/research-center`
- `GET /market/live-updates`
- `POST /market/trade-evaluation`
- `GET /openapi.json`
