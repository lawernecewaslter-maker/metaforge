# Download the EXE (No local Python required)

If you do **not** want to run Python on your PC, use the prebuilt artifact from GitHub Actions.

## How to get it

1. Open the repository on GitHub.
2. Click **Actions**.
3. Open workflow: **Build Windows EXE**.
4. Open the latest successful run.
5. Download artifact:
   - `MetaForgeTradeAI-win64` (zip), or
   - `MetaForgeTradeAI-exe` (raw exe)

## What you get

- `MetaForgeTradeAI.exe` you can run directly on Windows.

## Notes

- Windows may show SmartScreen warning on first run for unsigned binaries.
- If you want this to feel like a polished product, next step is code signing certificate + installer (MSI/Inno Setup).
