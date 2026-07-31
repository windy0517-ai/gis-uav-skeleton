@echo off
setlocal EnableExtensions

rem One-click launcher for the Yilan GIS demo system.
set "PROJECT_ROOT=%~dp0"
set "BACKEND_ROOT=%PROJECT_ROOT%backend"
set "VENV_ROOT=%BACKEND_ROOT%\.venv"
set "VENV_PYTHON=%VENV_ROOT%\Scripts\python.exe"
set "REQUIREMENTS=%BACKEND_ROOT%\requirements.txt"
set "DEPENDENCY_MARKER=%VENV_ROOT%\.dependencies-ready"
set "PROVIDER=mock"

title Yilan GIS Launcher
echo ========================================
echo       Yilan GIS one-click launcher
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 goto NO_PYTHON

if not exist "%VENV_PYTHON%" (
    echo [1/4] Creating virtual environment...
    python -m venv "%VENV_ROOT%"
    if errorlevel 1 goto VENV_FAILED
)

if not exist "%DEPENDENCY_MARKER%" (
    echo [2/4] Installing dependencies for first run...
    "%VENV_PYTHON%" -m pip install -r "%REQUIREMENTS%"
    if errorlevel 1 goto PIP_FAILED
    >"%DEPENDENCY_MARKER%" echo ready
) else (
    echo [2/4] Dependencies already installed.
)

echo [3/4] Starting backend service...
start "Yilan Backend" /D "%BACKEND_ROOT%" "%VENV_PYTHON%" app.py
timeout /t 3 /nobreak >nul

echo [4/4] Opening browser...
start "" "http://127.0.0.1:5000/?provider=%PROVIDER%"
echo.
echo System started. Keep the Yilan Backend window open.
timeout /t 3 /nobreak >nul
exit /b 0

:NO_PYTHON
echo Python 3.9 or newer was not found. Install Python and add it to PATH.
goto FAILED

:VENV_FAILED
echo Failed to create the virtual environment.
goto FAILED

:PIP_FAILED
echo Failed to install dependencies. Check your network and try again.
goto FAILED

:FAILED
echo.
pause
exit /b 1
