@echo off
REM Audio Transcription - Windows Launcher
REM Delegates to launcher.py for cross-platform setup

set SCRIPT_DIR=%~dp0

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python "%SCRIPT_DIR%launcher.py" %*
    exit /b %ERRORLEVEL%
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python3 "%SCRIPT_DIR%launcher.py" %*
    exit /b %ERRORLEVEL%
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3 "%SCRIPT_DIR%launcher.py" %*
    exit /b %ERRORLEVEL%
)

echo Error: Python 3 no encontrado.
echo Descargar de https://www.python.org/downloads/
echo Marcar "Add Python to PATH" durante la instalacion.
pause
exit /b 1
