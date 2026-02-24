@echo off
setlocal

REM Build MetaForge desktop app as Windows .exe with PyInstaller
REM Run from repository root on Windows.

python -m pip install --upgrade pip
python -m pip install pyinstaller

pyinstaller --noconfirm --onefile --windowed --name MetaForgeTradeAI desktop\ui_app.py

echo.
echo Build complete. EXE path:
echo dist\MetaForgeTradeAI.exe
