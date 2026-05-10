@echo off
rem AgentMEMO -- convenience launcher (Windows).
rem
rem First run: creates a .venv and installs the package + deps.
rem Subsequent runs: just launches the GUI.
rem
rem Usage:
rem   run.bat              (or double-click in Explorer)

setlocal
cd /d "%~dp0"

set "VENV=.venv"
set "VENV_PY=%VENV%\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo [setup] creating virtualenv at %VENV%
  python -m venv "%VENV%"
  if errorlevel 1 goto :error
)

"%VENV_PY%" -c "import agentmemo" >nul 2>&1
if errorlevel 1 (
  echo [setup] installing AgentMEMO and its dependencies ^(one-time, ~30s^)
  "%VENV_PY%" -m pip install --upgrade pip --quiet
  if errorlevel 1 goto :error
  "%VENV_PY%" -m pip install -e . --quiet
  if errorlevel 1 goto :error
)

"%VENV_PY%" -m agentmemo %*
goto :eof

:error
echo.
echo Setup failed. Make sure Python 3.10+ is installed and in PATH.
echo Try opening "Python" in the Start menu to check, or download from
echo https://www.python.org/downloads/  (tick "Add to PATH" during install).
echo.
pause
exit /b 1
