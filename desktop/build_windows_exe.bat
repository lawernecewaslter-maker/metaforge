@echo off
setlocal enabledelayedexpansion

REM Robust Windows build for MetaForgeTradeAI.exe
REM You can run this file from ANY folder; it auto-switches to repo root.

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"

echo [1/6] Locating Python...
set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY_CMD=python"
  )
)

if "%PY_CMD%"=="" (
  echo ERROR: Python not found. Install Python 3.10+ and check "Add Python to PATH".
  exit /b 1
)

echo Using: %PY_CMD%

echo [2/6] Creating build virtual environment...
if exist ".venv-build" rmdir /s /q ".venv-build"
%PY_CMD% -m venv .venv-build
if errorlevel 1 (
  echo ERROR: Failed to create virtual environment.
  exit /b 1
)

echo [3/6] Installing build dependencies...
call ".venv-build\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 (
  echo ERROR: pip upgrade failed.
  exit /b 1
)
python -m pip install pyinstaller
if errorlevel 1 (
  echo ERROR: pyinstaller install failed.
  exit /b 1
)

echo [4/6] Cleaning old build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "MetaForgeTradeAI.spec" del /q "MetaForgeTradeAI.spec"

echo [5/6] Building executable...
python -m PyInstaller --noconfirm --onefile --windowed --name MetaForgeTradeAI desktop\ui_app.py
if errorlevel 1 (
  echo ERROR: PyInstaller build failed.
  exit /b 1
)

echo [6/6] Verifying output...
if not exist "dist\MetaForgeTradeAI.exe" (
  echo ERROR: Build finished but dist\MetaForgeTradeAI.exe not found.
  exit /b 1
)

echo.
echo SUCCESS: Build complete.
echo EXE path: %REPO_ROOT%\dist\MetaForgeTradeAI.exe
endlocal
exit /b 0
